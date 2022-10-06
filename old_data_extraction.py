# from firebase_admin import firestore
# import pandas as pd
# import numpy as np
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from datetime import datetime, timedelta
# import json
# from google.cloud.firestore import Client
# from secret import access_secret
# from settings import project_id, firebase_database, fx_api_key, firestore_api_key, google_sheets_api_key, schedule_function_key, firebase_auth_api_key, cloud_storage_key
# from tools import error_email, export_gs_func, kpi_mapping, kpi_remove
# import streamlit as st
# import plotly.express as px  # pip install plotly-express
# import plotly.graph_objects as go
# import math
# from time import process_time
# import pytz
# from google.cloud import storage
# import os


# firestore_api_key = access_secret(firestore_api_key, project_id)
# firestore_api_key_dict = json.loads(firestore_api_key)
# fbcredentials = service_account.Credentials.from_service_account_info(firestore_api_key_dict)
# db = Client(firebase_database, fbcredentials)







# # #######################################################################################################
# # ############### Refreshing the csv data ###############################################################
# # #######################################################################################################
# # python -c 'from data_extraction import updating_industry_csv; updating_industry_csv()'

# @st.cache()
# def updating_industry_csv():

#     tz_SG = pytz.timezone('Singapore')
#     datenow = datetime.now(tz_SG)

#     #extracting the date from csv to confirm the dates of last download
#     df_date_updated = pd.read_csv('dataframe_csv/dataset_updated.csv', index_col=0)
#     industry_last_dl_date = df_date_updated.loc['industry', 'last_downloaded']

#     #convert datetime into a format that can be compared to datetime now - csv extracted datetime is fucked
#     industry_last_dl_date = industry_last_dl_date.split(".")[0]
#     industry_last_dl_date = datetime.strptime(industry_last_dl_date, '%Y-%m-%d %H:%M:%S')
#     #add timezone
#     industry_last_dl_date = tz_SG.localize(industry_last_dl_date)

#     #compare current datetime vs last csv updated datetime
#     difference = datenow - industry_last_dl_date 
#     hours_passed = difference.seconds/3600

#     if hours_passed > 24:
#         #proceed with extraction from firebase
#         industry_extract_csv()

#         #updating datetime when dataset is downloaded
#         df_date_updated = pd.read_csv('dataframe_csv/dataset_updated.csv', index_col=0)
#         df_date_updated.loc[(df_date_updated.index == 'industry'),'last_downloaded'] = datenow
#         df_date_updated.to_csv('dataframe_csv/dataset_updated.csv', index = True)

#         print("CSV updated")

#     else:
#         print("Skipping, only " + str(round(hours_passed,1)) + " hours has passed")
#         pass

#     # #comparing dates between dates inside csv and last extracted dates in firebase - POSSIBLY REDUNDANT
#     # df = pd.read_csv(csv, index_col=1)
#     # df['Date'] = pd.to_datetime(df['daily_agg_record_time'])
#     # earliest_csv_date = df['Date'].min()
#     # print (earliest_csv_date, 'earliest_csv_date')
#     # # ASCENDING - earliest first
#     # # DESCENDING - latest first
#     # date = db.collection('equity_daily_industry').order_by("daily_agg_record_time", direction=firestore.Query.ASCENDING).limit(1).get()
#     # earliest_fb_date = date[0]._data['daily_agg_record_time']
#     # print (earliest_fb_date, 'earliest_fb_date')


#     # #creating a fresh new csv to record last time dataset was updated
#     # tz_SG = pytz.timezone('Singapore')
#     # datenow = datetime.now(tz_SG)
#     # dataset = {
#     #     'data': ['industry', 'equity', 'country'], 
#     #     'last_downloaded': [datenow, datenow, datenow]
#     #     }
#     # df = pd.DataFrame(data=dataset)
#     # print (df)
#     # df.to_csv('dataframe_csv/dataset_updated.csv', index=False)








# # #################################################################################################
# # ####### Extracting daily equity raw data from firebase storing it in pickle #####################
# # #################################################################################################
# # python -c 'from data_extraction import data_extraction; daily_equity_extraction()'

# values_1 = ['grossMargins', 'operatingMargins', 'profitMargins',  'ebitdaMargins', 
#         'returnOnAssets', 'returnOnEquity', 'revenueGrowth', 'earningsGrowth',
#         'currentRatio', 'quickRatio', 'debtToEquity',
#         'heldPercentInsiders', 'heldPercentInstitutions',
#         'forwardPE', 'trailingPE', 'earningsQuarterlyGrowth', 'priceToSalesTrailing12Months',
#         'priceToBook', 'enterpriseToEbitda', 'enterpriseToRevenue',
#         'pegRatio', 'trailingPegRatio',
#         'trailingEps', 'forwardEps',
#         'trailingAnnualDividendYield', 'trailingAnnualDividendRate', 'fiveYearAvgDividendYield', 'dividendYield', 'dividendRate'
#         ]

# values_2 = ['marketCapUSD', 'totalRevenueUSD', 'ebitdaUSD']

# def daily_equity_extraction():

#     values_1.insert(0, 'industry')
#     values_2.insert(0, 'updated_datetime')

#     collection = 'equity_daily_kpi'
#     docs = db.collection(collection).stream()
#     # docs = db.collection(collection).limit(5).stream()

#     data = {}
#     for i in docs:
#         data_kpi = {}
#         for j in values_2:
#             try:
#                 data_kpi[j] = i._data[j]
#             except KeyError:
#                 data_kpi[j] = 0

#         for k in values_1:
#             try:
#                 data_kpi[k] = i._data['kpi'][k]
#             except KeyError:
#                 data_kpi[k] = 0

#         data[i._data['ticker']] = data_kpi

#     df = pd.DataFrame.from_dict(data)
#     df = df.transpose()

#     df.index.names = ['Ticker']

#     df.to_pickle('data/eq_daily_kpi.pickle')










# # #################################################################################################
# # ####### Extracting industry data to pickle ###############################################
# # #################################################################################################
# # python -c 'from data_extraction import industry_extract_csv; industry_extract_csv()'

# def industry_extract_csv():

#     collection = 'equity_daily_industry'
#     #### export required data to google sheets ######
#     docs = db.collection(collection).stream()

#     datalist = []

#     for i in docs:

#         # print (i._data['daily_agg_record_time'])
#         data = i._data['daily_agg']
#         data["industry"] = i.id


#         #inserting all the kpis into list to be exported to google sheets
#         kpilist = ['daily_agg_record_time', 'company_count', 'Sum_ebitdaUSD', 'Sum_marketCapUSD', 'Sum_totalRevenueUSD', 'Sum_fullTimeEmployees',
#         'Median_grossMargins', 'Median_operatingMargins', 'Median_ebitdaMargins', 'Median_profitMargins',
#         'Median_earningsGrowth', 'Median_revenueGrowth', 'Median_forwardEps', 'Median_trailingEps',
#         'Median_forwardPE', 'Median_trailingPE', 'Median_pegRatio', 'Median_trailingPegRatio',
#         'Median_enterpriseToEbitda', 'Median_enterpriseToRevenue', 'Median_returnOnEquity', 'Median_returnOnAssets',
#         'Median_heldPercentInstitutions', 'Median_heldPercentInsiders',
#         'Median_debtToEquity', 'Median_quickRatio', 'Median_currentRatio',
#         'Median_dividendYield', 'Median_dividendRate', 'Median_trailingAnnualDividendRate',
#         'Median_fiveYearAvgDividendYield', 'Median_trailingAnnualDividendYield',
#         'Median_earningsQuarterlyGrowth', 'Median_priceToBook', 'Median_priceToSalesTrailing12Months'
#             ]

#         for j in kpilist:
#             try:
#                 data[j] = data[j]
#                 #round off data to 3 decimal places
#                 data[j] = round(data[j],3)

#             except:
#                 data[j] = ""

#         #inserting the record time
#         data['daily_agg_record_time'] = i._data['daily_agg_record_time']

#         datalist.append(data)


#     kpilist.insert(0, 'industry')
#     df = pd.DataFrame(datalist)
#     df = df[kpilist]

#     # fill all the blanks with na
#     df.fillna('', inplace=True)

#     # cleaning the columns by removing sum and median
#     for i in kpilist:
#         # print (i)
#         if i.find('Sum') == 0:
#             newkpi = i[4:]#[:-3]
#             # print (newkpi)
#         elif i.find('Median') == 0:
#             newkpi = i[7:]
#             # print (newkpi)
#         else:
#             newkpi = i

#         df.rename(columns = {i:newkpi}, inplace = True)

#     df = df[((df['industry'] != 'Shell Companies'))]

#     ### exporting to google sheets
#     # export_gs_func("industry details", df, "testdata")


#     print (list(df.columns.values))


#     df.to_pickle('data/eq_daily_industry.pickle')



#     # df.to_pickle('data/eq_daily_kpi.pickle')
#     # df = pd.read_pickle('data/eq_daily_kpi.pickle')