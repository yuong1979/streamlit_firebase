import streamlit as st
import pandas as pd
import yfinance as yf


st.title('Finance dashboard')

tickers = ('TSLA', 'AAPL', 'MSFT', 'BTC-USD')

dropdown = st.multiselect("Pick your assets", tickers)

start = st.date_input("Start", value = pd.to_datetime('2021-01-01'))
end = st.date_input("End", value = pd.to_datetime('today'))

def relativeret(df):
    rel = df.pct_change()
    cumret = (1+rel).cumprod() - 1
    cumret = cumret.fillna(0)
    return cumret


if len(dropdown) > 0:
    # df = yf.download(dropdown, start, end)['Adj Close']
    df = relativeret(yf.download(dropdown, start, end)['Adj Close'])
    st.line_chart(df)


# based on tutorial on https://youtu.be/Km2KDo6tFpQ