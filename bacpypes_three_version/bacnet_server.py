import asyncio, time

from bacpypes3.debugging import ModuleLogger
from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.primitivedata import Real
from bacpypes3.app import Application
from bacpypes3.local.analog import AnalogValueObject
from bacpypes3.local.binary import BinaryValueObject
from bacpypes3.local.cmd import Commandable

import numpy as np
import pandas as pd

from sklearn.model_selection import TimeSeriesSplit
from sklearn.tree import DecisionTreeRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
from datetime import datetime

_debug = 0
_log = ModuleLogger(globals())

INTERVAL = 60.0  # dont adjust
MODEL_TRAIN_HOUR = 0  # midnight
DEFAULT_PV = -1.0
DAYS_TO_CACHE = 31


class CommandableAnalogValueObject(Commandable, AnalogValueObject):
    """
    Commandable Analog Value Object
    """


class SampleApplication:
    def __init__(self, args, **kwargs):
        self.args = args
        # Initialize the BACnet application
        self.app = Application.from_args(args)

        # Store additional keyword arguments as attributes and add them to the BACnet application
        for key, value in kwargs.items():
            setattr(self, key, value)
            # Assuming that the value is an instance of a BACnet object that should be added to the application
            self.app.add_object(value)

        self.one_hr_future_pwr_lv = DEFAULT_PV
        self.power_rate_of_change_lv = DEFAULT_PV
        self.high_load_bv_lv = "inactive"
        self.low_load_bv_lv = "inactive"

        self.max_power_found = 0
        self.columns = [
            "timestamp",
            "input_power_pv",
            "one_hr_future_pwr_pv",
            "power_rate_of_change_pv",
            "high_load_bv_pv",
            "low_load_bv_pv",
        ] + [f"generic_input_var_{i}_pv" for i in range(1, 11)]

        # Initialize the DataFrame with the columns and set 'timestamp' as the index
        self.data_cache = pd.DataFrame(columns=self.columns).set_index("timestamp")

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

        self.CACHE_LIMIT = 1440 * DAYS_TO_CACHE
        self.SPIKE_THRESHOLD_POWER_PER_MINUTE = 20
        self.BUILDING_POWER_SETPOINT = 20

        # create a task to update the values
        asyncio.create_task(self.update_bacnet_api())
        asyncio.create_task(self.run_forecasting_cycle())

    async def update_bacnet_api(self):
        while True:
            try:
                await asyncio.sleep(1)

                # Check if 'one_hr_future_pwr' is an attribute of self
                if hasattr(self, "one_hr_future_pwr"):
                    self.one_hr_future_pwr.presentValue = Real(
                        self.one_hr_future_pwr_lv
                    )

                # Similarly, for other attributes, check their existence before accessing
                if hasattr(self, "power_rate_of_change"):
                    self.power_rate_of_change.presentValue = Real(
                        self.power_rate_of_change_lv
                    )

                if hasattr(self, "high_load_bv"):
                    self.high_load_bv.presentValue = self.high_load_bv_lv

                if hasattr(self, "low_load_bv"):
                    self.low_load_bv.presentValue = self.low_load_bv_lv

            except Exception as e:
                _log.error(f"Error in update_bacnet_api: {e}")

    async def get_one_hr_future_pwr(self):
        if hasattr(self, "one_hr_future_pwr"):
            return self.one_hr_future_pwr.presentValue

    async def get_if_a_model_is_available(self):
        return hasattr(self.model, "coefs_")

    async def get_power_rate_of_change(self):
        if hasattr(self, "power_rate_of_change"):
            return self.power_rate_of_change.presentValue

    async def set_power_state_based_on_peak_valley(self):
        if self.is_peak:
            self.high_load_bv_lv("active")
            self.low_load_bv_lv("inactive")
            _log.debug("Setting BVs to Peak!")
        elif self.is_valley:
            self.high_load_bv_lv("inactive")
            self.low_load_bv_lv("active")
            _log.debug("Setting BVs to Valley!")
        else:
            self.high_load_bv_lv("inactive")
            self.low_load_bv_lv("inactive")
            _log.debug("Setting BVs to Valley!")

    async def create_dataset(self, y, input_window=60, forecast_horizon=1):
        dataX, dataY = [], []
        length = len(y) - input_window - forecast_horizon + 1
        _log.debug(f"LENGTH: {length}")
        for i in range(length):
            dataX.append(y[i : (i + input_window)])
            dataY.append(y[i + input_window : i + input_window + forecast_horizon])
        return np.array(dataX), np.array(dataY)

    async def calc_power_rate_of_change(self):
        if self.data_cache.empty:
            _log.debug(
                "Data cache is empty, cannot calculate power rate of change - RETURN"
            )
            return

        # Assume 'input_power_pv' is the name of the column you're interested in.
        gradient = self.data_cache["input_power_pv"].diff().dropna()
        current_rate_of_change = gradient.iloc[-1] if len(gradient) > 0 else 0

        # Here we assume your data cache has data at a regular interval, e.g., one value per minute
        window_size = 15  # for 15 minutes
        if len(gradient) >= window_size:
            avg_rate_of_change = gradient.iloc[-window_size:].mean()
        else:
            avg_rate_of_change = current_rate_of_change

        self.current_power_last_15mins_avg = avg_rate_of_change
        self.current_power_lv_rate_of_change = current_rate_of_change
        _log.debug("Power rate of change calculated.")

    async def check_percentiles(self, current_value):
        if self.data_cache.empty:
            _log.debug("Data cache is empty, cannot check percentiles.")
            return False, False

        # Assume 'input_power_pv' is the name of the column you're interested in.
        percentile_30 = self.data_cache["input_power_pv"].quantile(0.3)
        percentile_90 = self.data_cache["input_power_pv"].quantile(0.9)

        is_below_30th = current_value < percentile_30
        is_above_90th = current_value > percentile_90

        _log.debug("Percentiles checked.")
        return is_below_30th, is_above_90th

    async def train_model_thread_async(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.train_model_thread)

    async def train_model_thread(self):
        try:
            _log.debug("Preparing dataset for model training.")

            y = self.data_cache["input_power_pv"]

            feature_columns = [
                col for col in self.data_cache.columns if col not in ["input_power_pv"]
            ]
            X = self.data_cache[feature_columns]

            # Initialize the time series cross-validator
            tscv = TimeSeriesSplit(n_splits=5)

            # Initialize the model as a multi-output regressor
            model = MultiOutputRegressor(DecisionTreeRegressor(random_state=0))

            # Define parameter grid for hyperparameter tuning
            parameter_grid = {
                "estimator__max_depth": [None, 10, 20],
                "estimator__min_samples_split": [2, 5, 10],
                "estimator__min_samples_leaf": [1, 2, 4],
            }

            # Grid search with time series cross-validation
            grid_search = GridSearchCV(
                model, parameter_grid, cv=tscv, scoring="neg_mean_squared_error"
            )

            start_time = time.time()
            _log.debug(f"MODEL training GO! {time.ctime()}")

            grid_search.fit(X, y)

            end_time = time.time()
            _log.debug(f"MODEL training All Done! {time.ctime()}")

            # Extract the best model
            self.model = grid_search.best_estimator_

            # Training time in minutes
            self.total_training_time_minutes = (end_time - start_time) / 60
            self.last_train_time = datetime.now()

            _log.debug(
                f"Model trained successfully in {self.total_training_time_minutes:.2f} minutes on {self.last_train_time}."
            )

        except Exception as e:
            _log.debug(f"An error occurred during the model training: {e}")
            if _debug:
                raise e  # Instead of exiting, we raise the exception for debugging

    async def get_input_sensor_values(self):
        # Dictionary to store the sensor values
        sensor_values = {}

        # Get the present value of each defined sensor
        sensor_values["input_power"] = float(self.input_power.presentValue)
        sensor_values["one_hr_future_pwr"] = float(self.one_hr_future_pwr.presentValue)
        sensor_values["power_rate_of_change"] = float(self.power_rate_of_change.presentValue)
        sensor_values["high_load_bv"] = float(self.high_load_bv.presentValue)
        sensor_values["low_load_bv"] = float(self.low_load_bv.presentValue)

        # Retrieve present values for generic input variables
        for i in range(1, 11):
            sensor_name = f"generic_input_var_{i}"
            sensor_obj = getattr(self, sensor_name)
            sensor_values[sensor_name] = float(sensor_obj.presentValue)

        if _debug:
            _log.debug("sensor_values: %s", sensor_values)
            
        # Return the dictionary of sensor values
        return sensor_values

    async def poll_sensor_data(self, sensor_reading=None):
        sensor_reading = await self.get_input_sensor_values()
        if sensor_reading is not None:
            return datetime.now(), sensor_reading
        return None, None

    async def fetch_and_store_data(self):
        timestamp, new_data = await self.poll_sensor_data()

        if timestamp is None:
            return False

        _log.debug("new_data: %s", new_data)
        
        # Convert timestamp to the correct datetime type
        timestamp = pd.to_datetime(timestamp)
        new_data_df = pd.DataFrame(new_data, index=[timestamp])

        # Debugging: Print the contents of new_data_df
        _log.debug("new_data_df: %s", new_data_df)

        # Append the new DataFrame to the data_cache DataFrame
        self.data_cache = pd.concat([self.data_cache, new_data_df])

        # Sort the DataFrame by index just in case timestamps are out of order
        self.data_cache = self.data_cache.sort_index()

        # Check the DataFrame length and drop oldest rows if necessary
        if len(self.data_cache) > self.CACHE_LIMIT:
            self.data_cache = self.data_cache.iloc[-self.CACHE_LIMIT:]

        return True

    async def run_forecasting_cycle(self):
        while True:
            await asyncio.sleep(INTERVAL)
            _log.debug("run_forecasting_cycle GO!")

            data_available = await self.fetch_and_store_data()

            now = datetime.now()
            data_cache_len = self.data_cache.shape[0]
            power_meter_lv = self.data_cache["input_power_pv"].iloc[-1]

            if _debug:
                _log.debug("Data Cache Length: %s", data_cache_len)
                _log.debug("power_meter_lv LV: %s", power_meter_lv)
                _log.debug("Current Hour: %s", now.hour)
                _log.debug("Current Minute: %s", now.minute)
                _log.debug(
                    "Training Started Today: %s",
                    self.training_started_today,
                )
                _log.debug(
                    "Model Availability: %s", await self.get_if_a_model_is_available()
                )
                _log.debug(
                    "Model training time: %.2f minutes on %s",
                    self.total_training_time_minutes,
                    self.last_train_time,
                )

            if not data_available:
                _log.debug("Data Cache is empty - CONTINUE")
                continue 
            
            if self.data_cache["input_power_pv"].iloc[-1] == -1:
                _log.debug("Data Cache is empty - CONTINUE")
                continue

            if now.hour == self.model_train_hour and not self.training_started_today:
                # Start model training asynchronously
                await self.train_model_thread_async()
                self.training_started_today = True
            elif now.hour == 1:
                self.training_started_today = False

            if not await self.get_if_a_model_is_available():
                _log.debug("Model not trained yet, no data science - CONTINUE")
                continue

            y = np.array([item[1] for item in self.data_cache])
            self.forecasted_value_60 = self.model.predict(y[-60:].reshape(1, -1))[0]
            self.one_hr_future_pwr_lv(self.forecasted_value_60)

            self.calc_power_rate_of_change()
            self.power_rate_of_change_lv(self.current_power_lv_rate_of_change)

            self.is_valley, self.is_peak = self.check_percentiles(power_meter_lv)
            await self.set_power_state_based_on_peak_valley()


async def main():
    args = SimpleArgumentParser().parse_args()
    if _debug:
        _log.debug("args: %r", args)

    # Define the AnalogValueObjects and BinaryValueObjects before using them
    input_power = CommandableAnalogValueObject(
        objectIdentifier=("analogValue", 1),
        objectName="input-power-meter",
        presentValue=DEFAULT_PV,
        statusFlags=[0, 0, 0, 0],
        covIncrement=10.0,
        description="writeable target var for electricity power",
    )

    one_hr_future_pwr = AnalogValueObject(
        objectIdentifier=("analogValue", 2),
        objectName="one-hour-future-power",
        presentValue=DEFAULT_PV,
        statusFlags=[0, 0, 0, 0],
        covIncrement=10.0,
        description="model output electrical power one hour into the future",
    )

    power_rate_of_change = AnalogValueObject(
        objectIdentifier=("analogValue", 3),
        objectName="power-rate-of-change",
        presentValue=DEFAULT_PV,
        statusFlags=[0, 0, 0, 0],
        covIncrement=10.0,
        description="current electrical power rate of change",
    )

    high_load_bv = BinaryValueObject(
        objectIdentifier=("binaryValue", 1),
        objectName="high-load-conditions",
        presentValue="inactive",
        statusFlags=[0, 0, 0, 0],
        description="hi electrical load values detected",
    )

    low_load_bv = BinaryValueObject(
        objectIdentifier=("binaryValue", 2),
        objectName="low-load-conditions",
        presentValue="inactive",
        statusFlags=[0, 0, 0, 0],
        description="low electrical load values detected",
    )

    # Create generic input variables in a loop
    generic_input_vars = {}
    for i in range(1, 11):
        generic_input_vars[f"generic_input_var_{i}"] = CommandableAnalogValueObject(
            objectIdentifier=("analogValue", 3 + i),
            objectName=f"input-generic-sensor-{i}",
            presentValue=DEFAULT_PV,
            statusFlags=[0, 0, 0, 0],
            covIncrement=10.0,
            description="writeable generic explainer var for model",
        )

    # Instantiate the SampleApplication
    app = SampleApplication(
        args,
        input_power=input_power,
        one_hr_future_pwr=one_hr_future_pwr,
        power_rate_of_change=power_rate_of_change,
        high_load_bv=high_load_bv,
        low_load_bv=low_load_bv,
        **generic_input_vars,  # Add the generic input variables to the application
    )

    if _debug:
        _log.debug("app: %r", app)

    await asyncio.Future()

# Run the main coroutine
try:
    asyncio.run(main())
except (KeyboardInterrupt, asyncio.CancelledError):
    if _debug:
        _log.debug("Operation was interrupted")
except Exception as e:
    if _debug:
        _log.error(f"An unexpected error occurred: {e}")
