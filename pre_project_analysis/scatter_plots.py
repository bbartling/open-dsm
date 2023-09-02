import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from pandas.tseries.holiday import USFederalHolidayCalendar

# use string "CLOSED" for closed days
STORE_HOURS = {
    "monday": "9 - 5",
    "tuesday": "12 - 8",
    "wednesday": "9 - 5",
    "thursday": "12 - 8",
    "friday": "9 - 5",
    "saturday": "9 - 5",
    "sunday": "CLOSED",
}


# clean dataset
def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    cleaner = f"dataset has been cleaned"
    print(cleaner)
    return df[indices_to_keep].astype(np.float64)


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

def make_dummies(df):
    df["day_of_week"] = df.index.dayofweek
    df["weekend"] = np.where(df["day_of_week"].isin([5, 6]), 1, 0)
    df["month"] = df.index.month

    day_mapping = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }
    all_days = pd.Categorical(
        df["day_of_week"].map(day_mapping), categories=day_mapping.values()
    )
    day_dummies = pd.get_dummies(all_days).set_index(df.index)

    month_mapping = {
        1: "jan",
        2: "feb",
        3: "mar",
        4: "apr",
        5: "may",
        6: "jun",
        7: "jul",
        8: "aug",
        9: "sep",
        10: "oct",
        11: "nov",
        12: "dec",
    }

    all_months = pd.Categorical(
        df["month"].map(month_mapping), categories=month_mapping.values()
    )
    month_dummies = pd.get_dummies(all_months).set_index(df.index)

    """
    New Year's Day
    Martin Luther King Jr. Day
    Presidents Day
    Memorial Day
    Independence Day
    Labor Day
    Columbus Day
    Veterans Day
    Thanksgiving
    Christmas Day
    """
    cal = USFederalHolidayCalendar()
    first = df.index.min()
    last = df.index.max()

    print()
    print("df head: ", df.head())
    print("Data types: ", df.dtypes)
    print("First date: ", first)
    print("Last date: ", last)
    print("Index: ", df.index)
    print()

    holiday_dates = cal.holidays(start=first, end=last)

    df["holidays"] = df.index.isin(holiday_dates).astype(int)

    df = pd.concat([df, day_dummies, month_dummies], axis=1)
    df = df.drop(["day_of_week", "month"], axis=1)
    return df

# Ensure that df index is datetime
df.index = pd.to_datetime(df.index)

# Generate dummy variables
df = make_dummies(df)

# Separate the data into occupied and unoccupied datasets based on STORE_HOURS
# Convert to title case for consistency with df.index.day_name()
occupied_days = [day.title() for day, hours in STORE_HOURS.items() if hours != "CLOSED"]

# Your logic was correct here
occupied_df = df[df.index.day_name().isin(occupied_days)]

# Since there are only 7 days a week, and you have already found the occupied days,
# the rest of the days are unoccupied. So, you can simply use the reverse condition.
unoccupied_df = df[~df.index.day_name().isin(occupied_days)]

# Create scatter plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Scatter plot for occupied building data
ax1.scatter(occupied_df["HourlyDryBulbTemperature"], occupied_df["total_main_kw"], color='b', label='Occupied', s=10)
ax1.set_xlabel('Dry Bulb Temp (°F)')
ax1.set_ylabel('Power kW')
ax1.set_title('Occupied Building')
ax1.legend()
ax1.set_xlim(-15, 100)
ax1.set_ylim(0, 35)

# Scatter plot for unoccupied building data
ax2.scatter(unoccupied_df["HourlyDryBulbTemperature"], unoccupied_df["total_main_kw"], color='r', label='Unoccupied', s=10)
ax2.set_xlabel('Daily Dry Bulb Temp (°F)')
ax2.set_ylabel('Power kW')
ax2.set_title('Unoccupied Building')
ax2.legend()
ax2.set_xlim(-15, 100)
ax2.set_ylim(0, 35)

plt.savefig(f"./plots/occ_unnoc_scatter.png", dpi=300)
print(f"Plots saved successfully")

# Create subplots for line plots
fig, (ax3, ax4) = plt.subplots(2, 1, figsize=(12, 6))

# Line plot for weather data (Dry Bulb Temperature)
ax3.plot(weather_hourly.index, weather_hourly["HourlyDryBulbTemperature"], color='green', label='Dry Bulb Temp')
ax3.set_xlabel('Date')
ax3.set_ylabel('Temperature (°F)')
ax3.set_title('Hourly Dry Bulb Temperature')
ax3.legend()

# Line plot for power data
ax4.plot(df.index, df["total_main_kw"], color='purple', label='Power kW')
ax4.set_xlabel('Date')
ax4.set_ylabel('Power kW')
ax4.set_title('Hourly Power Consumption')
ax4.legend()

# Create subplots for line plots
fig2, (ax5, ax6) = plt.subplots(2, 1, figsize=(12, 6))

# Line plot for highest power data
highest_power_day = df[df['total_main_kw'] == df['total_main_kw'].max()]
print("highest power day: \n", highest_power_day)

highest_power_day_data = df[df.index.date == highest_power_day.index.date[0]]  # Corrected line

# Line plot for weather data (Dry Bulb Temperature) on the same day
ax5.plot(highest_power_day_data.index, highest_power_day_data["HourlyDryBulbTemperature"], color='green', label='Dry Bulb Temp')
ax5.set_xlabel('Date')
ax5.set_ylabel('Temperature (°F)')
ax5.set_title('Hourly Dry Bulb Temperature on Highest Power Day')
ax5.legend()

ax6.plot(highest_power_day_data.index, highest_power_day_data["total_main_kw"], color='purple', label='Power kW')
ax6.set_xlabel('Date')
ax6.set_ylabel('Power kW')
ax6.set_title('Power Consumption on Highest Power Day')
ax6.legend()

plt.tight_layout()


# Save plots
plt.savefig(f"./plots/high_power_day.png", dpi=300)
print(f"Plots saved successfully")

# plt.show()
