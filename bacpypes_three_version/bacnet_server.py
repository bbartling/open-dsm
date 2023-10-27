import asyncio, time

from bacpypes3.debugging import ModuleLogger
from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.primitivedata import Real
from bacpypes3.app import Application
from bacpypes3.local.analog import AnalogValueObject
from bacpypes3.local.binary import BinaryValueObject
from bacpypes3.local.cmd import Commandable

import numpy as np

from sklearn.neural_network import MLPRegressor
from datetime import datetime

_debug = 0
_log = ModuleLogger(globals())

INTERVAL = 60.0  # dont adjust
MODEL_TRAIN_HOUR = 0  # midnight
DEFAULT_PV = -1.0


class CommandableAnalogValueObject(Commandable, AnalogValueObject):
    """
    Commandable Analog Value Object
    """

class DataHanger:
    def __init__(self):
        self.one_hr_future_pwr_lv = DEFAULT_PV
        self.power_rate_of_change_lv = DEFAULT_PV
        self.high_load_bv_lv = "inactive"
        self.low_load_bv_lv = "inactive"

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
        
data_hanger = DataHanger()



class SampleApplication(Application):

    async def update_bacnet_api(self):
        counter = 0
        while True:
            try:
                await asyncio.sleep(0.5)

                one_hr_future_pwr.presentValue = Real(
                    self.data_hanger.one_hr_future_pwr_lv
                )
                power_rate_of_change.presentValue = Real(
                    self.data_hanger.power_rate_of_change_lv
                )
                high_load_bv.presentValue = self.data_hanger.high_load_bv_lv
                low_load_bv.presentValue = self.data_hanger.low_load_bv_lv

                counter += 1
                if counter == 120:
                    counter = 0
                    _log.debug("update_bacnet_api GO!")

            except Exception as e:
                _log.error(f"Error in update_bacnet_api: {e}")

    async def update_rolling_avg_data(self, timestamp, usage_kW):
        self.data_hanger.rolling_avg_data.append((timestamp, usage_kW))
        self.calculate_rolling_average()

    async def calculate_rolling_average(self, window_size=5):
        if len(self.data_hanger.rolling_avg_data) < window_size:
            return
        usage_values = np.array([item[1] for item in self.data_hanger.rolling_avg_data])
        rolling_avg = np.convolve(
            usage_values, np.ones(window_size) / window_size, mode="valid"
        )
        self.data_hanger.rolling_avg_data = self.data_hanger.rolling_avg_data[
            -len(rolling_avg) :
        ]
        for i in range(len(rolling_avg)):
            self.data_hanger.rolling_avg_data[i] = (
                self.data_hanger.rolling_avg_data[i][0],
                rolling_avg[i],
            )

    async def get_input_power(self):
        return input_power.presentValue

    async def get_one_hr_future_pwr(self):
        return one_hr_future_pwr.presentValue

    async def get_if_a_model_is_available(self):
        return hasattr(self.data_hanger.model, "coefs_")

    async def get_power_rate_of_change(self):
        return power_rate_of_change.presentValue

    async def set_power_state_based_on_peak_valley(self):
        if self.is_peak:
            self.data_hanger.high_load_bv_lv("active")
            self.data_hanger.low_load_bv_lv("inactive")
            _log.debug("Setting BVs to Peak!")
        elif self.is_valley:
            self.data_hanger.high_load_bv_lv("inactive")
            self.data_hanger.low_load_bv_lv("active")
            _log.debug("Setting BVs to Valley!")
        else:
            self.data_hanger.high_load_bv_lv("inactive")
            self.data_hanger.low_load_bv_lv("inactive")
            _log.debug("Setting BVs to Valley!")

    async def create_dataset(self, y, input_window=60, forecast_horizon=1):
        dataX, dataY = [], []
        length = len(y) - input_window - forecast_horizon + 1
        _log.debug(f"LENGTH: {length}")
        for i in range(length):
            dataX.append(y[i : (i + input_window)])
            dataY.append(y[i + input_window : i + input_window + forecast_horizon])
        return np.array(dataX), np.array(dataY)

    async def poll_sensor_data(self, sensor_reading=None):
        sensor_reading = await self.get_input_power()
        if sensor_reading is not None:
            return datetime.now(), sensor_reading
        return None, None

    async def fetch_and_store_data(self):
        timestamp, new_data = await self.poll_sensor_data()

        if timestamp is None:
            return False

        self.data_hanger.data_cache.append((timestamp, new_data))

        if len(self.data_hanger.data_cache) > self.data_hanger.CACHE_LIMIT:
            self.data_hanger.data_cache = self.data_hanger.data_cache[
                -self.data_hanger.CACHE_LIMIT :
            ]

        return True

    async def calc_power_rate_of_change(self):
        if len(self.data_hanger.data_cache) == 0:
            _log.debug(
                "Data cache is empty, cannot calculate power rate of change - RETURN"
            )
            return

        y_values = np.array([item[1] for item in self.data_hanger.data_cache])
        gradient = np.diff(y_values)
        current_rate_of_change = gradient[-1] if len(gradient) > 0 else 0

        if len(gradient) >= 15:
            avg_rate_of_change = (gradient[-1] - gradient[-15]) / 15.0
        else:
            avg_rate_of_change = current_rate_of_change

        self.data_hanger.current_power_last_15mins_avg = avg_rate_of_change
        self.data_hanger.current_power_lv_rate_of_change = current_rate_of_change
        _log.debug("Power rate of change calculated.")

    async def check_percentiles(self, current_value):
        if len(self.data_hanger.data_cache) == 0:
            _log.debug("Data cache is empty, cannot check percentiles.")
            return False, False

        y_values = np.array([item[1] for item in self.data_hanger.data_cache])
        percentile_30 = np.percentile(y_values, 30)
        percentile_90 = np.percentile(y_values, 90)

        is_below_30th = current_value < percentile_30
        is_above_90th = current_value > percentile_90

        _log.debug("Percentiles checked.")
        return is_below_30th, is_above_90th

    async def train_model_thread_async(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.train_model_thread)

    async def train_model_thread(self):
        try:
            _log.debug("Fitting the model.")
            X, Y = self.create_dataset(
                np.array([item[1] for item in self.data_hanger.data_cache])
            )

            start_time = time.time()
            self.data_hanger.model = MLPRegressor()
            self.data_hanger.model.fit(X, Y.ravel())

            self.data_hanger.total_training_time_minutes = (
                time.time() - start_time
            ) / 60
            self.data_hanger.last_train_time = datetime.now()

            _log.debug(
                f"Model trained successfully in {self.data_hanger.total_training_time_minutes:.2f} minutes on {self.last_train_time}."
            )

        except Exception as e:
            _log.debug(f"An error occurred during the model training: {e}")
            if _debug:
                exit(1)

    async def run_forecasting_cycle(self):
        while True:
            await asyncio.sleep(INTERVAL)
            _log.debug("run_forecasting_cycle GO!")

            data_available = await self.fetch_and_store_data()
            if not data_available:
                _log.debug("Data not available - CONTINUE")
                continue

            now = datetime.now()
            data_cache_len = len(self.data_hanger.data_cache)

            if _debug:
                _log.debug("Data Cache Length: %s", data_cache_len)
                _log.debug("Current Hour: %s", now.hour)
                _log.debug("Current Minute: %s", now.minute)
                _log.debug(
                    "Training Started Today: %s",
                    self.data_hanger.training_started_today,
                )
                _log.debug(
                    "Model Availability: %s", await self.get_if_a_model_is_available()
                )
                _log.debug(
                    "Model training time: %.2f minutes on %s",
                    self.data_hanger.total_training_time_minutes,
                    self.data_hanger.last_train_time,
                )

            if not self.data_hanger.data_cache:
                _log.debug("Data Cache is empty - CONTINUE")
                continue

            data_cache_lv = self.data_hanger.data_cache[-1][1]
            if _debug:
                _log.debug("Data Cache last value: %s", data_cache_lv)

            if data_cache_lv == -1.0:
                _log.debug("data_cache_lv == -1.0 - CONTINUE")
                continue

            if data_cache_len < 65:
                _log.debug("data_cache_len < 65 - CONTINUE")
                continue

            if (
                now.hour == self.data_hanger.model_train_hour
                and not self.data_hanger.training_started_today
            ):
                # Start model training asynchronously
                await self.train_model_thread_async()
                self.data_hanger.training_started_today = True
            elif now.hour == 1:
                self.data_hanger.training_started_today = False

            if not self.get_if_a_model_is_available():
                _log.debug("Model not trained yet, no data science - CONTINUE")
                continue

            y = np.array([item[1] for item in self.data_hanger.data_cache])
            self.data_hanger.forecasted_value_60 = self.data_hanger.model.predict(
                y[-60:].reshape(1, -1)
            )[0]
            self.data_hanger.one_hr_future_pwr_lv(self.data_hanger.forecasted_value_60)

            self.calc_power_rate_of_change()
            self.data_hanger.power_rate_of_change_lv(
                self.data_hanger.current_power_lv_rate_of_change
            )

            self.is_valley, self.is_peak = self.check_percentiles(data_cache_lv)
            self.set_power_state_based_on_peak_valley()


async def main():
    global input_power, one_hr_future_pwr, power_rate_of_change, \
        high_load_bv, low_load_bv
 
    data_hanger = DataHanger()

    args = SimpleArgumentParser().parse_args()
    if _debug:
        _log.debug("args: %r", args)

    app = SampleApplication().from_args(args)
    app.data_hanger = data_hanger 

    if _debug:
        _log.debug("app: %r", app)

    # Define the AnalogValueObjects and BinaryValueObjects before using them
    input_power = CommandableAnalogValueObject(
        objectIdentifier=("analogValue", 1),
        objectName="input-power-meter",
        presentValue=DEFAULT_PV,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
        description="writeable input for app buildings electricity power value",
    )

    one_hr_future_pwr = AnalogValueObject(
        objectIdentifier=("analogValue", 2),
        objectName="one-hour-future-power",
        presentValue=DEFAULT_PV,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
        description="electrical power one hour into the future",
    )

    power_rate_of_change = AnalogValueObject(
        objectIdentifier=("analogValue", 3),
        objectName="power-rate-of-change",
        presentValue=DEFAULT_PV,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
        description="current electrical power rate of change",
    )

    high_load_bv = BinaryValueObject(
        objectIdentifier=("binaryValue", 1),
        objectName="high-load-conditions",
        presentValue="inactive",
        statusFlags=[0, 0, 0, 0],
        description="Peak power usage detected, shed loads if possible",
    )

    low_load_bv = BinaryValueObject(
        objectIdentifier=("binaryValue", 2),
        objectName="low-load-conditions",
        presentValue="inactive",
        statusFlags=[0, 0, 0, 0],
        description="Low power usage detected, charge TES or battery okay",
    )

    app.add_object(input_power)
    app.add_object(one_hr_future_pwr)
    app.add_object(power_rate_of_change)
    app.add_object(high_load_bv)
    app.add_object(low_load_bv)

    try:
        await asyncio.gather(app.run_forecasting_cycle(), app.update_bacnet_api())
    except asyncio.CancelledError:
        if _debug:
            _log.debug("Tasks were cancelled")


# Run the main coroutine
try:
    asyncio.run(main())
except (KeyboardInterrupt, asyncio.CancelledError):
    if _debug:
        _log.debug("Operation was interrupted")
except Exception as e:
    if _debug:
        _log.error(f"An unexpected error occurred: {e}")
