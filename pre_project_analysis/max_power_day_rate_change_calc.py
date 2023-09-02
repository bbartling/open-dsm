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

# Load and clean the weather data
weather = pd.read_csv("hourly_weather_data.csv")
weather["Date"] = pd.to_datetime(weather["Date"])
weather.set_index("Date", inplace=True)

# Replace empty values with NaN
weather.replace("", np.nan, inplace=True)

# Convert weather data columns to float
for column in weather.columns:
    print(column)
    weather[column] = pd.to_numeric(weather[column], errors="coerce")

# Resample weather data to hourly, using the mean for simplicity
weather_hourly = weather.resample("H").mean()

# Join the power and weather data
df = power.join(weather_hourly)

print()
print("df head: ", df.head())
print("df tail: ", df.tail())
print()
print(df.columns)

# Ensure that df index is datetime
df.index = pd.to_datetime(df.index)

highest_power_day = df[df['total_main_kw'] == df['total_main_kw'].max()]
print("highest_power_day: \n", highest_power_day)

# Now you can proceed with the rest of your code
highest_power_day_data = df[df.index.date == highest_power_day.index.date[0]]

highest_rate_of_change = float('-inf')
highest_avg_hourly_rate_of_change = float('-inf')

for i in range(1, len(highest_power_day_data)):
    current_values = highest_power_day_data["total_main_kw"].iloc[:i+1].tolist()
    rate, avg_rate = calc_power_rate_of_change(current_values)
    
    highest_rate_of_change = max(highest_rate_of_change, rate)
    highest_avg_hourly_rate_of_change = max(highest_avg_hourly_rate_of_change, avg_rate)

print("Highest Rate of Change:", highest_rate_of_change)
print("Highest Hourly Avg Rate of Change:", highest_avg_hourly_rate_of_change)

# Line plot for weather data and power data on the same day
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.plot(highest_power_day_data.index, highest_power_day_data["HourlyDryBulbTemperature"], color='green', label='Dry Bulb Temp')
ax1.set_xlabel('Date')
ax1.set_ylabel('Temperature (°F)')
ax1.set_title('Hourly Dry Bulb Temperature on Highest Power Day')
ax1.legend()

ax2.plot(highest_power_day_data.index, highest_power_day_data["total_main_kw"], color='purple', label='Power kW')
ax2.set_xlabel('Date')
ax2.set_ylabel('Power kW')
ax2.set_title('Power Consumption on Highest Power Day')

# Create a custom legend for the power consumption plot
handles, labels = ax2.get_legend_handles_labels()
handles.append(plt.Line2D([], [], color='none'))  # Adding an empty artist for spacing
labels.append(f'Highest Rate of Change: {highest_rate_of_change:.2f}')
ax2.legend(handles, labels)

plt.tight_layout()

# Save plots
plt.savefig(f"./plots/high_power_day.png", dpi=300)
print(f"Plots saved successfully")

# Show plots
# plt.show()


