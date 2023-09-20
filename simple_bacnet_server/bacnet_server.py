#!/usr/bin/python

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

import pandas as pd
import numpy as np

from sklearn.neural_network import MLPRegressor
from datetime import datetime
import threading, time

_debug = 0
_log = ModuleLogger(globals())

register_object_type(AnalogValueCmdObject, vendor_id=999)

# sample data in seconds of power meter
# written to writeable AV
INTERVAL = 60.0
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
        print("input_power \n", self.input_power.presentValue)
        print("one_hr_future_pwr \n", self.one_hr_future_pwr.presentValue)
        print("power_rate_of_change \n", self.power_rate_of_change.presentValue)
        print("high_load_bv \n", self.high_load_bv.presentValue)
        print("low_load_bv \n", self.low_load_bv.presentValue)

        # Call the forecasting cycle
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

        self.rolling_avg_data = pd.DataFrame(columns=["Date", "Usage_kW"])

        self.data_counter = 0
        self.data_cache = pd.DataFrame(columns=["ds", "y"])

        self.current_power_last_15mins_avg_rate_of_change = None
        self.current_power_lv_rate_of_change = None
        self.forecasted_value_60 = None
        self.is_valley = None
        self.is_peak = None

        self.model = None
        self.last_train_time = None
        self.model_trained = False
        self.training_started_today = False
        self.total_training_time_minutes = 0

        self.DAYS_TO_CACHE = 28  # days of data one minute intervals
        self.CACHE_LIMIT = 1440 * self.DAYS_TO_CACHE
        self.SPIKE_THRESHOLD_POWER_PER_MINUTE = 20
        self.BUILDING_POWER_SETPOINT = 20

    def update_rolling_avg_data(self, timestamp, usage_kW):
        new_row = {"Date": timestamp, "Usage_kW": usage_kW}
        self.rolling_avg_data = self.rolling_avg_data.append(new_row, ignore_index=True)
        self.calculate_rolling_average()

    def calculate_rolling_average(self, window_size=60):
        self.rolling_avg_data["Date"] = pd.to_datetime(self.rolling_avg_data["Date"])
        self.rolling_avg_data["rolling_avg"] = (
            self.rolling_avg_data["Usage_kW"].rolling(window=window_size).mean()
        )
        self.rolling_avg_data.dropna(subset=["rolling_avg"], inplace=True)

    def set_one_hr_future_pwr(self, value):
        # Update the one_hr_future_pwr object's presentValue with the provided value
        self.one_hr_future_pwr.presentValue = Real(value)
        print("one_hr_future_pwr: \n", self.one_hr_future_pwr.presentValue)

    def set_power_rate_of_change(self, value):
        # Update the power_rate_of_change object's presentValue with the provided value
        self.power_rate_of_change.presentValue = Real(value)
        print("power_rate_of_change: \n", self.power_rate_of_change.presentValue)

    def set_high_load_bv(self, value_str):
        # Update the high_load_bv object's presentValue with the provided value
        # BVs can only be "active" or "inactive"
        self.high_load_bv.presentValue = value_str
        print("high_load_bv: \n", self.high_load_bv.presentValue)

    def set_low_load_bv(self, value_str):
        # Update the low_load_bv object's presentValue with the provided value
        # BVs can only be "active" or "inactive"
        self.low_load_bv.presentValue = value_str
        print("low_load_bv: \n", self.low_load_bv.presentValue)

    def get_input_power(self):
        # Return the input_power object's presentValue
        return self.input_power.presentValue

    def get_one_hr_future_pwr(self):
        # Return the one_hr_future_pwr object's presentValue
        return self.one_hr_future_pwr.presentValue
    
    def get_if_a_model_is_available(self):
        # Return bool is a model has been trained yet
        return hasattr(self.model, "coefs_")

    def get_power_rate_of_change(self):
        # Return the power_rate_of_change object's presentValue
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

        new_row = {"ds": timestamp, "y": new_data}
        self.data_cache = pd.concat(
            [self.data_cache, pd.DataFrame([new_row])], ignore_index=True
        )

        if len(self.data_cache) > self.CACHE_LIMIT:
            self.data_cache = self.data_cache.iloc[-self.CACHE_LIMIT :]
        return True


    def calc_power_rate_of_change(self):
        """
        Calculate electric power rate of change per unit of time
        from cached data. Used to detect if a spike has occurred.
        """

        # Extract the 'y' column
        y_values = self.data_cache['y'].values

        # Compute the gradient
        gradient = np.diff(y_values)
        current_rate_of_change = gradient[-1] if len(gradient) > 0 else 0

        # Average rate of change over the last 15 minutes
        if len(gradient) >= 15:
            avg_rate_of_change = (gradient[-1] - gradient[-15]) / 15.0
        else:
            avg_rate_of_change = current_rate_of_change

        self.current_power_last_15mins_avg = avg_rate_of_change
        self.current_power_lv_rate_of_change = current_rate_of_change
        

    def check_percentiles(self, current_value):
        # Use only the 'y' column for percentile calculation
        y_values = self.data_cache['y']
        
        percentile_30 = np.percentile(y_values, 30)
        percentile_90 = np.percentile(y_values, 90)

        is_below_30th = current_value < percentile_30
        is_above_90th = current_value > percentile_90

        return is_below_30th, is_above_90th


    def train_model_thread(self):
        try:
            print("Fit Model Called!")
            X, Y = self.create_dataset(self.data_cache["y"].values)

            start_time = time.time()
            self.model = MLPRegressor()
            self.model.fit(X, Y.ravel())

            self.total_training_time_minutes = (time.time() - start_time) / 60

            self.last_train_time = datetime.now()
            self.model_trained = True

            print(f"Model training time: {self.total_training_time_minutes:.2f} minutes on {self.last_train_time}")

        except Exception as e:
            print(f"An error occurred during the model training: {e}")
            # debug purposes exit the program totally
            if DEBUG_MODE:
                exit(1)
                

    def run_forecasting_cycle(self):
        now = datetime.now()
        data_cache_len = len(self.data_cache)

        if not self.data_cache.empty:
            data_cache_lv = self.data_cache['y'].iloc[-1]
        else:
            return

        # Skip model training if last y value is -1.0
        if data_cache_lv == -1.0:
            return
        
        # not enough data to train a model
        if data_cache_len < 65:
            return
            
        # Train a model at midnight just once
        if now.hour == 0 and not self.training_started_today:
            model_training_thread = threading.Thread(target=self.train_model_thread)
            model_training_thread.start()
            self.training_started_today = True
        elif now.hour == 1:
            self.training_started_today = False

        # If no model is trained yet, return
        if not self.model_trained or not self.get_if_a_model_is_available():
            return

        # Forecasting and other operations
        y = self.data_cache["y"].values
        self.forecasted_value_60 = self.model.predict(y[-60:].reshape(1, -1))[0]
        self.set_one_hr_future_pwr(self.forecasted_value_60)

        # Detect spikes and set power state
        self.calc_power_rate_of_change()
        self.set_power_rate_of_change(self.current_power_lv_rate_of_change)

        # set BACnet BVs for peak or valley
        self.is_valley, self.is_peak = self.check_percentiles(data_cache_lv)
        self.set_power_state_based_on_peak_valley()
        
        if DEBUG_MODE:
            print("data_cache_len: ", data_cache_len)
            print("now.hour: ", now.hour)
            print("now.minute: ", now.minute)
            print("self.training_started_today: ", self.training_started_today)
            print("data_cache_lv: ", data_cache_lv)



if __name__ == "__main__":
    parser = ConfigArgumentParser(description=__doc__)
    args = parser.parse_args()

    bacnet_server = BacnetServer(args.ini, args.ini.address)
    bacnet_server.run()
