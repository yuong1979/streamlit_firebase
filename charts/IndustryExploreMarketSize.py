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
colors = px.colors.qualitative.Plotly

# #################################################################################################
# ####### Tree chart ratios of industries ###############################################
# #################################################################################################
# python -c 'from charts.IndustryExploreMarketSize import Industry_Explore_Market_Size; Industry_Explore_Market_Size()'

def Industry_Explore_Market_Size():

    #hardcoded to save time in doing a unique extract from the raw pickle file
    cat_list = ['annual_profit&loss', 'annual_cashflow',  'quarterly_profit&loss', 'quarterly_cashflow', ]

    selected_cat = st.radio("Select Report", cat_list, horizontal=True)

    if selected_cat == 'quarterly_profit&loss':
        df = extract_hist_details_qtr_profitnloss()
        kpi_list = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'Ebit']
    elif selected_cat == 'quarterly_cashflow':
        df = extract_hist_details_qtr_cashflow()
        kpi_list = ['Total Cashflows From Investing Activities', 'Change To Netincome', 'Total Cash From Operating Activities', 'Net Income', 'Change In Cash', 'Total Cash From Financing Activities']
    elif selected_cat == 'annual_profit&loss':
        df = extract_hist_details_ann_profitnloss()
        kpi_list = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'Ebit']
    elif selected_cat == 'annual_cashflow':
        df = extract_hist_details_ann_cashflow()
        kpi_list = ['Total Cashflows From Investing Activities', 'Change To Netincome', 'Total Cash From Operating Activities', 'Net Income', 'Change In Cash', 'Total Cash From Financing Activities']



    #import industry to map to hist details
    df_ind = pd.read_pickle('data/eq_daily_kpi.pickle')
    df_ind = df_ind['industry']

    cols = df_ind.unique().tolist()

    # print (cols)

    # cols.remove(0)
    # cols.remove('')

    default_cols = cols[:4]

    selected_ind = st.multiselect(
        "Select an industry:",
        options = cols,
        default = default_cols
    )


    selected_kpi = st.selectbox(
        'Select a kpi',
        tuple(kpi_list),
    )

    tz_SG = pytz.timezone('Singapore')
    datenow = datetime.now(tz_SG)
    days_ago_annual = 365 * 4
    days_ago_quarterly = 400

    date_xyrs_ago = datenow - timedelta(days = days_ago_annual)
    date_xyrs_ago = date_xyrs_ago.date()
    start_of_year = date(date.today().year, 1, 1)
    #include this to avoid over/under reporting quarterly financials because some financials arrive early
    quarter_start = (datetime.today() - pd.tseries.offsets.QuarterBegin(startingMonth=1)).date()

    date_one_yr_ago = datenow - timedelta(days = days_ago_quarterly)
    date_one_yr_ago = date_one_yr_ago.date()

    # ############################################################################################
    # ## for testing purposes ### Remember to uncoment the portion that sends data below to a csv
    # ############################################################################################
    # df = extract_hist_details_qtr_cashflow()
    # kpi_list = ['Total Cashflows From Investing Activities', 'Change To Netincome', 'Total Cash From Operating Activities', 'Net Income', 'Change In Cash', 'Total Cash From Financing Activities']
    # selected_cat = "quarterly_cashflow"
    # selected_ind = [
    #     'Semiconductors', 'Biotechnology', 'Tobacco', 'Gold', 'Restaurants', 
    #     'Broadcasting', 'Silver',  'Software—Infrastructure', 'Personal Services', 'Steel', 
    #     'Airlines', 'Solar', 'Luxury Goods', 'Aluminum', 'Footwear & Accessories', 
    #     'Lumber & Wood Production', 'Household & Personal Products', 'Apparel Retail', 'Health Information Services',
    # ]
    # selected_kpi = 'Net Income'


    #import industry to map to hist details
    df_ind = pd.read_pickle('data/eq_daily_kpi.pickle')
    df_ind = df_ind['industry']
    df_merged = pd.merge(df, df_ind, how='left', left_on = 'ticker', right_index = True)


    #filtering only for required indicators
    all_df = df_merged[(df_merged['kpi'] == selected_kpi) & (df_merged['cattype'] == selected_cat)]

    by_ind_df = all_df.groupby(['industry', 'adj_last_date', 'cattype', 'kpi'])['values'].sum()
    by_ind_df = by_ind_df.reset_index()

    #getting the proportion by dividing the totals of entire market by sum of specific industries with the same adj_last_date
    by_ind_df['proportion'] = by_ind_df['values'] / by_ind_df.groupby(['adj_last_date'])['values'].transform('sum')
    by_ind_df['reversed_rank'] = by_ind_df.groupby(['adj_last_date'])['values'].transform('rank')
    #reverse the rank to get it to make sense - there is no way to do that in the previous
    by_ind_df['rank_max'] = by_ind_df['reversed_rank'].max().astype(int)
    by_ind_df['rank'] = by_ind_df['rank_max'] - by_ind_df['reversed_rank'].astype(int) + 1
    by_ind_df['rank_frac'] = by_ind_df['rank'].astype(str) + ' / ' + by_ind_df['rank_max'].astype(str)




    by_ind_df = by_ind_df[['industry','adj_last_date','values','proportion','rank','rank_frac']]
    # converting the dates to datetime so it can be filtered
    by_ind_df["adj_last_date"] = pd.to_datetime(by_ind_df["adj_last_date"]).dt.date


    #remove negative numbers if not the proportion does not make sense anymore
    by_ind_df = by_ind_df[(by_ind_df['proportion'] >= 0) 
                            & (by_ind_df['industry'] != 0) 
                            & (by_ind_df['industry'] != "")
                            & (by_ind_df['adj_last_date'] >= date_xyrs_ago)
                            ]


    quarter_cattypes = ['quarterly_balancesheet', 'quarterly_cashflow', 'quarterly_profit&loss']
    annual_cattypes = ['annual_balancesheet', 'annual_cashflow', 'annual_profit&loss']

    #start and end dates and customized to ensure that the numbers are compared like on like to one another
    if selected_cat in annual_cattypes:
        by_ind_df = by_ind_df[(by_ind_df['adj_last_date'] <= start_of_year)]
    elif selected_cat in quarter_cattypes:
        by_ind_df = by_ind_df[(by_ind_df['adj_last_date'] <= quarter_start) & (by_ind_df['adj_last_date'] >= date_one_yr_ago)]


    if selected_cat in annual_cattypes:
        by_ind_df = by_ind_df[(by_ind_df['adj_last_date'] <= start_of_year)]


    by_ind_df = by_ind_df[by_ind_df['industry'].isin(selected_ind)]


    # by_ind_df.to_csv('by_ind_df.csv', index=False)
    # merge_min_max_df.to_csv('merge_min_max_df.csv', index=False)

    # by_ind_df = pd.read_csv('by_ind_df.csv')
    # merge_min_max_df = pd.read_csv('merge_min_max_df.csv')


#############################################
########### Consolidated Charts #############
#############################################


    fig = go.Figure()

    count = 1
    for i in by_ind_df['industry']:

        df = by_ind_df[by_ind_df['industry'] == i ].copy()

        df['required'] = (df['proportion'].apply(lambda x: round(x*100, 2)).astype("string") + '%')
        df['required'] = df['required'].apply(lambda x: 'Proportion: ' + x)

        df['required1'] = df['values'].apply(convert_digits)
        df['required1'] = df['required1'].apply(lambda x: 'Value: ' + str(x))

        df['required2'] = df['rank_frac'].apply(lambda x: 'Rank vs other Industry: ' + str(x))

        df['Consolidated'] = df['required'] + "<br>" + df['required1'] + "<br>" + df['required2']

        dates = df['adj_last_date']
        rank = df['rank']
        #replace the below with consolidated and uncomment the top part to display values and proportion
        consolidate = df['Consolidated']

        dates = df['adj_last_date']
        rank = df['rank']
        view = df['values']
        val_max_extra = by_ind_df['values'].max() * 120/100
        val_min_extra = by_ind_df['values'].min() - (val_max_extra * 20/100)
        viewrange = [val_min_extra, val_max_extra]

        fig.add_trace(go.Scatter(
                            x=dates, 
                            y=view,
                            mode='lines+markers',
                            name=i,
                            hovertext=consolidate,
                            hoverlabel = dict(bordercolor = colors[(count-1)%len(colors)])
                            ))

        fig.add_annotation(
            x=dates.iloc[-1],
            y=view.iloc[-1],
            text='<b>'+i+'<b>',
            showarrow=True,
            ax = 20,
            ay = -20,
            font_color = colors[(count-1)%len(colors)],
            textangle = 360, # adjust text angle here
            font_size = 16 # adjust font size here
        )

        count = count + 1

    rank_min = by_ind_df['rank'].min()
    rank_max = by_ind_df['rank'].max()
    date_min = pd.to_datetime(by_ind_df['adj_last_date'].min())
    date_max = pd.to_datetime(by_ind_df['adj_last_date'].max())

    #with margin
    fig.update_xaxes(range = [date_min-pd.Timedelta(60, 'd'), date_max+pd.Timedelta(60, "d")])
    fig.update_yaxes(range = viewrange,)

    fig.update_layout(height=800, width=600,

                    showlegend=False, 
                    # title_text="Performance of industry " + str(selected_kpi),
                    legend=dict(
                        orientation='h',
                        yanchor="top",
                        y=1.02,
                        xanchor="left",
                        x=0
                        )
                    )
    fig.update_layout(hoverlabel = dict(font=dict(color='black'),bgcolor = 'white'),width = 1200)

    st.plotly_chart(fig, use_container_width=True)




########## grouping the dates to compare growth in the ranking of the company #############
########## Good to have but hard to implement - > focus on other improvements first #######


    # # print (by_ind_df)
    # ind_grp_maxmin = by_ind_df.groupby(['industry'])['adj_last_date'].agg(['max','min'])



    # #attaching the new rank that is dependant on the performance of the indicator at the start vs the end of dates
    # #merge on industry + max to get end rank
    # merge_min_max_df = pd.merge(ind_grp_maxmin, by_ind_df,  how='left', left_on=['industry','max'], right_on = ['industry','adj_last_date'])
    # merge_min_max_df.rename(columns = {'rank':'endrank'}, inplace = True)
    # merge_min_max_df = merge_min_max_df[['industry','max','min','endrank']]

    # #merge on industry + min to get start rank
    # merge_min_max_df = pd.merge(merge_min_max_df, by_ind_df,  how='left', left_on=['industry','min'], right_on = ['industry','adj_last_date'])
    # merge_min_max_df.rename(columns = {'rank':'startrank'}, inplace = True)
    # merge_min_max_df = merge_min_max_df[['industry','max','min','startrank','endrank']]

    # merge_min_max_df['difference'] = merge_min_max_df['startrank'] - merge_min_max_df['endrank']
    # merge_min_max_df['rankgrowth'] = merge_min_max_df['difference'].rank(ascending = False)
    # merge_min_max_df = merge_min_max_df.sort_values(by=['rankgrowth'])





#############################################
########### Multiple Charts #################
#############################################

    # ind_list = merge_min_max_df['industry'].unique().tolist()
    # ind_count = len(by_ind_df['industry'].unique().tolist())

    # nrow = int(ind_count/2) if ind_count%2==0 else int((ind_count/2)+1)
    # fig = make_subplots(rows=nrow, cols=2,
    #         subplot_titles=(ind_list)
    # )

    # count = 1
    # for i in merge_min_max_df['industry']:
    #     df = by_ind_df[by_ind_df['industry'] == i ].copy()

    #     df['required'] = (df['proportion'].apply(lambda x: round(x*100, 2)).astype("string") + '%')
    #     df['required'] = df['required'].apply(lambda x: 'Proportion: ' + x)

    #     df['required1'] = df['values'].apply(convert_digits)
    #     df['required1'] = df['required1'].apply(lambda x: 'Value: ' + str(x))

    #     df['required2'] = df['rank'].apply(lambda x: 'Rank: ' + str(x))

    #     df['Consolidated'] = df['required'] + "<br>" + df['required1'] + "<br>" + df['required2']

    #     dates = df['adj_last_date']
    #     rank = df['rank']
    #     #replace the below with consolidated and uncomment the top part to display values and proportion
    #     consolidate = df['Consolidated']

    #     row,col = list(itertools.product(range(1,int((ind_count/2)+2)),[1,2]))[count-1]

    #     fig.append_trace(go.Scatter(
    #         x=dates,
    #         y=rank,
    #         hovertext=consolidate,
    #     ), row=row, col=col)

    #     count = count + 1

    # rank_min = by_ind_df['rank'].min()
    # rank_max = by_ind_df['rank'].max()
    # date_min = pd.to_datetime(by_ind_df['adj_last_date'].min())
    # date_max = pd.to_datetime(by_ind_df['adj_last_date'].max())

    # #with margin
    # fig.update_xaxes(range = [date_min-pd.Timedelta(60, 'd'), date_max+pd.Timedelta(60, "d")])
    # fig.update_yaxes(
    #     range = [rank_max+10, rank_min-10],
    #     )


    # fig.update_layout(height=800, width=600,

    #                 showlegend=False, 
    #                 title_text="Performance of industry " + str(selected_kpi))

    # st.plotly_chart(fig, use_container_width=True)


















