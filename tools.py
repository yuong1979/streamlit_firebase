import smtplib
from email.message import EmailMessage
from settings import (project_id, firebase_database, fx_api_key, firestore_api_key, google_sheets_api_key, 
                    schedule_function_key, firebase_auth_api_key, email_password, cloud_storage_key)
from secret import access_secret
import pytz
from datetime import datetime
from google.oauth2 import service_account
from google.cloud.firestore import Client
from secret import access_secret
import pandas as pd
import json
from firebase_admin import firestore
from googleapiclient.discovery import build
import streamlit as st
import os
from google.cloud import storage
from dateutil import parser


email_password = access_secret(email_password, project_id)

google_sheets_api_key = access_secret(google_sheets_api_key, project_id)
google_sheets_api_key_dict = json.loads(google_sheets_api_key)
gscredentials = service_account.Credentials.from_service_account_info(google_sheets_api_key_dict)
REQUIRED_SPREADSHEET_ID = '1_lobEzbiuP9TE2UZqmqSAwizT8f2oeuZ8mVuUTbBAsA'
service = build('sheets', 'v4', credentials=gscredentials)
sheet = service.spreadsheets()






# ##############################################################################################################################
# ############### Downloading files from google storage for refreshing data files inside data/ .pickle #########################
# ##############################################################################################################################
# python -c 'from tools import update_data; update_data()'

# @st.experimental_memo - 2022-09-20 17:11:22.203 Thread 'Thread-628': missing ScriptRunContext
def update_data():

    df = pd.read_csv('data/datetime_update.csv')
    df = df.set_index('datatype')

    df['datetime'] = df['datetime'].apply(lambda x: parser.parse(x))

    earliest_datetime = df['datetime'].max()

    tz_SG = pytz.timezone('Singapore')
    current_datetime = datetime.now(tz_SG)
    #can choose to set and run it without if time_diff.days < set_target_days statement
    set_target_days = 1

    time_diff = current_datetime - earliest_datetime

    message = "Exiting because the latest entry has been extracted less than {} days ago".format(set_target_days)

    # if time_diff.days < set_target_days:
    #     print (message)
    #     return (message)
    #     exit()

    data_to_update = [
                    'eq_daily_agg.pickle',
                    'eq_daily_kpi.pickle',
                    'eq_daily_industry.pickle',
                    'eq_hist_price.pickle',
                    'eq_hist_details.pickle',
                    'eq_hist_sum.pickle',
                    'eq_dl_stats.pickle',
                    ]

    #Retrieving the bucket details
    key_str = str(access_secret(cloud_storage_key, project_id))
    storage_client = storage.Client(key_str)
    bucket = storage_client.get_bucket('test_cloud_storage_bucket_blockmacro')

    current_datetime = str(current_datetime)

    for i in data_to_update:


        #fix what seems to be data not downloading
        ###############################################
        ### Looks like there is an unsolved mystery here, download from gcp does not seem to work and overwrite existing files at times
        ### But when a testing csv is used - it works, it is vital to keep monitoring the extraction and whether or not it works
        ###############################################
        #loading new set of data into streamlit
        blop = bucket.blob(blob_name = i).download_as_string()
        # print (blop)
        path = 'data/' + str(i)
        with open (path, "wb") as f:
                f.write(blop)


        # # Initialise a client
        # storage_client = storage.Client(key_str)
        # # Create a bucket object for our bucket
        # bucket = storage_client.get_bucket('test_cloud_storage_bucket_blockmacro')
        # # Create a blob object from the filepath
        # blob = bucket.blob(blob_name = i)
        # path = 'data/' + str(i)
        # # Download the file to a destination
        # blob.download_to_filename(path)

        #updating the recordtime dataframe
        name = i.split('.')[0]
        datetime_df = df[df.index == name]
        df.loc[datetime_df.index,['datetime']] = current_datetime

    #update the datetime pickle
    df.to_csv('data/datetime_update.csv')

    st.session_state['data_download_datetime'] = earliest_datetime

    print ('data successfully updated')

    return ("Data successfully updated")




# #######################################################################################################
# ############### caching the reading of pickle to speed up loading #####################################
# #######################################################################################################
# python -c 'from tools import extract_industry_pickle; extract_industry_pickle()'

# @st.cache()
@st.experimental_memo
def extract_industry_pickle():
    df = pd.read_pickle('data/eq_daily_industry.pickle')
    cols = df.columns.values.tolist()
    #remove unwanted items
    df = df[((df['industry'] != 'Shell Companies'))]
    #remove time so the below can work
    cols.remove('daily_agg_record_time')
    for i in cols:
        #round all the data
        df[i] = df[i].apply(lambda x: x if isinstance(x, str) else round(x,3))
        #replace with none all those data that are empty
        df[i] = df[i].apply(lambda x: None if x == "" else x)

    df = df.sort_values(by='industry', ascending=True)
    return(df)




# if you need to speed up the filter runtime, you can try limiting the number of kpis accessible here
@st.experimental_memo
def extract_hist_details_ann_balancesheet():
    df = pd.read_pickle('data/eq_hist_details.pickle')
    df = df[ (df['cattype'] == 'annual_balancesheet')]
    return(df)

@st.experimental_memo
def extract_hist_details_ann_cashflow():
    df = pd.read_pickle('data/eq_hist_details.pickle')
    df = df[ (df['cattype'] == 'annual_cashflow')]
    return(df)

@st.experimental_memo
def extract_hist_details_ann_profitnloss():
    df = pd.read_pickle('data/eq_hist_details.pickle')
    df = df[ (df['cattype'] == 'annual_profit&loss')]
    return(df)

@st.experimental_memo
def extract_hist_details_qtr_balancesheet():
    df = pd.read_pickle('data/eq_hist_details.pickle')
    df = df[ (df['cattype'] == 'quarterly_balancesheet')]
    return(df)

@st.experimental_memo
def extract_hist_details_qtr_cashflow():
    df = pd.read_pickle('data/eq_hist_details.pickle')
    df = df[ (df['cattype'] == 'quarterly_cashflow')]
    return(df)

@st.experimental_memo
def extract_hist_details_qtr_profitnloss():
    df = pd.read_pickle('data/eq_hist_details.pickle')
    df = df[ (df['cattype'] == 'quarterly_profit&loss')]
    return(df)



# #######################################################################################################
# ############### convert digits to alphabets for large numbers ########################################
# #######################################################################################################
# python -c 'from tools import convert_digits; convert_digits()'

# trillion = 1000_000_000_000
# billion = 1000_000_000
# million = 1000_000
# thousand = 1000

# @st.experimental_memo
# def convert_digits(num):
#     if num >= trillion:
#         number = str(round(float(num / trillion),2)) + 'T'        
#     elif num >= billion:
#         number = str(round(float(num / billion),2)) + 'B'
#     elif num >= million:
#         number = str(round(float(num / million),2)) + 'M'
#     elif num >= thousand:
#         number = str(round(float(num / thousand),2)) + 'K'
#     else:
#         number = num
#     return number



trillion = 1000_000_000_000
billion = 1000_000_000
million = 1000_000
thousand = 1000

n_thousand = -1000
n_million = -1000_000
n_billion = -1000_000_000
n_trillion = -1000_000_000_000

@st.experimental_memo
def convert_digits(num):
    if num >= trillion:
        number = str(round(float(num / trillion),2)) + 'T'        
    elif num >= billion:
        number = str(round(float(num / billion),2)) + 'B'
    elif num >= million:
        number = str(round(float(num / million),2)) + 'M'
    elif num >= thousand:
        number = str(round(float(num / thousand),2)) + 'K'

    elif num <= n_trillion:
        number = str(round(float(num / trillion),2)) + 'T'

    elif num <= n_billion:
        number = str(round(float(num / billion),2)) + 'B'

    elif num <= n_million:
        number = str(round(float(num / million),2)) + 'M'

    elif num <= n_thousand:
        number = str(round(float(num / thousand),2)) + 'K'

    else:
        number = num
    return number







# #######################################################################################################
# ############### Error email ##########################################################################
# #######################################################################################################



def error_email(subject, content):
    EMAIL_ADDRESS = "macrokpi2022@gmail.com"
    EMAIL_PASSWORD = email_password
    from_contacts = [EMAIL_ADDRESS]
    to_contacts = [EMAIL_ADDRESS]
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_contacts
    msg['To'] = to_contacts
    content_to_send = content
    msg.set_content(content_to_send)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)







# #######################################################################################################
# ############### Sample email ##########################################################################
# #######################################################################################################
# python -c 'from email_function import sample_email; sample_email()'

def sample_email():
    EMAIL_ADDRESS = "macrokpi2022@gmail.com"
    EMAIL_PASSWORD = email_password
    contacts = [EMAIL_ADDRESS]
    msg = EmailMessage()
    msg['Subject'] = 'Grab dinner this weekend'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = contacts
    msg.set_content('How about dinner at 6pm this saturday ok,  dude dont be bwei swee!')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)







########################################################################################
###########  Export function to google sheets  #########################################
########################################################################################
# python -c 'from export_gs import export_gs_func; export_gs_func()'

def export_gs_func(name, df ,sheetinfo):

    dfcol = []
    for i in df.columns:
        try:
            i = i.strftime('%Y-%m-%d')
        except:
            pass
        dfcol.append(i)

    dfindex = []
    for i in df.index:
        dfindex.append([i])

    dflist = df.values.tolist()

    #Inject the values
    request = sheet.values().update(spreadsheetId=REQUIRED_SPREADSHEET_ID, 
        range=sheetinfo+"!B2", valueInputOption="USER_ENTERED", body={"values":dflist}).execute()

    #Inject the index
    request = sheet.values().update(spreadsheetId=REQUIRED_SPREADSHEET_ID, 
        range=sheetinfo+"!A2", valueInputOption="USER_ENTERED", body={"values":dfindex}).execute()

    #Inject the fields
    request = sheet.values().update(spreadsheetId=REQUIRED_SPREADSHEET_ID, 
        range=sheetinfo+"!B1", valueInputOption="USER_ENTERED", body={"values":[dfcol]}).execute()

    #Inject the name
    request = sheet.values().update(spreadsheetId=REQUIRED_SPREADSHEET_ID, 
        range=sheetinfo+"!A1", valueInputOption="USER_ENTERED", body={"values":[[name]]}).execute()


# # #######################################################################################################
# # ############### caching the reading of csv to speed up loading ########################################
# # #######################################################################################################
# # python -c 'from tools import extract_csv; extract_csv()'

# @st.cache()
# def extract_csv(csv):
#     df = pd.read_csv(csv, index_col=1)
#     df = df.drop("Unnamed: 0", axis='columns')
#     return df


#design extraction for csv
# check the folder to check if the industry data suffix has a date that is today, if it is today than go
# on to load the current csv if the suffix does not include a date that is today, then check firebase earliest
# industry date, if the industry date is more than 24 hours ago than extract and overwrite current csv file and
# name the csv suffix with todays date



# # #################################################################################################
# # ####### Extracting daily equity data to google sheets ###########################################
# # #################################################################################################
# # python -c 'from test import daily_equity_extract_gs; daily_equity_extract_gs()'

# def daily_equity_extract_gs():

#     collection = 'equity_daily_kpi'
#     docs = db.collection(collection).stream()
#     # docs = db.collection(collection).limit(200).stream()
#     datalist = []

#     x = 0
#     for i in docs:
#         data = {}
#         tier2data = i._data['kpi']
#         data["ticker"] = i._data['ticker']

#         #inserting all the kpis into list to be exported to google sheets
#         tier1kpilist = ['country','industry', 'ticker','ebitdaUSD', 'marketCapUSD', 'totalRevenueUSD', 'grossProfitsUSD' ]
#         tier2kpilist = ['currency','ebitda', 'marketCap', 'totalRevenue', 'grossProfits' ]

#         for j in tier1kpilist:
#             try:
#                 data[j] = i._data[j]
#             except:
#                 data[j] = ""

#         for k in tier2kpilist:
#             try:
#                 data[k] = tier2data[k]
#             except:
#                 data[k] = ""

#         datalist.append(data)
#         print (x, i._data['ticker'])
#         x = x + 1

#     df = pd.DataFrame(datalist)
#     df.fillna('', inplace=True)
#     df = df[df["country"] != ""]
#     export_gs_func(collection, df, "data")


# # ####################################################################################################################################
# # ############### To decide if the extraction needs to proceed (if the earliest extracted date is beyond a target) ###################
# # ####################################################################################################################################


# firestore_api_key = access_secret(firestore_api_key, project_id)
# firestore_api_key_dict = json.loads(firestore_api_key)
# fbcredentials = service_account.Credentials.from_service_account_info(firestore_api_key_dict)
# db = Client(firebase_database, fbcredentials)

# # if the earliest date is not 
# def decide_extraction(time_in_hours, collection, collection_updated_datetime):
#     tz_SG = pytz.timezone('Singapore')
#     # time_in_hours = 1
#     time_seconds = 60 * 60 * time_in_hours 
#     latest_entry = db.collection(collection).order_by(collection_updated_datetime, direction=firestore.Query.ASCENDING).limit(1).get()
#     time_diff = datetime.now(tz_SG) - latest_entry[0]._data[collection_updated_datetime]

#     if time_diff.seconds < time_seconds:
#         print ('exiting because the latest entry has been extracted less than 24 hours ago')
#         exit()




# # ##############################################################################################################################
# # ############### Downloading files from google storage for refreshing data files inside data/ .pickle #########################
# # ##############################################################################################################################
# # python -c 'from tools import test; test()'

# def test():

#     tz_SG = pytz.timezone('Singapore')
#     current_datetime = datetime.now(tz_SG)

#     # data_list = ['eq_daily_agg', 
#     #                 'eq_daily_kpi', 
#     #                 'eq_daily_industry', 
#     #                 'eq_hist_price', 
#     #                 'eq_hist_details']

#     # date_list = [current_datetime, 
#     #                 current_datetime, 
#     #                 current_datetime, 
#     #                 current_datetime, 
#     #                 current_datetime]


#     # df = pd.DataFrame({
#     #     'datatype': data_list,
#     #     'datetime': date_list
#     #     })

#     # print (df)

#     # df = df.set_index('datatype')
#     # df.to_csv('data/datetime_update.csv', index=True)

#     df = pd.read_csv('data/datetime_update.csv')
#     df = df.set_index('datatype')




kpi_remove = [
'company_count',
'ebitdaUSD',
'marketCapUSD',
'totalRevenueUSD',
'fullTimeEmployees',
'priceToSalesTrailing12Months',
'earningsQuarterlyGrowth',
'trailingAnnualDividendRate',
'fiveYearAvgDividendYield',
'trailingAnnualDividendYield',
'daily_agg_record_time',
]


kpi_mapping = {
'company_count': True,
'ebitdaUSD': True,
'marketCapUSD': True,
'totalRevenueUSD': True,
'fullTimeEmployees': False,

# profitability
'grossMargins': True,
'operatingMargins': True,
'ebitdaMargins': True,
'profitMargins': True,

# growth
'earningsGrowth': True,
'revenueGrowth': True,

# value
'forwardEps': True,
'trailingEps': True,

'forwardPE': False,
'trailingPE': False,

'pegRatio': False,
'trailingPegRatio': False,

'enterpriseToEbitda': False,
'enterpriseToRevenue': False,

'returnOnEquity': True,
'returnOnAssets': True,

# popularity
'heldPercentInstitutions': True,
'heldPercentInsiders': True,

# financial health
'debtToEquity': False,
'quickRatio': True,
'currentRatio': True,

# dividends
'dividendYield': True,
'dividendRate': True,
'trailingAnnualDividendRate': True,
'fiveYearAvgDividendYield': True,
'trailingAnnualDividendYield': True,

'earningsQuarterlyGrowth': True,
'priceToBook': False,
'priceToSalesTrailing12Months': False

}
