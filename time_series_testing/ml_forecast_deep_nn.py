import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import mean_squared_error
import csv


class MLP(nn.Module):
    def __init__(self, input_dim, hidden_layers):
        super(MLP, self).__init__()
        
        # Create the architecture based on the number of hidden layers provided
        layers = []
        for i in range(len(hidden_layers)):
            if i == 0:
                layers.append(nn.Linear(input_dim, hidden_layers[i]))
            else:
                layers.append(nn.Linear(hidden_layers[i-1], hidden_layers[i]))
            layers.append(nn.ReLU())
        
        layers.append(nn.Linear(hidden_layers[-1], 1))  # output layer
        
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class PowerMeterForecast:
    def __init__(self, csv_path):
        self.csv_data = pd.read_csv(csv_path)
        self.csv_data["Date"] = pd.to_datetime(self.csv_data["Date"])
        self.data_counter = 0
        self.data_cache = pd.DataFrame(columns=["ds", "y"])

        self.power_lv_rate_of_change_values = []
        self.prediction_errors_60 = []
        self.forecasted_values_60 = []
        self.forecasted_timestamps_60 = []
        self.actual_values_60 = []
        self.actual_values = []
        self.timestamps = []

        self.current_power_last_15mins_avg_rate_of_change = None
        self.current_power_lv_rate_of_change = None

        self.DAYS_TO_CACHE = 21  # days of data one minute intervals
        self.CACHE_LIMIT = 1440 * self.DAYS_TO_CACHE
        self.SPIKE_THRESHOLD_POWER_PER_MINUTE = 20
        self.BUILDING_POWER_SETPOINT = 20

    def create_dataset(self, y, input_window=60, forecast_horizon=1):
        dataX, dataY = [], []
        length = len(y) - input_window - forecast_horizon + 1
        print("LENGTH: ",length)
        for i in range(length):
            dataX.append(y[i : (i + input_window)])
            dataY.append(y[i + input_window : i + input_window + forecast_horizon])
        return np.array(dataX), np.array(dataY)

    def plot_main_results(self, axs):
        ax1 = axs[0]
        ax2 = axs[1]
        ax3 = axs[2]
        ax4 = axs[3]

        # Current Electrical Power
        color = "tab:blue"
        ax1.set_ylabel("Electrical Power - kW", color=color)
        print("timestamps right before plotting:", len(self.timestamps))
        print("actual_values right before plotting:", len(self.actual_values))

        ax1.plot(
            self.timestamps,
            self.actual_values,
            color=color,
            label="Current Electrical Power",
        )
        ax1.tick_params(axis="y", labelcolor=color)

        # Add horizontal lines for 90th and 60th percentiles
        percentile_90 = np.percentile(self.actual_values, 90)
        percentile_60 = np.percentile(self.actual_values, 60)
        ax1.axhline(percentile_90, color="red", linestyle="--", label="90th Percentile")
        ax1.axhline(
            percentile_60, color="green", linestyle="--", label="60th Percentile"
        )

        # Create a legend for ax1 that includes the horizontal lines
        ax1.legend(
            loc="upper left",
            labels=["Current Electrical Power", "90th Percentile", "60th Percentile"],
        )

        title = f"{self.mse_string}_{self.DAYS_TO_CACHE}_days_data"
        ax1.set_title(title)

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
            self.power_lv_rate_of_change_values,
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
        filename = f"results"
        self.save_plot(filename)

    def run_and_save_zoomed_plot(self):
        fig, axs = plt.subplots(nrows=4, figsize=(15, 20))  # Updated subplot count
        self.plot_zoomed_results(axs)
        filename = f"results_zoomed"
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
            "Timestamps": self.timestamps,
            "Actual_Values": self.actual_values,
            "Actual_Values_60": self.actual_values_60,
            "Forecasted_Values_60": self.forecasted_values_60,
            "Prediction_Errors_60": self.prediction_errors_60,
            "power_rate_change": self.power_lv_rate_of_change_values,
        }

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def calc_power_rate_of_change(self, current_value, model_trained):
        """
        calculate electric power rate of change per unit of time
        from cached data. Used to detect if a spike has occurred.
        """
        if model_trained:
            self.actual_values.append(current_value)

        gradient = np.diff(self.actual_values)
        current_rate_of_change = gradient[-1] if len(gradient) > 0 else 0

        # Average rate of change over the last 15 minutes
        if len(self.actual_values) > 15:
            avg_rate_of_change = (gradient[-1] - gradient[-15]) / 15.0
        else:
            avg_rate_of_change = current_rate_of_change

        self.current_power_last_15mins_avg = avg_rate_of_change
        return current_rate_of_change

    # check for peak or valley
    def check_percentiles(self, current_value):
        percentile_30 = np.percentile(self.actual_values, 30)
        percentile_90 = np.percentile(self.actual_values, 90)

        is_below_30th = current_value < percentile_30
        is_above_90th = current_value > percentile_90

        return is_below_30th, is_above_90th

    def run_forecasting_cycle(self, model_to_try):
        model = None
        last_train_time = None
        model_trained = False  # Add this flag
        epochs = 50  # Define number of training epochs

        # Define loss criterion and optimizer
        criterion = nn.MSELoss()

        # Check CUDA availability
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        while True:
            data_available = self.fetch_and_store_data()
            if not data_available:
                break

            current_time = self.data_cache["ds"].iloc[-1]
            current_value = self.data_cache["y"].iloc[-1]

            y = self.data_cache["y"].values

            if len(y) > 120 and (
                last_train_time is None
                or (current_time - last_train_time) >= pd.Timedelta(days=1)
            ):
                print("Fit Model Called!")
                X, Y = self.create_dataset(y)

                # Initialize the PyTorch MLP model
                model = model_to_try
                model = model.to(device) 
                optimizer = optim.Adam(model.parameters(), lr=0.01)
                
                # Convert numpy arrays to PyTorch tensors
                X_tensor = torch.tensor(X, dtype=torch.float32).to(device)  # Move tensor to CUDA
                Y_tensor = torch.tensor(Y, dtype=torch.float32).to(device)  # Move tensor to CUDA

                # Train the model
                for epoch in range(epochs):
                    optimizer.zero_grad()
                    outputs = model(X_tensor)
                    loss = criterion(outputs, Y_tensor)
                    loss.backward()
                    optimizer.step()

                last_train_time = current_time
                model_trained = True

            if not model_trained:
                print(f"model hasn't trained yet {current_time}")
                continue  # Skip the rest of the loop if the model isn't trained

            # attempts to detect a spike, like equipment startup
            current_rate_of_change = self.calc_power_rate_of_change(
                current_value, model_trained
            )

            forecasted_value_60 = model(torch.tensor(y[-60:].reshape(1, -1), dtype=torch.float32)).item()


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

            is_valley, is_peak = self.check_percentiles(current_value)
            if is_valley:
                print("Valley!")
            elif is_peak:
                print("Peak!")

            current_error = (forecasted_value_60 - actual_value_60) ** 2

            self.power_lv_rate_of_change_values.append(current_rate_of_change)

            self.actual_values_60.append(actual_value_60)
            self.forecasted_values_60.append(forecasted_value_60)
            self.prediction_errors_60.append(current_error)
            self.timestamps.append(current_time)
            self.forecasted_timestamps_60.append(future_time)

            """
            NOTE: self.actual_values.append(current_value) gets
            appended in the calc_power_rate_of_change method
            """

            print(f"{current_time} - {current_value} - {current_rate_of_change}")
            print(
                f"{future_time} - {actual_value_60} - {forecasted_value_60} - {current_error}"
            )
            print()

            print(len(self.timestamps))
            print(len(self.forecasted_values_60))
            print(len(self.forecasted_timestamps_60))
            print(len(self.actual_values_60))
            print(len(self.power_lv_rate_of_change_values))
            print(len(self.prediction_errors_60))
            print()

        mse_60 = round(mean_squared_error(self.forecasted_values_60, self.actual_values_60),2)
        self.mse_string = f"MSE: {mse_60}"
        print(self.mse_string)
        print()

        print("timestamps: ", len(self.timestamps))
        print("forecasted_values_60: ", len(self.forecasted_values_60))
        print("forecasted_timestamps_60: ", len(self.forecasted_timestamps_60))
        print("actual_values_60: ", len(self.actual_values_60))
        print(
            "power_lv_rate_of_change_values: ", len(self.power_lv_rate_of_change_values)
        )
        print("prediction_errors_60: ", len(self.prediction_errors_60))
        print()
        

execution_times = []

# Now, you can define models with different depths by just varying the hidden_layers argument:
mlp_model1 = MLP(input_dim=60, hidden_layers=[30]) # 1 hidden layer with 30 units
mlp_model2 = MLP(input_dim=60, hidden_layers=[40, 20]) # 2 hidden layers with 40 and 20 units respectively
mlp_model3 = MLP(input_dim=60, hidden_layers=[50, 30, 10]) # 3 hidden layers
mlp_model4 = MLP(input_dim=60, hidden_layers=[120, 80, 40, 10]) # 4 hidden layers
mlp_model5 = MLP(input_dim=60, hidden_layers=[100, 80, 60, 40, 20]) # 5 hidden layers

models = [
    ("MLP_1_Hidden", mlp_model1),
    ("MLP_2_Hidden", mlp_model2),
    ("MLP_3_Hidden", mlp_model3),
    ("MLP_4_Hidden", mlp_model4),
    ("MLP_5_Hidden", mlp_model5)
]


for model_name, model in models:
    print("Starting model: ", model_name)

    st = time.time()

    csv_path = "./data/egauge_data_reversed_output.csv"
    forecast_app = PowerMeterForecast(csv_path)
    forecast_app.run_forecasting_cycle(model)

    et = time.time()

    elapsed_time = et - st
    execution_times.append((model_name, elapsed_time))

    print(f"Execution time in seconds for {model_name}:", elapsed_time)
    print(f"Execution time in minutes for {model_name}:", elapsed_time // 60)

    forecast_app.run_and_save_main_plot()
    forecast_app.run_and_save_zoomed_plot()

    # Save the model name in the .png filenames
    forecast_app.save_plot(f"results_{model_name}")
    forecast_app.save_plot(f"results_zoomed_{model_name}")

# Save execution times to a CSV file
with open('execution_times.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Model', 'Execution Time (Seconds)'])
    csv_writer.writerows(execution_times)




