import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('./data/raw_data.csv')

# Convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Perform forward filling followed by back filling for missing values
df.fillna(method='ffill', inplace=True)
df.fillna(method='bfill', inplace=True)

# drop duplicate rows
df = df.drop_duplicates()

# Calculate rolling average for each column, including 'Date'
df_rolling_avg = df.rolling(window=3, min_periods=1, on='Date').mean()

# Save the resulting DataFrame to a CSV file
df_rolling_avg.to_csv('./data/processed_data.csv')

# Remove 'Date' column from the DataFrame
df_rolling_avg = df_rolling_avg.drop('Date', axis=1)

# Iterate through columns and save plots for each column
for column in df_rolling_avg.columns:
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(df['Date'], df_rolling_avg[column])
    ax.set_xlabel('Date')
    ax.set_ylabel(column)
    plt.savefig(f'./images/{column}_plot.png')
    plt.close()


