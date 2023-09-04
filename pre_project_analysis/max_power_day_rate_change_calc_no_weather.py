import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def calc_power_rate_of_change(values):
    # Assuming values is a list or pandas Series of electricity usage.
    if len(values) > 1:
        current_rate_of_change = values[-1] - values[-2]
    else:
        current_rate_of_change = 0

    # Ignore negative rate of change.
    current_rate_of_change = max(current_rate_of_change, 0)

    if len(values) > 60:
        last_hour_values = values[-61:-1]
        avg_rate_of_change = (last_hour_values[-1] - last_hour_values[0]) / 60.0
    else:
        avg_rate_of_change = current_rate_of_change

    # Ignore negative average rate of change.
    avg_rate_of_change = max(avg_rate_of_change, 0)

    return current_rate_of_change, avg_rate_of_change


# Load the electricity data
power = pd.read_csv("hourly_electric_data.csv")
power["Date"] = pd.to_datetime(power["Date"])
power.set_index("Date", inplace=True)

# Ensure that df index is datetime
power.index = pd.to_datetime(power.index)

highest_power_day = power[power['total_main_kw'] == power['total_main_kw'].max()]
print("highest_power_day: \n", highest_power_day)

# Now you can proceed with the rest of your code
highest_power_day_data = power[power.index.date == highest_power_day.index.date[0]]

highest_rate_of_change = float('-inf')
highest_avg_hourly_rate_of_change = float('-inf')

for i in range(1, len(highest_power_day_data)):
    current_values = highest_power_day_data["total_main_kw"].iloc[:i+1].tolist()
    rate, avg_rate = calc_power_rate_of_change(current_values)
    
    highest_rate_of_change = max(highest_rate_of_change, rate)
    highest_avg_hourly_rate_of_change = max(highest_avg_hourly_rate_of_change, avg_rate)

print("Highest Rate of Change:", highest_rate_of_change)
print("Highest Hourly Avg Rate of Change:", highest_avg_hourly_rate_of_change)

# Line plot for power data on the same day
plt.figure(figsize=(10, 6))
plt.plot(highest_power_day_data.index, highest_power_day_data["total_main_kw"], color='purple', label='Power kW')
plt.xlabel('Date')
plt.ylabel('Power kW')
plt.title('Power Consumption on Highest Power Day')

# Create a custom legend for the power consumption plot
plt.legend()
plt.tight_layout()

# Save plot
plt.savefig(f"./plots/high_power_day_no_weather.png", dpi=300)
print(f"Plot saved successfully")
