import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
import time

# Read the CSV files
data1 = pd.read_csv("data1.csv")
data2 = pd.read_csv("data2.csv")

# Convert the date columns to datetime
data1['Date'] = pd.to_datetime(data1['Date'])
data2['Date'] = pd.to_datetime(data2['Date'])

# Set the datetime as the index
data1.set_index('Date', inplace=True)
data2.set_index('Date', inplace=True)

# Merge the DataFrames using merge_asof
df = pd.merge_asof(data1.sort_index(), data2.sort_index(), left_index=True, right_index=True, direction='nearest')
df = df.ffill().bfill()

# Check the data types after conversion
print(df.dtypes)

print(df.describe())

#df.plot()
#plt.show()

# Calculate the correlation matrix
correlation_matrix = df.corr()

# Print the correlation matrix
print(correlation_matrix)

# Plot the correlation matrix as a heatmap
plt.figure(figsize=(12, 8))  # Adjust the figure size as needed
plt.rcParams['font.size'] = 6  # Adjust the font size as needed
plt.imshow(correlation_matrix, cmap='coolwarm', interpolation='nearest')
plt.colorbar()
plt.title('Correlation Matrix')
plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=90)
plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)
plt.xticks(rotation=45)  # Rotate x-axis tick labels by 45 degrees
plt.yticks(rotation=0)   # Keep y-axis tick labels as they are
plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.15)  # Adjust the margins as needed
plt.savefig('correlation_matrix.png')
plt.show()



