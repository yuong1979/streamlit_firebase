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
    st.session_state.tick_type=st.session_state.tic_EquityExploreDetail

def handle_select_industry():
    st.session_state.ind_type=st.session_state.ind_EquityExploreDetail

# #################################################################################################
# ####### Testing ###############################################
# #################################################################################################
# python -c 'from EquityExploreDetail import Equity_Explore_Detail; Equity_Explore_Detail()'

def Equity_Explore_Detail():

    dffin = pd.read_pickle('data/eq_hist_details.pickle')

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
    #     key = "ind_EquityExploreDetail",
    #     on_change = handle_select_industry
    # )

    # #recording the selected industry from sessions
    # st.session_state['ind_type'] = selected_ind

    #retrieving the selected industry from sessions
    if 'tick_type' not in st.session_state:
        index_no = 0
    else:
        sel_tick = st.session_state['tick_type']
        index_no = merged_ticker_list.index(sel_tick)


    selected_choice = st.selectbox(
        'Select a Ticker',
        tuple(merged_ticker_list),
        index=index_no,
        key = "tic_EquityExploreDetail",
        on_change = handle_select_ticker
    )

    selected_ticker = ticker_df.index[ticker_df['merged_name']==selected_choice].item()

    #recording the selected industry from sessions
    st.session_state['tick_type'] = selected_choice

    #hardcoded to save time in doing a unique extract from the raw pickle file
    cat_list = ['annual_balancesheet', 'annual_cashflow', 'annual_profit&loss', 'quarterly_balancesheet', 'quarterly_cashflow', 'quarterly_profit&loss']

    col1, col2 = st.columns(2)


    with col1:
        selected_cat = st.radio("Select Report", cat_list, horizontal=True)

    if selected_cat == 'annual_balancesheet':
        df = extract_hist_details_ann_balancesheet()
        kpi_list = df['kpi'].unique().tolist()
    elif selected_cat == 'annual_cashflow':
        df = extract_hist_details_ann_cashflow()
        kpi_list = df['kpi'].unique().tolist()
    elif selected_cat == 'annual_profit&loss':
        df = extract_hist_details_ann_profitnloss()
        kpi_list = df['kpi'].unique().tolist()
    elif selected_cat == 'quarterly_balancesheet':
        df = extract_hist_details_qtr_balancesheet()
        kpi_list = df['kpi'].unique().tolist()
    elif selected_cat == 'quarterly_cashflow':
        df = extract_hist_details_qtr_cashflow()
        kpi_list = df['kpi'].unique().tolist()
    elif selected_cat == 'quarterly_profit&loss':
        df = extract_hist_details_qtr_profitnloss()
        kpi_list = df['kpi'].unique().tolist()

    with col2:
        selected_kpi = st.selectbox(
            'Select an indicator',
            tuple(kpi_list),
            index=0,
        )

    selected_comparison = st.radio(
        "Select indicator to compare with",
        ('Price', 'Industry Totals'), horizontal=True)



    # selected_ticker = ticker_df.index[ticker_df['merged_name']==selected_choice].item()

    dffin = dffin[ (dffin['ticker'] == selected_ticker) & (dffin['kpi'] == selected_kpi) & (dffin['cattype'] == selected_cat)]
    # dffin['date'] = pd.to_datetime(dffin['date'], format='%Y-%m-%d')
    dffin_date_list = dffin['date'].tolist()
    dffin_val_list = dffin['values'].tolist()


    ########### injecting only month end price ###########
    df_price = pd.read_pickle('data/eq_hist_price.pickle')
    # df_price['date'] =  pd.to_datetime(df_price['date'], format='%Y-%m-%d')
    # df_price = df_price[df_price['date'].dt.is_month_end]
    df_price = df_price[ (df_price['ticker'] == selected_ticker) ]
    df_price = df_price.sort_values(by='date', ascending=True)
    price_date_list = df_price['date'].tolist()
    price_price_list = df_price['price'].tolist()

    ########### injecting Median industry numbers ###########
    df_industry_sum = pd.read_pickle('data/eq_hist_sum.pickle')
    selected_industry = ticker_df[ticker_df.index == selected_ticker]['industry'].values[0]
    df_industry_sum = df_industry_sum.groupby(["last_date", "industry", "cattype", "kpi"])['values'].sum()
    df_industry_sum = df_industry_sum.reset_index()
    df_industry = df_industry_sum[(df_industry_sum['industry'] == selected_industry) & (df_industry_sum['cattype'] == selected_cat) & (df_industry_sum['kpi'] == selected_kpi)]
    df_industry = df_industry.sort_values(by='last_date', ascending=True)
    industry_sum_date_list = df_industry['last_date'].tolist()
    industry_sum_values_list = df_industry['values'].tolist()


    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Bar(x=dffin_date_list, y=dffin_val_list, name="yaxis data"),
        secondary_y=False,
    )

    if selected_comparison == 'Price':
        fig.add_trace(
            go.Scatter(x=price_date_list, y=price_price_list, name="yaxis2 data"),
            secondary_y=True,
        )
    else:
        fig.add_trace(
            go.Bar(x=industry_sum_date_list, y=industry_sum_values_list, name="yaxis2 data"),
            secondary_y=True,
        )



    # Add figure title
    fig.update_layout(
        title_text="Double Y Axis Example"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="xaxis title")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)


    st.plotly_chart(fig, use_container_width=True)



