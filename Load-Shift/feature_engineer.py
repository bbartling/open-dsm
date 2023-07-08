import pandas as pd
import os

from functions import *

os.makedirs("images", exist_ok=True)

# Set threshold for high power in watts
HIGH_POWER_THRESHOLD = 60000

# used if the daily weather hi temp forecast is below
# take no action for load shifting
OUTDOOR_DRYBULB_HI_LIMIT = 70

# default to noon
MIN_LOAD_SHIFT_START_HOUR = pd.to_datetime('12:00:00').time()

# create a plot of one day to verify sequencing
SEQUENCING_CHECK_DATE_PLOT = '2022-06-14'

df = pd.read_csv("./data/processed_data.csv", parse_dates=["Date"])
df = df.drop(columns=["Unnamed: 0", "jci_vavs_air_flow_cfm", "trane_vavs_air_flow_cfm"])
df.set_index("Date", inplace=True)

# Apply the function on the dataframe
df = calculate_target(df,MIN_LOAD_SHIFT_START_HOUR,HIGH_POWER_THRESHOLD)
print(df)

# create plots
plot_data_by_date(df,SEQUENCING_CHECK_DATE_PLOT)
plot_correlation_matrix(df)
plot_actions_by_hour(df)

# add in next hours weather data
# df = calculate_next_hour_averages(df, "out_temp_F", 8)
# print(df)

# save final data used to test ML model
df.to_csv("./data/final.csv")










