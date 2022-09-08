import pandas as pd
import numpy as np
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove

import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go



# #################################################################################################
# ####### Spider chart ratios of individual industries ###############################################
# #################################################################################################
# python -c 'from samples import radar_chart; radar_chart()'

def radar_chart():

    df = pd.read_csv('dataframe_csv/industry_data.csv', index_col=1)
    df = df.drop("Unnamed: 0", axis='columns')

    # cols = df.columns.values.tolist()

    #to be replaced with cols on top when finish using
    cols = ['forwardEps', 'trailingEps', 'forwardPE', 'trailingPE', 'pegRatio', 'trailingPegRatio', 'enterpriseToEbitda', 'enterpriseToRevenue']

    #remove unwanted kpis
    cols = [i for i in cols if i not in kpi_remove]

    selected_ind = 'Credit Services'

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

        dfnew = dfnew.replace('', np.nan)
        dfnew = dfnew.dropna(subset=[i])
        dfnew[i] = dfnew[i].astype(float)

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
        rank_fraction[i] = str(int(rank_val[i])) + "/" + str(int(rank_max[i]))

        # print (' ')
        # print (i)
        # print ("value_abs", value_abs[i])

        # print ("value_max - nr", value_max[i])
        # print ("value_min - nr", value_min[i])
        # print ("value_median" , value_median[i])
        # print ("adj_value" , adj_value[i])
        # print ("adj_range" , adj_range[i])

        # print ('-')

        # print ("rank_val" , rank_val[i])
        # print ("rank_median" , rank_median[i])
        # print ("rank_fraction" , rank_fraction[i])
        # print ("rank_max" , rank_max[i])

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



    ### Add both values_list and rank_d_maxrank_list to hover text below
    ### Add both values_list as a label to the chart also
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r = main_list,
        theta = cols,
        fill = 'toself',
        # showlegend=True,
        fillcolor = 'green',
        line_shape = 'spline', #linear
        text = main_list,
        opacity=0.6,
        mode = 'markers', 
        hovertext = rank_d_maxrank_list, 
        hoverinfo = 'name', 
    ))

    # fig.add_trace(go.Scatterpolar(
    #     r = median_list,
    #     theta = cols,
    #     fill = 'toself',
    # ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=False,
        range=[0, 1]
        )),
    showlegend=False
    )

    fig.show()