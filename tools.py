import smtplib
from email.message import EmailMessage
from settings import (project_id, firebase_database, fx_api_key, firestore_api_key, google_sheets_api_key, 
                    schedule_function_key, firebase_auth_api_key, email_password)
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

email_password = access_secret(email_password, project_id)

google_sheets_api_key = access_secret(google_sheets_api_key, project_id)
google_sheets_api_key_dict = json.loads(google_sheets_api_key)
gscredentials = service_account.Credentials.from_service_account_info(google_sheets_api_key_dict)
REQUIRED_SPREADSHEET_ID = '1_lobEzbiuP9TE2UZqmqSAwizT8f2oeuZ8mVuUTbBAsA'
service = build('sheets', 'v4', credentials=gscredentials)
sheet = service.spreadsheets()






# #######################################################################################################
# ############### Refreshing the csv data ###############################################################
# #######################################################################################################
# python -c 'from tools import updating_industry_csv; updating_industry_csv()'

@st.cache()
def updating_industry_csv():

    tz_SG = pytz.timezone('Singapore')
    datenow = datetime.now(tz_SG)

    #extracting the date from csv to confirm the dates of last download
    df_date_updated = pd.read_csv('dataframe_csv/dataset_updated.csv', index_col=0)
    industry_last_dl_date = df_date_updated.loc['industry', 'last_downloaded']

    #convert datetime into a format that can be compared to datetime now - csv extracted datetime is fucked
    industry_last_dl_date = industry_last_dl_date.split(".")[0]
    industry_last_dl_date = datetime.strptime(industry_last_dl_date, '%Y-%m-%d %H:%M:%S')
    #add timezone
    industry_last_dl_date = tz_SG.localize(industry_last_dl_date)

    #compare current datetime vs last csv updated datetime
    difference = datenow - industry_last_dl_date 
    hours_passed = difference.seconds/3600

    if hours_passed > 24:
        #proceed with extraction from firebase
        industry_extract_csv()

        #updating datetime when dataset is downloaded
        df_date_updated = pd.read_csv('dataframe_csv/dataset_updated.csv', index_col=0)
        df_date_updated.loc[(df_date_updated.index == 'industry'),'last_downloaded'] = datenow
        df_date_updated.to_csv('dataframe_csv/dataset_updated.csv', index = True)

        print("CSV updated")

    else:
        print("Skipping, only " + str(round(hours_passed,1)) + " hours has passed")
        pass

    # #comparing dates between dates inside csv and last extracted dates in firebase - POSSIBLY REDUNDANT
    # df = pd.read_csv(csv, index_col=1)
    # df['Date'] = pd.to_datetime(df['daily_agg_record_time'])
    # earliest_csv_date = df['Date'].min()
    # print (earliest_csv_date, 'earliest_csv_date')
    # # ASCENDING - earliest first
    # # DESCENDING - latest first
    # date = db.collection('equity_daily_industry').order_by("daily_agg_record_time", direction=firestore.Query.ASCENDING).limit(1).get()
    # earliest_fb_date = date[0]._data['daily_agg_record_time']
    # print (earliest_fb_date, 'earliest_fb_date')


    # #creating a fresh new csv to record last time dataset was updated
    # tz_SG = pytz.timezone('Singapore')
    # datenow = datetime.now(tz_SG)
    # dataset = {
    #     'data': ['industry', 'equity', 'country'], 
    #     'last_downloaded': [datenow, datenow, datenow]
    #     }
    # df = pd.DataFrame(data=dataset)
    # print (df)
    # df.to_csv('dataframe_csv/dataset_updated.csv', index=False)








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





# #################################################################################################
# ####### Extracting industry data to CSV ###############################################
# #################################################################################################
# python -c 'from tools import industry_extract_csv; industry_extract_csv()'

def industry_extract_csv():

    collection = 'equity_daily_industry'
    #### export required data to google sheets ######
    docs = db.collection(collection).stream()

    datalist = []

    for i in docs:

        # print (i._data['daily_agg_record_time'])
        data = i._data['daily_agg']
        data["industry"] = i.id


        #inserting all the kpis into list to be exported to google sheets
        kpilist = ['daily_agg_record_time', 'company_count', 'Sum_ebitdaUSD', 'Sum_marketCapUSD', 'Sum_totalRevenueUSD', 'Sum_fullTimeEmployees',
        'Median_grossMargins', 'Median_operatingMargins', 'Median_ebitdaMargins', 'Median_profitMargins',
        'Median_earningsGrowth', 'Median_revenueGrowth', 'Median_forwardEps', 'Median_trailingEps',
        'Median_forwardPE', 'Median_trailingPE', 'Median_pegRatio', 'Median_trailingPegRatio',
        'Median_enterpriseToEbitda', 'Median_enterpriseToRevenue', 'Median_returnOnEquity', 'Median_returnOnAssets',
        'Median_heldPercentInstitutions', 'Median_heldPercentInsiders',
        'Median_debtToEquity', 'Median_quickRatio', 'Median_currentRatio',
        'Median_dividendYield', 'Median_dividendRate', 'Median_trailingAnnualDividendRate',
        'Median_fiveYearAvgDividendYield', 'Median_trailingAnnualDividendYield',
        'Median_earningsQuarterlyGrowth', 'Median_priceToBook', 'Median_priceToSalesTrailing12Months'
            ]

        for j in kpilist:
            try:
                data[j] = data[j]
                #round off data to 3 decimal places
                data[j] = round(data[j],3)

            except:
                data[j] = ""

        #inserting the record time
        data['daily_agg_record_time'] = i._data['daily_agg_record_time']

        datalist.append(data)


    kpilist.insert(0, 'industry')
    df = pd.DataFrame(datalist)
    df = df[kpilist]

    # fill all the blanks with na
    df.fillna('', inplace=True)

    # cleaning the columns by removing sum and median
    for i in kpilist:
        # print (i)
        if i.find('Sum') == 0:
            newkpi = i[4:]#[:-3]
            # print (newkpi)
        elif i.find('Median') == 0:
            newkpi = i[7:]
            # print (newkpi)
        else:
            newkpi = i

        df.rename(columns = {i:newkpi}, inplace = True)

    df = df[((df['industry'] != 'Shell Companies'))]

    ### exporting to google sheets
    # export_gs_func("industry details", df, "testdata")

    # print (df)


    df.to_csv('dataframe_csv/industry_data.csv', index = True)


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
