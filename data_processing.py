from firebase_admin import firestore
import pandas as pd
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json
from google.cloud.firestore import Client
from secret import access_secret
from settings import project_id, firebase_database, fx_api_key, firestore_api_key, google_sheets_api_key, schedule_function_key, firebase_auth_api_key
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import math
from time import process_time




firestore_api_key = access_secret(firestore_api_key, project_id)
firestore_api_key_dict = json.loads(firestore_api_key)
fbcredentials = service_account.Credentials.from_service_account_info(firestore_api_key_dict)
db = Client(firebase_database, fbcredentials)






# #################################################################################################
# ####### Processing median ranking and other aggregates for daily ##############################
# #################################################################################################
# python -c 'from data_processing import daily_equity_processing; daily_equity_processing()'


def daily_equity_processing():

    df = pd.read_pickle('data/daily_equity_kpi.pickle')

    t1_start = process_time()

    ind_unq = df['industry'].unique().tolist()

    cln_ind_unq = [x for x in ind_unq if x != 'nan']

    # #temporary industry list for testing
    # cln_ind_unq = [
    #     'Steel', 'Airlines', 'Gold', 'Leisure', 'Asset Management', 'Biotechnology', 'Credit Services',
    #     'Capital Markets', 'Chemicals', 'Coking Coal', 'Communication Equipment', 'Computer Hardware', 
    #     'Confectioners', 'Conglomerates', 'Consulting Services', 'Consumer Electronics', 'Copper'
    #     ]

    #removing company_count form the dictionary because it is not part of the kpi to be ranked
    del kpi_mapping['company_count']
    del kpi_mapping['fullTimeEmployees']

    ind_count = len (cln_ind_unq)

    daily_eq_agg_df = pd.DataFrame(columns = ['industry', 'kpi', 'value','rank_fraction', 'rank_%', 'median', 'sum', 'max', 'min'])

    count = 0
    for i in cln_ind_unq:
        newdf = df[df['industry'] == i]

        for key, value in kpi_mapping.items():
            # print(key, value)
            value_df = newdf[[key]]
            count_eq = value_df[key].count()
            finaldf = value_df.dropna(subset=[key])

            finaldf['count_eq'] = count_eq
            finaldf['kpi'] = key
            finaldf['industry'] = i
            finaldf['value'] = value_df

            try:
                if value == True:
                    finaldf['rank'] = finaldf[key].rank(ascending=False)
                    finaldf['max'] = finaldf['value'].max()
                    finaldf['min'] = finaldf['value'].min()               
                else:
                    finaldf['rank'] = finaldf[key].rank(ascending=True)
                    finaldf['max'] = finaldf['value'].min()
                    finaldf['min'] = finaldf['value'].max()     

                finaldf['rank_fraction'] = finaldf["rank"].astype(int).astype(str) + "/" + str(count_eq)
                finaldf['rank_%'] = 1 - (finaldf['rank'] / finaldf["count_eq"])
                finaldf['rank_%'] = finaldf['rank_%'].astype(float).round(decimals = 2)
                finaldf['median'] = finaldf['value'].median()
                finaldf['sum'] = finaldf['value'].sum()
                
            except:
                finaldf['rank_fraction'] = 'nan'
                finaldf['rank'] = 'nan'
                finaldf['rank_%'] = 'nan'
                finaldf['median'] = 'nan'
                finaldf['sum'] = 'nan'
                finaldf['max'] = 'nan'
                finaldf['min'] = 'nan'


            #add a function to change all those with 1/1 or 1 in rank_% to nan

            finaldf.drop(columns=[key, 'rank', 'count_eq'], inplace=True)
            daily_eq_agg_df = pd.concat([daily_eq_agg_df, finaldf])

        count = count + 1
        print (str(count) + "/" + str(ind_count))


    # daily_eq_agg_df.to_csv('daily_eq_agg_df.csv')

    daily_eq_agg_df.to_pickle('data/daily_eq_agg_df.pickle')


    t1_stop = process_time()
    print("Elapsed time during the whole program in seconds:",
                                         t1_stop-t1_start) 




