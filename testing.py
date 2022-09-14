import pandas as pd
import numpy as np
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove

import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go



# #################################################################################################
# ####### Spider chart ratios of individual industries ###############################################
# #################################################################################################
# python -c 'from testing import radar_chart; radar_chart()'


import plotly.express as px


def radar_chart():

    
    df = pd.read_csv('dataframe_csv/industry_data.csv', index_col=1)
    df = df.drop("Unnamed: 0", axis='columns')

    cols = df.columns.values.tolist()

    # #to be replaced with cols on top when finish using
    # cols = ['forwardEps', 'trailingEps', 'forwardPE', 'trailingPE', 'pegRatio', 'trailingPegRatio', 'enterpriseToEbitda', 'enterpriseToRevenue']

    #remove unwanted kpis
    cols = [i for i in cols if i not in kpi_remove]


    cols_profit_growth = ['grossMargins', 'operatingMargins', 'ebitdaMargins', 'profitMargins', 'earningsGrowth', 'revenueGrowth']

    cols_value = ['forwardEps', 'trailingEps', 'forwardPE', 'trailingPE', 'pegRatio', 'trailingPegRatio', 'enterpriseToEbitda', 'enterpriseToRevenue']

    cols_popularity = ['heldPercentInstitutions', 'heldPercentInsiders']

    cols_financialhealth = ['debtToEquity', 'quickRatio', 'currentRatio']

    cols_financialhealth = ['dividendYield', 'dividendRate', 'trailingAnnualDividendRate', 'fiveYearAvgDividendYield', 'trailingAnnualDividendYield']


    ind_list = df.index.values.tolist()

    Default_cols = cols[:len(cols)-10]

    selected_ind = 'Uranium'
    # selected_ind = 'Steel'

    # Steel
    # Steel & Iron
    # Telecom Services
    # Telecom Services - Foreign
    # Textile Manufacturing
    # Thermal Coal
    # Tobacco
    # Tools & Accessories
    # Travel Services
    # Trucking
    # Uranium


    #collecting the median and max values for comparison
    value_abs = {}
    value_max = {}
    value_min = {}
    value_median = {}
    adj_value = {} #adj value for ratios that are negative in nature - debt/equity
    adj_range = {} #adj value for max range to include negative values

    rank_max = {}
    rank_val = {}
    rank_median = {}
    rank_fraction = {}

    rank_df = {}

    for i in cols:
        dfnew = df[[i]]
        value_abs[i] = dfnew[i][[selected_ind]].values[0] 
        value_max[i] = dfnew[i].max()
        value_min[i] = dfnew[i].min()
        value_median[i] = dfnew[i].median()

        # if the kpi ratio is negative = good, than reverse the order to rank it - debt/equity
        if kpi_mapping[i] == True:

            adj_range[i] = value_max[i] - value_min[i]
            adj_value[i] = value_abs[i] - value_min[i]

            rank_df[i] = dfnew[i].rank(ascending=True)

        else:

            adj_range[i] = value_max[i] - value_min[i]
            #to get the value(which is reversed), we need to take the maximum range and minus the difference between min(which is best) and the value
            adj_value[i] = adj_range[i] - (value_abs[i] - value_min[i])

            rank_df[i] = dfnew[i].rank(ascending=False)

        rank_median[i] = round(rank_df[i].count()/2)
        rank_max[i] = rank_df[i].count()
        rank_val[i] = (rank_df[i][[selected_ind]].values)[0]
        try:
            rank_fraction[i] = str(int(rank_val[i])) + "/" + str(int(rank_max[i]))
        except:
            rank_fraction[i] = ""

    #normalizing the numbers for insertion into chart
    rank_list = list(rank_val.values())
    values_list = list(value_abs.values())
    rank_d_maxrank_list = list(rank_fraction.values()) 
    main_list = []
    median_list = []
    for i, value in enumerate(rank_max):

        item = rank_list[i] / rank_max[value]
        item = round(item, 3)
        main_list.append(item)

        item = rank_median[value] / rank_max[value]
        item = round(item, 3)
        median_list.append(item)

    print (cols)
    print (main_list)
    print (value_abs)
    print (rank_val)
    print (rank_fraction)
    print (value_median)






    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r = main_list,
        theta = cols,
        fill = 'toself',
        fillcolor = 'green',
        line_shape = 'spline', #linear #spline
        text = values_list, 
        opacity=0.6,
        mode = 'markers+text', 
        textfont_color='red', 
        marker_color='green',
    ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=False,
        range=[0, 1]
        )),
    autosize=False,
    height=800,
    showlegend=False
    )
    
    hovertemplate = ('Ranking: %{customdata[0]}<br>' + 'Value: %{customdata[1]}<br><extra></extra>') #AT
    customdata = np.stack((rank_d_maxrank_list, values_list), axis=-1) #AT
    fig.update_traces(customdata=customdata,hovertemplate=hovertemplate) #AT


    # # st.plotly_chart(fig, use_container_width=True)

    fig.show()