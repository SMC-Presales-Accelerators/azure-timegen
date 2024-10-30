import os
import time
import uuid
import streamlit as st
import pandas as pd
import numpy as np
from nixtla import NixtlaClient
from dotenv import load_dotenv

from utilsforecast.losses import mae
from utilsforecast.evaluation import evaluate

from statsforecast import StatsForecast
from statsforecast.models import CrostonClassic, CrostonOptimized, IMAPA, TSB

load_dotenv()

TIMEGEN_URL = os.getenv("TIMEGEN_URL")
TIMEGEN_API_KEY = os.getenv("TIMEGEN_API_KEY")

# Instantiate the Nixtla Client
nixtla_client = NixtlaClient(
    base_url=TIMEGEN_URL,
    api_key=TIMEGEN_API_KEY,
)

st.title('TIMEGEN-1 Forecasting Comparison')

st.markdown(
    """
    For this specific situation instead of just doing a basic forecasting, we will compare the forecasting results with the actual data.
    We will also compare to some other forecasting models to see how well TIMEGEN performs.
    """
)

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

    unique_id_column = st.selectbox('Select your Unique ID (grouping) column', ["None"] + list(df.columns))

    number_of_predictions = st.number_input('How many timeframes do you want to predict?', 1, 100)

    if(st.button('Predict')):
        df_transformed = df.copy()
        if(unique_id_column == "None"):
            unique_id_column = "unique_id"
            df_transformed["unique_id"] = "time_series"

        df_transformed = df_transformed[[time_column, prediction_column, unique_id_column]]
        df_transformed[time_column] = pd.to_datetime(df_transformed[time_column])

        df_transformed[prediction_column] = np.log(df_transformed[prediction_column] + 1)

        test_df = df_transformed.groupby(unique_id_column).tail(number_of_predictions)

        input_df = df_transformed.drop(test_df.index).reset_index(drop=True)

        start = time.time()
        # Forecast
        forecast_df = nixtla_client.forecast(
            model="azureai",
            df=input_df,
            h=number_of_predictions,
            level=[80],
            finetune_steps=10,
            finetune_loss="mae",
            time_col=time_column,
            target_col=prediction_column,
            id_col=unique_id_column
        )
        end = time.time()

        st.write(f"TIMEGEN took {end - start} seconds to predict {number_of_predictions} timeframes.")
        cols = [col for col in forecast_df.columns if col not in [time_column, unique_id_column]]

        for col in cols:
            forecast_df[col] = np.exp(forecast_df[col]) - 1

        test_df[prediction_column] = np.exp(test_df[prediction_column]) - 1

        # Plot predictions

        st.pyplot(
            nixtla_client.plot(
                test_df, forecast_df, models=["TimeGPT"], level=[80], time_col=time_column, target_col=prediction_column
            )
        )

        forecast_df[time_column] = pd.to_datetime(forecast_df[time_column])

        test_df = pd.merge(test_df, forecast_df, "left", [unique_id_column, time_column])

        evaluation = evaluate(
            test_df, metrics=[mae], models=["TimeGPT"], target_col=prediction_column, id_col=unique_id_column
        )

        average_metrics = evaluation.groupby("metric")["TimeGPT"].mean()
        st.write(average_metrics)
