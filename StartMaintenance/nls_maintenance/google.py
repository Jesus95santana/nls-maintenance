import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import difflib
from GoogleTest.googleConnect import google_connect, make_nls_request, NLS_SPREADSHEET_ID, TEMPLATE_SHEET_NAME

load_dotenv()

# Constants
NLS_GOOGLE_STATUS = os.getenv("NLS_GOOGLE_STATUS_FILTER")

service = google_connect()

#
#
#
# Listing & Displaying
#
#
#


def return_list_all_sites(values: list[list[str]]) -> str:
    """
    Given the `values` list from Sheets API (first row = headers),
    produce a text outline of:

    Folder: {Folder_Name}
      List: {List_Name}
          - {Site_Name} ({Status})
    """
    lines = []
    current_folder = None
    current_list = None

    # skip header
    for row in values[1:]:
        # new Folder row: only A is filled
        if len(row) >= 1 and row[0] and len(row) == 1:
            current_folder = row[0]
            lines.append(f"Folder: {current_folder}")
            current_list = None
            continue

        # new List row: A and B filled, but no site
        if len(row) >= 2 and row[1] and len(row) == 2:
            current_list = row[1]
            lines.append(f"  List: {current_list}")
            continue

        # site row: A, B, C at minimum; status in D if present
        if len(row) >= 3:
            site = row[2]
            status = row[3] if len(row) >= 4 else ""
            lines.append(f"      - {site} ({status})")
            continue

        # anything else (empty rows) we skip
    output = "\n".join(lines)
    print(output)
    return output


def get_sheet_id_by_name(sheet_name):
    # Fetch the list of sheets in the spreadsheet
    sheet_metadata = service.spreadsheets().get(spreadsheetId=NLS_SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get("sheets", "")

    # Search for the sheet ID based on the provided name
    for sheet in sheets:
        if sheet["properties"]["title"] == sheet_name:
            return sheet["properties"]["sheetId"]
    return None


def get_previous_month_title() -> str:
    """
    Returns a string like "May 2025" for the month prior to today.
    """
    today = datetime.now()
    # Move to the first of this month, then subtract one day → last day of prev month
    first_of_this_month = today.replace(day=1)
    last_of_prev_month = first_of_this_month - timedelta(days=1)
    return last_of_prev_month.strftime("%B %Y")


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
        response = service.spreadsheets().batchUpdate(spreadsheetId=NLS_SPREADSHEET_ID, body=body).execute()
        new_sheet_id = response["replies"][0]["duplicateSheet"]["properties"]["sheetId"]
        print(f"Cloned sheet with title: {title}, Sheet ID: {new_sheet_id}")
        return new_sheet_id
    except Exception as e:
        print(f"Failed to clone the sheet: {e}")
        return None


def insert_and_fill_row(sheet_id, row_index, new_row_values):
    """
    Inserts a blank row at `row_index` (zero–based) in the sheet with ID sheet_id,
    then writes new_row_values into columns A–D of that row.
    """
    requests = [
        # 1) insert a blank row
        {
            "insertDimension": {
                "range": {"sheetId": sheet_id, "dimension": "ROWS", "startIndex": row_index, "endIndex": row_index + 1},
                "inheritFromBefore": False,
            }
        },
        # 2) write the A–D values into that new row
        {
            "updateCells": {
                "start": {
                    "sheetId": sheet_id,
                    "rowIndex": row_index,
                    "columnIndex": 0,  # column A
                },
                "rows": [{"values": [{"userEnteredValue": {"stringValue": str(v)}} for v in new_row_values]}],
                "fields": "userEnteredValue",
            }
        },
    ]

    body = {"requests": requests}
    service.spreadsheets().batchUpdate(spreadsheetId=NLS_SPREADSHEET_ID, body=body).execute()


#
def create_nls_sheet(columns_to_clone: list[str]) -> int | None:
    """
    Ensure that a sheet for the current month exists. If it does not:
      1. Duplicate your TEMPLATE_SHEET_NAME → current_month_title.
      2. If a previous-month sheet exists, fetch its data and copy ONLY the columns
         in `columns_to_clone` into the new sheet (leaving all other columns blank).

    Returns:
      - The sheetId of the existing or newly created sheet on success,
      - None if we failed to create/get it.
    """
    # 1) Determine this month’s and last month’s titles
    current_title = datetime.now().strftime("%B %Y")
    prev_title = get_previous_month_title()

    # 2) If “current month” already exists, just return its ID:
    existing = get_sheet_id_by_name(current_title)
    if existing is not None:
        print(f"🔍 Sheet '{current_title}' already exists (ID={existing}).")
        return existing

    # 3) Duplicate the TEMPLATE sheet → new sheet called “current_title”
    print(f"✂️  Creating new sheet by cloning template: '{TEMPLATE_SHEET_NAME}' → '{current_title}'")
    new_sheet_id = clone_sheet(current_title, TEMPLATE_SHEET_NAME)
    if new_sheet_id is None:
        print("❌ Could not duplicate the template sheet. Aborting.")
        return None

    # 4) If last month’s sheet exists, pull its values and copy only desired columns:
    prev_id = get_sheet_id_by_name(prev_title)
    if prev_id is None:
        print(f"ℹ️ No sheet named '{prev_title}' found. Leaving '{current_title}' with just the template headers.")
        return new_sheet_id

    # 5) Read ALL values from last month’s sheet:
    #    We assume at most, say, columns A→Z (you can adjust the range if you have more columns).
    prev_range = f"'{prev_title}'!A1:Z1000"
    prev_result = service.spreadsheets().values().get(spreadsheetId=NLS_SPREADSHEET_ID, range=prev_range).execute()
    prev_values = prev_result.get("values", [])
    if not prev_values:
        print(f"⚠️ '{prev_title}' is empty. No data to copy.")
        return new_sheet_id

    # 6) Determine which column-indices in row 1 we want to copy:
    header_row = prev_values[0]
    # Build a mapping: header name → its zero‐based index in prev sheet
    header_to_index = {h: i for i, h in enumerate(header_row)}

    # Make a list of zero‐based indices of columns we want to clone. If a column in
    # columns_to_clone doesn’t appear in header, we’ll skip it (but still leave that column blank).
    cols_indices: list[int] = []
    for col_name in columns_to_clone:
        if col_name in header_to_index:
            cols_indices.append(header_to_index[col_name])
        else:
            print(f"⚠️ Column '{col_name}' not found in '{prev_title}' header; skipping it.")

    if not cols_indices:
        print("⚠️ None of the requested columns were found in the previous sheet. Nothing to copy.")
        return new_sheet_id

    # 7) Build a new “partial” data‐array for ALL rows of last month—but only in the chosen columns.
    #    We will preserve the full header, but for data‐rows we blank out everything except the chosen columns.
    max_cols = len(header_row)
    new_data: list[list[str]] = []

    # Row 1 in the new sheet should be exactly the same header as template (which we assume matches prev header),
    # so let’s copy header_row into new_data[0]:
    new_data.append(header_row)

    # For rows 2…N in prev_values, we copy only chosen columns; other columns become "".
    for old_row in prev_values[1:]:
        # Pad old_row to the full width so indexing doesn’t break:
        padded_old = old_row + [""] * (max_cols - len(old_row))

        # Re‐build a new row of length=max_cols:
        new_row = []
        for col_idx in range(max_cols):
            if col_idx in cols_indices:
                new_row.append(padded_old[col_idx])
            else:
                new_row.append("")  # leave blank
        new_data.append(new_row)

    # 8) Write new_data into the newly created sheet (current_title).
    #    We need a range cover from A1 to however many rows/columns we have.
    num_rows = len(new_data)
    num_cols = max_cols

    # Convert num_cols to column letter. E.g. 1 → A, 2 → B, … 26→Z, 27→AA
    def _column_letter(n: int) -> str:
        result = ""
        while n > 0:
            n, rem = divmod(n - 1, 26)
            result = chr(65 + rem) + result
        return result

    last_col_letter = _column_letter(num_cols)  # e.g. “I” if max_cols==9

    write_range = f"'{current_title}'!A1:{last_col_letter}{num_rows}"
    body = {"values": new_data}

    service.spreadsheets().values().update(
        spreadsheetId=NLS_SPREADSHEET_ID,
        range=write_range,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()

    print(f"✅ Created '{current_title}' (sheetId={new_sheet_id}) and copied columns {columns_to_clone} from '{prev_title}'.")
    return new_sheet_id

    # 6) formatting
    # print("All changes have been applied.")
    # print("Applying conditional formatting…")
    # color_formatting(sheet_id, 3, title)


def compute_row_diffs(old_rows, new_rows):
    """
    Returns a list of tuples:
        ('insert',  old_index,  new_rows_slice)
        ('delete', old_rows_slice, new_index)
        ('replace', old_index, new_row)
    """
    # convert each row-list to a tuple so they become hashable
    hashable_old = [tuple(r) for r in old_rows]
    hashable_new = [tuple(r) for r in new_rows]
    sm = difflib.SequenceMatcher(None, hashable_old, hashable_new)
    diffs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "insert":
            # new_rows[j1:j2] were inserted at position i1
            diffs.append(("insert", i1, new_rows[j1:j2]))
        elif tag == "delete":
            # old_rows[i1:i2] were deleted
            diffs.append(("delete", old_rows[i1:i2], i1))
        elif tag == "replace":
            # rows i1..i2 replaced by j1..j2
            # we’ll treat each replaced row as a separate diff
            length = max(i2 - i1, j2 - j1)
            for k in range(length):
                old = old_rows[i1 + k] if i1 + k < i2 else None
                new = new_rows[j1 + k] if j1 + k < j2 else None
                diffs.append(("replace", i1 + k, old, new))
    return diffs


def check_for_data_update(sheet_id, range_name, new_data):
    try:
        result = service.spreadsheets().values().get(spreadsheetId=NLS_SPREADSHEET_ID, range=range_name).execute()
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


def hex_to_rgb_norm(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return {"red": r / 255.0, "green": g / 255.0, "blue": b / 255.0}


def color_formatting(sheet_id, status_column_index, sheet_title):
    # Assuming `NLS_GOOGLE_STATUS` contains a JSON string of statuses
    try:
        status_list = json.loads(NLS_GOOGLE_STATUS)
    except json.JSONDecodeError:
        print("Failed to decode NLS_GOOGLE_STATUS_FILTER. Please check its format.")
        return

    # Defining colors for each status
    PURPLE = hex_to_rgb_norm("#cb8ccb")
    YELLOW = hex_to_rgb_norm("#ffff00")
    CYAN = hex_to_rgb_norm("#00ffff")
    GREEN = hex_to_rgb_norm("00ff00")
    RED = hex_to_rgb_norm("ea4335")
    CORNBLUE = hex_to_rgb_norm("4285f4")
    status_colors = {
        "complete": GREEN,  # Green
        status_list[0]: CYAN,  # Blue
        status_list[1]: PURPLE,  # Purple
        status_list[2]: YELLOW,  # Yellow
        status_list[3]: CYAN,
        status_list[4]: CORNBLUE,
        status_list[-1]: RED,
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
    response = service.spreadsheets().batchUpdate(spreadsheetId=NLS_SPREADSHEET_ID, body=body).execute()
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
            formatted_data.append([folder_name, list_name, "", ""])  # List type row

            # sort the tasks by lower-cased name
            for task in sorted(lst["tasks"], key=lambda t: t["name"].lower()):
                task_name = task["name"]
                status = task["status"]
                formatted_data.append([folder_name, list_name, task_name, status])

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
        result = service.spreadsheets().values().get(spreadsheetId=NLS_SPREADSHEET_ID, range=range_name).execute()
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
            spreadsheetId=NLS_SPREADSHEET_ID, range=f"{title}!{cell_address}", valueInputOption="USER_ENTERED", body=body
        ).execute()

        # Apply color formatting based on the data
        color = determine_background_color(data, column_name)
        apply_background_color(NLS_SPREADSHEET_ID, cell_address, color)

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


def apply_background_color(NLS_SPREADSHEET_ID, cell_address, color):
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
    response = service.spreadsheets().batchUpdate(spreadsheetId=NLS_SPREADSHEET_ID, body=body).execute()
    print("Background color applied:", response)


def column_to_index(column):
    """Convert a column letter (e.g., 'A') into its corresponding index (e.g., 1)."""
    return sum((ord(char) - 64) * (26**idx) for idx, char in enumerate(reversed(column.upper())))
