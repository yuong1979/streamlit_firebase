import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_industry_pickle, convert_digits
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np
import datetime
from charts.EquityExploreRatiosRankings import Equity_Explore_Ratios_Rankings


def handle_select_industry():
    st.session_state.ind_type=st.session_state.ind_EquityExploreIndustryMarket

# def gohome():
#     st.session_state['page'] = 'Home'

# def industry():
#     st.session_state['page'] = 'Industry'

def handle_select_ticker():
    st.session_state.tick_type=st.session_state.tic_IndustryExploreRatiosMarketSize
    st.session_state['page'] = 'Equities'

    # st.success(st.session_state.tic_IndustryExploreRatiosMarketSize)
    # Equity_Explore_Ratios_Rankings()
    # st.stop()




# #################################################################################################
# ####### Tree chart ratios of industries ###############################################
# #################################################################################################
# python -c 'from charts.EquityExploreIndustryMarket import Industry_Explore_Industry_Market; Industry_Explore_Industry_Market()'

def Industry_Explore_Industry_Market():

    df = pd.read_pickle('data/eq_daily_kpi.pickle')

    last_recorded_datetime = df['updated_datetime'].min().strftime("%b %d %Y %H:%M:%S")

    #clean the data up to remove unwanted
    df = df.drop('isEsgPopulated', axis=1)
    df = df[((df['industry'] != 'Shell Companies'))]

    #sort the rank from the largest industry by marketcap to the lowest industry by market cap
    df_ind = df.groupby(["industry"]).sum()[["marketCapUSD"]].sort_values(by="marketCapUSD", ascending=False)
    df_ind = df_ind.reset_index()
    industry_list = df_ind['industry'].tolist()

    allcols = df.columns.values.tolist()
    #remove unwanted kpis and custom list
    cols = [i for i in allcols if i not in kpi_remove]
    cols.remove("industry")
    cols.remove("updated_datetime")
    cols.remove("shortName")
    cols.remove("alpha_ebitdaUSD")
    cols.remove("alpha_totalRevenueUSD")
    cols.remove("alpha_marketCapUSD")

    #Prepare the selectors in a list for selection
    size_kpi = ['ebitdaUSD', 'marketCapUSD', 'totalRevenueUSD']
    tuple_kpi_select = tuple(cols)
    tuple_size_kpi_select = tuple(size_kpi)
    tuple_ind_select = tuple(industry_list)

    #clean the size of the scatterplot because it does not allow nan values and negative values -> replaced with zero
    df['marketCapUSD'] = df['marketCapUSD'].replace(np.nan, 0)
    df['totalRevenueUSD'] = df['totalRevenueUSD'].replace(np.nan, 0)
    df['ebitdaUSD'] = df['ebitdaUSD'].replace(np.nan, 0)
    df['ebitdaUSD'] = df['ebitdaUSD'].apply(lambda x: 0 if x < 0 else x)


    #retrieving the selected industry from sessions
    if 'ind_type' in st.session_state:
        sel_ind = st.session_state['ind_type']
        index_no = industry_list.index(sel_ind)
    else:
        index_no = 0


    selected_ind = st.selectbox(
        'Select x axis',
        tuple_ind_select,
        index = index_no,
        key = "ind_EquityExploreIndustryMarket",
        on_change = handle_select_industry
    )

    #recording the selected industry from sessions
    st.session_state['ind_type'] = selected_ind


    with st.container():
        # st.write("Indicators for X/Y axis")
        col1, col2 = st.columns(2)
        with col1:
            selected_kpi_x = st.selectbox(
                'Select x axis',
                tuple_kpi_select,
                index=0,
                key = "ind_IndustryExploreRatiosMarketSize",
            )

        with col2:
            selected_kpi_y = st.selectbox(
                'Select y axis',
                tuple_kpi_select,
                index=1,
            )

    with st.container():
        # st.write("Indicators for color and size")
        col1, col2 = st.columns(2)
        with col1:
            selected_kpi_size = st.selectbox(
                'Select size',
                tuple_size_kpi_select,
                index=1,
            )

        with col2:
            selected_kpi_color = st.selectbox(
                'Select color',
                tuple_kpi_select,
                index=2,
            )

    # selected_ind = "Banks—Regional"
    # selected_kpi_x = 'grossMargins'
    # selected_kpi_y = 'operatingMargins'
    # selected_kpi_size = 'marketCapUSD'
    # selected_kpi_color = 'profitMargins'

    df = df[df['industry'] == selected_ind]
    df = df.reset_index()


    marketCapUSD_sum = df['marketCapUSD'].sum().item()
    marketCapUSD_sum = convert_digits(marketCapUSD_sum)

    ebitdaUSD_sum = df['ebitdaUSD'].sum().item()
    ebitdaUSD_sum = convert_digits(ebitdaUSD_sum)

    totalRevenueUSD_sum = df['totalRevenueUSD'].sum().item()
    totalRevenueUSD_sum = convert_digits(totalRevenueUSD_sum)

    company_count = df['Ticker'].count().item()

    st.write("")

    with st.container():
        st.write("Total Industry Indicators")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric = "MarketCap"
            col1.metric(label = metric, value = marketCapUSD_sum)

        with col2:
            metric = "Revenue"
            col2.metric(label = metric, value = totalRevenueUSD_sum)

        with col3:
            metric = "Ebitda"
            col3.metric(label = metric, value = ebitdaUSD_sum)

        with col4:
            metric = "Company Count"
            col4.metric(label = metric, value = company_count)

    shortname_list = df['shortName'].tolist()
    ticker_list = df['Ticker'].tolist()
    selected_kpi_x_list = df[selected_kpi_x].tolist()
    selected_kpi_y_list = df[selected_kpi_y].tolist()
    selected_kpi_size_list = df[ "alpha_" + selected_kpi_size].tolist()
    selected_kpi_color_list = df[selected_kpi_color].tolist()



    log_type = True
    #interesting because you see oil and gas ahead of all the rest
    fig = px.scatter(df, 
                    x = selected_kpi_x, 
                    y = selected_kpi_y, 
                    size = selected_kpi_size, 
                    color=selected_kpi_color,
                    hover_name = "industry", log_x = log_type, log_y = log_type, size_max = 60)


    hovertemplate = (

                    'Company' + ': %{customdata[0]}<br>' + 
                    'Ticker' + ': %{customdata[1]}<br>' + 
                    selected_kpi_size + ': %{customdata[2]}<br>' + 
                    selected_kpi_color + ': %{customdata[3]}<br>' + 
                    selected_kpi_x + ': %{customdata[4]}<br>' + 
                    selected_kpi_y + ': %{customdata[5]}<br>' + 
                    '<extra></extra>'
                    )

    customdata = np.stack((shortname_list, ticker_list, selected_kpi_size_list, selected_kpi_color_list, selected_kpi_x_list, selected_kpi_y_list), axis=-1)
    fig.update_traces(customdata=customdata,hovertemplate=hovertemplate)

    st.plotly_chart(fig, use_container_width=True)
    # fig.show() 




    st.write("Related equities under Industry :" + selected_ind)



    # For Retrieving the  ticker list
    ticker_df = pd.read_pickle('data/eq_daily_kpi.pickle')
    # To include shortnames
    ticker_df['merged_name'] = ticker_df.index.astype(str) + " / " + ticker_df['shortName'].astype(str)
    remove_list = ['isEsgPopulated', 'updated_datetime']
    ticker_df = ticker_df.drop(remove_list, axis=1)
    ticker_df = ticker_df[ticker_df['industry'] == selected_ind]
    ticker_df = ticker_df.sort_values(by='marketCapUSD', ascending=False)
    merged_ticker_list = ticker_df['merged_name'].tolist()

    # print (ticker_df.columns.tolist())

    # print (cols)

    #adding both sets of lists together
    size_kpi.extend(cols)
    kpi_list = size_kpi

    selected_ticker_kpi = st.selectbox(
        'Set a default ticker',
        tuple(kpi_list),
        index=1,
    )

    if selected_ticker_kpi == "marketCapUSD":
        selected_ticker_adj = 'alpha_marketCapUSD'
    elif selected_ticker_kpi == "totalRevenueUSD":
        selected_ticker_adj = 'alpha_totalRevenueUSD'
    elif selected_ticker_kpi == "ebitdaUSD":
        selected_ticker_adj = 'alpha_ebitdaUSD'
    else:
        selected_ticker_adj = selected_ticker_kpi

    # test = ticker_df[selected_ticker_kpi]
    ticker_df['merged_w_kpi'] = ticker_df['merged_name'].astype(str) + " - " + ticker_df[selected_ticker_adj].astype(str)


    if selected_ticker_kpi:
        ticker_df = ticker_df.sort_values(by=selected_ticker_kpi, ascending=False)
        merged_ticker_list = ticker_df['merged_w_kpi'].tolist()


    #retrieving the selected industry from sessions
    if 'tick_type' in st.session_state:
        sel_tic = st.session_state['tick_type']

        #try except to fix issues related to industry changes that ticker inside session will not match
        try:
            index_no = merged_ticker_list.index(sel_tic)
            selected_choice = ticker_df[ticker_df[ 'merged_w_kpi'] == sel_tic]['merged_name'].values[0]
            st.info("Default Ticker set to : " + selected_choice)
        except:
            index = 0
    else:
        index_no = 0


    selected_mix = st.radio(
        "List of equities under the same industry: select your default equity for analysis",
        (merged_ticker_list),
        horizontal=True,
        index=index_no,
        on_change = handle_select_ticker,
        key='tic_IndustryExploreRatiosMarketSize',
        )

    #using this to overwrite the handle_select_ticker because the handle function saves a version that is merged_w_kpi and you dont want that
    #because it doesnt translate to other charts when you switch 
    selected_choice = ticker_df[ticker_df[ 'merged_w_kpi'] == selected_mix]['merged_name'].values[0]
    st.session_state['tick_type'] = selected_choice


    st.caption("Last updated :" + str(last_recorded_datetime))








    # st.write("Related equities under Industry :" + selected_ind)



    # # For Retrieving the  ticker list
    # ticker_df = pd.read_pickle('data/eq_daily_kpi.pickle')
    # # To include shortnames
    # ticker_df['merged_name'] = ticker_df.index.astype(str) + " / " + ticker_df['shortName'].astype(str)
    # remove_list = ['isEsgPopulated', 'alpha_marketCapUSD', 'alpha_totalRevenueUSD', 'alpha_ebitdaUSD', 'updated_datetime']
    # ticker_df = ticker_df.drop(remove_list, axis=1)
    # ticker_df = ticker_df[ticker_df['industry'] == selected_ind]
    # ticker_df = ticker_df.sort_values(by='marketCapUSD', ascending=False)
    # merged_ticker_list = ticker_df['merged_name'].tolist()


    # #adding both sets of lists together
    # size_kpi.extend(cols)
    # kpi_list = size_kpi

    # selected_ticker_kpi = st.selectbox(
    #     'Set a default ticker',
    #     tuple(kpi_list),
    #     index=1,
    # )

    # if selected_ticker_kpi:
    #     ticker_df = ticker_df.sort_values(by=selected_ticker_kpi, ascending=False)
    #     merged_ticker_list = ticker_df['merged_name'].tolist()


    # #retrieving the selected industry from sessions
    # if 'tick_type' in st.session_state:
    #     sel_tic = st.session_state['tick_type']

    #     #try except to fix issues related to industry changes that ticker inside session will not match
    #     try:
    #         index_no = merged_ticker_list.index(sel_tic)
    #         st.info("Default Ticker : " + st.session_state.tick_type)
    #     except:
    #         index = 0
    # else:
    #     index_no = 0


    # selected_choice = st.radio(
    #     "List of equities under the same industry: select your default equity for analysis",
    #     (merged_ticker_list),
    #     horizontal=True,
    #     index=index_no,
    #     on_change = handle_select_ticker,
    #     key='tic_IndustryExploreRatiosMarketSize',
    #     )

    # # selected_choice = ticker_df[ 'mix' == selected_mix]['merged_name']

    # st.session_state['tick_type'] = selected_choice
    # print (selected_choice)




























    # if selected_choice == 'Comedy':
    #     st.write('You selected comedy.')
    # else:
    #     st.write("You didn't select comedy.")

    #recording the selected industry from sessions

    # selected_choice = st.selectbox(
    #     'Set a default ticker',
    #     tuple(merged_ticker_list),
    #     index=index_no,
    #     key = "tic_IndustryExploreRatiosMarketSize",
    #     on_change = handle_select_ticker
    # )


    # col1, col2, col3 = st.columns([1,1,1])

    # with col1:
    #     st.button('1')
    # with col2:
    #     st.button('2')
    # with col3:
    #     st.button('3')

    # # buttons is a much more fanciful way of acheive the goal, try column dropdown first - if it works, think about button
    # print (st.session_state)
    # buttons = []
    # for i in merged_ticker_list:
    #     buttons.append(st.button(str(i)))
    # for i, button in enumerate(buttons):
    #     if button:
    #         st.write(f"{i} button was clicked")
    #         test = "bomms"
    #         st.session_state.tick_type='test'




    # for i in eq_list:
    #     i = st.button(
    #                     i,
    #                     key='radiomonkey',
    #                     on_click=equities,
    #     )

    # st.session_state.ind_type=st.session_state.ind_EquityExploreIndustryMarket






    