import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



def calculate_target(df,MIN_LOAD_SHIFT_START_HOUR,HIGH_POWER_THRESHOLD):

    df["action"] = "no_action_required"  # By default, set all actions as "no_action_required"

    # Find the indices where the building power is above the HIGH_POWER_THRESHOLD
    high_power_indices = df[df["rtu_power"] > HIGH_POWER_THRESHOLD].index

    # Calculate the start times for float_setpoints_upward and load_shifting_idle
    float_setpoints_upward_start_indices = high_power_indices - pd.DateOffset(hours=4)
    load_shifting_idle_start_indices = high_power_indices - pd.DateOffset(hours=2)

    # Assign the appropriate action based on the calculated times
    df.loc[float_setpoints_upward_start_indices, "action"] = "building_precooling_start"
    df.loc[load_shifting_idle_start_indices, "action"] = "load_shifting_idle"

    min_timestamp = high_power_indices.min()
    print("min_timestamp: ",min_timestamp)

    if min_timestamp.time() < MIN_LOAD_SHIFT_START_HOUR:
        high_power_indices = high_power_indices[high_power_indices.time >= MIN_LOAD_SHIFT_START_HOUR]

    df.loc[high_power_indices, "action"] = "float_setpoints_upward"

    # Map the action values to a numerical scale
    action_mapping = {
        'no_action_required': 0,
        'building_precooling_start': 1,
        'load_shifting_idle': 2,
        'float_setpoints_upward': 3
    }
    df['action'] = df['action'].map(action_mapping)

    return df


def plot_data_by_date(df, date_string):
    # Filter the DataFrame for the specified date
    filtered_df = df[df.index.date == pd.to_datetime(date_string).date()]

    # Create a new figure with a single subplot
    fig, ax1 = plt.subplots(figsize=(15, 10))

    # Plot 'rtu_power'
    ax1.plot(filtered_df.index, filtered_df['rtu_power'], color='blue')
    ax1.set_ylabel('HVAC power - Watts', color='blue')

    # Create a second y-axis
    ax2 = ax1.twinx()

    # Plot 'action' on the second y-axis
    ax2.plot(filtered_df.index, filtered_df['action'], color='red')
    ax2.set_ylabel('action', color='red')

    # Replace the numeric y-axis labels with action names
    action_mapping_inverse = {
        0: 'no_action_required',
        1: 'building_precooling_start',
        2: 'load_shifting_idle',
        3: 'float_setpoints_upward'
    }
    ax2.set_yticks(list(action_mapping_inverse.keys()))
    ax2.set_yticklabels(list(action_mapping_inverse.values()))

    # Set the x-axis formatter to display only hours
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    ax1.set_xlabel('Time of Day')

    plt.savefig(f'./images/rtu_power_and_action_{date_string}.png')  # Save the plot as an image
    plt.show()


def plot_correlation_matrix(df):
    # Calculate correlation matrix
    corr = df.corr()

    # Create a mask to display only the lower triangle of the matrix
    mask = np.triu(np.ones_like(corr, dtype=bool))

    # Create a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Set up the plot figure
    plt.figure(figsize=(14, 14))

    # Draw the heatmap with the mask and correct aspect ratio
    heatmap = sns.heatmap(
        corr,
        mask=mask,
        cmap=cmap,
        vmax=1,
        vmin=-1,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.5},
        annot=True,
    )

    # Rotate and align the x-axis tick labels
    heatmap.set_xticklabels(
        heatmap.get_xticklabels(), rotation=45, horizontalalignment="right"
    )

    plt.title("Correlation Matrix")
    plt.savefig("./images/correlation_matrix.png")  # Save the plot as an image
    plt.show()


def plot_actions_by_hour(df):
    # Extract hour from Date
    df['Hour'] = df.index.hour

    # Create a violin plot of actions by hour of day
    plt.figure(figsize=(10, 6))
    violin_plot = sns.violinplot(x="action", y="Hour", data=df)
    plt.title("Actions by Hour of Day")

    # Replace the numeric x-axis labels with action names
    action_mapping_inverse = {
        0: 'no_action_required',
        1: 'building_precooling_start',
        2: 'load_shifting_idle',
        3: 'float_setpoints_upward'
    }
    violin_plot.set_xticklabels([action_mapping_inverse[int(tick.get_text())] for tick in violin_plot.get_xticklabels()])

    plt.savefig("./images/actions_by_hour.png")  # Save the plot as an image
    plt.show()
