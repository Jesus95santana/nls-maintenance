import os
from dotenv import load_dotenv
from datetime import datetime
import json
from GoogleTest.googleConnect import google_connect, SPREADSHEET_ID, TEMPLATE_SHEET_NAME

load_dotenv()

# Constants
CLICKUP_STATUS = os.getenv("CLICKUP_STATUS_FILTER")

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


def create_or_update_sheet(data):
    title = datetime.now().strftime("%B %Y")
    sheet_id = get_sheet_id_by_name(title)

    if sheet_id is None:
        print(f"Sheet does not exist, creating new sheet: {title}")
        sheet_id = clone_sheet(title, TEMPLATE_SHEET_NAME)
    else:
        print(f"Sheet already exists: {title}")

    if not sheet_id:
        print("Failed to create or retrieve the sheet ID.")
        return

    range_name = f"{title}!A1:E{len(data)}"

    changes = check_for_data_update(sheet_id, range_name, data)

    if changes:
        print("Data has changed. Here are the proposed changes:")
        for row_index, old_row, new_row in changes:
            print(f"Row {row_index + 1} changed from {old_row} to {new_row}")

        confirm = input("Apply all changes? (y) yes / (n) no): ")
        if confirm.lower() == "y":
            for row_index, old_row, new_row in changes:
                row_range = f"{title}!A{row_index + 1}:E{row_index + 1}"
                body = {"values": [new_row]}
                result = (
                    service.spreadsheets()
                    .values()
                    .update(spreadsheetId=SPREADSHEET_ID, range=row_range, valueInputOption="USER_ENTERED", body=body)
                    .execute()
                )
                print(f"Updated row {row_index + 1}")
            print("All changes have been applied.")
        else:
            print("No changes have been applied.")
    else:
        print("No changes detected, no update necessary.")


def check_for_data_update(sheet_id, range_name, new_data):
    try:
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        existing_data = result.get("values", [])
        changed_rows = []

        # Determine the maximum number of columns to ensure all rows are the same length
        max_columns = max(max((len(row) for row in existing_data), default=0), max((len(row) for row in new_data), default=0))

        # Extend each row in existing and new data to max_columns
        normalized_existing_data = [row + [""] * (max_columns - len(row)) for row in existing_data]
        normalized_new_data = [row + [""] * (max_columns - len(row)) for row in new_data]

        for index, (old_row, new_row) in enumerate(zip(normalized_existing_data, normalized_new_data)):
            if old_row != new_row:
                changed_rows.append((index, old_row, new_row))

        return changed_rows
    except Exception as e:
        print(f"Failed to retrieve or compare data: {str(e)}")
        return []  # Return an empty list indicating potential need for updating all data due to an error


def color_formatting(sheet_id, status_column_index, sheet_title):
    # Assuming `CLICKUP_STATUS` contains a JSON string of statuses
    try:
        status_list = json.loads(CLICKUP_STATUS)
    except json.JSONDecodeError:
        print("Failed to decode CLICKUP_STATUS_FILTER. Please check its format.")
        return

    # Defining colors for each status
    status_colors = {
        "Complete": {"red": 0.0, "green": 1.0, "blue": 0.0},  # Green
        status_list[0]: {"red": 0.5, "green": 0.0, "blue": 0.5},  # Purple
        status_list[1]: {"red": 1.0, "green": 1.0, "blue": 0.0},  # Yellow
        status_list[2]: {"red": 0.0, "green": 0.0, "blue": 1.0},  # Blue
    }

    requests = []
    for status, color in status_colors.items():
        requests.append(
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 1,  # Assuming headers are in the first row
                                "endRowIndex": 1000,  # Adjust as necessary
                                "startColumnIndex": status_column_index,
                                "endColumnIndex": status_column_index + 1,
                            }
                        ],
                        "booleanRule": {
                            "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": status}]},
                            "format": {"backgroundColor": color},
                        },
                    },
                    "index": 0,  # Rule priority order
                }
            }
        )

    # Send batchUpdate to apply all formatting rules
    body = {"requests": requests}
    response = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    # print(f"Conditional formatting applied: {response}")


def google_list_formatter(raw_data):
    """
    Formats data from ClickUp API responses for Google Sheets.
    Organizes data hierarchically by folder and list type.

    :param raw_data: Nested list of dictionaries, detailing folders, their lists, and tasks.
    :return: List of lists, where each inner list is a row suitable for Google Sheets.
    """
    formatted_data = [["Folder", "List", "Task Name", "Status"]]

    # Loop through each folder (e.g., Active Plans, Raincastle)
    for folder in raw_data:
        folder_name = folder["name"]
        formatted_data.append([folder_name, "", "", ""])  # Folder row

        # Loop through each list type within the folder (e.g., Monthly Clients, Quarterly Clients)
        for lst in folder["lists"]:
            list_name = lst["name"]
            formatted_data.append(["", list_name, "", ""])  # List type row

            # Loop through each task within the list
            for task in lst["tasks"]:
                task_name = task["name"]
                status = task["status"]
                formatted_data.append(["", "", task_name, status])  # Task detail row

    return formatted_data
