import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_industry_pickle#, convert_digits
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np
import datetime




# @st.experimental_memo
# def alter_size_df(df, size_kpi):
#     for i in size_kpi:
#         #fillna works here because we are only cleaning usd amounts, it should not be used for % KPIs
#         df[i].fillna(0, inplace=True)
#         #convert number to zero if it is an empty string or less than zero because zero below zero does not make sense for size
#         df[i] = df[i].apply(lambda x: 0 if (isinstance(x, str) or x < 0) else x)
#         name = str(i) + "_short"
#         df[name] = df[i]
#         #create two columns with shortened numbers for easy viewing of large numbers
#         df[name] = df[name].apply(convert_digits)
#     return df



# #################################################################################################
# ####### Tree chart ratios of industries ###############################################
# #################################################################################################
# python -c 'from test import ratios_by_industry_bubblechart; ratios_by_industry_bubblechart()'

def Industry_Explore_Ratios_Market_Size():

    # df = pd.read_pickle('data/eq_daily_industry.pickle')
    df = extract_industry_pickle()

    # print (df.dtypes)

    last_recorded_datetime = df['daily_agg_record_time'].min().strftime("%b %d %Y %H:%M:%S")

    allcols = df.columns.values.tolist()
    #remove unwanted kpis
    cols = [i for i in allcols if i not in kpi_remove]
    cols.remove("industry")

    # df = convert_emptystr2na(df,cols)

    test = ['company_count', 'ebitdaUSD', 'marketCapUSD', 'totalRevenueUSD', 'fullTimeEmployees']

    size_kpi = ['ebitdaUSD', 'marketCapUSD', 'totalRevenueUSD']

    tuple_kpi_select = tuple(cols)
    tuple_size_kpi_select = tuple(size_kpi)

    # #remove negative profits and include new columns with shortened names for numbers
    # df = alter_size_df(df, size_kpi)


    # #remove negative profits and include new columns with shortened names for numbers
    trillion = 1000_000_000_000
    billion = 1000_000_000
    million = 1000_000
    thousand = 1000

    for i in size_kpi:
        #fillna works here because we are only cleaning usd amounts, it should not be used for % KPIs
        df[i].fillna(0, inplace=True)
        #convert number to zero if it is an empty string or less than zero because zero below zero does not make sense for size
        df[i] = df[i].apply(lambda x: 0 if (isinstance(x, str) or x < 0) else x)
        name = str(i) + "_short"
        df.loc[df[i] >= thousand, name] = df[i].astype(float).divide(thousand).round(2).astype(str) + "K"
        df.loc[df[i] >= million, name] = df[i].astype(float).divide(million).round(2).astype(str) + "M"
        df.loc[df[i] >= billion, name] = df[i].astype(float).divide(billion).round(2).astype(str) + "B"
        df.loc[df[i] >= trillion, name] = df[i].astype(float).divide(trillion).round(2).astype(str) + "T"



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

    industry_list = df['industry'].tolist()
    selected_kpi_x_list = df[selected_kpi_x].tolist()
    selected_kpi_y_list = df[selected_kpi_y].tolist()
    selected_kpi_size_list = df[selected_kpi_size + "_short"].tolist()
    selected_kpi_color_list = df[selected_kpi_color].tolist()



    log_type = True
    #interesting because you see oil and gas ahead of all the rest
    fig = px.scatter(df, x = selected_kpi_x, y = selected_kpi_y, size = selected_kpi_size, 
                    color=selected_kpi_color,
                    hover_name = "industry", log_x = log_type, log_y = log_type, size_max = 60)


    hovertemplate = (

                    'Industry' + ': %{customdata[0]}<br>' + 
                    selected_kpi_size + ': %{customdata[1]}<br>' + 
                    selected_kpi_color + ': %{customdata[2]}<br>' + 
                    selected_kpi_x + ': %{customdata[3]}<br>' + 
                    selected_kpi_y + ': %{customdata[4]}<br>' + 
                    '<extra></extra>'
                    )

    customdata = np.stack((industry_list, selected_kpi_size_list, selected_kpi_color_list, selected_kpi_x_list, selected_kpi_y_list), axis=-1)
    fig.update_traces(customdata=customdata,hovertemplate=hovertemplate)

    st.plotly_chart(fig, use_container_width=True)
    # fig.show()

    st.caption("Last updated :" + str(last_recorded_datetime))
