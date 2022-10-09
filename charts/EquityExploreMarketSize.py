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
# python -c 'from charts.EquityExploreMarketSize import Equity_Explore_Market_Size; Equity_Explore_Market_Size()'

def Equity_Explore_Market_Size():

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


    # # To include shortnames
    # ticker_df['merged_name'] = ticker_df.index.astype(str) + " / " + ticker_df['shortName'].astype(str)

    # #Selecting the ticker so it starts from the biggest in market cap down to the lowest, also selected all neccessary columns only so speed is increased
    # ticker_df = ticker_df.filter(['marketCapUSD', 'merged_name', 'industry'])
    # #replace with none all those data that are empty
    # ticker_df['marketCapUSD'] = ticker_df['marketCapUSD'].apply(lambda x: None if x == "" else x)
    # ticker_df = ticker_df.sort_values(by='marketCapUSD', ascending=False)
    # merged_ticker_list = ticker_df['merged_name'].tolist()


    #import industry to map to hist details
    df_daily_kpi = pd.read_pickle('data/eq_daily_kpi.pickle')

    # print (df_daily_kpi.columns.tolist())


    ind_list = df_daily_kpi['industry'].unique().tolist()

    selected_ind = st.selectbox(
        'Select an industry',
        tuple(ind_list),
    )


    ticker_df = df_daily_kpi.sort_values(by='marketCapUSD', ascending=False)
    ticker_df['merged_name'] = ticker_df.index.astype(str) + " / " + ticker_df['shortName'].astype(str)

    # print (ticker_df)

    ticker_list = ticker_df[ticker_df['industry'] == selected_ind]['merged_name'].tolist()
    default_ticker_list = ticker_list[:6]


    selected_tics = st.multiselect(
        "Select an equity:",
        options = ticker_list,
        default = default_ticker_list
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


    # ## for testing purposes ###
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


    # #import industry to map to hist details
    # df_ind = pd.read_pickle('data/eq_daily_kpi.pickle')
    # ticker_df = ticker_df['industry','merged_name']


    df_merged = pd.merge(df, ticker_df, how='left', left_on = 'ticker', right_index = True)

    #select the neccessary indicators
    all_df = df_merged[(df_merged['kpi'] == selected_kpi) & (df_merged['cattype'] == selected_cat) & (df_merged['industry'] == selected_ind)]
    ticker_df = all_df.groupby(['ticker','merged_name', 'adj_last_date', 'cattype', 'kpi'])['values'].sum()
    ticker_df = ticker_df.reset_index()


    #getting the proportion by dividing the totals of entire market by sum of specific industries with the same adj_last_date
    ticker_df['proportion'] = ticker_df['values'] / ticker_df.groupby(['adj_last_date'])['values'].transform('sum')
    ticker_df['reversed_rank'] = ticker_df.groupby(['adj_last_date'])['values'].transform('rank')
    #reverse the rank to get it to make sense - there is no way to do that in the previous
    ticker_df['rank_max'] = ticker_df['reversed_rank'].max().astype(int)
    ticker_df['rank'] = ticker_df['rank_max'] - ticker_df['reversed_rank'].astype(int) + 1
    ticker_df['rank_frac'] = ticker_df['rank'].astype(str) + ' / ' + ticker_df['rank_max'].astype(str)


    ticker_df.to_csv('ticker_df.csv', index=False)
    ticker_df = pd.read_csv('ticker_df.csv')


    #select the ticker only after the kpi has been ranked
    ticker_df = ticker_df[(ticker_df['merged_name'].isin(selected_tics))]


    ticker_df = ticker_df[['ticker','merged_name','adj_last_date','values','proportion','rank','rank_frac']]
    # converting the dates to datetime so it can be filtered
    ticker_df["adj_last_date"] = pd.to_datetime(ticker_df["adj_last_date"]).dt.date


    #remove negative numbers if not the proportion does not make sense anymore
    ticker_df = ticker_df[(ticker_df['proportion'] >= 0) 
                            & (ticker_df['ticker'] != 0) 
                            & (ticker_df['ticker'] != "")
                            & (ticker_df['adj_last_date'] >= date_xyrs_ago)
                            ]



    quarter_cattypes = ['quarterly_balancesheet', 'quarterly_cashflow', 'quarterly_profit&loss']
    annual_cattypes = ['annual_balancesheet', 'annual_cashflow', 'annual_profit&loss']

    #start and end dates and customized to ensure that the numbers are compared like on like to one another
    if selected_cat in annual_cattypes:
        ticker_df = ticker_df[(ticker_df['adj_last_date'] <= start_of_year)]
    elif selected_cat in quarter_cattypes:
        ticker_df = ticker_df[(ticker_df['adj_last_date'] <= quarter_start) & (ticker_df['adj_last_date'] >= date_one_yr_ago)]



    if selected_cat in annual_cattypes:
        ticker_df = ticker_df[(ticker_df['adj_last_date'] <= start_of_year)]





    fig = go.Figure()

    count = 1
    for i in ticker_df['ticker']:
        df = ticker_df[ticker_df['ticker'] == i ].copy()
        merged_name = df['merged_name'].values[0]

        df['required'] = (df['proportion'].apply(lambda x: round(x*100, 2)).astype("string") + '%')
        df['required'] = df['required'].apply(lambda x: 'Proportion: ' + x)

        df['required1'] = df['values'].apply(convert_digits)
        df['required1'] = df['required1'].apply(lambda x: 'Value: ' + str(x))

        df['required2'] = df['rank_frac'].apply(lambda x: 'Rank vs Competitors: ' + str(x))

        df['Consolidated'] = df['required'] + "<br>" + df['required1'] + "<br>" + df['required2']

        dates = df['adj_last_date']
        #replace the below with consolidated and uncomment the top part to display values and proportion
        consolidate = df['Consolidated']

        view = df['values']
        val_max_extra = ticker_df['values'].max() * 120/100
        val_min_extra = ticker_df['values'].min() - (val_max_extra * 20/100)
        viewrange = [val_min_extra, val_max_extra]
        dates = df['adj_last_date']
        

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
            text='<b>'+merged_name+'<b>',
            showarrow=True,
            ax = 20,
            ay = -20,
            font_color = colors[(count-1)%len(colors)],
            textangle = 360, # adjust text angle here
            font_size = 16 # adjust font size here
        )

        count = count + 1



    date_min = pd.to_datetime(ticker_df['adj_last_date'].min())
    date_max = pd.to_datetime(ticker_df['adj_last_date'].max())

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

    # # getting the earliest and latest date
    # ind_grp_maxmin = ticker_df.groupby(['ticker','merged_name'])['adj_last_date'].agg(['max','min'])


    # #attaching the new rank that is dependant on the performance of the indicator at the start vs the end of dates
    # #merge on ticker + max to get end rank
    # merge_min_max_df = pd.merge(ind_grp_maxmin, ticker_df,  how='left', left_on=['ticker','max'], right_on = ['ticker','adj_last_date'])
    # merge_min_max_df.rename(columns = {'rank':'endrank'}, inplace = True)
    # merge_min_max_df = merge_min_max_df[['ticker','max','min','endrank']]

    # #merge on ticker + min to get start rank
    # merge_min_max_df = pd.merge(merge_min_max_df, ticker_df,  how='left', left_on=['ticker','min'], right_on = ['ticker','adj_last_date'])
    # merge_min_max_df.rename(columns = {'rank':'startrank'}, inplace = True)
    # merge_min_max_df = merge_min_max_df[['ticker','merged_name','max','min','startrank','endrank']]


    # merge_min_max_df['difference'] = merge_min_max_df['startrank'] - merge_min_max_df['endrank']
    # merge_min_max_df['rankgrowth'] = merge_min_max_df['difference'].rank(ascending = False)
    # merge_min_max_df = merge_min_max_df.sort_values(by=['rankgrowth'])

    # merge_min_max_df = ticker_df


    # ticker_df.to_csv('test1.csv', index=False)
    # merge_min_max_df.to_csv('test.csv', index=False)

















    # tic_list = merge_min_max_df['merged_name'].unique().tolist()
    # ind_count = len(ticker_df['ticker'].unique().tolist())


    # nrow = int(ind_count/2) if ind_count%2==0 else int((ind_count/2)+1)
    # fig = make_subplots(rows=nrow, cols=2,
    #         subplot_titles=(tic_list)
    # )

    # count = 1
    # for i in merge_min_max_df['ticker']:
    #     df = ticker_df[ticker_df['ticker'] == i ].copy()

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

    # rank_min = ticker_df['rank'].min()
    # rank_max = ticker_df['rank'].max()
    # date_min = pd.to_datetime(ticker_df['adj_last_date'].min())
    # date_max = pd.to_datetime(ticker_df['adj_last_date'].max())

    # #with margin
    # fig.update_xaxes(range = [date_min-pd.Timedelta(60, 'd'), date_max+pd.Timedelta(60, "d")])
    # fig.update_yaxes(
    #     range = [rank_max+10, rank_min-10],
    #     )


    # fig.update_layout(height=800, width=600,

    #                 showlegend=False, 
    #                 title_text="Performance of Equities " + str(selected_kpi))

    # st.plotly_chart(fig, use_container_width=True)
























