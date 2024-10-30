import os
import requests
import streamlit as st
import pandas as pd
import altair as alt
from functools import reduce
from datetime import date, timedelta
from nixtla import NixtlaClient
from dotenv import load_dotenv

load_dotenv()

TIMEGEN_URL = os.getenv("TIMEGEN_URL")
TIMEGEN_API_KEY = os.getenv("TIMEGEN_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# Instantiate the Nixtla Client
nixtla_client = NixtlaClient(
    base_url=TIMEGEN_URL,
    api_key=TIMEGEN_API_KEY,
)

st.title('TIMEGEN-1 Stock Forecasting')

ticker = st.text_input('Stock Symbol to Forecast', 'MSFT')

today = date.today()
yesterday = today - timedelta(days=1)
twoyears = today - timedelta(days=715)

if(st.button('Predict')):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{twoyears}/{yesterday}?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
    with st.spinner("Forecasting Stock Prices"):
        resp = requests.get(url=url)
        data = resp.json()

        df = pd.DataFrame(data['results'])

        df = df[['t', 'o', 'h', 'l', 'c']]

        df.rename(columns={'t': 'date', 'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close'}, inplace=True)

        # Remove 5 hours worth of milliseconds
        df.date = df.date - (5 * 60 * 60 * 1000)

        df.date = pd.to_datetime(df.date, unit='ms')

        #idx = pd.date_range(twoyears, yesterday)

        #df.index = pd.DatetimeIndex(df.date)

        #df = df.reindex(idx, method='pad')

        #df['date_refilled'] = df.index

        #df = df.reset_index(drop=True)

        #df.date = df.date_refilled

        #df = df.drop(columns=['date_refilled'])

        # st.dataframe(df)

        df_close = nixtla_client.forecast(
            df=df[['date', 'close']],
            freq='B',
            h=7,
            time_col='date',
            target_col='close',
        )

        df_close.rename(columns={'TimeGPT': 'close'}, inplace=True)
        
        df_open = nixtla_client.forecast(
            df=df[['date', 'open']],
            freq='B',
            h=7,
            time_col='date',
            target_col='open',
        )

        df_open.rename(columns={'TimeGPT': 'open'}, inplace=True)

        df_high = nixtla_client.forecast(
            df=df[['date', 'high']],
            freq='B',
            h=7,
            time_col='date',
            target_col='high',
        )

        df_high.rename(columns={'TimeGPT': 'high'}, inplace=True)

        df_low = nixtla_client.forecast(
            df=df[['date', 'low']],
            freq='B',
            h=7,
            time_col='date',
            target_col='low',
        )

        df_low.rename(columns={'TimeGPT': 'low'}, inplace=True)

        forecasts = [df_open, df_high, df_low, df_close]

        df_forecast = reduce(lambda  left,right: pd.merge(left,right,on=['date'],
                                                how='outer'), forecasts)
        
        df_forecast = pd.concat([df.tail(30), df_forecast])

        # st.dataframe(df_forecast)

        # Plot predictions
        #st.pyplot(nixtla_client.plot(
        #    df=df.tail(30), forecasts_df=forecast_df, time_col='date', target_col='close_price'
        #))

        open_close_color = alt.condition(
            "datum.open <= datum.close",
            alt.value("#06982d"),
            alt.value("#ae1325")
        )

        base = alt.Chart(df_forecast).encode(
            alt.X('date:T')
                .axis(format='%m/%d/%y', labelAngle=-45)
                .title('Date'),
            color=open_close_color
        )

        #base = base.mark_rule(color='pink', strokeDash=[4,2]).encode(x=alt.XValue(yesterday))

        rule = base.mark_rule().encode(
            alt.Y('low:Q')
                .title('Price')
                .scale(zero=False),
            alt.Y2('high:Q')
        )

        bar = base.mark_bar().encode(
            alt.Y('open:Q'),
            alt.Y2('close:Q')
        )

        st.altair_chart(rule + bar, use_container_width=True)

    
