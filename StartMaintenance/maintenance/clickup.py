import os
from dotenv import load_dotenv
import json
import re
from datetime import datetime
import requests
import whois
from ClickupTest.clickupConnect import make_request, CLICKUP_BASE_URL

from .google import update_google_sheet

_latest_wp_version = None

load_dotenv()

# Constants
USER = os.getenv("CLICKUP_USER_ID")
STATUS = os.getenv("CLICKUP_STATUS_FILTER")
TEAM = os.getenv("CLICKUP_TEAM_ID")


#
#
#
# Listing & Displaying
#
#
#


def fetch_shared_folders(team_id):
    """
    Fetches shared folders from a specific ClickUp team.
    :param team_id: The ID of the team in ClickUp.
    :return: None
    """
    url = f"{CLICKUP_BASE_URL}/team/{team_id}/shared"
    response = make_request(url)
    if response and "shared" in response and "folders" in response["shared"]:
        folders = response["shared"]["folders"]
        print("Shared Folders:")
        for index, folder in enumerate(folders):
            print(f"{index + 1}: {folder['name']} (ID: {folder['id']})")

        # Prompt user to select a folder
        folder_index = int(input("Enter the number of the folder you want to work on: ")) - 1
        if 0 <= folder_index < len(folders):
            selected_folder = folders[folder_index]
            print(f"You selected: {selected_folder['name']} (ID: {selected_folder['id']})")
            return selected_folder
        else:
            print("Invalid selection.")
            return None
    else:
        print("No shared folders found or failed to fetch folders.")
        return None


def list_folder_lists(folder):
    """
    Lists the lists within the selected folder.
    :param folder: The folder dictionary containing details and lists.
    :return: None
    """
    lists = folder.get("lists", [])
    if lists:
        print("Lists in the selected folder:")
        for lst in lists:
            print(f"- {lst['name']} (ID: {lst['id']}), Task Count: {lst['task_count']}")
    else:
        print("No lists found in the selected folder.")


def fetch_all_tasks_by_folder(team_id):
    """
    Fetches all tasks grouped by lists in each folder for a given team.
    :param team_id: The ID of the team in ClickUp.
    :return: None
    """
    url = f"{CLICKUP_BASE_URL}/team/{team_id}/shared"
    response = make_request(url)
    if response and "shared" in response and "folders" in response["shared"]:
        folders = response["shared"]["folders"]
        for folder in folders:
            # print(f"\nFolder: {folder['name']} (ID: {folder['id']})")
            print(f"\nFolder: {folder['name']}")
            for lst in folder["lists"]:
                # print(f"  List: {lst['name']} (ID: {lst['id']})")
                print(f"  List: {lst['name']}")
                list_sites(lst["id"], [USER])  # Based On Assigned Clickup User
    else:
        print("Failed to fetch folders or no folders found.")


def list_sites(list_id, assignee_ids):
    """
    Fetches tasks from a specific ClickUp list filtered by assignee IDs and statuses.
    :param list_id: The ID of the list in ClickUp.
    :param assignee_ids: List of assignee IDs to filter tasks.
    :return: None
    """
    # Load the CLICKUP_STATUS_FILTER from the environment and format it for the URL
    status_filter = os.getenv("CLICKUP_STATUS_FILTER", "[]")
    # Evaluating the string to a list
    status_filter = eval(status_filter)
    # Forming the status part of the URL
    statuses = "&".join([f"statuses[]={status}" for status in status_filter])

    # Forming the assignee part of the URL
    assignees = "&".join([f"assignees[]={id}" for id in assignee_ids])

    # Constructing the URL with both statuses and assignees
    url = f"{CLICKUP_BASE_URL}/list/{list_id}/task?{assignees}&{statuses}"

    # Making the request to the ClickUp API
    response = make_request(url)

    if response and "tasks" in response:
        # Output tasks with their names and statuses
        for task in response["tasks"]:
            task_status = task.get("status", {}).get("status", "No status found")
            print(f"      - {task['name']} (Status: {task_status})")
    else:
        print("    No tasks found or failed to fetch tasks for List ID:", list_id)


def return_fetch_all_tasks_by_folder(team_id):
    print("Retrieving Clickup Data")
    """
    Fetches all tasks grouped by lists in each folder for a given team.
    :param team_id: The ID of the team in ClickUp.
    :return: List of all folders and their lists with tasks.
    """
    url = f"{CLICKUP_BASE_URL}/team/{team_id}/shared"
    response = make_request(url)
    all_folders_data = []
    if response and "shared" in response and "folders" in response["shared"]:
        folders = response["shared"]["folders"]
        for folder in folders:
            folder_data = {"name": folder["name"], "lists": []}
            for lst in folder["lists"]:
                list_data = {"name": lst["name"], "tasks": return_list_sites(lst["id"], [USER])}
                folder_data["lists"].append(list_data)
            all_folders_data.append(folder_data)
    return all_folders_data


def return_list_sites(list_id, assignee_ids):
    """
    Fetches tasks from a specific ClickUp list filtered by assignee IDs and statuses.
    :param list_id: The ID of the list in ClickUp.
    :param assignee_ids: List of assignee IDs to filter tasks.
    :return: List of dictionaries, each representing a task.
    """
    status_filter = os.getenv("CLICKUP_STATUS_FILTER", "[]")
    status_filter = eval(status_filter)  # Consider safety or alternatives like json.loads if possible
    statuses = "&".join([f"statuses[]={status}" for status in status_filter])
    assignees = "&".join([f"assignees[]={id}" for id in assignee_ids])
    url = f"{CLICKUP_BASE_URL}/list/{list_id}/task?{assignees}&{statuses}"

    response = make_request(url)
    if response and "tasks" in response:
        return [{"name": task["name"], "status": task.get("status", {}).get("status", "No status found")} for task in response["tasks"]]
    else:
        return []


#
#
#
# Maintenance & Modifying
#
#
#


def list_folders():
    url = f"{CLICKUP_BASE_URL}/team/{TEAM}/shared"
    response = make_request(url)  # Ensure make_request returns the API response

    # Access the nested 'folders' key inside 'shared'
    if response and "shared" in response and "folders" in response["shared"]:
        folders = response["shared"]["folders"]
        if folders:
            print("\nAvailable folders:")
            for index, folder in enumerate(folders):
                print(f"{index + 1}. Folder: {folder['name']}")
            return folders
        else:
            print("No folders found.")
            return None
    else:
        print("No folders found or there was an error fetching folders.")
        return None


def list_lists(folder_id):
    url = f"{CLICKUP_BASE_URL}/folder/{folder_id}/list"  # Make sure the endpoint is correct
    response = make_request(url)

    # You need to assign the response from make_request to a variable, typically 'response' is used
    if response and "lists" in response:
        lists = response["lists"]
        if lists:
            print("\nLists in the selected folder:")
            for index, lst in enumerate(lists):  # Avoid using 'list' as it shadows a built-in
                print(f"{index + 1}. List Name: {lst['name']}")
            return lists
        else:
            print("No lists found.")
            return None
    else:
        print("No lists found or there was an error fetching lists.")
        return None


def list_sites_maintenance(list_id, assignee_ids=[USER]):
    """
    Fetches tasks from a specific ClickUp list filtered by assignee IDs and statuses.
    """
    try:
        status_filter = json.loads(os.getenv("CLICKUP_STATUS_FILTER", "[]"))
    except json.JSONDecodeError:
        print("Error decoding the CLICKUP_STATUS_FILTER. Please check its format.")
        return []

    statuses = "&".join(f"statuses[]={status}" for status in status_filter)
    assignees = "&".join(f"assignees[]={id}" for id in assignee_ids)
    url = f"{CLICKUP_BASE_URL}/list/{list_id}/task?{assignees}&{statuses}"

    response = make_request(url)
    if response and "tasks" in response:
        tasks = response["tasks"]
        if tasks:
            print(f"Tasks in List ID {list_id}:")
            for index, task in enumerate(tasks, start=1):  # Start numbering from 1
                task_status = task.get("status", {}).get("status", "No status found")
                print(f"{index}. {task['name']} (Status: {task_status})")
        else:
            print(f"No tasks found for List ID {list_id}.")
        return tasks
    else:
        print(f"Failed to fetch tasks for List ID {list_id}.")
        return []


def get_task(task_id):
    url = f"{CLICKUP_BASE_URL}/task/{task_id}"
    try:
        response = make_request(url)  # Ensure make_request returns the API response properly
        if response:
            # Directly return the response if it does not use a 'task' key
            return response
        else:
            print(f"No response or invalid response received from API for Task ID {task_id}.")
    except Exception as e:
        print(f"An error occurred while fetching task: {e}")
    return None


def display_task_details(task):
    fields_to_display = {
        "1. Broken Links Report": "Broken Links Report",
        "2. Date Completed": "Date Completed",
        "3. Date for Email Subject Line (Month & Year)": "Date for Email Subject Line (Month & Year)",
        "4. Website URL": "Website URL",
        "5. WordPress Version": "WordPress Version",
        "6. Notes for Maintenance": "Notes for Maintenance Report",
        "7. Number of Plugins Updated": "Number of Plugins Updated",
        "8. Domain Expiration": "Domain Expiration",
    }

    for key, field_name in fields_to_display.items():
        value = get_custom_field_value(task, field_name)

        if key == "6. Notes for Maintenance":
            print("{:<50} {}".format(key + ":", value))
            analyze_notes_for_maintenance(task, value)  # Show subitems like 6.1, 6.2
        else:
            print("{:<50} {}".format(key + ":", value))


def analyze_notes_for_maintenance(task, notes_text):
    current_year = str(datetime.now().year)
    current_month = str(datetime.now().month).zfill(2)  # Ensure "04" instead of "4"

    lines = notes_text.splitlines()
    footer_status = "Empty"
    slider_status = "Empty"

    for line in lines:
        lower_line = line.lower()

        # === Footer Check ===
        if "footer" in lower_line:
            if current_year in line:
                footer_status = "✅ Updated"
            else:
                footer_status = "❌ Outdated"

        # === Slider Check ===
        if "slider" in lower_line:
            if current_month in line:
                slider_status = "✅ Updated"
            else:
                slider_status = "❌ Outdated"

    print("{:<50} {}".format("      6.1 Footer updated this year:", footer_status))
    print("{:<50} {}".format("      6.2 Slider Revolution updated:", slider_status))
    note_values = [footer_status, slider_status]
    return note_values


# def format_date(timestamp):
#     """Convert Unix timestamp (in milliseconds) to a human-readable date."""
#     if timestamp is not None:
#         # Convert milliseconds to seconds
#         timestamp = int(timestamp) / 1000
#         return datetime.utcfromtimestamp(timestamp).strftime("%m/%d/%Y")
#     return "Not specified"


def show_broken_links(task, passed, failed):
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    for field in task.get("custom_fields", []):
        if field["name"] == "Broken Links Report":
            attachments = field.get("value", [])
            if not attachments:
                return "Empty"  # No prefix if nothing has been uploaded

            try:
                most_recent_report = attachments[0]
                report_date_ms = int(most_recent_report["date"])
                report_date = datetime.utcfromtimestamp(report_date_ms / 1000)

                prefix = passed if (report_date.year == current_year and report_date.month == current_month) else failed

                return prefix + report_date.strftime("%m|%d|%Y")
            except (KeyError, ValueError, IndexError):
                return failed + "Invalid Report Format"

    return failed + "Field Not Found"


def get_latest_wp_version():
    global _latest_wp_version
    if _latest_wp_version:
        return _latest_wp_version
    try:
        response = requests.get("https://api.wordpress.org/core/version-check/1.7/")
        response.raise_for_status()
        data = response.json()
        _latest_wp_version = data["offers"][0]["current"]
        return _latest_wp_version
    except Exception as e:
        return None


def get_dns_expiry(domain):
    """Retrieve the domain expiration date using WHOIS."""
    try:
        domain_info = whois.whois(domain)
        expiration_date = domain_info.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        return expiration_date
    except Exception as e:
        return None  # fail silently for now


def get_custom_field_value(task, field_name, debug=False):
    passed = "✅ Updated | "
    failed = "❌ Outdated | "

    if field_name == "Broken Links Report":
        return show_broken_links(task, passed, failed)

    # Loop once through all custom fields
    for field in task.get("custom_fields", []):
        if field.get("name") != field_name:
            continue

        value = field.get("value", "Not specified")

        # === Special Case: Date Completed ===
        if field_name == "Date Completed":
            if debug:
                print("RAW Date Completed value:", value)

            try:
                # ClickUp provides timestamp in ms
                timestamp = int(value) / 1000
                completed_date = datetime.fromtimestamp(timestamp)
                now = datetime.now()
                is_this_month = completed_date.month == now.month and completed_date.year == now.year
                prefix = passed if is_this_month else failed
                return prefix + completed_date.strftime("%m|%d|%Y")
            except Exception as e:
                return f"⚠️ Invalid timestamp | {value}"

        # === Special Case: Date for Email Subject Line (Month & Year) ===
        if field_name == "Date for Email Subject Line (Month & Year)":
            if debug:
                print("RAW Date for Email Subject Line (Month & Year) value:", value)

            try:
                # Parse string like "February 2025"
                field_date = datetime.strptime(value, "%B %Y")
                now = datetime.now()
                is_this_month = field_date.month == now.month and field_date.year == now.year
                prefix = passed if is_this_month else failed
                return prefix + value
            except Exception as e:
                return f"⚠️ Invalid format | {value}"

        # === Special Case: WordPress Version ===
        if field_name == "WordPress Version":
            if debug:
                print("RAW WordPress Version value:", value)

            latest_version = get_latest_wp_version()
            if latest_version:
                is_current = value.strip() == latest_version.strip()
                prefix = passed if is_current else failed
                return prefix + value
            else:
                return f"⚠️ Could not fetch latest version | {value}"

        # === Special Case: Domain Expiration ===
        if field_name == "Domain Expiration":
            try:
                # Convert ClickUp expiration timestamp (in ms) to datetime
                clickup_exp = datetime.fromtimestamp(int(value) / 1000).date()

                # Extract domain from Website URL field
                domain = None
                for f in task.get("custom_fields", []):
                    if f["name"] == "Website URL":
                        domain = f.get("value", "").replace("https://", "").replace("http://", "").strip("/")
                        break

                whois_exp = get_dns_expiry(domain).date() if domain else None

                if not whois_exp:
                    return failed + "WHOIS lookup failed"

                if whois_exp != clickup_exp:
                    return failed + f"WHOIS: {whois_exp.strftime('%m/%d/%Y')} ≠ ClickUp: {clickup_exp.strftime('%m/%d/%Y')}"

                return passed + whois_exp.strftime("%m/%d/%Y")

            except Exception as e:
                return f"⚠️ Error comparing expiration: {e}"

        return value

    return "No data"


def get_field_id_by_name(task, field_name):
    custom_fields = task.get("custom_fields", [])
    for field in custom_fields:
        if field["name"] == field_name:
            return field["id"]
    return None


def update_custom_field(task_id, field_id, value, value_type=None):
    url = f"{CLICKUP_BASE_URL}/task/{task_id}/field/{field_id}"

    if value_type == "plugin":
        print("Updating Plugin")
        value = str(value)

    elif value_type == "footer":
        print("Updating Footer Note")
        text, updated_text = value
        current_year = str(datetime.now().year)
        footer_pattern = re.compile(r"(footer\s+)(20[2-4]\d)", re.IGNORECASE)

        if footer_pattern.search(text):
            # Replace only the footer year
            value = footer_pattern.sub(lambda m: f"{m.group(1)}{current_year}", text)
        elif text == "Not specified":
            value = f"{updated_text}"
        else:
            # Append the updated year if no year is found
            value = f"{text}{updated_text}"

    elif value_type == "slider":
        print("Updating Slider Note")
        text, updated_text = value
        current_date = str(datetime.now().strftime("%m/%d/%y"))
        slider_pattern = re.compile(r"(revolution\s+)(\d{2}/\d{2}/\d{2})", re.IGNORECASE)

        if slider_pattern.search(text):
            # Replace only the slider date
            value = slider_pattern.sub(lambda m: f"{m.group(1)}{current_date}", text)
        elif text == "Not specified":
            value = f"{updated_text}"
        else:
            # Append the updated year if no year is found
            value = f"{text}{updated_text}"

    elif value_type == "note":
        print("Adding Note to Clickup")
        text, updated_text = value
        value = f"{text}{updated_text}"

    elif value_type == "date":
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            value = int(dt.timestamp()) * 1000
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

    payload = {"value": value}

    response = make_request(url, "post", payload)
    if response is not None:
        print("Field updated successfully.")
    else:
        print("Failed to update field. Please try again later.")


def update_plugins(site_name, task_id, field_id):
    try:
        total_updates = int(input("How many plugins need to be updated?: ").strip())
        print("Proceed to update all of the plugins...")

        failed_plugins = int(input("❌ How many plugins failed to update?: ").strip())
        successful_updates = total_updates - failed_plugins

        print("\n✅ Plugin Update Summary:")
        print(f"- Total Plugins Intended for Update: {total_updates}")
        print(f"- Successfully Updated Plugins: {successful_updates}")
        print(f"- Failed Plugins: {failed_plugins}")

        # Call the function to update Google Sheets
        update_google_sheet(site_name, successful_updates, "Plugins Updated")
        update_custom_field(task_id, field_id, successful_updates, "plugin")

    except ValueError:
        print("⚠️ Please enter valid numbers only.")


def maintenance_notes(site_name, task_id, field_id, text):
    while True:
        print("1. Unable to Update Footer Year")
        print("2. Add Additional Note")
        print("Type '.' to go back.")
        update_input = input("Which to update? ").strip()

        if update_input == ".":
            break

        if update_input == "1":
            update_google_sheet(site_name, None, "Footer 2025")
            break

        elif update_input == "2":
            updated_text = input("Type your note to append to clickup: ").strip()
            texts = [text, updated_text]
            update_custom_field(task_id, field_id, texts, "note")
            update_google_sheet(site_name, updated_text, "Notes")
            break

        else:
            print("Not a valid choice.")


def update_footer(site_name, task_id, field_id, text):
    print("Updating Footer Note")
    current_year = datetime.now().year
    updated_text = f"Updated Copyright footer {current_year}"
    update_google_sheet(site_name, "Done", "Footer 2025")
    texts = [text, updated_text]
    update_custom_field(task_id, field_id, texts, "footer")


def update_slider(site_name, task_id, field_id, text):
    print("Updating Slider Note")
    current_date = datetime.now().strftime("%m/%d/%y")
    updated_text = f"Updated Slider Revolution {current_date}"
    update_google_sheet(site_name, "Done", "Slider Rev Update")
    texts = [text, updated_text]
    update_custom_field(task_id, field_id, texts, "slider")


def date_completed(task_id, field_id):
    print("Updating Date Completed Field")
    today = datetime.now()
    timestamp = int(today.timestamp() * 1000)  # Convert to milliseconds
    update_custom_field(task_id, field_id, timestamp)


def date_email_subject_line(task_id, field_id):
    print("Updating Date for Email Subject Field")
    today = datetime.now()
    value = today.strftime("%B %Y")  # Output will be like "April 2025"
    update_custom_field(task_id, field_id, value)


def wordpress_version(task_id, field_id):
    print("Updating WordPress Version Field")
    latest_version = get_latest_wp_version()
    value = latest_version.strip()
    update_custom_field(task_id, field_id, value)


def domain_exp(site_name, task, task_id, field_id):
    print("Updating Domain Expiration Field")
    # Extract domain from Website URL field
    domain = None
    for f in task.get("custom_fields", []):
        if f["name"] == "Website URL":
            domain = f.get("value", "").replace("https://", "").replace("http://", "").strip("/")
            break
    if not domain:
        print("Domain not found.")
        return

    whois_exp = get_dns_expiry(domain)  # Assume this returns a datetime or date

    if not whois_exp:
        print("Could not retrieve WHOIS expiration date.")
        return

    if isinstance(whois_exp, datetime):
        dt = whois_exp
    else:
        # Convert date to datetime at midnight
        dt = datetime.combine(whois_exp, datetime.min.time())
    update_google_sheet(site_name, "Done", "Slider Rev Update")
    timestamp = int(dt.timestamp() * 1000)  # Convert to milliseconds
    update_custom_field(task_id, field_id, timestamp)


def filter_clickup_values(clickup_values):
    filtered_values = []

    for value in clickup_values:
        if isinstance(value, str):
            lowered = value.lower()
            if "updated" in lowered:
                filtered_values.append("Done")
            elif "empty" in lowered:
                filtered_values.append("N/A")
            elif "outdated" in lowered or "no data" in lowered:
                filtered_values.append("Incomplete")
            else:
                filtered_values.append(value)
        elif value is None:
            filtered_values.append("Incomplete")
        else:
            filtered_values.append(value)

    return filtered_values


def clickup_sync_google(site_name, task):
    # Define only the fields you want to fetch and display
    fields_to_display = {
        "1. Broken Links Report": "Broken Links Report",
        "2. Number of Plugins Updated": "Number of Plugins Updated",
        "3. Domain Expiration": "Domain Expiration",
        "Notes for Maintenance": "Notes for Maintenance Report",
    }
    clickup_values = []

    for key, field_name in fields_to_display.items():
        value = get_custom_field_value(task, field_name)
        if key == "Notes for Maintenance":
            note_values = analyze_notes_for_maintenance(task, value)  # Show subitems like 6.1, 6.2
            footer_value, slider_value = note_values
            clickup_values.append(footer_value)
            clickup_values.append(slider_value)
        else:
            clickup_values.append(value)

    # 🔍 Apply filtering logic
    filtered_values = filter_clickup_values(clickup_values)

    update_google_sheet(site_name, filtered_values[0], "Broken Links")
    update_google_sheet(site_name, filtered_values[1], "Plugins Updated")
    update_google_sheet(site_name, filtered_values[2], "DNS Check")
    update_google_sheet(site_name, filtered_values[3], "Footer 2025")
    update_google_sheet(site_name, filtered_values[4], "Slider Rev Update")


def change_clickup_status(site_name, task_id):
    status_list = json.loads(os.getenv("CLICKUP_STATUS_FILTER"))
    for index, status in enumerate(status_list, start=1):
        print(f"{index}. {status}")

    update_input = input("Enter your choice: ").strip()

    choice = int(update_input) - 1
    if 0 <= choice < len(status_list):
        selected_status = status_list[choice]
        url = f"{CLICKUP_BASE_URL}/task/{task_id}"
        payload = {"status": selected_status}
        print(f"You selected: {selected_status}")
        make_request(url, "put", payload)
        update_google_sheet(site_name, selected_status, "Status")
        print("Task status updated successfully!")
    else:
        print("Invalid choice. Please enter a number from the list.")
