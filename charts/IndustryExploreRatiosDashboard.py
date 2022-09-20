import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_csv, extract_industry_pickle, convert_digits
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np

# #################################################################################################
# ####### Spider chart ratios of individual industries ###############################################
# #################################################################################################
# python -c 'from IndustryDashboard import Industry_Dashboard; Industry_Dashboard()'


def handle_select():
    st.session_state.ind_type=st.session_state.ind_IndustryExploreRatiosDashboard



def Industry_Explore_Ratios_Dashboard():

    # df = pd.read_pickle('data/eq_daily_industry.pickle')
    df = extract_industry_pickle()

    last_recorded_datetime = df['daily_agg_record_time'].min().strftime("%b %d %Y %H:%M:%S")

    cols = df.columns.values.tolist()
    cols.remove("industry")

    # df = convert_emptystr2na(df,cols)

    # #to be replaced with cols on top when finish using
    # cols = ['forwardEps', 'trailingEps', 'forwardPE', 'trailingPE', 'pegRatio', 'trailingPegRatio', 'enterpriseToEbitda', 'enterpriseToRevenue']

    df.set_index('industry', inplace=True)

    #remove unwanted kpis
    cols = [i for i in cols if i not in kpi_remove]

    ind_list = df.index.values.tolist()

    # ind_type = "Uranium"

    #retrieving the selected industry from sessions
    if 'ind_type' in st.session_state:
        sel_ind = st.session_state['ind_type']
        index_no = ind_list.index(sel_ind)
    else:
        index_no = 0

    col1, col2 = st.columns(2)

    with col1:
        selected_ind = st.selectbox(
            'Select an industry',
            tuple(ind_list),
            index = index_no,
            key = "ind_IndustryExploreRatiosDashboard",
            on_change = handle_select
        )
    with col2:
        st.write('')

    # #recording the selected industry from sessions
    # if 'ind_type' not in st.session_state:
    #     st.session_state['ind_type'] = selected_ind


    company_count = df.loc[selected_ind, 'company_count']
    market_cap = df.loc[selected_ind, 'marketCapUSD']
    total_revenue = df.loc[selected_ind, 'totalRevenueUSD']

    market_cap = convert_digits(market_cap)
    total_revenue = convert_digits(total_revenue)

    selected_kpi = cols

    #collecting the median and max values for comparison
    value_abs = {}
    value_max = {}
    value_min = {}
    value_median = {}
    adj_value = {} #adj value for ratios that are negative in nature - debt/equity
    adj_range = {} #adj value for max range to include negative values

    delta_to_median = {}
    delta_to_median_sign = {}

    rank_max = {}
    rank_val = {}
    rank_median = {}
    rank_fraction = {}

    rank_df = {}

    for i in selected_kpi:
        dfnew = df[[i]]
        value_abs[i] = dfnew[i][[selected_ind]].values[0] 
        value_max[i] = dfnew[i].max()
        value_min[i] = dfnew[i].min()
        value_median[i] = round(dfnew[i].median(),3)

        # if the kpi ratio is negative = good, than reverse the order to rank it - debt/equity
        if kpi_mapping[i] == True:

            adj_range[i] = value_max[i] - value_min[i]
            adj_value[i] = value_abs[i] - value_min[i]
            rank_df[i] = dfnew[i].rank(ascending=False)
            delta_to_median[i] = round((value_abs[i] - value_median[i]), 3)
            
        else:

            adj_range[i] = value_max[i] - value_min[i]
            #to get the value(which is reversed), we need to take the maximum range and minus the difference between min(which is best) and the value
            adj_value[i] = adj_range[i] - (value_abs[i] - value_min[i])
            rank_df[i] = dfnew[i].rank(ascending=True)
            delta_to_median[i] = round((value_median[i] - value_abs[i]), 3)

        delta_to_median_sign[i] = "normal"
        rank_median[i] = round(rank_df[i].count()/2)
        rank_max[i] = rank_df[i].count()
        rank_val[i] = (rank_df[i][[selected_ind]].values)[0]

        try:
            rank_fraction[i] = str(int(rank_val[i])) + "/" + str(int(rank_max[i]))
        except:
            rank_fraction[i] = 0


    #normalizing the numbers for insertion into chart
    rank_list = list(rank_val.values())
    values_list = list(value_abs.values())
    rank_fraction_list = list(rank_fraction.values()) 
    main_list = []
    median_rank_list = []
    for i, value in enumerate(rank_max):
        #ranking ranks 0 to 1 so those with lower ranks should have higher scores therefore 1 -rank/maxrank is neccessary
        item = 1 - (rank_list[i] / rank_max[value])
        item = round(item, 3)
        main_list.append(item)

        item = 1 - (rank_median[value] / rank_max[value])
        item = round(item, 3)
        median_rank_list.append(item)

    # print (value_abs, 'value_abs')
    # print (value_max, 'value_max')
    # print (value_min, 'value_min')
    # print (value_median, 'value_median')
    # print (rank_max, 'rank_max')
    # print (rank_val, 'rank_val')
    # print (rank_median, 'rank_median')
    # print (rank_fraction, 'rank_fraction')

    with open('style/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Number of companies : " + str(company_count))

        with col2:
            st.subheader("Market Cap : " + str(market_cap))

        with col3:
            st.subheader("Total Revenue : " + str(total_revenue))



        with st.container():
            st.write("Profitability Indicators")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric = "grossMargins"
                col1.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col2:
                metric = "operatingMargins"
                col2.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col3:
                metric = "ebitdaMargins"
                col3.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col4:
                metric = "profitMargins"
                col4.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))

        st.markdown('---')
        with st.container():
            st.write("Growth & Dividends Indicators")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric = "earningsGrowth"
                col1.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col2:
                metric = "revenueGrowth"
                col2.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))

            with col3:
                metric = "dividendYield"
                col3.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col4:
                metric = "dividendRate"
                col4.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))





        st.markdown('---')
        with st.container():
            st.write("Value Indicators")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric = "forwardEps"
                col1.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col2:
                metric = "trailingEps"
                col2.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col3:
                metric = "forwardPE"
                col3.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col4:
                metric = "trailingPE"
                col4.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))

            st.write('\n')
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric = "enterpriseToEbitda"
                col1.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col2:
                metric = "enterpriseToRevenue"
                col2.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col3:
                metric = "returnOnEquity"
                col3.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))
            with col4:
                metric = "returnOnAssets"
                col4.metric(label = metric, value = value_abs[metric], 
                    delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                st.caption('Industry Median: ' + str(value_median[metric]))


            st.markdown('---')
            with st.container():
                st.write("Financial Health Indicators")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    metric = "debtToEquity"
                    col1.metric(label = metric, value = value_abs[metric], 
                        delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                    st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                    st.caption('Industry Median: ' + str(value_median[metric]))
                with col2:
                    metric = "quickRatio"
                    col2.metric(label = metric, value = value_abs[metric], 
                        delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                    st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                    st.caption('Industry Median: ' + str(value_median[metric]))
                with col3:
                    metric = "currentRatio"
                    col3.metric(label = metric, value = value_abs[metric], 
                        delta = delta_to_median[metric], delta_color = delta_to_median_sign[metric])
                    st.caption('Industry Rank: ' + str(rank_fraction[metric]))
                    st.caption('Industry Median: ' + str(value_median[metric]))


        st.caption("Last updated :" + str(last_recorded_datetime))




        # with st.container():
        #     st.subheader("Financial Indicators")
        #     col1, col2, col3, col4, col5 = st.columns(5)
        #     col1.metric("Temperature", "70 °F", "1.2 °F")
        #     col2.metric("Wind", "9 mph", "-8%")
        #     col3.metric("Humidity", "86%", "4%")
        #     col4.metric(label="Active developers", value=123, delta=123, delta_color="off")
        #     col5.metric(label="Gas price", value=4, delta=-0.5, delta_color="inverse")


        # with st.container():
        #     st.subheader("Profitability Indicators")
        #     col1, col2, col3, col4, col5 = st.columns(5)
        #     col1.metric("Temperature", "70 °F", "1.2 °F")
        #     col2.metric("Wind", "9 mph", "-8%")
        #     col3.metric("Humidity", "86%", "4%")
        #     col4.metric(label="Active developers", value=123, delta=123, delta_color="off")
        #     col5.metric(label="Gas price", value=4, delta=-0.5, delta_color="inverse")

        # with st.container():
        #     st.subheader("Popularity Indicators")
        #     col1, col2, col3, col4, col5 = st.columns(5)
        #     col1.metric("Temperature", "70 °F", "1.2 °F")
        #     col2.metric("Wind", "9 mph", "-8%")
        #     col3.metric("Humidity", "86%", "4%")
        #     col4.metric(label="Active developers", value=123, delta=123, delta_color="off")
        #     col5.metric(label="Gas price", value=4, delta=-0.5, delta_color="inverse")

        # with st.container():
        #     st.subheader("Growth Indicators")
        #     col1, col2, col3, col4, col5 = st.columns(5)
        #     col1.metric("Temperature", "70 °F", "1.2 °F")
        #     col2.metric("Wind", "9 mph", "-8%")
        #     col3.metric("Humidity", "86%", "4%")
        #     col4.metric(label="Active developers", value=123, delta=123, delta_color="off")
        #     col5.metric(label="Gas price", value=4, delta=-0.5, delta_color="inverse")

        # with st.container():
        #     st.subheader("Value Indicators")
        #     col1, col2, col3, col4, col5 = st.columns(5)
        #     col1.metric("Temperature", "70 °F", "1.2 °F")
        #     col2.metric("Wind", "9 mph", "-8%")
        #     col3.metric("Humidity", "86%", "4%")
        #     col4.metric(label="Active developers", value=123, delta=123, delta_color="off")
        #     col5.metric(label="Gas price", value=4, delta=-0.5, delta_color="inverse")







        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r = main_list,
            theta = cols,
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

        fig.add_trace(go.Scatterpolar(
            r = median_rank_list,
            theta = cols,
            # fill = 'toself',
        ))

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
        
        hovertemplate = ('Ratio: %{customdata[0]}<br>' + 'Ranking: %{customdata[1]}<br>' + 'Value: %{customdata[2]}<br><extra></extra>') #AT
        customdata = np.stack((cols, rank_fraction_list, values_list), axis=-1) #AT
        fig.update_traces(customdata=customdata,hovertemplate=hovertemplate) #AT


        # st.plotly_chart(fig, use_container_width=True)


        # fig.show()


    # with st.container():
    #     st.write("This is inside the container")

    #     # You can call any Streamlit command, including custom components:
    #     st.bar_chart(np.random.randn(50, 3))

    # st.write("This is outside the container")