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



email_password = access_secret(email_password, project_id)

google_sheets_api_key = access_secret(google_sheets_api_key, project_id)
google_sheets_api_key_dict = json.loads(google_sheets_api_key)
gscredentials = service_account.Credentials.from_service_account_info(google_sheets_api_key_dict)
REQUIRED_SPREADSHEET_ID = '1_lobEzbiuP9TE2UZqmqSAwizT8f2oeuZ8mVuUTbBAsA'
service = build('sheets', 'v4', credentials=gscredentials)
sheet = service.spreadsheets()



# #######################################################################################################
# ############### Refreshing data files inside data/ .pickle for google storage #########################
# #######################################################################################################
# python -c 'from data_extraction import update_data; update_data()'

# @st.experimental_memo
def update_data():

    df = pd.read_pickle('data/datetime_update.pickle')
    earliest_datetime = df['datetime'].max()

    tz_SG = pytz.timezone('Singapore')
    current_datetime = datetime.now(tz_SG)

    time_in_hours = 24
    time_seconds = 60 * 60 * time_in_hours

    time_diff = current_datetime - earliest_datetime

    message = "Exiting because the latest entry has been extracted less than {} hours ago".format(time_in_hours)

    if time_diff.seconds < time_seconds:
        return (message)
        exit()

    data_to_update = ['eq_daily_agg.pickle', 'eq_daily_kpi.pickle', 'eq_daily_industry.pickle']

    #Retrieving the bucket details
    key_str = str(access_secret(cloud_storage_key, project_id))
    storage_client = storage.Client(key_str)
    bucket = storage_client.get_bucket('test_cloud_storage_bucket_blockmacro')

    for i in data_to_update:

        #loading new set of data into streamlit
        blop = bucket.blob(blob_name = i).download_as_string()
        path = 'data/' + str(i)
        with open (path, "wb") as f:
                f.write(blop)

        #updating the recordtime dataframe
        name = i.split('.')[0]
        datetime_df = df[df['datatype'] == name]
        df.loc[datetime_df.index,['datatype','datetime']] = [name,current_datetime]
    

    #update the datetime pickle
    df.to_pickle('data/datetime_update.pickle')

    return ("Data successfully updated")




# #######################################################################################################
# ############### caching the reading of csv to speed up loading ########################################
# #######################################################################################################
# python -c 'from tools import extract_industry_pickle; extract_industry_pickle()'

# @st.cache()
@st.experimental_memo
def extract_industry_pickle():
    df = pd.read_pickle('data/eq_daily_industry.pickle')
    cols = df.columns.values.tolist()
    for i in cols:
        df[i] = df[i].apply(lambda x: None if x=="" else x)
    # print (df)
    return(df)



# #######################################################################################################
# ############### caching the reading of csv to speed up loading ########################################
# #######################################################################################################
# python -c 'from tools import extract_csv; extract_csv()'

@st.cache()
def extract_csv(csv):
    df = pd.read_csv(csv, index_col=1)
    df = df.drop("Unnamed: 0", axis='columns')
    return df


#design extraction for csv
# check the folder to check if the industry data suffix has a date that is today, if it is today than go
# on to load the current csv if the suffix does not include a date that is today, then check firebase earliest
# industry date, if the industry date is more than 24 hours ago than extract and overwrite current csv file and
# name the csv suffix with todays date



# #######################################################################################################
# ############### convert digits to alphabets for large numbers ########################################
# #######################################################################################################
# python -c 'from tools import convert_digits; convert_digits()'

trillion = 1000000000000
billion = 1000000000
million = 1000000
thousand = 1000

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


# ####################################################################################################################################
# ############### To decide if the extraction needs to proceed (if the earliest extracted date is beyond a target) ###################
# ####################################################################################################################################




firestore_api_key = access_secret(firestore_api_key, project_id)
firestore_api_key_dict = json.loads(firestore_api_key)
fbcredentials = service_account.Credentials.from_service_account_info(firestore_api_key_dict)
db = Client(firebase_database, fbcredentials)

# if the earliest date is not 
def decide_extraction(time_in_hours, collection, collection_updated_datetime):
    tz_SG = pytz.timezone('Singapore')
    # time_in_hours = 1
    time_seconds = 60 * 60 * time_in_hours 
    latest_entry = db.collection(collection).order_by(collection_updated_datetime, direction=firestore.Query.ASCENDING).limit(1).get()
    time_diff = datetime.now(tz_SG) - latest_entry[0]._data[collection_updated_datetime]

    if time_diff.seconds < time_seconds:
        print ('exiting because the latest entry has been extracted less than 24 hours ago')
        exit()





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
