import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Load environment variables
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_KEY_PATH')
SPREADSHEET_ID = os.getenv('GOOGLE_SHEET_ID')
SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME', 'Sheet1')  # Default if not provided

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def test_google_sheet_connection():
    try:
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        read_range = f"'{SHEET_NAME}'!A1"
        write_range = f"'{SHEET_NAME}'!A1"

        # Try reading
        read_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=read_range).execute()
        values = read_result.get('values', [])
        print("✅ Read test passed. Value at A1:", values[0][0] if values else "[empty]")

        # Try writing
        test_value = [["✅ Connection Successful"]]
        body = {'values': test_value}
        write_result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID, range=write_range,
            valueInputOption='USER_ENTERED', body=body).execute()
        print(f"✅ Write test passed. {write_result.get('updatedCells')} cell(s) updated.")
    except HttpError as e:
        print("❌ Google Sheets API error:", e)
    except Exception as e:
        print("❌ An error occurred:", e)
