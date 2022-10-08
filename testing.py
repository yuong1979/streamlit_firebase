import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_industry_pickle#, convert_digits
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np
import datetime
from datetime import date
from tools import (
    extract_industry_pickle,
    extract_hist_details_ann_balancesheet, extract_hist_details_ann_cashflow, extract_hist_details_ann_profitnloss,
    extract_hist_details_qtr_balancesheet, extract_hist_details_qtr_cashflow, extract_hist_details_qtr_profitnloss,
    convert_digits
)
import pytz
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import itertools



by_ind_df = pd.read_csv('by_ind_df.csv')
merge_min_max_df = pd.read_csv('merge_min_max_df.csv')


fig = go.Figure()

count = 1
for i in merge_min_max_df['industry']:

    df = by_ind_df[by_ind_df['industry'] == i ].copy()

    df['required'] = (df['proportion'].apply(lambda x: round(x*100, 2)).astype("string") + '%')
    df['required'] = df['required'].apply(lambda x: 'Proportion: ' + x)

    df['required1'] = df['values'].apply(convert_digits)
    df['required1'] = df['required1'].apply(lambda x: 'Value: ' + str(x))

    df['required2'] = df['rank'].apply(lambda x: 'Rank: ' + str(x))

    df['Consolidated'] = df['required'] + "<br>" + df['required1'] + "<br>" + df['required2']

    dates = df['adj_last_date']
    rank = df['rank']
    #replace the below with consolidated and uncomment the top part to display values and proportion
    consolidate = df['Consolidated']

    dates = df['adj_last_date']
    rank = df['rank']

    fig.add_trace(go.Scatter(
                        x=dates, 
                        y=rank,
                        mode='lines+markers',
                        name=i,
                        hovertext=consolidate,
                        ))

    count = count + 1

rank_min = by_ind_df['rank'].min()
rank_max = by_ind_df['rank'].max()
date_min = pd.to_datetime(by_ind_df['adj_last_date'].min())
date_max = pd.to_datetime(by_ind_df['adj_last_date'].max())

#with margin
fig.update_xaxes(range = [date_min-pd.Timedelta(60, 'd'), date_max+pd.Timedelta(60, "d")])
fig.update_yaxes(
    range = [rank_max+10, rank_min-10],
    )

fig.update_layout(height=800, width=600,


                title_text="Performance of industry ",
                showlegend=False, 
                # legend=dict(
                #     orientation='h',
                #     yanchor="top",
                #     y=1.02,
                #     xanchor="left",
                #     x=0
                #     )
                )

fig.show()
