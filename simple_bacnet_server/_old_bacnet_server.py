import subprocess
import configparser
from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.core import run
from bacpypes.task import RecurringTask
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogValueObject, register_object_type, BinaryValueObject
from bacpypes.local.object import AnalogValueCmdObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.service.cov import ChangeOfValueServices
from bacpypes.service.object import ReadWritePropertyMultipleServices
from bacpypes.primitivedata import Real

import numpy as np

from sklearn.neural_network import MLPRegressor
from datetime import datetime
import threading, time

_debug = 0
_log = ModuleLogger(globals())

register_object_type(AnalogValueCmdObject, vendor_id=999)

INTERVAL = 60.0
MODEL_TRAIN_HOUR = 0
DEBUG_MODE = True

@bacpypes_debugging
class SampleApplication(
    BIPSimpleApplication, ReadWritePropertyMultipleServices, ChangeOfValueServices
):
    pass

@bacpypes_debugging
class DoDataScience(RecurringTask):
    def __init__(
        self,
        interval,
        input_power,
        one_hr_future_pwr,
        power_rate_of_change,
        high_load_bv,
        low_load_bv,
    ):
        super().__init__(interval * 1000)
        self.interval = interval
        self.input_power = input_power
        self.one_hr_future_pwr = one_hr_future_pwr
        self.power_rate_of_change = power_rate_of_change
        self.high_load_bv = high_load_bv
        self.low_load_bv = low_load_bv
        self.power_forecast = PowerMeterForecast(
            self.input_power,
            self.one_hr_future_pwr,
            self.power_rate_of_change,
            self.high_load_bv,
            self.low_load_bv,
        )

    def process_task(self):
        if DEBUG_MODE:
            print()
            print("input_power: ", self.input_power.presentValue)
            print("one_hr_future_pwr: ", self.one_hr_future_pwr.presentValue)
            print("power_rate_of_change: ", self.power_rate_of_change.presentValue)
            print("high_load_bv: ", self.high_load_bv.presentValue)
            print("low_load_bv: ", self.low_load_bv.presentValue)

        self.power_forecast.run_forecasting_cycle()

class BacnetServer:
    def __init__(self, ini_file, address):
        self.this_device = LocalDeviceObject(ini=ini_file)
        self.app = SampleApplication(self.this_device, address)

        self.input_power = AnalogValueCmdObject(
            objectIdentifier=("analogValue", 1),
            objectName="input-power-meter",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="writeable input for app buildings electricity power value",
        )
        self.app.add_object(self.input_power)

        self.one_hr_future_pwr = AnalogValueObject(
            objectIdentifier=("analogValue", 2),
            objectName="one-hour-future-power",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="electrical power one hour into the future",
        )
        self.app.add_object(self.one_hr_future_pwr)

        self.power_rate_of_change = AnalogValueObject(
            objectIdentifier=("analogValue", 3),
            objectName="power-rate-of-change",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="current electrical power rate of change",
        )
        self.app.add_object(self.power_rate_of_change)

        self.high_load_bv = BinaryValueObject(
            objectIdentifier=("binaryValue", 1),
            objectName="high-load-conditions",
            presentValue="inactive",
            statusFlags=[0, 0, 0, 0],
            description="Peak power usage detected, shed loads if possible",
        )
        self.app.add_object(self.high_load_bv)

        self.low_load_bv = BinaryValueObject(
            objectIdentifier=("binaryValue", 2),
            objectName="low-load-conditions",
            presentValue="inactive",
            statusFlags=[0, 0, 0, 0],
            description="Low power usage detected, charge TES or battery okay",
        )
        self.app.add_object(self.low_load_bv)

        self.task = DoDataScience(
            INTERVAL,
            self.input_power,
            self.one_hr_future_pwr,
            self.power_rate_of_change,
            self.high_load_bv,
            self.low_load_bv,
        )
        self.task.install_task()

    def run(self):
        run()

class PowerMeterForecast:
    def __init__(
        self,
        input_power,
        one_hr_future_pwr,
        power_rate_of_change,
        high_load_bv,
        low_load_bv,
    ):
        self.input_power = input_power
        self.one_hr_future_pwr = one_hr_future_pwr
        self.power_rate_of_change = power_rate_of_change
        self.high_load_bv = high_load_bv
        self.low_load_bv = low_load_bv

        self.rolling_avg_data = []
        self.data_counter = 0
        self.data_cache = []

        self.current_power_last_15mins_avg_rate_of_change = None
        self.current_power_lv_rate_of_change = None
        self.forecasted_value_60 = None
        self.is_valley = None
        self.is_peak = None

        self.model = None
        self.last_train_time = None
        self.training_started_today = False
        self.total_training_time_minutes = 0
        self.model_train_hour = MODEL_TRAIN_HOUR

        self.DAYS_TO_CACHE = 28
        self.CACHE_LIMIT = 1440 * self.DAYS_TO_CACHE
        self.SPIKE_THRESHOLD_POWER_PER_MINUTE = 20
        self.BUILDING_POWER_SETPOINT = 20

    def update_rolling_avg_data(self, timestamp, usage_kW):
        self.rolling_avg_data.append((timestamp, usage_kW))
        self.calculate_rolling_average()

    def calculate_rolling_average(self, window_size=60):
        if len(self.rolling_avg_data) < window_size:
            return
        usage_values = np.array([item[1] for item in self.rolling_avg_data])
        rolling_avg = np.convolve(usage_values, np.ones(window_size) / window_size, mode='valid')
        self.rolling_avg_data = self.rolling_avg_data[-len(rolling_avg):]
        for i in range(len(rolling_avg)):
            self.rolling_avg_data[i] = (self.rolling_avg_data[i][0], rolling_avg[i])

    def set_one_hr_future_pwr(self, value):
        self.one_hr_future_pwr.presentValue = Real(value)
        print("one_hr_future_pwr: ", self.one_hr_future_pwr.presentValue)

    def set_power_rate_of_change(self, value):
        self.power_rate_of_change.presentValue = Real(value)
        print("power_rate_of_change: ", self.power_rate_of_change.presentValue)

    def set_high_load_bv(self, value_str):
        self.high_load_bv.presentValue = value_str
        print("high_load_bv: ", self.high_load_bv.presentValue)

    def set_low_load_bv(self, value_str):
        self.low_load_bv.presentValue = value_str
        print("low_load_bv: ", self.low_load_bv.presentValue)

    def get_input_power(self):
        return self.input_power.presentValue

    def get_one_hr_future_pwr(self):
        return self.one_hr_future_pwr.presentValue

    def get_if_a_model_is_available(self):
        return hasattr(self.model, "coefs_")

    def get_power_rate_of_change(self):
        return self.power_rate_of_change.presentValue

    def set_power_state_based_on_peak_valley(self):
        if self.is_peak:
            self.set_high_load_bv("active")
            self.set_low_load_bv("inactive")
            print("Setting BVs to Peak!")
        elif self.is_valley:
            self.set_high_load_bv("inactive")
            self.set_low_load_bv("active")
            print("Setting BVs to Valley!")
        else:
            self.set_high_load_bv("inactive")
            self.set_low_load_bv("inactive")
            print("Setting BVs to Valley!")

    def create_dataset(self, y, input_window=60, forecast_horizon=1):
        dataX, dataY = [], []
        length = len(y) - input_window - forecast_horizon + 1
        print("LENGTH: ", length)
        for i in range(length):
            dataX.append(y[i : (i + input_window)])
            dataY.append(y[i + input_window : i + input_window + forecast_horizon])
        return np.array(dataX), np.array(dataY)

    def poll_sensor_data(self, sensor_reading=None):
        sensor_reading = self.get_input_power()
        if sensor_reading is not None:
            return datetime.now(), sensor_reading
        return None, None

    def fetch_and_store_data(self):
        timestamp, new_data = self.poll_sensor_data()

        if timestamp is None:
            return False

        self.data_cache.append((timestamp, new_data))

        if len(self.data_cache) > self.CACHE_LIMIT:
            self.data_cache = self.data_cache[-self.CACHE_LIMIT:]

        return True

    def calc_power_rate_of_change(self):
        if len(self.data_cache) == 0:
            return

        y_values = np.array([item[1] for item in self.data_cache])
        gradient = np.diff(y_values)
        current_rate_of_change = gradient[-1] if len(gradient) > 0 else 0

        if len(gradient) >= 15:
            avg_rate_of_change = (gradient[-1] - gradient[-15]) / 15.0
        else:
            avg_rate_of_change = current_rate_of_change

        self.current_power_last_15mins_avg = avg_rate_of_change
        self.current_power_lv_rate_of_change = current_rate_of_change

    def check_percentiles(self, current_value):
        if len(self.data_cache) == 0:
            return False, False

        y_values = np.array([item[1] for item in self.data_cache])
        percentile_30 = np.percentile(y_values, 30)
        percentile_90 = np.percentile(y_values, 90)

        is_below_30th = current_value < percentile_30
        is_above_90th = current_value > percentile_90

        return is_below_30th, is_above_90th

    def train_model_thread(self):
        try:
            print("Fit Model Called!")
            X, Y = self.create_dataset(np.array([item[1] for item in self.data_cache]))

            start_time = time.time()
            self.model = MLPRegressor()
            self.model.fit(X, Y.ravel())

            self.total_training_time_minutes = (time.time() - start_time) / 60
            self.last_train_time = datetime.now()
            
            print(
                f"Model Trained Success Minutes: \n{self.total_training_time_minutes:.2f}"
            )
            
        except Exception as e:
            print(f"An error occurred during the model training: {e}")
            if DEBUG_MODE:
                exit(1)

    def run_forecasting_cycle(self):
        data_available = self.fetch_and_store_data()
        if not data_available:
            print("Data not available. Returning early.")
            return

        now = datetime.now()
        data_cache_len = len(self.data_cache)

        if DEBUG_MODE:
            print("Data Cache Length: ", data_cache_len)
            print("Current Hour: ", now.hour)
            print("Current Minute: ", now.minute)
            print("Training Started Today: ", self.training_started_today)
            print("Model Availability: ", self.get_if_a_model_is_available())
            print(
                f"Model training time: {self.total_training_time_minutes:.2f} minutes on {self.last_train_time}"
            )

        if not self.data_cache:
            print("Data Cache is empty - RETURN")
            return

        data_cache_lv = self.data_cache[-1][1]
        if DEBUG_MODE:
            print("Data Cache last value: ", data_cache_lv)

        if data_cache_lv == -1.0:
            print("data_cache_lv == -1.0 - RETURN")
            return

        if data_cache_len < 65:
            print("data_cache_len < 65 - RETURN")
            return

        if now.hour == self.model_train_hour and not self.training_started_today:
            model_training_thread = threading.Thread(target=self.train_model_thread)
            model_training_thread.start()
            self.training_started_today = True
        elif now.hour == 1:
            self.training_started_today = False

        if not self.get_if_a_model_is_available():
            print("Model not trained yet, no data science - RETURN")
            return

        y = np.array([item[1] for item in self.data_cache])
        self.forecasted_value_60 = self.model.predict(y[-60:].reshape(1, -1))[0]
        self.set_one_hr_future_pwr(self.forecasted_value_60)

        self.calc_power_rate_of_change()
        self.set_power_rate_of_change(self.current_power_lv_rate_of_change)

        self.is_valley, self.is_peak = self.check_percentiles(data_cache_lv)
        self.set_power_state_based_on_peak_valley()

def get_ip_address():
    try:
        output = subprocess.check_output(["ip", "route", "get", "1"]).decode("utf-8")
        for line in output.split("\n"):
            if "src" in line:
                return line.strip().split("src")[1].split()[0]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def update_ini_with_constants(new_address):
    config = configparser.ConfigParser()
    config.read("BACpypes.ini")
    if "BACpypes" not in config:
        config["BACpypes"] = {}
    
    config["BACpypes"]["address"] = f"{new_address}/24"
    config["BACpypes"]["objectname"] = "OpenDsm"
    config["BACpypes"]["objectidentifier"] = "500001"
    config["BACpypes"]["maxapdulengthaccepted"] = "1024"
    config["BACpypes"]["segmentationsupported"] = "segmentedBoth"
    config["BACpypes"]["vendoridentifier"] = "15"

    with open("BACpypes.ini", "w") as configfile:
        config.write(configfile)

def main():
    detected_ip_address = get_ip_address()
    use_constants = False
    if detected_ip_address:
        print(f"Detected IP Address: {detected_ip_address}")
        use_constants = True
    else:
        print("Unable to find IP address. Using default INI values.")
    
    if use_constants:
        update_ini_with_constants(detected_ip_address)

    parser = ConfigArgumentParser(description=__doc__)
    args = parser.parse_args()

    bacnet_server = BacnetServer(args.ini, args.ini.address)
    bacnet_server.run()

if __name__ == "__main__":
    main()
