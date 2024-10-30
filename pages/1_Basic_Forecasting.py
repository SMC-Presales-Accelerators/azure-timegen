import os
import streamlit as st
import pandas as pd
from nixtla import NixtlaClient
from dotenv import load_dotenv

load_dotenv()

TIMEGEN_URL = os.getenv("TIMEGEN_URL")
TIMEGEN_API_KEY = os.getenv("TIMEGEN_API_KEY")

# Instantiate the Nixtla Client
nixtla_client = NixtlaClient(
    base_url=TIMEGEN_URL,
    api_key=TIMEGEN_API_KEY,
)

st.title('TIMEGEN-1 Forecasting')

uploaded_data = st.file_uploader('Time Series Data File (CSV or Excel)', [
    'csv', 'xlsx'
])

if uploaded_data is not None:
    df = pd.DataFrame()
    if('.xlsx' in uploaded_data.name):
        df = pd.read_excel(uploaded_data)
    elif('.csv' in uploaded_data.name):
        df = pd.read_csv(uploaded_data)
    else:
        st.write("Unknown File Type uploaded")

    time_column = st.selectbox('Select your Time column', list(df.columns))

    prediction_column = st.selectbox('Select your Prediction column', list(df.columns))

    number_of_predictions = st.number_input('How many timeframes do you want to predict?', 1, 100)

    if(st.button('Predict')):
        # Forecast
        forecast_df = nixtla_client.forecast(
            df=df,
            h=number_of_predictions,
            time_col=time_column,
            target_col=prediction_column,
        )

        # Plot predictions
        st.pyplot(nixtla_client.plot(
            df=df.tail(number_of_predictions*3), forecasts_df=forecast_df, time_col=time_column, target_col=prediction_column
        ))

    
