#!/usr/bin/python

from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.core import run
from bacpypes.task import RecurringTask
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogValueObject, register_object_type
from bacpypes.local.object import AnalogValueCmdObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.service.cov import ChangeOfValueServices
from bacpypes.service.object import ReadWritePropertyMultipleServices

import pandas as pd
import numpy as np

from sklearn.neural_network import MLPRegressor
import datetime

_debug = 0
_log = ModuleLogger(globals())

register_object_type(AnalogValueCmdObject, vendor_id=999)

# sample data in seconds of power meter
# written to writeable AV
INTERVAL = 60.0

@bacpypes_debugging
class SampleApplication(
    BIPSimpleApplication, ReadWritePropertyMultipleServices, ChangeOfValueServices
):
    pass

@bacpypes_debugging
class DoDataScience(RecurringTask):
    def __init__(self, interval, input_power, one_hr_future_pwr, power_rate_of_change):
        super().__init__(interval * 1000)
        self.interval = interval
        self.input_power = input_power
        self.one_hr_future_pwr = one_hr_future_pwr
        self.power_rate_of_change = power_rate_of_change

    def process_task(self):
        
        print("input_power \n", self.input_power.presentValue)
        print("one_hr_future_pwr \n", self.one_hr_future_pwr.presentValue)
        print("power_rate_of_change \n", self.power_rate_of_change.presentValue)

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
            description="writeable input for app buildings electricity power value"
        )
        self.app.add_object(self.input_power)

        self.one_hr_future_pwr = AnalogValueObject(
            objectIdentifier=("analogValue", 2),
            objectName="one-hour-future-power",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="electrical power one hour into the future"
        )
        self.app.add_object(self.one_hr_future_pwr)

        self.power_rate_of_change = AnalogValueObject(
            objectIdentifier=("analogValue", 3),
            objectName="power-rate-of-change",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="current electrical power rate of change"
        )
        self.app.add_object(self.power_rate_of_change)

        self.task = DoDataScience(
            INTERVAL, self.input_power, self.one_hr_future_pwr, self.power_rate_of_change
        )
        self.task.install_task()

    def run(self):
        run()


class PowerMeterForecast:
    def __init__(self):
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

        self.DAYS_TO_CACHE = 21  # days of data one minute intervals
        self.CACHE_LIMIT = 1440 * self.DAYS_TO_CACHE
        self.SPIKE_THRESHOLD_POWER_PER_MINUTE = 20
        self.BUILDING_POWER_SETPOINT = 20
        
    def update_rolling_avg_data(self, timestamp, usage_kW):
        new_row = {"Date": timestamp, "Usage_kW": usage_kW}
        self.rolling_avg_data = self.rolling_avg_data.append(new_row, ignore_index=True)
        self.calculate_rolling_average()

    def calculate_rolling_average(self, window_size=60):
        self.rolling_avg_data["Date"] = pd.to_datetime(self.rolling_avg_data["Date"])
        self.rolling_avg_data["rolling_avg"] = self.rolling_avg_data["Usage_kW"].rolling(window=window_size).mean()
        self.rolling_avg_data.dropna(subset=["rolling_avg"], inplace=True)
        
    def update_input_power(self, timestamp, sensor_reading):
        # Update the input_power object's presentValue with the sensor_reading
        self.input_power.presentValue = sensor_reading

    def get_input_power(self):
        # Return the input_power object's presentValue
        return self.input_power.presentValue

    def get_one_hr_future_pwr(self):
        # Return the one_hr_future_pwr object's presentValue
        return self.one_hr_future_pwr.presentValue

    def get_power_rate_of_change(self):
        # Return the power_rate_of_change object's presentValue
        return self.power_rate_of_change.presentValue

    def create_dataset(self, y, input_window=60, forecast_horizon=1):
        dataX, dataY = [], []
        length = len(y) - input_window - forecast_horizon + 1
        print("LENGTH: ",length)
        for i in range(length):
            dataX.append(y[i : (i + input_window)])
            dataY.append(y[i + input_window : i + input_window + forecast_horizon])
        return np.array(dataX), np.array(dataY)

    def poll_sensor_data(self, sensor_reading=None):
        if sensor_reading is not None:
            return pd.Timestamp(datetime.now(), sensor_reading)
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
        calculate electric power rate of change per unit of time
        from cached data. Used to detect if a spike has occurred.
        """

        gradient = np.diff(self.data_cache)
        current_rate_of_change = gradient[-1] if len(gradient) > 0 else 0

        # Average rate of change over the last 15 minutes
        if len(self.data_cache) > 15:
            avg_rate_of_change = (gradient[-1] - gradient[-15]) / 15.0
        else:
            avg_rate_of_change = current_rate_of_change

        self.current_power_last_15mins_avg = avg_rate_of_change
        self.current_power_lv_rate_of_change = current_rate_of_change

    # check for peak or valley
    def check_percentiles(self, current_value):
        percentile_30 = np.percentile(self.data_cache, 30)
        percentile_90 = np.percentile(self.data_cache, 90)

        is_below_30th = current_value < percentile_30
        is_above_90th = current_value > percentile_90

        return is_below_30th, is_above_90th

    def run_forecasting_cycle(self):
        
        data_available = self.fetch_and_store_data()
        if not data_available:
            return

        current_time = self.data_cache["ds"].iloc[-1]
        current_value = self.data_cache["y"].iloc[-1]

        print("run_forecasting_cycle current_value: ",current_value)

        if current_value = -1.0 # default vals its not getting data
            return

        y = self.data_cache["y"].values

        if len(y) > 120 and (
            self.last_train_time is None
            # or (current_time - last_train_time) >= pd.Timedelta(days=1)
        ):
            print("Fit Model Called!")
            X, Y = self.create_dataset(y)

            self.model = MLPRegressor()
            
            self.model.fit(X, Y.ravel())
            self.last_train_time = current_time
            self.model_trained = True

        if not self.model_trained:
            print(f"model hasn't trained yet {current_time}")
            return

        # attempts to detect a spike, like equipment startup
        self.calc_power_rate_of_change()

        self.forecasted_value_60 = self.model.predict(y[-60:].reshape(1, -1))[0]

        self.is_valley, self.is_peak = self.check_percentiles(current_value)
        
        if self.is_valley:
            print("Valley!")
        elif self.is_peak:
            print("Peak!")


if __name__ == "__main__":
    parser = ConfigArgumentParser(description=__doc__)
    args = parser.parse_args()
    power_forecast = PowerMeterForecast()
    bacnet_server = BacnetServer(args.ini, args.ini.address)
    bacnet_server.run()
