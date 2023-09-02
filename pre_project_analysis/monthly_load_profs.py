import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pandas.tseries.holiday import USFederalHolidayCalendar


# clean dataset
def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    cleaner = f"dataset has been cleaned"
    print(cleaner)
    return df[indices_to_keep].astype(np.float64)

def avg_load_profile_maker(df,month_num,label):
    data = df.loc[df.index.month.isin([month_num])]
    mondays = data.loc[(data.index.weekday == 0)]
    mondays = mondays.groupby(mondays.index.hour)['total_main_kw'].mean()
    tuesdays = data.loc[(data.index.weekday == 1)]
    tuesdays = tuesdays.groupby(tuesdays.index.hour)['total_main_kw'].mean()
    wednesdays = data.loc[(data.index.weekday == 2)]
    wednesdays = wednesdays.groupby(wednesdays.index.hour)['total_main_kw'].mean()
    thursdays = data.loc[(data.index.weekday == 3)]
    thursdays = thursdays.groupby(thursdays.index.hour)['total_main_kw'].mean()
    fridays = data.loc[(data.index.weekday == 4)]
    fridays = fridays.groupby(fridays.index.hour)['total_main_kw'].mean()
    saturdays = data.loc[(data.index.weekday == 5)]
    saturdays = saturdays.groupby(saturdays.index.hour)['total_main_kw'].mean()
    sundays = data.loc[(data.index.weekday == 6)]
    sundays = sundays.groupby(sundays.index.hour)['total_main_kw'].mean()
    df_all_by_weekday_num = pd.concat([mondays, tuesdays, wednesdays, thursdays, fridays, saturdays, sundays], axis=1)
    df_all_by_weekday_num.columns = ['mondays', 'tuesdays', 'wednesdays', 'thursdays', 'fridays', 'saturdays', 'sundays']
    df_all_by_weekday_num.plot(ylabel ='total_main_kw', ylim=(0, df.total_main_kw.max()), xlabel ='Hour Of Day', title=f'Averaged Hourly Electric Load Profiles For The Month of {label}',figsize=(25, 8))

                               
# Load the electricity data
df = pd.read_csv("hourly_electric_data.csv")
df["Date"] = pd.to_datetime(df["Date"])
df.set_index("Date", inplace=True)

df = clean_dataset(df)

print(df.columns)
print()
print(df)
print()

max_days = df.sort_values(by='total_main_kw', ascending=False).head(10)
max_days_weekdays = max_days[max_days.index.weekday.isin([0,1,2,3,4,5,6])]
max_days_weekdays.index.day_name().value_counts()
print("max_days_weekdays: \n",max_days_weekdays)

plt.figure(figsize=(10, 6))
max_days_weekdays.plot(kind='bar', y='total_main_kw', legend=False)
plt.xticks(rotation=45, ha='right')
plt.xlabel('Date')
plt.ylabel('total_main_kw')
plt.title('Top 10 Max Load Days (Weekdays)')
plt.tight_layout()

plt.savefig('./plots/max_load_days.png', dpi=300)
# plt.show()


months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

for month_num in range(1, 13):
    this_month = months[month_num - 1]
    print(f"Month {month_num}: {this_month}")
    
    plot = avg_load_profile_maker(df, month_num, this_month)

    plt.savefig(f"./plots/{this_month}_avg_load_prof.png", dpi=300)
    print(f"{this_month} saved successfully")

