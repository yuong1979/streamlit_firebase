import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_industry_pickle
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np


# #################################################################################################
# ####### Spider chart ratios of individual equities ###############################################
# #################################################################################################
# python -c 'from test import ratios_ranked_per_industry_radar; ratios_ranked_per_industry_radar()'




def handle_select_ticker():
    st.session_state.tick_type=st.session_state.tic_EquityExploreRatiosRankings

# def handle_select_industry():
#     st.session_state.ind_type=st.session_state.ind_EquityExploreRatiosRankings

def Equity_Explore_Ratios_Rankings():

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


    df = pd.read_pickle('data/eq_daily_agg.pickle')

    # last_recorded_datetime = df['daily_agg_record_time'].min().strftime("%b %d %Y %H:%M:%S")

    ticker_list = df.index.unique().tolist()
    kpi_list = df.kpi.unique().tolist()
    kpi_list.remove("ebitdaUSD")
    kpi_list.remove("totalRevenueUSD")
    kpi_list.remove("marketCapUSD")

    Default_kpis = kpi_list[:len(kpi_list)-20]

    # st.write('\n')
    # st.markdown('---')

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
    #     key = "ind_EquityExploreRatiosRankings",
    #     on_change = handle_select_industry
    # )

    # #recording the selected industry from sessions
    # st.session_state['ind_type'] = selected_ind

    #retrieving the selected ticker from sessions
    if 'tick_type' not in st.session_state:
        index_no = 0
    else:

        sel_tick = st.session_state['tick_type']
        print (sel_tick)

        # print (merged_ticker_list, 'merged list')

        index_no = merged_ticker_list.index(sel_tick)


    col1, col2 = st.columns([1,2])

    with col1:
        selected_choice = st.selectbox(
            'Select an company',
            tuple(merged_ticker_list),
            # types[st.session_state['type']],
            index=index_no,
            key = "tic_EquityExploreRatiosRankings",
            on_change = handle_select_ticker
        )

    selected_tick = ticker_df.index[ticker_df['merged_name']==selected_choice].item()
 
    with col2:
        selected_kpi = st.multiselect(
            "Select a ratio:",
            options = kpi_list,
            default = Default_kpis
        )

    #recording the selected industry from sessions
    st.session_state['tick_type'] = selected_choice
    print(selected_choice)

    # if len(selected_kpi) >= 15:
    #     st.error('User may only choose a maximum of 14 ratios')
    #     st.stop()

    df = df[(df.index == selected_tick)]
    df['value'] = df['value'].apply(lambda x: round(x, 3))

    main_list = []
    values_list = []
    rank_fraction_list = []
    # median_rank_list = []

    # a loop is done because if filter is done on the dataframe it will not include non existing values which will be required when kpi is selected
    for i in selected_kpi:
        value = df[df.kpi == i]['value']
        rank = df[df.kpi == i]['rank_%']
        rank_fraction = df[df.kpi == i]['rank_fraction']
        median = df[df.kpi == i]['median']
        try:

            values_list.append(value.values[0])
            main_list.append(rank.values[0])
            rank_fraction_list.append(rank_fraction.values[0])
            # median_rank_list.append(median.values[0])
        except:

            values_list.append(np.nan)
            main_list.append(np.nan)
            rank_fraction_list.append(np.nan)
            # median_rank_list.append(np.nan)

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r = main_list,
        theta = selected_kpi,
        fill = 'toself',
        # showlegend=True,
        fillcolor = 'green',
        line_shape = 'spline', #linear
        text = values_list, 
        opacity=0.6,
        mode = 'markers+text', 
        textfont_color='red', 
        # textposition='bottom center',
        marker_color='green',

    ))

    # fig.add_trace(go.Scatterpolar(
    #     r = median_rank_list,
    #     theta = selected_kpi,
    #     # fill = 'toself',
    # ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=False,
        range=[0, 1]
        )),
        showlegend=False
    )

    fig.update_layout(
        autosize=False,
        # width=800,
        # margin=dict(l=20, r=20, t=100, b=100),
        height=800,
    )
    
    hovertemplate = ('Ratio: %{customdata[0]}<br>' + 'Ranking: %{customdata[1]}<br>' + 'Value: %{customdata[2]}<br><extra></extra>')
    customdata = np.stack((selected_kpi, rank_fraction_list, values_list), axis=-1)
    fig.update_traces(customdata=customdata,hovertemplate=hovertemplate)


    st.plotly_chart(fig, use_container_width=True)

#     st.caption("Last updated :" + str(last_recorded_datetime))



