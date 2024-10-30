import streamlit as st

st.set_page_config(
    page_title="TIMEGEN Demo",
    page_icon="👋",
)

st.write("# Welcome to our TIMEGEN Demo! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    TIMEGEN is a forecasting model that uses the Nixtla library to predict future values in a time series dataset.

    Here we can show how generative models can be for more than just text or image based use. 

    If you do not have a dataset to upload, you can use one of the following datasets:
      - [Air Passengers Dataset](https://raw.githubusercontent.com/Nixtla/transfer-learning-time-series/main/datasets/air_passengers.csv)
      - [Electricity Consumption Dataset](https://raw.githubusercontent.com/Nixtla/transfer-learning-time-series/main/datasets/electricity_consumption.csv)
      - [Coffee Machine Usage Dataset](/app/static/coffee_by_the_hour.csv)
"""
)