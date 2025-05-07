import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Load environment variables
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_KEY_PATH")
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
NLS_SPREADSHEET_ID = os.getenv("NLS_GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Sheet1")  # Default if not provided
TEMPLATE_SHEET_NAME = os.getenv("GOOGLE_SHEET_TEMPLATE")  # This is the name of the tab to clone

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def google_connect():
    """Create and return a Google Sheets API service object."""
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=credentials)
    return service


def make_nls_request(range_notation: str) -> dict:
    """
    Fetch the given range from the sheet and return the raw JSON response.
    Example range_notation: "'Sheet1'!A1:I"
    """
    service = google_connect()
    sheet = service.spreadsheets()
    try:
        return sheet.values().get(spreadsheetId=NLS_SPREADSHEET_ID, range=range_notation).execute()
    except HttpError as e:
        print("❌ API error on make_request:", e)
        return {}


def test_google_sheet_connection():
    try:
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()

        read_range = f"'{SHEET_NAME}'!A1"
        write_range = f"'{SHEET_NAME}'!A1"

        # Try reading
        read_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=read_range).execute()
        values = read_result.get("values", [])
        print("✅ Read test passed. Value at A1:", values[0][0] if values else "[empty]")

        # Try writing
        test_value = [["✅ Connection Successful"]]
        body = {"values": test_value}
        write_result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=write_range, valueInputOption="USER_ENTERED", body=body).execute()
        print(f"✅ Write test passed. {write_result.get('updatedCells')} cell(s) updated.")
    except HttpError as e:
        print("❌ Google Sheets API error:", e)
    except Exception as e:
        print("❌ An error occurred:", e)
