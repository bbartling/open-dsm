import subprocess
import configparser
import csv

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
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from datetime import datetime
import threading, time

_debug = 0
_log = ModuleLogger(globals())

register_object_type(AnalogValueCmdObject, vendor_id=999)

INTERVAL = 60.0
MODEL_TRAIN_HOUR = 0
USE_CACHE_ON_START = True
DAYS_TO_CACHE = 365 # modify later for SQLite db
LSTM_SEQUENCE_LENGTH = 120

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
        model_rsme,
        model_training_time,
        high_load_bv,
        low_load_bv,
    ):
        super().__init__(interval * 1000)
        self.interval = interval
        self.input_power = input_power
        self.one_hr_future_pwr = one_hr_future_pwr
        self.power_rate_of_change = power_rate_of_change
        self.model_rsme = model_rsme
        self.model_training_time = model_training_time
        self.high_load_bv = high_load_bv
        self.low_load_bv = low_load_bv
        
        self.power_forecast = PowerMeterForecast(
            self.input_power,
            self.one_hr_future_pwr,
            self.power_rate_of_change,
            self.model_rsme,
            self.model_training_time,
            self.high_load_bv,
            self.low_load_bv,
        )
        if USE_CACHE_ON_START:
            _log.debug(f"USE_CACHE_ON_START True - Starting CSV file data loading.")
            self.power_forecast.load_data_from_csv(on_start=True)
        else:
            _log.debug(f"USE_CACHE_ON_START False - Skipping CSV file data loading.")

    def process_task(self):
        if _debug:
            _log.debug("input_power: %s", self.input_power.presentValue)
            _log.debug("one_hr_future_pwr: %s", self.one_hr_future_pwr.presentValue)
            _log.debug(
                "power_rate_of_change: %s", self.power_rate_of_change.presentValue
            )
            _log.debug("high_load_bv: %s", self.high_load_bv.presentValue)
            _log.debug("low_load_bv: %s", self.low_load_bv.presentValue)

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
        
        self.model_rsme = AnalogValueObject(
            objectIdentifier=("analogValue", 4),
            objectName="model-rsme",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="root mean squared error of models accuracy",
        )
        self.app.add_object(self.model_rsme)

        self.model_training_time = AnalogValueObject(
            objectIdentifier=("analogValue", 5),
            objectName="model-training-time",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="model training time in minutes",
        )
        self.app.add_object(self.model_training_time)

        self.high_load_bv = BinaryValueObject(
            objectIdentifier=("binaryValue", 1),
            objectName="high-load-conditions",
            presentValue="inactive",
            statusFlags=[0, 0, 0, 0],
            description="peak power usage detected, shed loads if possible",
        )
        self.app.add_object(self.high_load_bv)

        self.low_load_bv = BinaryValueObject(
            objectIdentifier=("binaryValue", 2),
            objectName="low-load-conditions",
            presentValue="inactive",
            statusFlags=[0, 0, 0, 0],
            description="low power usage detected, charge TES or battery okay",
        )
        self.app.add_object(self.low_load_bv)

        self.task = DoDataScience(
            INTERVAL,
            self.input_power,
            self.one_hr_future_pwr,
            self.power_rate_of_change,
            self.model_rsme,
            self.model_training_time,
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
        model_rsme,
        model_training_time,
        high_load_bv,
        low_load_bv,
    ):
        self.input_power = input_power
        self.one_hr_future_pwr = one_hr_future_pwr
        self.power_rate_of_change = power_rate_of_change
        self.model_rsme = model_rsme
        self.model_training_time = model_training_time
        self.high_load_bv = high_load_bv
        self.low_load_bv = low_load_bv

        self.data_is_available = False
        self.data_cache = [] # very small holds LSTM seq data only

        self.current_power_last_15mins_avg_rate_of_change = None
        self.current_power_lv_rate_of_change = None
        self.forecasted_value_60 = None
        self.is_valley = None
        self.is_peak = None
        self.peak_valley_last_adjustment_time = None
        self.peak_valley_req_time_delta = 900  # seconds

        # Sequence lengths to experiment with in LSTM
        self.sequence_length = LSTM_SEQUENCE_LENGTH
        self.best_mse = float("inf")
        self.rmse = 0
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.last_train_time = None
        self.training_started_today = False
        self.total_training_time_minutes = 0
        self.model_train_hour = MODEL_TRAIN_HOUR
        self.model_is_training = False

    def set_one_hr_future_pwr(self, value):
        self.one_hr_future_pwr.presentValue = Real(value)
        _log.debug("one_hr_future_pwr: %s", self.one_hr_future_pwr.presentValue)

    def set_power_rate_of_change(self, value):
        self.power_rate_of_change.presentValue = Real(value)
        _log.debug("power_rate_of_change: %s", self.power_rate_of_change.presentValue)
        
    def set_model_rsme(self, value):
        self.model_rsme.presentValue = Real(value)
        _log.debug("model_rsme: %s", self.model_rsme.presentValue)
        
    def set_model_training_time(self, value):
        self.model_training_time.presentValue = Real(value)
        _log.debug("model_training_time: %s", self.model_training_time.presentValue)

    def set_high_load_bv(self, value_str):
        self.high_load_bv.presentValue = value_str
        _log.debug("high_load_bv: %s", self.high_load_bv.presentValue)

    def set_low_load_bv(self, value_str):
        self.low_load_bv.presentValue = value_str
        _log.debug("low_load_bv: %s", self.low_load_bv.presentValue)

    def get_input_power(self):
        return self.input_power.presentValue

    def get_one_hr_future_pwr(self):
        return self.one_hr_future_pwr.presentValue

    def get_if_a_model_is_available(self):
        return self.model is not None

    def get_power_rate_of_change(self):
        return self.power_rate_of_change.presentValue

    def set_power_state_based_on_peak_valley(self):
        # Check if the last adjustment time is None or if enough time has passed
        # to prevent short cycling on peak or valley BACnet BV
        if (
            self.peak_valley_last_adjustment_time is None
            or (datetime.now() - self.peak_valley_last_adjustment_time).total_seconds()
            >= self.peak_valley_req_time_delta
        ):
            if self.is_peak:
                self.set_high_load_bv("active")
                self.set_low_load_bv("inactive")
                _log.debug("Setting BVs to Peak!")

            elif self.is_valley:
                self.set_high_load_bv("inactive")
                self.set_low_load_bv("active")
                _log.debug("Setting BVs to Valley!")

            else:
                self.set_high_load_bv("inactive")
                self.set_low_load_bv("inactive")
                _log.debug("Setting BVs to Valley!")

            # Update the last adjustment time
            self.peak_valley_last_adjustment_time = datetime.now()

    def save_all_data_to_csv(self, filename="data.csv"):
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for data in self.data_cache:
                timestamp, value = data
                row = [timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"), value]
                writer.writerow(row)

    def save_a_row_of_data_to_csv(self, timestamp, new_data, filename="data.csv"):
        with open(filename, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            row = [timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"), new_data]
            writer.writerow(row)

    def load_data_from_csv(self, filename="data.csv", on_start=False):
        local_cache = []

        try:
            with open(filename, "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                    value = row[1]
                    local_cache.append((timestamp, value))
        except FileNotFoundError:
            _log.debug(f"CSV file '{filename}' not found. Skipping data loading.")
        except Exception as e:
            _log.error(f"Error loading data from CSV: {e}")

        # Check if data is available based on the sequence length
        self.data_is_available = len(local_cache) >= self.sequence_length

        if on_start:
            # Fill self.data_cache with the last 120 floats
            if len(local_cache) >= self.sequence_length:
                self.data_cache = local_cache[-self.sequence_length:]

        return local_cache

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

        if len(self.data_cache) > self.sequence_length:
            self.data_cache = self.data_cache[-self.sequence_length :]

        self.save_a_row_of_data_to_csv(timestamp, new_data)

        return True

    def calc_power_rate_of_change(self):
        """
        Calcs current readings electrical rate of change
        Is BACnet Analog Value object for controls sys logic

        Returns:
        - float
        """

        # Load ALL data from the CSV source
        data = self.load_data_from_csv()

        if len(data) < 2:
            return 0.0  # Not enough data points to calculate rate of change

        timestamps = [item[0] for item in data]
        y_values = [
            float(item[1]) for item in data
        ]  # Convert y_values to float

        # Convert timestamps to datetime objects
        timestamps = [
            ts
            if isinstance(ts, datetime)
            else datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f")
            for ts in timestamps
        ]

        # Calculate time differences in seconds
        time_diffs = [
            (timestamps[i] - timestamps[i - 1]).total_seconds()
            for i in range(1, len(timestamps))
        ]

        # Calculate rate of change
        gradient = np.diff(y_values)
        current_rate_of_change = gradient[-1] / time_diffs[-1]

        if len(time_diffs) >= 15:
            avg_rate_of_change = (gradient[-1] - gradient[-15]) / sum(time_diffs[-15:])
        else:
            avg_rate_of_change = current_rate_of_change

        self.current_power_last_15mins_avg = avg_rate_of_change
        self.current_power_lv_rate_of_change = current_rate_of_change
        return current_rate_of_change

    def check_percentiles(self, current_value):
        """
        Used to predict electrical load profile peak or valley
        For battery or EV charging or peak shaving etc
        Is BACnet object for peak or valley

        Returns:
        - bool of percentiles of cached data
        """
        # Load ALL data from the CSV source
        data = self.load_data_from_csv()
        
        if len(data) < 2:
            return False, False  # Not enough data points to calculate percentiles

        # Extract y-values directly without dealing with timestamps
        y_values = [float(item[1]) for item in data]  # Updated line

        # Calculate percentiles using numpy
        percentile_30 = np.percentile(y_values, 30)
        percentile_90 = np.percentile(y_values, 90)

        # Calculate percentiles relative to the current value
        is_below_30th = current_value < percentile_30
        is_above_90th = current_value > percentile_90

        return is_below_30th, is_above_90th

    def scale_data(self):
        """
        Scale the input data using the MinMaxScaler for LSTM training

        Returns:
        - scaled_data: Scaled data
        """
        _log.debug("scale data hit")
        
        data = self.load_data_from_csv()

        # Extract float values
        float_values = [float(item[1]) for item in data]

        # Scale float values
        float_values_array = np.array(float_values).reshape(-1, 1)
        self.scaler_float = MinMaxScaler()  # Store the scaler as an instance attribute
        scaled_float_values = self.scaler_float.fit_transform(float_values_array)

        _log.debug(
            f"scaled_float_values shape: {scaled_float_values.shape}, \
            scaled_float_values type: {type(scaled_float_values)}"
        )

        return scaled_float_values

    def create_dataset(self, data, seq_length, pred_length):
        """
        Called when LSTM is trained
        Saves data to CSV format

        Returns:
        - numpy arrays of X, y
        """
        _log.debug(f"data shape: {data.shape}, data type: {type(data)}")
        
        X, y = [], []
        for i in range(seq_length, len(data) - pred_length):
            X.append(data[i - seq_length : i, 0])
            y.append(data[i : i + pred_length, 0])

        dataX = np.array(X)
        dataY = np.array(y)

        _log.debug(f"dataX shape: {dataX.shape}, dataX type: {type(dataX)}")
        _log.debug(f"dataY shape: {dataY.shape}, dataY type: {type(dataY)}")

        return dataX, dataY

    def train_model_thread(self):
        best_mse = float("inf")
        best_length = self.sequence_length
        self.model_is_training = True

        try:
            _log.debug("Fit Model Called!")

            # Scale the data using the same MinMaxScaler
            # all data comes from CSV file
            scaled_data = self.scale_data()
            _log.debug(
                f"scaled_data type: {type(scaled_data)}, scaled_data value: {scaled_data}"
            )

            # Load your preprocessed data for the fixed sequence length
            X, Y = self.create_dataset(
                scaled_data, seq_length=best_length, pred_length=60
            )

            _log.debug(f"X shape: {X.shape}, Y shape: {Y.shape}")
            _log.debug(f"X type: {type(X)}, Y type: {type(Y)}")

            X = np.reshape(X, (X.shape[0], X.shape[1], 1))

            # Split data into train and test
            train_size = int(0.67 * len(X))
            X_train, y_train = X[:train_size], Y[:train_size]
            X_test, y_test = X[train_size:], Y[train_size:]

            _log.debug(
                f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}"
            )
            _log.debug(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

            # Define and compile your LSTM model
            model = Sequential()
            model.add(LSTM(50, return_sequences=True, input_shape=(best_length, 1)))
            model.add(LSTM(50, return_sequences=False))
            model.add(Dense(60))
            model.compile(optimizer="adam", loss="mean_squared_error")

            # Define the EarlyStopping callback with patience
            early_stop = EarlyStopping(
                monitor="val_loss", patience=5, verbose=1, restore_best_weights=True
            )

            # Define the ModelCheckpoint callback to save the best model
            model_checkpoint = ModelCheckpoint(
                "best_model.h5", monitor="val_loss", save_best_only=True
            )

            start_time = time.time()

            # Train LSTM model with validation data and early stopping
            history = model.fit(
                X_train,
                y_train,
                batch_size=64,
                epochs=200,
                validation_data=(X_test, y_test),
                callbacks=[early_stop, model_checkpoint],
            )

            # Validate model
            predictions = model.predict(X_test)
            _log.debug(f"predictions shape: {predictions.shape}")

            predictions = self.scaler_float.inverse_transform(predictions)
            y_test_original = self.scaler_float.inverse_transform(y_test)
            _log.debug(f"y_test_original shape: {y_test_original.shape}")

            mse = mean_squared_error(y_test_original, predictions)
            self.rmse = np.sqrt(mse)

        except Exception as e:
            _log.debug(f"An error occurred during the model training: {e}")
            if _debug:
                exit(1)

        self.total_training_time_minutes = (time.time() - start_time) / 60
        self.last_train_time = datetime.now()
        self.rmse = np.sqrt(best_mse)
        
        # update bacnet API so metrics can be logged on control sys
        self.set_model_training_time(self.total_training_time_minutes)
        self.set_model_rsme(self.rmse)
        
        # Load the best model
        self.model = tf.keras.models.load_model("best_model.h5")
        _log.debug(f"Model Training Success")
        self.model_is_training = False

    def run_forecasting_cycle(self):
        """
        Executes a forecasting cycle, performing the following steps:
        1. Fetches and stores data, returning early if no data is available.
        2. Checks if the data cache meets the required length for forecasting.
        3. Initiates model training at a specific hour, if not already started.
        4. Once the LSTM model is trained:
        - Forecasts the next hour's power usage values.
        - Calculates the rate of change of power usage.
        - Identifies peak and valley points in the power usage distribution.
        - Sets the power state based on the identified peak and valley points.
        """
        data_available = self.fetch_and_store_data()
        if not data_available:
            _log.debug("Data not available. Returning early.")
            return

        now = datetime.now()
        data_cache_len = len(self.data_cache)

        if _debug:
            _log.debug("Data Cache Length: %s", data_cache_len)
            _log.debug("Current Hour: %s", now.hour)
            _log.debug("Current Minute: %s", now.minute)
            _log.debug(
                "Model Train Hour: %s %s",
                self.model_train_hour,
                self.model_train_hour + 1,
            )
            _log.debug("Training Started Today: %s", self.training_started_today)
            _log.debug("Model Availability: %s", self.get_if_a_model_is_available())
            _log.debug("Model RMSE: %.2f", self.rmse)
            _log.debug(
                "Model training time for sequence length %d: %.2f minutes on %s",
                self.sequence_length,
                self.total_training_time_minutes,
                self.last_train_time,
            )

        if not self.data_cache:
            _log.debug("Data Cache is empty - RETURN")
            return

        data_cache_lv = self.data_cache[-1][1]
        if _debug:
            _log.debug("Data Cache last value: %s", data_cache_lv)

        if data_cache_lv == -1.0:
            _log.debug("data_cache_lv == -1.0 - RETURN")
            return

        if not self.data_is_available:
            _log.debug("self.data_is_available is False - RETURN")
            return

        if (
            now.hour == self.model_train_hour
            and not self.training_started_today
            and not self.model_is_training
        ):
            _log.debug("train model thread GO!")
            model_training_thread = threading.Thread(target=self.train_model_thread)
            model_training_thread.start()
            self.training_started_today = True

        elif now.hour == self.model_train_hour + 1:
            self.training_started_today = False

        if not self.get_if_a_model_is_available():
            _log.debug("Model not trained yet, no data science - RETURN")
            return

        # Only use the last `self.sequence_length` values from `data_cache` for forecasting
        last_seq_vals = [item[1] for item in self.data_cache[-self.sequence_length:]]
        last_seq_vals = np.array(last_seq_vals, dtype=float).reshape(1, self.sequence_length, 1)

        forecast = self.model.predict(last_seq_vals)
        forecast = self.scaler_float.inverse_transform(forecast)

        # Retrieve the last forecasted value for electric reading one hour into the future
        self.forecasted_value_60 = float(forecast[0][-1])

        _log.debug("Last forecasted value: %s", self.forecasted_value_60)

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
        _log.debug("An error occurred:  %s", e)
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
        _log.debug("Detected IP Address:  %s", detected_ip_address)
        use_constants = True
    else:
        _log.debug("Unable to find IP address. Using default INI values.")

    if use_constants:
        update_ini_with_constants(detected_ip_address)

    parser = ConfigArgumentParser(description=__doc__)
    args = parser.parse_args()

    bacnet_server = BacnetServer(args.ini, args.ini.address)

    bacnet_server.run()


if __name__ == "__main__":
    main()
