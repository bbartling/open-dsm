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
        self.data_cache = pd.DataFrame(columns=["ds", "y"])
        self.days_to_cache = 7  # days of data one minute intervals
        self.CACHE_LIMIT = 1440 * self.days_to_cache
        self.prediction_errors_60 = []
        self.forecasted_values_60 = []
        self.forecasted_timestamps_60 = []
        self.actual_values_60 = []
        self.actual_values = []
        self.timestamps = []
        self.power_lv_rate_of_change_list = []
        self.current_power_last_hour_avg_rate_of_change = None
        self.current_power_lv_rate_of_change = None
        self.SPIKE_THRESHOLD_POWER_MINUTE = 20
        self.BUILDING_POWER_SETPOINT = 20

    def create_dataset(self, y, input_window=60, forecast_horizon=1):
        dataX, dataY = [], []
        for i in range(len(y) - input_window - forecast_horizon + 1):
            dataX.append(y[i: (i + input_window)])
            dataY.append(y[i + input_window: i + input_window + forecast_horizon])
        return np.array(dataX), np.array(dataY)
    
    def plot_main_results(self, axs):
        ax1 = axs[0]
        ax2 = axs[1]
        ax3 = axs[2]
        ax4 = axs[3]

        # Current Electrical Power
        color = "tab:blue"
        ax1.set_ylabel("Electrical Power - kW", color=color)
        ax1.plot(
            self.timestamps,
            self.actual_values,
            color=color,
            label="Current Electrical Power",
        )
        ax1.tick_params(axis="y", labelcolor=color)

        # plot forecasted power to actual power 60 minutes into the future
        ax2.set_ylabel("Electrical Power - kW", color="tab:orange")
        ax2.plot(
            self.timestamps,
            self.forecasted_values_60,
            color="tab:orange",
            label="Forecasted 60 Mins Future Electrical Power",
        )
        ax2.plot(
            self.forecasted_timestamps_60,
            self.actual_values_60,
            color="tab:blue",
            label="Actual 60 Mins Future Electrical Power",
        )
        ax2.legend(loc="upper left")

        # Calculate rate of change on current power to predict a spike
        ax3.set_ylabel("Rate of Change", color="tab:green")
        ax3.plot(
            self.timestamps,
            self.power_lv_rate_of_change_list,
            color="tab:green",
            label="Positive only rate-of-change power / unit of time",
        )
        ax3.tick_params(axis="y", labelcolor="tab:green")
        ax3.legend(loc="upper left")

        # Mean squared error of predicted and actual future power
        ax4.set_ylabel("MSE of predicted Vs actual future power", color="tab:purple")
        ax4.plot(
            self.timestamps,
            self.prediction_errors_60,
            color="tab:purple",
            label="Mean Squared Error",
        )
        ax4.tick_params(axis="y", labelcolor="tab:purple")
        ax4.legend(loc="upper left")

    def plot_zoomed_results(self, axs):
        color = "tab:blue"
        self.plot_main_results(axs)

        max_power_idx = self.actual_values.index(max(self.actual_values))
        max_power_date = self.timestamps[max_power_idx]

        zoom_start_date = max_power_date - pd.Timedelta(hours=12)
        zoom_end_date = max_power_date + pd.Timedelta(hours=12)

        for ax in axs:
            ax.set_xlim(zoom_start_date, zoom_end_date)

        axs[1].set_xlabel("Time")
        axs[1].set_ylabel("Electrical Power - kW", color=color)

        axs[2].set_xlabel("Time")
        axs[2].set_ylabel("Rate of Change", color="tab:green")

    def save_plot(self, filename):
        plt.tight_layout()
        plt.savefig(f"./plots/{filename}.png", format="png", dpi=300)
        print(f"Plot saved to {filename}")

    def run_and_save_main_plot(self):
        fig, axs = plt.subplots(nrows=4, figsize=(15, 20))
        self.plot_main_results(axs)
        filename = f"ml_forecast"
        self.save_plot(filename)

    def run_and_save_zoomed_plot(self):
        fig, axs = plt.subplots(nrows=4, figsize=(15, 20))  # Updated subplot count
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
            self.data_cache = self.data_cache.iloc[-self.CACHE_LIMIT:]
        return True

    def save_data_to_csv(self, filename):
        data = {
            "Timestamps": self.timestamps,
            "Actual_Values": self.actual_values,
            "Actual_Values_60": self.actual_values_60,
            "Forecasted_Values_60": self.forecasted_values_60,
            "Prediction_Errors_60": self.prediction_errors_60,
            "power_rate_change": self.power_lv_rate_of_change_list,
        }

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def calc_power_rate_of_change(self, current_value):
        if len(self.actual_values) > 1:
            current_rate_of_change = current_value - self.actual_values[-2]
            # Exclude negative rate of change
            current_rate_of_change = max(0, current_rate_of_change)
        else:
            current_rate_of_change = 0

        if len(self.actual_values) > 60:
            last_hour_values = self.actual_values[-61:-1]
            avg_rate_of_change = (last_hour_values[-1] - last_hour_values[0]) / 60.0
            # Exclude negative average rate of change
            avg_rate_of_change = max(0, avg_rate_of_change)
        else:
            avg_rate_of_change = current_rate_of_change

        self.current_power_last_hour_avg = avg_rate_of_change


    def run_forecasting_cycle(self):
        model = None
        last_train_time = None

        while True:
            data_available = self.fetch_and_store_data()
            if not data_available:
                break

            current_time = self.data_cache["ds"].iloc[-1]
            current_value = self.data_cache["y"].iloc[-1]

            # attempts to detect a spike, like equipment startup
            self.calc_power_rate_of_change(current_value)

            y = self.data_cache["y"].values

            # Only train if there are more than 60+1 data points in data_cache
            if len(y) > 61 and (
                last_train_time is None
                or (current_time - last_train_time) >= pd.Timedelta(days=1)
            ):
                print("Fit Model Called!")
                X, Y = self.create_dataset(y)
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X, Y.ravel())
                last_train_time = current_time

            if model is None:
                print(f"model hasn't trained yet {current_time}")
                continue  # Keep looping the Model hasn't been trained yet

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
                else 0  # default value
            )

            # (Optional) Spike detection and capacity limit logic can be added here if needed.

            self.actual_values.append(current_value)
            self.actual_values_60.append(actual_value_60)
            self.forecasted_values_60.append(forecasted_value_60)
            self.prediction_errors_60.append(
                (forecasted_value_60 - actual_value_60) ** 2
            )
            self.timestamps.append(current_time)
            self.forecasted_timestamps_60.append(future_time)

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

forecast_app.save_data_to_csv("./data/forecasted_data.csv")
print("All done")
