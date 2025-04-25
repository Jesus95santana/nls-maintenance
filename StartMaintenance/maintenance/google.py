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
        return None

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
    try:
        response = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        new_sheet_id = response["replies"][0]["duplicateSheet"]["properties"]["sheetId"]
        print(f"Cloned sheet with title: {title}, Sheet ID: {new_sheet_id}")
        return new_sheet_id
    except Exception as e:
        print(f"Failed to clone the sheet: {e}")
        return None


#
def create_or_update_sheet(data):
    title = datetime.now().strftime("%B %Y")
    sheet_id = get_sheet_id_by_name(title)

    if sheet_id is None:
        print(f"Sheet does not exist, creating new sheet: {title}")
        sheet_id = clone_sheet(title, TEMPLATE_SHEET_NAME)
        if sheet_id is None:
            print("Failed to create or retrieve the sheet ID.")
            return
        # Since the sheet is new, insert all data directly without checking for changes
        range_name = f"{title}!A1:J{len(data)}"  # Ensure range covers all necessary columns and rows
        body = {"values": data}
        try:
            result = (
                service.spreadsheets()
                .values()
                .update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption="USER_ENTERED", body=body)
                .execute()
            )
            print("New sheet populated with initial data.")
            print("Applying conditional formatting...")
            color_formatting(sheet_id, 3, title)  # Apply formatting
        except Exception as e:
            print(f"Failed to populate new sheet: {e}")
    else:
        print(f"Sheet already exists: {title}")
        # Existing sheet logic to check and update changes
        range_name = f"{title}!A1:J{len(data)}"  # Adjust range to fit data
        changes = check_for_data_update(sheet_id, range_name, data)
        if changes:
            print("Data has changed. Here are the proposed changes:")
            for row_index, old_row, new_row in changes:
                print(f"Row {row_index + 1} changed from {old_row} to {new_row}")

            confirm = input("Apply all changes? (y) yes / (n) no): ")
            if confirm.lower() == "y":
                for row_index, old_row, new_row in changes:
                    row_range = f"{title}!A{row_index + 1}:J{row_index + 1}"
                    body = {"values": [new_row]}
                    service.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID, range=row_range, valueInputOption="USER_ENTERED", body=body
                    ).execute()
                    print(f"Updated row {row_index + 1}")
                print("All changes have been applied.")
                print("Applying conditional formatting...")
                color_formatting(sheet_id, 3, title)  # Apply formatting

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
        "complete": {"red": 0.0, "green": 1.0, "blue": 0.0},  # Green
        status_list[1]: {"red": 0.0, "green": 0.0, "blue": 1.0},  # Blue
        status_list[2]: {"red": 0.5, "green": 0.0, "blue": 0.5},  # Purple
        status_list[3]: {"red": 1.0, "green": 1.0, "blue": 0.0},  # Yellow
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
    formatted_data = [
        ["Folder", "List", "Task Name", "Status", "Plugins Updated", "Footer 2025", "DNS Check", "Slider Rev Update", "Broken Links", "Notes"]
    ]

    # Loop through each folder (e.g., Active Plans, Raincastle)
    for folder in raw_data:
        folder_name = folder["name"]
        formatted_data.append([folder_name, "", "", ""])  # Folder row

        # Loop through each list type within the folder (e.g., Monthly Clients, Quarterly Clients)
        for lst in folder["lists"]:
            list_name = lst["name"]
            formatted_data.append([folder_name, list_name, "", ""])  # List type row

            # Loop through each task within the list
            for task in lst["tasks"]:
                task_name = task["name"]
                status = task["status"]
                formatted_data.append([folder_name, list_name, task_name, status])  # Task detail row

    return formatted_data


#
#
#
# Maintenance & Modifying
#
#
#


def update_google_sheet(site_name, data, column_name):
    service = google_connect()
    title = datetime.now().strftime("%B %Y")
    sheet_id = get_sheet_id_by_name(title)

    if not sheet_id:
        print(f"No sheet found for {title}. Please check the sheet name.")
        return

    range_name = f"{title}!A1:Z1000"
    try:
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        values = result.get("values", [])

        if not values:
            print("The sheet is empty or the range is incorrect.")
            return

        if len(values[0]) < 3:
            print("Header does not contain enough columns.")
            return

        header = values[0]
        try:
            column_index = header.index(column_name) + 1
        except ValueError:
            print(f"Column {column_name} not found.")
            return

        row_number = None
        for i, row in enumerate(values, start=1):
            if len(row) > 2 and row[2].strip().lower() == site_name.strip().lower():
                row_number = i
                break

        if row_number is None:
            print(f"Site name '{site_name}' not found in the sheet.")
            return

        if not data:
            data = "Incomplete"

        cell_address = f"{get_column_letter(column_index)}{row_number}"
        body = {"values": [[data]], "range": f"{title}!{cell_address}", "majorDimension": "ROWS"}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=f"{title}!{cell_address}", valueInputOption="USER_ENTERED", body=body
        ).execute()

        # Apply color formatting based on the data
        color = determine_background_color(data, column_name)
        apply_background_color(SPREADSHEET_ID, cell_address, color)

    except Exception as e:
        print(f"An error occurred: {e}")


def get_column_letter(column_index):
    """Converts an index to a column letter (e.g., 1 -> 'A', 2 -> 'B', ... 27 -> 'AA')."""
    result = ""
    while column_index > 0:
        column_index, remainder = divmod(column_index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def determine_background_color(data, column_name):
    if not isinstance(data, str):
        data = str(data)  # Ensure we are working with a string

    lowered = data.strip().lower()

    if lowered == "incomplete":
        # Light Red
        return {"red": 1.0, "green": 0.6, "blue": 0.6}
    elif lowered == "n/a" or lowered == "0":
        # Light Blue
        return {"red": 0.7, "green": 0.85, "blue": 1.0}
    elif "done" in lowered:
        # Green
        return {"red": 0.0, "green": 1.0, "blue": 0.0}
    elif lowered.isdigit():
        # Numeric, treat as success (green)
        return {"red": 0.0, "green": 1.0, "blue": 0.0}
    else:
        # Default to Yellow (for unknown but non-critical values)
        return {"red": 1.0, "green": 1.0, "blue": 0.0}


def apply_background_color(spreadsheet_id, cell_address, color):
    service = google_connect()
    title = datetime.now().strftime("%B %Y")
    sheet_id = get_sheet_id_by_name(title)
    # Parse column letter and row number from cell_address
    column_letter = "".join(filter(str.isalpha, cell_address))
    row_number = "".join(filter(str.isdigit, cell_address))

    if not sheet_id:
        print(f"No sheet found with the title '{title}'.")
        return

    # Construct the request body for updating cell format
    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": int(row_number) - 1,  # Convert to zero-based index
                    "endRowIndex": int(row_number),
                    "startColumnIndex": column_to_index(column_letter) - 1,
                    "endColumnIndex": column_to_index(column_letter),
                },
                "cell": {"userEnteredFormat": {"backgroundColor": color}},
                "fields": "userEnteredFormat.backgroundColor",
            }
        }
    ]

    body = {"requests": requests}

    # Send the request to the Sheets API
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    print("Background color applied:", response)


def column_to_index(column):
    """Convert a column letter (e.g., 'A') into its corresponding index (e.g., 1)."""
    return sum((ord(char) - 64) * (26**idx) for idx, char in enumerate(reversed(column.upper())))
