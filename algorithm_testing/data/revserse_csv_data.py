import pandas as pd

# Read the CSV file
input_file = './egauge_data.csv'
output_file = './egauge_data_reversed_output.csv'

# Read the CSV into a pandas DataFrame
df = pd.read_csv(input_file)

# reverse the order of rows
df_reverse_rows = df.iloc[::-1]

print(df_reverse_rows)

# Save the reversed DataFrame to a new CSV file
df_reverse_rows.to_csv(output_file, index=False)

print("Reversed data saved to", output_file)
