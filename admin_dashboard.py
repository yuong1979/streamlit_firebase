
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
    except:
        pass        

    # if 'page' not in st.session_state:
    #     st.session_state['page'] = 'Home'

    # if 'ind_type' in st.session_state:
    #     sel_ind = st.session_state['ind_type']
