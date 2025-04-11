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


def create_or_notify_sheet(data):
    """
    Creates a new Google Sheet from a template if it does not exist for the current month,
    or updates it if it already exists.
    :param data: The data to be written to the Google Sheet.
    """
    title = datetime.now().strftime("%B %Y")  # Automatically generate the title as "Month Year"
    sheet_id = get_sheet_id_by_name(title)

    if sheet_id is None:
        print(f"Sheet does not exist, creating new sheet: {title}")
        sheet_id = clone_sheet(title, TEMPLATE_SHEET_NAME)
    else:
        print(f"Sheet already exists: {title}")

    print("Updating Sheet With Clickup Data")
    new_sheet_id = get_sheet_id_by_name(title)

    # Assuming sheet_id is correctly returned from the clone_sheet function
    if new_sheet_id:
        # print(data)
        range_name = f"'{title}'!A1"  # Adjust if your data should start elsewhere
        body = {"values": data}
        result = (
            service.spreadsheets()
            .values()
            .update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption="USER_ENTERED", body=body)
            .execute()
        )
        print(f"{result.get('updatedCells')} cells updated.")
    else:
        print("Failed to update sheet.")


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
