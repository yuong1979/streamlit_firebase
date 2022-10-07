
import pandas as pd
from dateutil import parser
import streamlit as st
import threading
from tools import update_data



# #######################################################################################################
# ############### convert digits to alphabets for large numbers ########################################
# #######################################################################################################
# python -c 'from admin_dashboard import task; task()'


def task():
    print ('start task')
    threading.Thread(target=update_data).start()

def refresh():
    st.experimental_rerun()

def data_stats():
        try:
            eq_daily_agg = pd.read_pickle('data/eq_daily_agg.pickle')
            st.write("eq_daily_agg " + "loaded")
        except:
            st.write("eq_daily_agg " + "NOT loaded")
        try:
            eq_daily_industry = pd.read_pickle('data/eq_daily_industry.pickle')
            recordtime = eq_daily_industry['daily_agg_record_time'].max()
            st.write("eq_daily_industry " + "latest loaded : " + str(recordtime))
        except:
            st.write("eq_daily_industry " + "NOT loaded")
        try:
            eq_daily_kpi = pd.read_pickle('data/eq_daily_kpi.pickle')
            recordtime = eq_daily_kpi['updated_datetime'].max()
            st.write("eq_daily_kpi " + "latest loaded : " + str(recordtime))
        except:
            st.write("eq_daily_kpi " + "NOT loaded")
        try:
            eq_hist_details = pd.read_pickle('data/eq_hist_details.pickle')
            recordtime = eq_hist_details['date'].max()  
            st.write("eq_hist_details " + "latest loaded : " + str(recordtime))
        except:
            st.write("eq_hist_details " + "NOT loaded")
        try:
            eq_hist_price = pd.read_pickle('data/eq_hist_price.pickle')
            recordtime = eq_hist_price['date'].max()  
            st.write("eq_hist_price " + "latest loaded : " + str(recordtime))
        except:
            st.write("eq_hist_price " + "NOT loaded")
        try:
            eq_hist_sum = pd.read_pickle('data/eq_hist_sum.pickle')
            recordtime = eq_hist_sum['qtr_last_date'].max()  
            st.write("eq_hist_sum " + "latest loaded : " + str(recordtime))
        except:
            st.write("eq_hist_sum " + "NOT loaded")

        col1, col2 = st.columns(2)

        data_df = pd.read_pickle('data/eq_dl_stats.pickle')
        data_df = data_df.rename({'rounded_updated_datetime': 'datetime', 'count_fx_ticker': 'count'}, axis=1).copy()

        with col1:
            equity_daily_kpi_df = data_df[data_df['type'] == 'equity_daily_kpi'].copy()
            equity_daily_kpi_df.drop(['type'], axis=1, inplace=True)
            st.subheader('equity_daily_kpi')
            st.table(data=equity_daily_kpi_df)

            equity_price_history_df = data_df[data_df['type'] == 'equity_price_history'].copy()
            equity_price_history_df.drop(['type'], axis=1, inplace=True)
            st.subheader('equity_price_history')
            st.table(data=equity_price_history_df)

        with col2:
            equity_financials = data_df[data_df['type'] == 'equity_financials'].copy()
            equity_financials.drop(['type'], axis=1, inplace=True)
            st.subheader('equity_financials')
            st.table(data=equity_financials)

            fxhistorical_df = data_df[data_df['type'] == 'fxhistorical'].copy()
            fxhistorical_df.drop(['type'], axis=1, inplace=True)
            st.subheader('fxhistorical')
            st.table(data=fxhistorical_df)



def ad_dash():

    try:

        email = st.session_state['user']['email']

        df = pd.read_csv('data/datetime_update.csv')
        df = df.set_index('datatype')
        df['datetime'] = df['datetime'].apply(lambda x: parser.parse(x))
        earliest_datetime = df['datetime'].max()

        st.session_state['data_download_datetime'] = earliest_datetime

        if email == 'yuong1979@gmail.com':

            st.write("Logged in as admin: ", email)
            st.write("Last download datetime is: ", earliest_datetime)

            st.button("Run download Data", key=None, help=None, on_click=task, disabled=False)
            st.button("Refresh page", key=None, help=None, on_click=refresh, disabled=False)

            data_stats()

    except:
        pass        

    if 'page' not in st.session_state:
        st.session_state['page'] = 'Home'

    if 'ind_type' in st.session_state:
        sel_ind = st.session_state['ind_type']
