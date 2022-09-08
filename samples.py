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
    max_rank_dict = {}
    rank_dict = {}
    medianrank = {}
    abs_value_dict = {}
    rank_d_maxrank_dict = {}
    for i in cols:
        dfnew = df[[i]]

        dfnew = dfnew.replace('', np.nan)
        dfnew = dfnew.dropna(subset=[i])
        dfnew[i] = dfnew[i].astype(float)

        value = dfnew[i][[selected_ind]].values[0] 
        abs_value_dict[i] = value

        # if the kpi ratio is negative = good, than reverse the order to rank it - debt/equity
        if kpi_mapping[i] == True:
            dfnew[i] = dfnew[i].rank(ascending=True)
        else:
            dfnew[i] = dfnew[i].rank(ascending=False)

        medianrank[i] = round(dfnew[i].count()/2)
        max_rank_dict[i] = dfnew[i].count()
        rank_dict[i] = (dfnew[i][[selected_ind]].values)[0]
        rank_d_maxrank_dict[i] = str(int(rank_dict[i])) + "/" + str(int(max_rank_dict[i]))


    #normalizing the numbers for insertion into chart

    rank_list = list(rank_dict.values())
    values_list = list(abs_value_dict.values())
    rank_d_maxrank_list = list(rank_d_maxrank_dict.values()) 
    main_list = []
    median_list = []
    for i, value in enumerate(max_rank_dict):

        item = rank_list[i] / max_rank_dict[value]
        item = round(item, 3)
        main_list.append(item)

        item = medianrank[value] / max_rank_dict[value]
        item = round(item, 3)
        median_list.append(item)


    #remove the radius ticker

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

    fig.add_trace(go.Scatterpolar(
        r = median_list,
        theta = cols,
        fill = 'toself',
    ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=False,
        range=[0, 1]
        )),
    showlegend=False
    )

    fig.show()