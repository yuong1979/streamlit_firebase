
import pandas as pd
import numpy as np
from google.cloud.firestore import Client
from secret import access_secret
from settings import project_id, firebase_database, fx_api_key, firestore_api_key, google_sheets_api_key, schedule_function_key, firebase_auth_api_key
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account


google_sheets_api_key = access_secret(google_sheets_api_key, project_id)
google_sheets_api_key_dict = json.loads(google_sheets_api_key)
gscredentials = service_account.Credentials.from_service_account_info(google_sheets_api_key_dict)
REQUIRED_SPREADSHEET_ID = '1_lobEzbiuP9TE2UZqmqSAwizT8f2oeuZ8mVuUTbBAsA'
service = build('sheets', 'v4', credentials=gscredentials, cache_discovery=False)
sheet = service.spreadsheets()



# #################################################################################################
# ####### Correlation ###############################################
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