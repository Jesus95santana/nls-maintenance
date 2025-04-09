from datetime import datetime
from GoogleTest.googleConnect import google_connect, SPREADSHEET_ID, TEMPLATE_SHEET_NAME

service = google_connect()


def get_sheet_id_by_name(sheet_name):
    # Fetch the list of sheets in the spreadsheet
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get("sheets", "")

    # Search for the sheet ID based on the provided name
    for sheet in sheets:
        if sheet["properties"]["title"] == sheet_name:
            return sheet["properties"]["sheetId"]
    return None


def clone_sheet(title, source_sheet_name):
    source_sheet_id = get_sheet_id_by_name(source_sheet_name)
    if source_sheet_id is None:
        print(f"No sheet found with the name {source_sheet_name}")
        return

    # Clone the specified sheet to a new one with the specified title
    body = {
        "requests": [
            {
                "duplicateSheet": {
                    "sourceSheetId": source_sheet_id,
                    "newSheetName": title,
                }
            }
        ]
    }
    response = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"Cloned sheet with title: {title}")


def create_or_notify_sheet():
    # Automatically generate the title as "Month Year"
    title = datetime.now().strftime("%B %Y")  # e.g., "March 2025"

    # Check if a sheet with this title already exists
    if get_sheet_id_by_name(title):
        print(f"Sheet already exists: {title}")
    else:
        # Clone a new sheet from the template since it doesn't exist
        clone_sheet(title, TEMPLATE_SHEET_NAME)
