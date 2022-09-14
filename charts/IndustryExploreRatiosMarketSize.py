import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_csv
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np



trillion = 1000000000000
billion = 1000000000
million = 1000000
thousand = 1000

def convert_digits(num):
    if num >= trillion:
        number = str(round(float(num / trillion),2)) + 'T'        
    elif num >= billion:
        number = str(round(float(num / billion),2)) + 'B'
    elif num >= million:
        number = str(round(float(num / million),2)) + 'M'
    elif num >= thousand:
        number = str(round(float(num / thousand),2)) + 'K'
    else:
        number = num
    return number

def convert_negative(num):
    if num < 0:
        number = 0
    else:
        number = num
    return number

@st.cache()
def clean_dataframe(df, size_kpi):
    for i in size_kpi:
        df[i].fillna(0, inplace=True)
        df[i] = df[i].apply(convert_negative)
        name = str(i) + "_short"
        df[name] = df[i]
        #create two columns with shortened numbers for easy viewing of large numbers
        df[name] = df[name].apply(convert_digits)
    return df



# #################################################################################################
# ####### Tree chart ratios of industries ###############################################
# #################################################################################################
# python -c 'from test import ratios_by_industry_bubblechart; ratios_by_industry_bubblechart()'

def Industry_Explore_Ratios_Market_Size():

    df = extract_csv('dataframe_csv/industry_data.csv')

    last_recorded_datetime = df['daily_agg_record_time'].min().split('.')[0]

    allcols = df.columns.values.tolist()
    #remove unwanted kpis
    cols = [i for i in allcols if i not in kpi_remove]

    df = df.reset_index()

    test = ['company_count', 'ebitdaUSD', 'marketCapUSD', 'totalRevenueUSD', 'fullTimeEmployees']

    size_kpi = ['ebitdaUSD', 'marketCapUSD', 'totalRevenueUSD']

    tuple_kpi_select = tuple(cols)
    tuple_size_kpi_select = tuple(size_kpi)

    #remove negative profits and include new columns with shortened names for numbers
    df = clean_dataframe(df, size_kpi)

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
