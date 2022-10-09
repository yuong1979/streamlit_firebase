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
import inspect
import pytz
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import math
from time import process_time

# imports
from plotly.subplots import make_subplots
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_industry_pickle, convert_digits


firestore_api_key = access_secret(firestore_api_key, project_id)
firestore_api_key_dict = json.loads(firestore_api_key)
fbcredentials = service_account.Credentials.from_service_account_info(firestore_api_key_dict)
db = Client(firebase_database, fbcredentials)

google_sheets_api_key = access_secret(google_sheets_api_key, project_id)
google_sheets_api_key_dict = json.loads(google_sheets_api_key)
gscredentials = service_account.Credentials.from_service_account_info(google_sheets_api_key_dict)
REQUIRED_SPREADSHEET_ID = '1_lobEzbiuP9TE2UZqmqSAwizT8f2oeuZ8mVuUTbBAsA'
service = build('sheets', 'v4', credentials=gscredentials, cache_discovery=False)
sheet = service.spreadsheets()






@st.experimental_memo
def alter_size_df(df, size_kpi):


    for i in size_kpi:

        print (i)

        #fillna works here because we are only cleaning usd amounts, it should not be used for % KPIs
        df[i].fillna(0, inplace=True)
        #convert number to zero if it is an empty string or less than zero because zero below zero does not make sense for size
        df[i] = df[i].apply(lambda x: 0 if (isinstance(x, str) or x < 0) else x)
        name = str(i) + "_short"
        df[name] = df[i]
        #create two columns with shortened numbers for easy viewing of large numbers
        df[name] = df[name].apply(convert_digits)



    # if num >= trillion:
    #     number = str(round(float(num / trillion),2)) + 'T'        
    # elif num >= billion:
    #     number = str(round(float(num / billion),2)) + 'B'
    # elif num >= million:
    #     number = str(round(float(num / million),2)) + 'M'
    # elif num >= thousand:
    #     number = str(round(float(num / thousand),2)) + 'K'
    # else:
    #     number = num
    # return number


    return df


# df['ebitdaUSD_short']
# df['marketCapUSD_short']
# df['totalRevenueUSD_short']




# #################################################################################################
# ####### Testing ###############################################
# #################################################################################################
# python -c 'from test import test; test()'



def test():

    print ('test')

    df = pd.read_pickle('data/eq_hist_details.pickle')



    dfbl = df[df['cattype'] == 'annual_profit&loss']
    dfbl = dfbl['kpi'].unique()

    for i in dfbl:
        print (i)


    # print (dfbl['kpi'].unique())

    









    # Key Items

    # Gross Profit
    # Net Income
    # Operating Income
    # Total Revenue
    # Ebit

    # Total Cashflows From Investing Activities
    # Change To Netincome
    # Total Cash From Operating Activities
    # Net Income
    # Change In Cash
    # Total Cash From Financing Activities

    # Total Current Assets
    # Total Stockholder Equity
    # Total Current Liabilities
    # Total Assets


    #### for reference
    # rslt_df = dataframe[(dataframe['Age'] == 21) &
    #       dataframe['Stream'].isin(options)]

    # df = df[(df['cattype'] == 'financials') & (df['ticker'] == 'TSLA') & (df['kpi'] == 'Ebit')]
    # df = df[(df['kpi'] == 'Gross Profit') & (df['ticker'] == 'TSLA')]



# #################################################################################################
# ####### Tree chart ratios of industries ###############################################
# #################################################################################################
# python -c 'from test import ratios_by_industry_treemap; ratios_by_industry_treemap()'



def ratios_by_industry_treemap():
    print ('test')

    df = px.data.gapminder().query("year == 2007")

    print (df)

    fig = px.treemap(df, 
                    path=[px.Constant("world"), 'continent', 'country'], 
                    values='pop',
                    color='lifeExp', 
                    hover_data=['iso_alpha'],
                    color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df['lifeExp'], weights=df['pop']))
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    fig.show()




# #################################################################################################
# ####### Correlation #############################################################################
# #################################################################################################
# python -c 'from others import correlation; correlation()'

def correlation():

    df = pd.read_csv('dataframe_csv/industry_data.csv', index_col=1)
    df = df.drop("Unnamed: 0", axis='columns')

    cols = df.columns.values.tolist()
    # changing all values to floats in dataframe
    for i in cols:
        df[i] = df[i].replace('', np.nan).dropna().astype(float)
    correlation_matrix = df.corr()
    correlation_matrix.to_csv('dataframe_csv/correlation_matrix.csv', index = True)

    # # consider removing shell companies industry because it is screwing up everything
    # # export to google sheets on heatmap indicates that return on assets and return on equity are correlated at 0.885
    # # export to google sheets on heatmap indicates that quick ratio and current ratio are correlated at 0.860
    # # export to google sheets on heatmap indicates that profit margins and ebitamargins are correlated at 0.826
    # # export to google sheets on heatmap indicates that Median_earningsQuarterlyGrowth and Median_earningsGrowth are correlated at 0.94
    # # export to google sheets on heatmap indicates that Median_dividendRate and Median_trailingAnnualDividendRate are correlated at 0.97




# 'ebitdaUSD': True,
# 'marketCapUSD': True,
# 'totalRevenueUSD': True,
# 'profitMargins': True,
# 'earningsGrowth': True,
# 'revenueGrowth': True,

# 'forwardEps': True,
# 'trailingEps': True,

# 'forwardPE': False,
# 'trailingPE': False,

# 'pegRatio': False,
# 'trailingPegRatio': False,

# 'enterpriseToEbitda': False,
# 'enterpriseToRevenue': False,

# 'returnOnEquity': True,
# 'returnOnAssets': True,


# 'dividendYield': True,
# 'dividendRate': True,





# #################################################################################################
# ####### Extracting daily equity data to google sheets ###########################################
# #################################################################################################
# python -c 'from test import daily_fx_gs; daily_fx_gs()'

def daily_fx_gs():
    collection = 'fxhistorical'
    docs = db.collection(collection).order_by("datetime_format", direction=firestore.Query.DESCENDING).limit(1).get()
    data = docs[0]._data['currencyrates']
    df = pd.DataFrame.from_records(data,index=['Rates'])
    result = df.transpose()
    print(result)
    export_gs_func(collection, result, "FX")






# testdf = df.loc["Airlines", 'Median_returnOnEquity']








# #################################################################################################
# #############Google drive connection - NOT WORKING - to delete
# #################################################################################################



# from __future__ import print_function

# import os.path

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# from google.oauth2 import service_account
# from googleapiclient.http import MediaFileUpload



# def main():

#     SCOPES = ['https://www.googleapis.com/auth/drive']
#     SERVICE_ACCOUNT_FILE = 'credentials.json'

#     credentials = service_account.Credentials.from_service_account_file(
#             SERVICE_ACCOUNT_FILE, scopes=SCOPES)



#     # """Shows basic usage of the Drive v3 API.
#     # Prints the names and ids of the first 10 files the user has access to.
#     # """
#     # creds = None
#     # # The file token.json stores the user's access and refresh tokens, and is
#     # # created automatically when the authorization flow completes for the first
#     # # time.
#     # if os.path.exists('token.json'):
#     #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # # If there are no (valid) credentials available, let the user log in.
#     # if not creds or not creds.valid:
#     #     if creds and creds.expired and creds.refresh_token:
#     #         creds.refresh(Request())
#     #     else:
#     #         flow = InstalledAppFlow.from_client_secrets_file(
#     #             'credentials.json', SCOPES)
#     #         creds = flow.run_local_server(port=0)
#     #     # Save the credentials for the next run
#     #     with open('token.json', 'w') as token:
#     #         token.write(creds.to_json())


#     service = build('drive', 'v3', credentials=credentials)






#     # try:
#     #     national_parks = ['Yellowstone', 'Rocky Mountains', 'Yosemite']

#     #     for national_park in national_parks:
#     #         File_metadata = {
#     #             'name': national_park,
#     #             'mimeType': 'application/vnd.google-apps.folder'

#     #         }
        
#     #     service.files().create(body=File_metadata).execute()
#     #     print ("files uploaded")

#     # except HttpError as error:
#     #     # TODO(developer) - Handle errors from drive API.
#     #     print(f'An error occurred: {error}')





#     # try:
#     #     response = service.files().list(
#     #         q="name='Personal' and mimeType='application/vnd.google-apps.folder'", spaces='drive'
#     #     ).execute()
#     #     print (response)
#     #     if not response['files']:
#     #         file_metadata = {
#     #             'name': "Backupfolder2022",
#     #             "mimeType": "application/vnd.google-apps.folder"
#     #         }
#     #         file = service.files().create(body=file_metadata, fields="id").execute()
#     #         folder_id = file.get('id')
#     #     else:
#     #         folder_id = response['files'][0]['id']
#     #     for file in os.listdir('data'):
#     #         file_metadata = {
#     #             "name": file,
#     #             "parents": [folder_id]
#     #         }
#     #         media = MediaFileUpload(f"data/{file}")
#     #         upload_file = service.files().create(body=file_metadata,
#     #                                             media_body=media,
#     #                                             fields="id").execute()
#     #         print ("backed up files")


#     # except HttpError as error:
#     #     # TODO(developer) - Handle errors from drive API.
#     #     print(f'An error occurred: {error}')










#     # try:
#     #     # Call the Drive v3 API
#     #     results = service.files().list(
#     #         pageSize=10, fields="nextPageToken, files(id, name)").execute()
#     #     items = results.get('files', [])

#     #     if not items:
#     #         print('No files found.')
#     #         return
#     #     print('Files:')
#     #     for item in items:
#     #         print(u'{0} ({1})'.format(item['name'], item['id']))

#     # except HttpError as error:
#     #     # TODO(developer) - Handle errors from drive API.
#     #     print(f'An error occurred: {error}')





# if __name__ == '__main__':
#     main()



















list_of_all_kpis = ['updated_datetime', 'ticker',
'shortName', 'longBusinessSummary','symbol', 'sector', 'industry', 'country', 'marketCap',  
'returnOnAssets', 'returnOnEquity', 'revenueGrowth', 'revenuePerShare',
'grossMargins', 'operatingMargins', 'profitMargins',  'ebitdaMargins',
'forwardPE', 'trailingPE', 'earningsQuarterlyGrowth', 'earningsGrowth', 'priceToSalesTrailing12Months', 
'trailingEps', 'forwardEps', 
'pegRatio', 'trailingPegRatio',
'currentRatio', 'quickRatio', 'debtToEquity', 
'bookValue', 'enterpriseValue', 'priceToBook', 
'freeCashflow', 'operatingCashflow', 'dividendYield', 'dividendRate', 
'totalRevenue', 'grossProfits', 'ebitda', 'totalDebt', 'beta',
'currency', 'financialCurrency',
'heldPercentInsiders', 'heldPercentInstitutions', 'isEsgPopulated',
'trailingAnnualDividendYield', 'trailingAnnualDividendRate', 'fiveYearAvgDividendYield', 'lastDividendValue', 'lastDividendDate',
'targetMedianPrice',  'targetMeanPrice', 'currentPrice', 
'volume', 'averageVolume', 'averageVolume10days', 'averageDailyVolume10Day',
'longName', 'city', 'address1',
'fiftyTwoWeekHigh',  'shortRatio',  'underlyingSymbol', 'twoHundredDayAverage', 'nextFiscalYearEnd', 
'logo_url',  'regularMarketPreviousClose', 'numberOfAnalystOpinions',  'floatShares', 'fullTimeEmployees', 
'mostRecentQuarter', 'payoutRatio',  'totalCashPerShare', 'sharesShortPriorMonth',  
'sharesOutstanding', 'recommendationMean', 'lastSplitFactor', 'bidSize', 'totalCash', 'dayLow', 'sharesShort', 
'enterpriseToEbitda', 'regularMarketOpen', 'exDividendDate',  'fiftyTwoWeekLow', 'enterpriseToRevenue']







# Advertising Agencies
# Aerospace & Defense
# Agricultural Inputs
# Airlines
# Airports & Air Services
# Aluminum
# Apparel Manufacturing
# Apparel Retail
# Asset Management
# Auto & Truck Dealerships
# Auto Manufacturers
# Auto Manufacturers - Major
# Auto Parts
# Banks—Diversified
# Banks—Regional
# Beverages—Brewers
# Beverages—Non-Alcoholic
# Beverages—Wineries & Distilleries
# Biotechnology
# Broadcasting
# Building Materials
# Building Materials Wholesale
# Building Products & Equipment
# Business Equipment & Supplies
# Capital Markets
# Chemicals
# Coking Coal
# Communication Equipment
# Computer Hardware
# Confectioners
# Conglomerates
# Consulting Services
# Consumer Electronics
# Copper
# Credit Services
# Department Stores
# Diagnostics & Research
# Discount Stores
# Drug Manufacturers—General
# Drug Manufacturers—Specialty & Generic
# Education & Training Services
# Electrical Equipment & Parts
# Electronic Components
# Electronic Gaming & Multimedia
# Electronics & Computer Distribution
# Engineering & Construction
# Entertainment
# Farm & Heavy Construction Machinery
# Farm Products
# Financial Conglomerates
# Financial Data & Stock Exchanges
# Food Distribution
# Footwear & Accessories
# Furnishings, Fixtures & Appliances
# Gambling
# Gold
# Grocery Stores
# Health Information Services
# Healthcare Plans
# Home Improvement Retail
# Household & Personal Products
# Industrial Distribution
# Information Technology Services
# Infrastructure Operations
# Insurance Brokers
# Insurance—Diversified
# Insurance—Life
# Insurance—Property & Casualty
# Insurance—Reinsurance
# Insurance—Specialty
# Integrated Freight & Logistics
# Internet Content & Information
# Internet Retail
# Leisure
# Lodging
# Lumber & Wood Production
# Luxury Goods
# Marine Shipping
# Medical Care Facilities
# Medical Devices
# Medical Distribution
# Medical Instruments & Supplies
# Metal Fabrication
# Mortgage Finance
# Oil & Gas Drilling
# Oil & Gas E&P
# Oil & Gas Equipment & Services
# Oil & Gas Integrated
# Oil & Gas Midstream
# Oil & Gas Refining & Marketing
# Other Industrial Metals & Mining
# Other Precious Metals & Mining
# Packaged Foods
# Packaging & Containers
# Paper & Paper Products
# Personal Services
# Pharmaceutical Retailers
# Pollution & Treatment Controls
# Publishing
# REIT—Diversified
# REIT—Healthcare Facilities
# REIT—Hotel & Motel
# REIT—Industrial
# REIT—Mortgage
# REIT—Office
# REIT—Residential
# REIT—Retail
# REIT—Specialty
# Railroads
# Real Estate Services
# Real Estate—Development
# Real Estate—Diversified
# Recreational Vehicles
# Rental & Leasing Services
# Residential Construction
# Resorts & Casinos
# Restaurants
# Scientific & Technical Instruments
# Security & Protection Services
# Semiconductor Equipment & Materials
# Semiconductors
# Shell Companies
# Silver
# Software—Application
# Software—Infrastructure
# Solar
# Specialty Business Services
# Specialty Chemicals
# Specialty Industrial Machinery
# Specialty Retail
# Staffing & Employment Services
# Steel
# Steel & Iron
# Telecom Services
# Telecom Services - Foreign
# Textile Manufacturing
# Thermal Coal
# Tobacco
# Tools & Accessories
# Travel Services
# Trucking
# Uranium
# Utilities—Diversified
# Utilities—Independent Power Producers
# Utilities—Regulated Electric
# Utilities—Regulated Gas
# Utilities—Regulated Water
# Utilities—Renewable
# Waste Management





# ## CHART DOES NOT MAKE SENSE, YOU NEED TO CHANGE THIS FOR THE MAX RANGE = MIN + MAX VALUE ####
# # #################################################################################################
# # ####### Spider chart ratios of individual industries ###############################################
# # #################################################################################################
# # python -c 'from test import ratios_per_industry_radar; ratios_per_industry_radar()'


# def ratios_per_industry_radar():

#     df = pd.read_csv('dataframe_csv/industry_data.csv', index_col=1)
#     df = df.drop("Unnamed: 0", axis='columns')

#     cols = df.columns.values.tolist()
#     #remove unwanted kpis
#     cols = [i for i in cols if i not in kpi_remove]

#     #collecting the median and max values for comparison
#     maxrange = {}
#     medianrange = {}
#     for i in df.columns.values.tolist():
#         # print (i)
#         dfnew = df[[i]]

#         # # using the MAX for normal kpis and MIN for kpis that are reversed like debt/equity
#         # if kpi_mapping[i] == True:
#         #     dfmax = dfnew.max().values
#         #     maxrange[i] = dfmax[0]
#         # else:
#         #     dfmax = dfnew.min().values
#         #     maxrange[i] = dfmax[0]


#         dfmax = dfnew.max().values
#         maxrange[i] = dfmax[0]

#         # not in using min or max because its median
#         dfmedian = dfnew.median().values
#         medianrange[i] = dfmedian[0]


#     selected_ind = 'Auto Parts'

#     #select all the kpis related to the selected industry for using
#     selected_ind_df = df.loc[df.index == selected_ind]
#     selected_ind_df = selected_ind_df.values.tolist()[0]

#     # lognum = 1.1

#     #normalizing the numbers before inserting them into chart
#     main_df = []
#     median_df = []
#     for i, value in enumerate(maxrange):

#         # if kpi_mapping[value] == True:

#         #     item = selected_ind_df[i] / maxrange[value]
#         #     # item = math.log(item + 1, lognum)
#         #     item = round(item, 3)
#         #     main_df.append(item)

#         # else:

#         #     item = (1/selected_ind_df[i]) / maxrange[value]
#         #     # item = math.log(item + 1, lognum)
#         #     item = round(item, 3)
#         #     main_df.append(item)

#         item = selected_ind_df[i] / maxrange[value]
#         # item = math.log(item + 1, lognum)
#         item = round(item, 3)
#         main_df.append(item)


#         item = medianrange[value] / maxrange[value]
#         # item = math.log(item + 1, lognum)
#         item = round(item, 3)
#         median_df.append(item)

#     # max_range = math.log( 1 + 1 , lognum)
#     max_range = 1

#     fig = go.Figure()

#     fig.add_trace(go.Scatterpolar(
#         r = main_df,
#         theta = cols,
#         fill = 'toself',
#         name = 'Product A'
#     ))

#     fig.add_trace(go.Scatterpolar(
#         r = median_df,
#         theta = cols,
#         fill = 'toself',
#         name = 'Product B'
#     ))

#     fig.update_layout(
#     polar=dict(
#         radialaxis=dict(
#         visible=True,
#         range=[0, max_range]
#         )),
#     showlegend=False
#     )

#     fig.show()