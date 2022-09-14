from unittest import skip
import pandas as pd
import numpy as np
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove

import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go


# #################################################################################################
# ####### Ratios by industries ####################################################################
# #################################################################################################
# python -c 'from samplestest import test; test()'

def test():

    # ratios_by_industry()
    df = pd.read_csv('dataframe_csv/industry_data.csv', index_col=1)
    df = df.drop("Unnamed: 0", axis='columns')
    cols = df.columns.values.tolist()
    #remove unwanted kpis
    cols = [i for i in cols if i not in kpi_remove]

    ind_list = df.index.values.tolist()

    selected_ind = 'Steel'
    # selected_kpi = ['debtToEquity']
    selected_kpi = ['debtToEquity','returnOnEquity']
    # selected_kpi = ['returnOnEquity']

    color_discrete_map = {}
    for i in ind_list:
        color_discrete_map[i] = "grey"
    
    color_discrete_map[selected_ind] = "red"

    color_discrete_map_1 = {}
    for i in ind_list:
        color_discrete_map_1[i] = "white"
    

    for kpi in selected_kpi:
        # selected_kpi_list = [kpi]
        #to determine if the ratio is postive or negative
        if kpi_mapping[kpi] == True:
            df_grouped = df.sort_values(by=[kpi], ascending=False )
        else:
            df_grouped = df.sort_values(by=[kpi], ascending=True )

        df_grouped = df_grouped[kpi]
        df_grouped = df_grouped.reset_index()
        df_transposed = df_grouped.transpose()
        df_list = df_transposed.values.tolist()

        # print (df_list[0])

        max_number = max(df_list[1])
        min_number = min(df_list[1])

        inverted_df = []
        for i in df_list[1]:
            if i < 0:
                x = max_number
            else:
                x = max_number - i
            inverted_df.append(x)

        inverted_df_plus = []
        for i in df_list[1]:
            if min_number > 0:
                x = 0
            else:
                if i > 0:
                    x = min_number
                else:
                    x = min_number - i

            inverted_df_plus.append(x)


        fig = px.bar(
            df_grouped,
            x = 'industry',
            y = kpi,
            color = 'industry', 
            color_discrete_map = color_discrete_map,
            title=f'<b>{kpi}</b>',
            template='plotly_white',
            orientation="v",
        )

        fig.add_bar(
                    x = df_list[0], 
                    y = inverted_df,
                    marker_color='white',
                    hoverinfo = 'skip',
                    )

        fig.add_bar(
                    x = df_list[0], 
                    y = inverted_df_plus,
                    marker_color='white',
                    # hovertext="",
                    hoverinfo = 'skip',

                    )

        fig.update_layout(
            barmode="relative",
            showlegend=False,
        )

        hovertemplate = ('Industry: %{customdata[0]}<br>' + 'Value: %{customdata[1]}<br><extra></extra>')
        customdata = np.stack((df_list[0], df_list[1]), axis=-1)
        fig.update_traces(
            customdata=customdata,
            hovertemplate=hovertemplate,

            )

        fig.show()

