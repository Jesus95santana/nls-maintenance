import os
from dotenv import load_dotenv
import json
import re
from datetime import datetime
from ClickupTest.clickupConnect import make_request, CLICKUP_BASE_URL

from .google import update_google_sheet

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
        print("{:<50} {}".format(key + ":", value))


def format_date(timestamp):
    """Convert Unix timestamp (in milliseconds) to a human-readable date."""
    if timestamp is not None:
        # Convert milliseconds to seconds
        timestamp = int(timestamp) / 1000
        return datetime.utcfromtimestamp(timestamp).strftime("%m/%d/%Y")
    return "Not specified"


def show_broken_links(task):
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    for field in task.get("custom_fields", []):
        if field["name"] == "Broken Links Report":
            attachments = field.get("value", [])
            if not attachments:  # Check if the list is empty
                return "Empty"
            try:
                # Assuming the most recent report is the first one
                most_recent_report = attachments[0]
                report_date_ms = int(most_recent_report["date"])
                report_date = datetime.utcfromtimestamp(report_date_ms / 1000)
                if report_date.year == current_year and report_date.month == current_month:
                    return "Updated"
                else:
                    return "Not Updated"
            except (KeyError, ValueError, IndexError):
                return "not updated"  # Default to not updated if any errors occur
    return "empty"  # If the field is not found


def get_custom_field_value(task, field_name):
    if field_name == "Broken Links Report":
        return show_broken_links(task)
    for field in task.get("custom_fields", []):
        if field["name"] == field_name:
            value = field.get("value", "Not specified")
            if "Date" in field_name or "Expiration" in field_name:
                try:
                    return format_date(value)
                except ValueError:
                    return value
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
        year_pattern = r"\b(20[2-4]\d)\b"
        if re.search(year_pattern, text):
            # Replace the existing year
            value = re.sub(year_pattern, str(datetime.now().year), text)
        else:
            # Append the updated year if no year is found
            value = f"{text}\n{updated_text}"

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
    print("1. Footer Year Updated")
    print("2. Unable to Update Footer Year")
    print("3. Add Additional Note")
    update_input = input("Which to update?").strip()

    if update_input == "1":
        # Updated Copyright footer 2025
        current_year = datetime.now().year
        # This regex pattern finds four consecutive digits that look like a year close to the current year
        updated_text = f"Updated Copyright footer {current_year}"
        update_google_sheet(site_name, "Done", "Footer 2025")
        texts = [text, updated_text]
        update_custom_field(task_id, field_id, texts, "footer")

    elif update_input == "2":
        update_google_sheet(site_name, None, "Footer 2025")

    elif update_input == "3":
        print("Add Aditional Notes: not built yet")
        # broken_links()

    else:
        print("Not a valid choice.")
