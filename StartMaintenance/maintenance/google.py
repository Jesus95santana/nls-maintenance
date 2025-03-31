import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Set the path to your service account key file
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_KEY_PATH')

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Authenticate and construct service
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# ID of the Google Sheet
spreadsheet_id = os.getenv('GOOGLE_SHEET_ID')

# Example of reading from the spreadsheet
def read_sheet(range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            print(row)

# Example of writing to the spreadsheet
def write_sheet(range_name, values):
    body = {'values': values}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='USER_ENTERED', body=body).execute()
    print(f"{result.get('updatedCells')} cells updated.")

# Usage
# read_sheet('March 2025!A1:E10')
# write_sheet('Sheet1!A12', [['Hello', 'World']])
