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
power = pd.read_csv("egauge_data_reversed_output.csv")
power["Date"] = pd.to_datetime(power["Date"])
power.set_index("Date", inplace=True)

# Ensure that df index is datetime
power.index = pd.to_datetime(power.index)

highest_power_day = power[power['Usage_kW'] == power['Usage_kW'].max()]
print("highest_power_day: \n", highest_power_day)

# Now you can proceed with the rest of your code
highest_power_day_data = power[power.index.date == highest_power_day.index.date[0]]

highest_rate_of_change = float('-inf')
highest_avg_hourly_rate_of_change = float('-inf')

for i in range(1, len(highest_power_day_data)):
    current_values = highest_power_day_data["Usage_kW"].iloc[:i+1].tolist()
    rate, avg_rate = calc_power_rate_of_change(current_values)
    
    highest_rate_of_change = max(highest_rate_of_change, rate)
    highest_avg_hourly_rate_of_change = max(highest_avg_hourly_rate_of_change, avg_rate)

print("Highest Rate of Change:", highest_rate_of_change)
print("Highest Hourly Avg Rate of Change:", highest_avg_hourly_rate_of_change)

# Create a new figure with subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

power_plot = ax1.plot(highest_power_day_data.index, highest_power_day_data["Usage_kW"], color='purple', label='Power kW')
rate_plot = ax2.plot(highest_power_day_data.index[1:], np.diff(highest_power_day_data["Usage_kW"]), color='blue', label=f'Current Power + or - Max Rate of Change: {highest_rate_of_change:.2f} kW/hour')
avg_rate_plot = ax3.plot(highest_power_day_data.index[60:], np.diff(highest_power_day_data["Usage_kW"], n=60) / 60, color='green', label=f'Average Hourly Rate of Change: {highest_avg_hourly_rate_of_change:.2f} kW/hour')


# Plot power consumption data on the same day
ax1.set_ylabel('Power kW')
ax1.set_title('Power Consumption on Highest Power Day')

# Plot current rate of change
ax2.set_ylabel('Rate of Change kW/hour')

# Plot average hourly rate of change
ax3.set_xlabel('Date')
ax3.set_ylabel('Avg Rate of Change kW/hour')

# Add legends with highest rate of change values
ax1.legend(loc='upper left')
ax2.legend(loc='upper left')
ax3.legend(loc='upper left')


# Adjust layout
plt.tight_layout()

# Save plot
plt.savefig(f"./plots/high_power_day_with_rate_of_change.png", dpi=300)
print(f"Plot saved successfully")
