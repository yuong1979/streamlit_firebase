import pandas as pd
import plotly.express as px  # pip install plotly-express
import streamlit as st
import numpy as np
from plotly.subplots import make_subplots
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
from tools import (
    extract_industry_pickle,
    extract_hist_details_ann_balancesheet, extract_hist_details_ann_cashflow, extract_hist_details_ann_profitnloss,
    extract_hist_details_qtr_balancesheet, extract_hist_details_qtr_cashflow, extract_hist_details_qtr_profitnloss
)

def handle_select_ticker():
    st.session_state.tick_type=st.session_state.tic_EquityExploreTimeSeries

def handle_select_industry():
    st.session_state.ind_type=st.session_state.ind_EquityExploreTimeSeries

# #################################################################################################
# ####### Testing ###############################################
# #################################################################################################
# python -c 'from EquityExploreDetail import Equity_Explore_Time_Series; Equity_Explore_Time_Series()'

def Equity_Explore_Time_Series():

    # For Retrieving the  ticker list
    ticker_df = pd.read_pickle('data/eq_daily_kpi.pickle')

    # To include shortnames
    ticker_df['merged_name'] = ticker_df.index.astype(str) + " / " + ticker_df['shortName'].astype(str)

    #Selecting the ticker so it starts from the biggest in market cap down to the lowest, also selected all neccessary columns only so speed is increased
    ticker_df = ticker_df.filter(['marketCapUSD', 'merged_name', 'industry'])
    #replace with none all those data that are empty
    ticker_df['marketCapUSD'] = ticker_df['marketCapUSD'].apply(lambda x: None if x == "" else x)
    ticker_df = ticker_df.sort_values(by='marketCapUSD', ascending=False)
    merged_ticker_list = ticker_df['merged_name'].tolist()

    # ind = extract_industry_pickle()
    # ind_list = ind.industry.values.tolist()

    # #retrieving the selected industry from sessions
    # if 'ind_type' in st.session_state:
    #     sel_ind = st.session_state['ind_type']
    #     index_no = ind_list.index(sel_ind)
    # else:
    #     index_no = 0

    # selected_ind = st.selectbox(
    #     'Select an industry',
    #     tuple(ind_list),
    #     index = index_no,
    #     key = "ind_EquityExploreTimeSeries",
    #     on_change = handle_select_industry
    # )

    # #recording the selected industry from sessions
    # st.session_state['ind_type'] = selected_ind

    #retrieving the selected ticker from sessions
    if 'tick_type' not in st.session_state:
        index_no = 0
    else:
        sel_tick = st.session_state['tick_type']
        index_no = merged_ticker_list.index(sel_tick)

    col1, col2 = st.columns(2)

    with col1:
        selected_choice = st.selectbox(
            'Select a Ticker',
            tuple(merged_ticker_list),
            index=index_no,
            key = "tic_EquityExploreTimeSeries",
            on_change = handle_select_ticker
        )

    selected_ticker = ticker_df.index[ticker_df['merged_name']==selected_choice].item()

    #recording the selected industry from sessions
    st.session_state['tick_type'] = selected_choice

    #hardcoded to save time in doing a unique extract from the raw pickle file
    cat_list = ['annual_balancesheet', 'annual_cashflow', 'annual_profit&loss', 'quarterly_balancesheet', 'quarterly_cashflow', 'quarterly_profit&loss']

    with col2:
        selected_cat = st.radio("Select Report", cat_list, horizontal=True)

    if selected_cat == 'annual_balancesheet':
        df = extract_hist_details_ann_balancesheet()
        kpi_list = ['Total Current Assets', 'Total Stockholder Equity', 'Total Current Liabilities', 'Total Liab', 'Total Assets']
    elif selected_cat == 'annual_cashflow':
        df = extract_hist_details_ann_cashflow()
        kpi_list = ['Total Cashflows From Investing Activities', 'Change To Netincome', 'Total Cash From Operating Activities', 'Net Income', 'Change In Cash', 'Total Cash From Financing Activities']
    elif selected_cat == 'annual_profit&loss':
        df = extract_hist_details_ann_profitnloss()
        kpi_list = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'Ebit']
    elif selected_cat == 'quarterly_balancesheet':
        df = extract_hist_details_qtr_balancesheet()
        kpi_list = ['Total Current Assets', 'Total Stockholder Equity', 'Total Current Liabilities', 'Total Liab', 'Total Assets']
    elif selected_cat == 'quarterly_cashflow':
        df = extract_hist_details_qtr_cashflow()
        kpi_list = ['Total Cashflows From Investing Activities', 'Change To Netincome', 'Total Cash From Operating Activities', 'Net Income', 'Change In Cash', 'Total Cash From Financing Activities']
    elif selected_cat == 'quarterly_profit&loss':
        df = extract_hist_details_qtr_profitnloss()
        kpi_list = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'Ebit']

    ########### injecting only month end price ###########
    df_price = pd.read_pickle('data/eq_hist_price.pickle')
    # df_price['date'] =  pd.to_datetime(df_price['date'], format='%Y-%m-%d')
    # df_price = df_price[df_price['date'].dt.is_month_end]
    df_price = df_price[ (df_price['ticker'] == selected_ticker) ]
    df_price = df_price.sort_values(by='date', ascending=True)
    price_date_list = df_price['date'].tolist()
    price_price_list = df_price['price'].tolist()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for i in kpi_list:
        df_final = df[ (df['ticker'] == selected_ticker) & (df['kpi'] == i) & (df['cattype'] == selected_cat)]
        df_final.sort_values(by='date', ascending=True)
        dfvalues = df_final['values'].tolist()
        dfdate = df_final['date'].tolist()

        fig.add_trace(
            go.Bar(x = dfdate, y = dfvalues, name=i),
            secondary_y=False,
        )

    fig.add_trace(
        go.Scatter(x = price_date_list, y = price_price_list, name = "Price"),
        secondary_y=True,
    )
    
    st.plotly_chart(fig, use_container_width=True)



