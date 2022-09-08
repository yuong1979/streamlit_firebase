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


email_password = access_secret(email_password, project_id)

google_sheets_api_key = access_secret(google_sheets_api_key, project_id)
google_sheets_api_key_dict = json.loads(google_sheets_api_key)
gscredentials = service_account.Credentials.from_service_account_info(google_sheets_api_key_dict)
REQUIRED_SPREADSHEET_ID = '1_lobEzbiuP9TE2UZqmqSAwizT8f2oeuZ8mVuUTbBAsA'
service = build('sheets', 'v4', credentials=gscredentials)
sheet = service.spreadsheets()



# #######################################################################################################
# ############### Error email ##########################################################################
# #######################################################################################################

# python -c 'from email_function import error_email; error_email()'

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
# ####### Extracting industry data to google sheets ###############################################
# #################################################################################################
# python -c 'from tools import industry_extract_gs; industry_extract_gs()'

def industry_extract_gs():

    collection = 'equity_daily_industry'
    #### export required data to google sheets ######
    docs = db.collection(collection).stream()

    datalist = []

    for i in docs:
        data = i._data['daily_agg']
        data["industry"] = i.id

        # #inserting all the kpis into list to be exported to google sheets
        # kpilist = ['Median_currentRatio', 'Median_debtToEquity', 'Median_earningsGrowth', 'Median_ebitdaMargins', 
        #     'Median_grossMargins', 'Median_heldPercentInsiders', 'Median_operatingMargins', 'Median_profitMargins', 
        #     'Median_quickRatio', 'Median_returnOnAssets', 'Median_returnOnEquity', 'Median_revenueGrowth', 
        #     'Sum_ebitdaUSD', 'Sum_fullTimeEmployees', 'Sum_marketCapUSD', 'Sum_totalRevenueUSD',
        #     ]

        #inserting all the kpis into list to be exported to google sheets
        kpilist = [ 'company_count', 'Sum_ebitdaUSD', 'Sum_marketCapUSD', 'Sum_totalRevenueUSD', 'Sum_fullTimeEmployees',
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
            except:
                data[j] = ""

        datalist.append(data)

    kpilist.insert(0, 'industry')
    df = pd.DataFrame(datalist)
    df = df[kpilist]

    # fill all the blanks with na
    df.fillna('', inplace=True)

    # cleaning the columns by removing sum and median
    for i in kpilist:
        print (i)
        if i.find('Sum') == 0:
            newkpi = i[4:]#[:-3]
            print (newkpi)
        elif i.find('Median') == 0:
            newkpi = i[7:]
            print (newkpi)
        else:
            newkpi = i

        df.rename(columns = {i:newkpi}, inplace = True)

    df = df[((df['industry'] != 'Shell Companies'))]

    ### exporting to google sheets
    # export_gs_func("industry details", df, "testdata")

    df.to_csv('dataframe_csv/industry_data.csv', index = True)


# #################################################################################################
# ####### Extracting daily equity data to google sheets ###########################################
# #################################################################################################
# python -c 'from test import daily_equity_extract_gs; daily_equity_extract_gs()'

def daily_equity_extract_gs():

    collection = 'equity_daily_kpi'
    docs = db.collection(collection).stream()
    # docs = db.collection(collection).limit(200).stream()
    datalist = []

    x = 0
    for i in docs:
        data = {}
        tier2data = i._data['kpi']
        data["ticker"] = i._data['ticker']

        #inserting all the kpis into list to be exported to google sheets
        tier1kpilist = ['country','industry', 'ticker','ebitdaUSD', 'marketCapUSD', 'totalRevenueUSD', 'grossProfitsUSD' ]
        tier2kpilist = ['currency','ebitda', 'marketCap', 'totalRevenue', 'grossProfits' ]

        for j in tier1kpilist:
            try:
                data[j] = i._data[j]
            except:
                data[j] = ""

        for k in tier2kpilist:
            try:
                data[k] = tier2data[k]
            except:
                data[k] = ""

        datalist.append(data)
        print (x, i._data['ticker'])
        x = x + 1

    df = pd.DataFrame(datalist)
    df.fillna('', inplace=True)
    df = df[df["country"] != ""]
    export_gs_func(collection, df, "data")





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
