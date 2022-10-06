import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_industry_pickle
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np



# #################################################################################################
# ####### Bar chart ratios of individual industries ###############################################
# #################################################################################################
# python -c 'from IndustryExploreRatiosDetails import Equity_Explore_Ratios_Details; Equity_Explore_Ratios_Details()'



# sort and and convert dataframe into a format that can be displayed in chart 
@st.experimental_memo
def process_dataframe(df, kpi_mapping, kpi):
    #to determine if the ratio is postive or negative
    if kpi_mapping[kpi] == True:
        df_grouped = df.sort_values(by=[kpi], ascending=True )
    else:
        df_grouped = df.sort_values(by=[kpi], ascending=False )

    df_grouped = df_grouped[[kpi, 'Name']]
    df_grouped = df_grouped.reset_index()

    return df_grouped


def handle_select():
    st.session_state.ind_type=st.session_state.ind_IndustryExploreRatiosDetails


def Equity_Explore_Ratios_Detail():

    df = pd.read_pickle('data/eq_daily_kpi.pickle')



    # To include shortnames
    df['Name'] = df.index.astype(str) + " / " + df['shortName'].astype(str)

    # #Selecting the ticker so it starts from the biggest in market cap down to the lowest, also selected all neccessary columns only so speed is increased
    # ticker_df = ticker_df.filter(['marketCapUSD', 'Name', 'industry'])
    # #replace with none all those data that are empty
    # ticker_df['marketCapUSD'] = ticker_df['marketCapUSD'].apply(lambda x: None if x == "" else x)
    df = df.sort_values(by='marketCapUSD', ascending=False)
    merged_ticker_list = df['Name'].tolist()
    


    # ticker_list = df.index.values.tolist()





    last_recorded_datetime = df['updated_datetime'].min().strftime("%b %d %Y %H:%M:%S")

    cols = df.columns.values.tolist()
    #remove unwanted kpis
    cols = [i for i in cols if i not in kpi_remove]
    cols.remove("industry")
    cols.remove("updated_datetime")
    cols.remove("shortName")
    cols.remove("isEsgPopulated")
    cols.remove("alpha_marketCapUSD")
    cols.remove("alpha_totalRevenueUSD")
    cols.remove("alpha_ebitdaUSD")


    # st.write('\n')
    # st.markdown('---')

    default_testing = ['grossMargins', 'operatingMargins']

    # #retrieving the selected industry from sessions
    # if 'ind_type' in st.session_state:
    #     sel_ind = st.session_state['ind_type']
    #     index_no = ind_list.index(sel_ind)
    # else:
    #     index_no = 0


    col1, col2 = st.columns([1,2])

    with col1:
        selected_choice = st.selectbox(
            'Select an industry',
            tuple(merged_ticker_list),
            # index=index_no,
            # key = "ind_IndustryExploreRatiosDetails",
            # on_change = handle_select,
        )

    #convert merged name to a ticker that can be read    
    selected_ticker = df[df['Name'] == selected_choice].index.values[0]


    # print (st.session_state)

    # if 'ind_type' not in st.session_state:
    #     st.session_state['ind_type'] = selected_ind

    with col2:
        selected_kpi = st.multiselect(
            "Select a ratio:",
            options= cols ,
            default= None
        )

    # print (st.session_state)

    if len(selected_kpi) >= 4:
        st.error('User may only choose a maximum of 3 ratios')
        st.stop()
    
    # #recording the selected industry from sessions
    # st.session_state['selected_ind'] = selected_ind

    selected_ind = df[df.index == selected_ticker]['industry'].values[0]
    ticker_list = df[df['industry'] == selected_ind].index.values

    df = df[df['industry'] == selected_ind]

    color_map = {}
    for i in ticker_list:
        color_map[i] = "lightgrey"
    
    color_map[selected_ticker] = "red"


    for kpi in selected_kpi: 

        with open('style/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            with st.container():

                df_grouped = process_dataframe(df, kpi_mapping, kpi)

                value = df.loc[selected_ticker, kpi].round(3)

                if kpi_mapping[kpi] == True:
                    maximum = df_grouped[kpi].max().round(3)
                    minimum = df_grouped[kpi].min().round(3)
                else:
                    minimum = df_grouped[kpi].max().round(3)
                    maximum = df_grouped[kpi].min().round(3)

                median = df_grouped[kpi].median().round(3)

                st.write('\n')

                st.subheader(kpi)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(label="Value", value=value)
                col2.metric(label="Market Maximum", value=maximum)
                col3.metric(label="Market Minimum", value=minimum)
                col4.metric(label="Market Median", value=median)



                fig = px.bar(
                    df_grouped,
                    x = kpi,
                    y = 'Name',
                    color = 'Ticker',
                    color_discrete_map = color_map,
                    # title=f'<b>{kpi}</b>',
                    template='plotly_white',
                    orientation="h",
                )

                fig.update_layout(
                    barmode="relative",
                    showlegend=False,
                    autosize=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    # width=800,
                    margin=dict(l=20, r=20, t=40, b=40),
                    # width=1000,
                    # height=1000,
                )

                st.plotly_chart(fig)

    st.caption("Last updated :" + str(last_recorded_datetime))























