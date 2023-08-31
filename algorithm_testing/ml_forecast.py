import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


class PowerMeterForecast:
    def __init__(self, csv_path):
        self.csv_data = pd.read_csv(csv_path)
        self.csv_data["Date"] = pd.to_datetime(self.csv_data["Date"])
        self.data_counter = 0
        self.mse_string = ""
        self.data_cache = pd.DataFrame(columns=["ds", "y"])
        self.days_to_cache = 1
        self.CACHE_LIMIT = 144 * self.days_to_cache
        self.prediction_errors_60 = []
        self.forecasted_values_60 = []
        self.actual_values_60 = []
        self.actual_values = []
        self.timestamps = []

    def create_dataset(self, y, input_window=60, forecast_horizon=1):
        dataX, dataY = [], []
        for i in range(len(y) - input_window - forecast_horizon + 1):
            dataX.append(y[i : (i + input_window)])
            dataY.append(y[i + input_window : i + input_window + forecast_horizon])
        return np.array(dataX), np.array(dataY)

    def plot_main_results(self, axs):
        color = "tab:blue"
        # Plot for Current Electrical Power
        axs[0].set_ylabel("Electrical Power - kW", color=color)
        axs[0].plot(
            self.timestamps,
            self.actual_values,
            color=color,
            label="Current Electrical Power",
        )
        axs[0].tick_params(axis="y", labelcolor=color)
        axs[0].legend(loc="upper left")

        # Plot for 60 mins forecasts and actuals
        axs[1].set_ylabel("Electrical Power - kW", color=color)
        axs[1].plot(
            self.timestamps,
            self.forecasted_values_60,
            color=color,
            label="60 Mins Future Forecasted Electrical Power",
        )
        axs[1].plot(
            self.timestamps,
            self.actual_values_60,
            color="tab:orange",
            label="60 Mins Future Actual Electrical Power",
        )
        axs[1].tick_params(axis="y", labelcolor=color)
        axs[1].legend(loc="upper left")

        # Error plot
        error_colors = ["tab:purple"]
        error_data = [self.prediction_errors_60]
        labels = ["Squared Error 60 Minutes Future to Actual"]

        for ax, color, data, label in zip(axs[2:], error_colors, error_data, labels):
            ax.set_ylabel(label, color=color)
            ax.plot(self.timestamps, data, color=color)
            ax.tick_params(axis="y", labelcolor=color)

    def plot_zoomed_results(self, axs):
        color = "tab:blue"
        self.plot_main_results(axs)  # Reuse the main plot generation logic

        # Find the date with the maximum electrical power value
        max_power_idx = self.actual_values.index(max(self.actual_values))
        max_power_date = self.timestamps[max_power_idx]

        # Use max_power_date as the center and zoom around it
        zoom_start_date = max_power_date - pd.Timedelta(
            hours=12
        )  # 12 hours before the max value
        zoom_end_date = max_power_date + pd.Timedelta(
            hours=12
        )  # 12 hours after the max value

        # Set x-axis limits for all subplots
        for ax in axs:
            ax.set_xlim(zoom_start_date, zoom_end_date)

        axs[1].set_xlabel("Time")  # Changed from axs[0] to axs[1]
        axs[1].set_ylabel("Electrical Power - kW", color=color)  # Changed from axs[0] to axs[1]


    def save_plot(self, filename):
        plt.tight_layout()
        plt.savefig(f"./plots/{filename}.png", format='png', dpi=300)
        print(f"Plot saved to {filename}")

    def run_and_save_main_plot(self):
        fig, axs = plt.subplots(nrows=3, figsize=(15, 15))
        self.plot_main_results(axs)
        filename = f"ml_forecast"
        self.save_plot(filename)

    def run_and_save_zoomed_plot(self):
        fig, axs = plt.subplots(nrows=3, figsize=(15, 15))
        self.plot_zoomed_results(axs)
        filename = f"ml_forecast_zoomed"
        self.save_plot(filename)

    def poll_sensor_data(self):
        if self.data_counter < len(self.csv_data):
            data_row = self.csv_data.iloc[self.data_counter]
            self.data_counter += 1
            return pd.Timestamp(data_row["Date"]), data_row["Usage_kW"]
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
    
    def save_data_to_csv(self, filename):
        data = {
            'Timestamps': self.timestamps,
            'Actual_Values': self.actual_values,
            'Actual_Values_60': self.actual_values_60,
            'Forecasted_Values_60': self.forecasted_values_60,
            'Prediction_Errors_60': self.prediction_errors_60
        }

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def run_forecasting_cycle(self):
        model = None
        last_train_time = None

        while True:
            data_available = self.fetch_and_store_data()
            if not data_available:
                break

            current_time = self.data_cache["ds"].iloc[-1]
            current_value = self.data_cache["y"].iloc[-1]

            y = self.data_cache["y"].values

            # Only train if there are more than 60+1 data points in data_cache
            if len(y) > 61 and (
                last_train_time is None
                or (current_time - last_train_time) >= pd.Timedelta(days=1)
            ):
                print("Fit Model Called!")
                X, Y = self.create_dataset(y)
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X, Y.ravel())  # Use ravel() here
                last_train_time = current_time

            if model is None:
                print(f"model hasnt trained yet {current_time}")
                continue  # Model hasn't been trained yet

            forecasted_value_60 = model.predict(y[-60:].reshape(1, -1))[0]
            
            future_time = current_time + pd.Timedelta(minutes=60)
            actual_value_60 = (
                self.csv_data.loc[
                    (self.csv_data["Date"] >= future_time)
                    & (self.csv_data["Date"] < future_time + pd.Timedelta(minutes=1)),
                    "Usage_kW",
                ].values[0]
                if not self.csv_data.loc[
                    (self.csv_data["Date"] >= future_time)
                    & (self.csv_data["Date"] < future_time + pd.Timedelta(minutes=1)),
                    "Usage_kW",
                ].empty
                else 0 # default value
            )  

            self.actual_values.append(current_value)
            self.actual_values_60.append(actual_value_60)
            self.forecasted_values_60.append(forecasted_value_60)
            self.prediction_errors_60.append((forecasted_value_60 - actual_value_60) ** 2)
            self.timestamps.append(current_time)

            print(f"current_time {current_time} - {current_value}")
            print(f"future_time {future_time} - {actual_value_60}")
            print()
            
        mse_60 = mean_squared_error(self.forecasted_values_60, self.actual_values_60)
        self.mse_string = f"MSE: {mse_60}"
        print(self.mse_string)

# Execution time tracking
st = time.time()

csv_path = "./data/egauge_data_reversed_output.csv"
forecast_app = PowerMeterForecast(csv_path)
forecast_app.run_forecasting_cycle()

et = time.time()

elapsed_time = et - st
print("Execution time in seconds:", elapsed_time)
print("Execution time in minutes:", elapsed_time // 60)

forecast_app.run_and_save_main_plot()
forecast_app.run_and_save_zoomed_plot()

forecast_app.save_data_to_csv('./data/forecasted_data.csv')
print("All done")