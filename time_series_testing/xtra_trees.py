from sklearn.tree import ExtraTreeRegressor
import pandas as pd
import numpy as np
import argparse
from sklearn.model_selection import TimeSeriesSplit
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time

MODEL = "ExtraTreeRegressor"
HIGHEST_POWER_DAY = 3


def get_nth_highest_day(df, n=1):
    sorted_df = df.sort_values("main_power_watts", ascending=False)
    sorted_df["date"] = sorted_df.index.date
    unique_days = sorted_df["date"].unique()
    if n > len(unique_days):
        raise ValueError("n is larger than the number of days in the dataset")
    nth_highest_day_date = unique_days[n - 1]
    nth_highest_day_data = df[df.index.date == nth_highest_day_date]
    return nth_highest_day_data


# Define default values for command-line arguments
DEFAULT_CORRELATION = 0.99

# Create an ArgumentParser object
parser = argparse.ArgumentParser(
    description="Train a regression model with adjustable correlation threshold."
)

# Add an argument for the correlation threshold
parser.add_argument(
    "--corr",
    type=float,
    default=DEFAULT_CORRELATION,
    help="Correlation threshold for feature selection (default: {})".format(
        DEFAULT_CORRELATION
    ),
)

# Parse the command-line arguments
args = parser.parse_args()

# Assign the correlation threshold to the CORRELATION constant
CORRELATION = args.corr

# Read the CSV files
data1 = pd.read_csv("data1.csv")
data2 = pd.read_csv("data2.csv")

# Convert the date columns to datetime
data1["Date"] = pd.to_datetime(data1["Date"])
data2["Date"] = pd.to_datetime(data2["Date"])

# Set the datetime as the index
data1.set_index("Date", inplace=True)
data2.set_index("Date", inplace=True)

# Merge the DataFrames using merge_asof
df = pd.merge_asof(
    data1.sort_index(),
    data2.sort_index(),
    left_index=True,
    right_index=True,
    direction="nearest",
)
df = df.ffill().bfill()

print(df.columns)

# Compute the absolute correlation matrix
correlation_matrix = df.corr().abs()

# Select the upper triangle of the correlation matrix
upper = correlation_matrix.where(
    np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
)

print("DOING CORR: ", CORRELATION)

features_to_check_for_correlation = df.drop(columns=["main_power_watts"]).columns
to_drop = [
    column
    for column in upper.columns
    if any(upper[column] > CORRELATION) and column in features_to_check_for_correlation
]

print("Cols to drop \n", to_drop)

# Drop features from the dataframe
df = df.drop(columns=to_drop, errors="ignore")

# Drop features from the dataframe
df = df.drop(columns=to_drop, errors="ignore")

print(df.columns)

# Check for duplicate indices
if df.index.duplicated().any():
    print("Duplicate indices found.")
    df = df[~df.index.duplicated()]

# Choose a specific day for plotting
highest_power_day = get_nth_highest_day(df, HIGHEST_POWER_DAY)
highest_power_day_data = highest_power_day

# remove highest days power so the model doesnt train on it
df = df[df.index.date != highest_power_day_data.index.date[0]]

# Assuming the index is unique after the previous check or correction
forecast_horizon = 60
y = pd.concat(
    [df["main_power_watts"].shift(-i) for i in range(forecast_horizon)], axis=1
)
y.columns = [f"t+{i}" for i in range(forecast_horizon)]

# Drop the last 'forecast_horizon' rows in 'df' which do not have corresponding future values in 'y'
df = df[:-forecast_horizon]

# Define 'X' after dropping 'forecast_horizon' to avoid using future data in training
X = df.drop(columns=["main_power_watts"])

# Also, drop the last 'forecast_horizon' rows from 'y' to remove NaN values
y = y[:-forecast_horizon]

# Time series split for validation
tscv = TimeSeriesSplit(n_splits=5)

# Wrap ExtraTreeRegressor for multi-output regression
model = MultiOutputRegressor(ExtraTreeRegressor(random_state=0))


# Parameter grid for ExtraTreesRegressor
parameter_grid = {
    "estimator__max_depth": [None, 10, 20, 30],
    "estimator__min_samples_split": [2, 5, 10],
    "estimator__min_samples_leaf": [1, 2, 4],
}

# Time Series Cross Validator
time_series_cv = TimeSeriesSplit(n_splits=5).split(X)

# Grid Search with time series cross-validation
grid_search = GridSearchCV(
    model, parameter_grid, cv=time_series_cv, scoring="neg_mean_squared_error"
)

start = time.time()
print(f"{MODEL} training GO! {time.ctime()}")

grid_search.fit(X, y)

end = time.time()
print(f"{MODEL} All Done! {time.ctime()}")

# Time taken to train
time_in_seconds = end - start
time_in_minutes = round(time_in_seconds / 60, 2)

print(f"Training time: {time_in_seconds:.2f} seconds ({time_in_minutes:.2f} minutes)")

# Best model after grid search
best_model = grid_search.best_estimator_

# Predict using best model
predictions = best_model.predict(X)

# Compute metrics
mse = mean_squared_error(y, predictions)
rsme = round(np.sqrt(mse), 2)
r2 = round(r2_score(y, predictions), 2)

model_training_info_str = (
    MODEL
    + f" RMSE: {rsme} R^2: {r2} Train Time Minutes: {time_in_minutes} Corr: {CORRELATION}"
)
print(model_training_info_str)

# Use the last rows of the training data as future_X
future_X = X.tail(forecast_horizon)

# Predict the next 60 future values
future_predictions = best_model.predict(future_X)

print(f"Future Predictions: {future_predictions}")

# Prepare 'X_day' by dropping the target variable
X_day = highest_power_day_data.drop(columns=["main_power_watts"])

# Prepare 'y_day' by including only the target variable for the selected day
y_day = highest_power_day_data["main_power_watts"]

# Predict for the selected day
predictions_day = best_model.predict(X_day)

# For a simple plot of the next immediate prediction at each time step:
first_step_predictions = predictions_day[:, 0]

# Plotting the predictions for the selected day
plt.figure(figsize=(15, 5))
plt.plot(highest_power_day_data.index, y_day, label="Actual", marker="o")
plt.plot(
    highest_power_day_data.index,
    first_step_predictions,
    label="Predicted",
    marker="x",
    linestyle="--",
)
plt.title(model_training_info_str)
plt.xlabel("Time of Day")
plt.ylabel("Main Power Watts")
plt.legend()

# Improve the x-axis with proper date formatting
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.gca().xaxis.set_major_locator(mdates.HourLocator())
plt.gcf().autofmt_xdate()

# Save the plot as a PNG file
filename = f"{MODEL}_corr_{CORRELATION}.png"
plt.savefig(filename)

# plt.show()
