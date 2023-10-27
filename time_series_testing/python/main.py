import csv
from datetime import datetime
import time

import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.models import Sequential

LSTM_SEQUENCE_LENGTH = 120
CSV_FILE_NAME = "data.csv"
BEST_MODEL_FILE_NAME = "best_model.h5"


class PowerMeterForecast:
    def __init__(self):
        self.data_is_available = False
        self.data_cache = []  # very small holds LSTM seq data only

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
        self.model_is_training = False

    def load_data_from_csv(self, filename=CSV_FILE_NAME, on_start=False):
        """
        Load data from CSV file.

        Args:
            filename (str): The name of the CSV file.
            on_start (bool): Whether the function is called on start.

        Returns:
            list: The loaded data.
        """
        local_cache = []

        try:
            with open(filename, "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                    value = row[1]
                    local_cache.append((timestamp, value))
        except FileNotFoundError:
            print(f"CSV file '{filename}' not found. Skipping data loading.")
        except Exception as e:
            print(f"Error loading data from CSV: {e}")

        self.data_is_available = len(local_cache) >= self.sequence_length

        if on_start and len(local_cache) >= self.sequence_length:
            self.data_cache = local_cache[-self.sequence_length:]

        return local_cache

    def scale_data(self):
        """
        Scale data using MinMaxScaler.

        Returns:
            np.ndarray: The scaled data.
        """
        print("scale data hit")
        data = self.load_data_from_csv()

        float_values = [float(item[1]) for item in data]
        float_values_array = np.array(float_values).reshape(-1, 1)

        self.scaler_float = MinMaxScaler()
        scaled_float_values = self.scaler_float.fit_transform(float_values_array)

        print(f"scaled_float_values shape: {scaled_float_values.shape}, "
              f"scaled_float_values type: {type(scaled_float_values)}")

        return scaled_float_values

    def create_dataset(self, data, seq_length, pred_length):
        """
        Create dataset for training the model.

        Args:
            data (np.ndarray): The data.
            seq_length (int): The sequence length.
            pred_length (int): The prediction length.

        Returns:
            tuple: The dataset.
        """
        print(f"data shape: {data.shape}, data type: {type(data)}")

        X, y = [], []
        for i in range(seq_length, len(data) - pred_length):
            X.append(data[i - seq_length:i, 0])
            y.append(data[i:i + pred_length, 0])

        dataX = np.array(X)
        dataY = np.array(y)

        print(f"dataX shape: {dataX.shape}, dataX type: {type(dataX)}")
        print(f"dataY shape: {dataY.shape}, dataY type: {type(dataY)}")

        return dataX, dataY

    def train_model_thread(self):
        self.model_is_training = True
        start_time = time.time()

        try:
            print("Fit Model Called!")
            scaled_data = self.scale_data()
            X, Y = self.create_dataset(scaled_data, self.sequence_length, 60)

            print(f"X shape: {X.shape}, Y shape: {Y.shape}")
            print(f"X type: {type(X)}, Y type: {type(Y)}")

            X = np.reshape(X, (X.shape[0], X.shape[1], 1))

            train_size = int(0.67 * len(X))
            X_train, y_train = X[:train_size], Y[:train_size]
            X_test, y_test = X[train_size:], Y[train_size:]

            print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
            print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

            model = Sequential()
            model.add(LSTM(50, return_sequences=True, input_shape=(self.sequence_length, 1)))
            model.add(LSTM(50, return_sequences=False))
            model.add(Dense(60))
            model.compile(optimizer="adam", loss="mean_squared_error")

            early_stop = EarlyStopping(monitor="val_loss", patience=5, verbose=1, restore_best_weights=True)
            model_checkpoint = ModelCheckpoint(BEST_MODEL_FILE_NAME, monitor="val_loss", save_best_only=True)

            history = model.fit(X_train, y_train, batch_size=64, epochs=200, validation_data=(X_test, y_test),
                                callbacks=[early_stop, model_checkpoint])

            predictions = model.predict(X_test)
            print(f"predictions shape: {predictions.shape}")

            predictions = self.scaler_float.inverse_transform(predictions)
            y_test_original = self.scaler_float.inverse_transform(y_test)
            print(f"y_test_original shape: {y_test_original.shape}")

            mse = mean_squared_error(y_test_original, predictions)
            self.best_mse = min(self.best_mse, mse)  # Update best_mse with the minimum MSE
            self.rmse = np.sqrt(self.best_mse)

        except Exception as e:
            print(f"An error occurred during the model training: {e}")

        finally:
            self.total_training_time_minutes = (time.time() - start_time) / 60
            self.last_train_time = datetime.now()
            self.model = tf.keras.models.load_model(BEST_MODEL_FILE_NAME)
            print("Model Training Success")
            self.model_is_training = False
            print(f"Model RSME: {self.rmse}")


def main():
    run_lstm = PowerMeterForecast()
    run_lstm.train_model_thread()


if __name__ == "__main__":
    main()
