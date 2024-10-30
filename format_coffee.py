import pandas as pd

df = pd.read_csv('coffee.csv')

df.datetime = pd.to_datetime(df.datetime)
df_grouped = df.groupby(pd.Grouper(key="datetime", freq="1h")).count()

df_clean = df_grouped[['datetime', 'date']]

df_clean.rename(columns={'date': 'sales_count'}, inplace=True)

df_clean.to_csv('coffee_by_the_hour.csv')