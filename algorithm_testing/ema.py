import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time


class SensorDataForecast:
    def __init__(self, csv_path):
        self.csv_data = pd.read_csv(csv_path)
        self.data_counter = 0
        self.mse_string = ""
        self.data_cache = pd.DataFrame(columns=["ds", "y"])
        self.days_to_cache = 1
        self.CACHE_LIMIT = 1440 * self.days_to_cache
        self.prediction_errors_60 = []
        self.prediction_errors_30 = []
        self.prediction_errors_15 = []
        self.prediction_errors_5 = []
        self.timestamps = []
        self.forecasted_values_60 = []
        self.actual_values = []

    def exponential_moving_average(self, data, alpha=0.3):
        ema = [data[0]]
        for i in range(1, len(data)):
            ema.append(alpha * data[i] + (1 - alpha) * ema[i - 1])
        return np.array(ema)

    def plot_main_results(self, axs):
        color = 'tab:blue'
        axs[0].set_ylabel('Electrical Power - kW', color=color)
        axs[0].plot(self.timestamps, self.actual_values, color=color, label="Actual Values")
        axs[0].plot(self.timestamps, self.forecasted_values_60, color='tab:red', label="Forecasted Values")
        axs[0].tick_params(axis='y', labelcolor=color)
        axs[0].legend(loc="upper left")

        error_colors = ['tab:green', 'tab:orange', 'tab:purple', 'tab:pink']
        error_data = [self.prediction_errors_60, self.prediction_errors_30, self.prediction_errors_15, self.prediction_errors_5]
        labels = ["Squared Error 60", "Squared Error 30", "Squared Error 15", "Squared Error 5"]

        for ax, color, data, label in zip(axs[1:], error_colors, error_data, labels):
            ax.set_ylabel(label, color=color)
            ax.plot(self.timestamps, data, color=color)
            ax.tick_params(axis='y', labelcolor=color)
            
    def plot_zoomed_results(self, axs):
        color = 'tab:blue'
        self.plot_main_results(axs)  # Reuse the main plot generation logic

        # Find the date with the maximum electrical power value
        max_power_idx = self.actual_values.index(max(self.actual_values))
        max_power_date = self.timestamps[max_power_idx]

        # Use max_power_date as the center and zoom around it
        zoom_start_date = max_power_date - pd.Timedelta(hours=12)  # 12 hours before the max value
        zoom_end_date = max_power_date + pd.Timedelta(hours=12)    # 12 hours after the max value

        # Set x-axis limits for all subplots
        for ax in axs:
            ax.set_xlim(zoom_start_date, zoom_end_date)

        axs[0].set_xlabel('Time')
        axs[0].set_ylabel('Electrical Power - kW', color=color)

    def save_plot(self, filename):
        plt.tight_layout()
        plt.savefig(f"./plots/{filename}", dpi=300)
        print(f"Plot saved to {filename}")

    def run_and_save_main_plot(self):
        fig, axs = plt.subplots(nrows=5, figsize=(15, 15))
        self.plot_main_results(axs) 
        filename = f"ema_forecast.png"
        self.save_plot(filename)

    def run_and_save_zoomed_plot(self):
        fig, axs = plt.subplots(nrows=5, figsize=(15, 15))
        self.plot_zoomed_results(axs) 
        filename = f"ema_forecast_zoomed.png"
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

    def run_forecasting_cycle(self):
        while True:
            data_available = self.fetch_and_store_data()
            if not data_available:
                break

            if len(self.data_cache) < 60:
                continue  # Not enough data for forecasting

            current_time = self.data_cache["ds"].iloc[-1]
            y = self.data_cache["y"].values.tolist()
            current_value = self.data_cache["y"].iloc[-1]

            # Use the last 60 values to calculate the forecasted average value
            ema_next_60_mean = np.mean(self.exponential_moving_average(y[-60:]))
            actual_values_60_mean = np.mean(self.data_cache["y"].iloc[-60:])
            error_60 = (ema_next_60_mean - actual_values_60_mean) ** 2

            # Use the last 30 values to calculate the forecasted average value
            ema_next_30_mean = np.mean(self.exponential_moving_average(y[-30:]))
            actual_values_30_mean = np.mean(self.data_cache["y"].iloc[-30:])
            error_30 = (ema_next_30_mean - actual_values_30_mean) ** 2

            # Use the last 15 values to calculate the forecasted average value
            ema_next_15_mean = np.mean(self.exponential_moving_average(y[-15:]))
            actual_values_15_mean = np.mean(self.data_cache["y"].iloc[-15:])
            error_15 = (ema_next_15_mean - actual_values_15_mean) ** 2

            # Use the last 5 values to calculate the forecasted average value
            ema_next_5_mean = np.mean(self.exponential_moving_average(y[-5:]))
            actual_values_5_mean = np.mean(self.data_cache["y"].iloc[-5:])
            error_5 = (ema_next_5_mean - actual_values_5_mean) ** 2

            self.actual_values.append(current_value)
            self.forecasted_values_60.append(ema_next_60_mean)
            self.timestamps.append(current_time)

            self.prediction_errors_60.append(error_60)
            self.prediction_errors_30.append(error_30)
            self.prediction_errors_15.append(error_15)
            self.prediction_errors_5.append(error_5)

            print(current_time)
            print(current_value)
            print()

        mse_60 = np.mean(self.prediction_errors_60)
        mse_30 = np.mean(self.prediction_errors_30)
        mse_15 = np.mean(self.prediction_errors_15)
        mse_5 = np.mean(self.prediction_errors_5)
        self.mse_string = f"MSE 60: {round(mse_60,3)} MSE 30: {round(mse_30,3)} MSE 15: {round(mse_15,3)} MSE 5: {round(mse_5,3)}"
        print(self.mse_string)


# Execution time tracking
st = time.time()

csv_path = "./process_raw_data/egauge_data_reversed_output.csv"
forecast_app = SensorDataForecast(csv_path)
forecast_app.run_forecasting_cycle()

forecast_app.run_and_save_main_plot()
forecast_app.run_and_save_zoomed_plot()

et = time.time()

elapsed_time = et - st
print("Execution time in seconds:", elapsed_time)
print("Execution time in minutes:", elapsed_time // 60)
