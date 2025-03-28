import os
from dotenv import load_dotenv
import requests
import json
import whois
from urllib.parse import urlparse
from datetime import datetime

# Constants
CLICKUP_TOKEN = os.getenv('CLICKUP_TOKEN')
CLICKUP_BASE_URL = os.getenv('CLICKUP_BASE_URL')
CLICKUP_SPACE_ID = os.getenv('CLICKUP_SPACE_ID')
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": TOKEN
}

def get_domain_name(url):
    """Extract the domain name from a URL."""
    if not urlparse(url).scheme:
        url = 'http://' + url
    parsed_url = urlparse(url)
    return parsed_url.netloc

def get_dns_expiry(domain):
    """Retrieve the domain expiration date using WHOIS."""
    try:
        domain_info = whois.whois(domain)
        if isinstance(domain_info.expiration_date, list):
            expiration_date = domain_info.expiration_date[0]
        else:
            expiration_date = domain_info.expiration_date
        return expiration_date.strftime('%Y-%m-%d') if expiration_date else 'No expiration date found'
    except Exception as e:
        return f"Error retrieving information for {domain}: {e}"

def make_request(url, method='get', data=None):
    """Handles making HTTP requests and error management."""
    try:
        if method == 'get':
            response = requests.get(url, headers=HEADERS)
        else:
            response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()  # This will raise an error for non-200 status codes
        return response.json() if response.content else None  # Extract JSON safely
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code} {e.response.reason}")
        if e.response.content:
            print("Error details:", e.response.json())
        return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def confirm_connection():
    url = CLICKUP_BASE_URL + "/user"
    response = make_request(url)
    if response:
        print("Connection confirmed. User data received successfully.")
        print(response)

def fetch_folders(space_id):
    url = f"{CLICKUP_BASE_URL}/space/{space_id}/folder"
    return make_request(url)

def list_folders(folders):
    if folders and 'folders' in folders and folders['folders']:
        print("\nAvailable folders:")
        for index, folder in enumerate(folders['folders']):
            print(f"{index + 1}. Folder Name: {folder['name']}")
        return folders['folders']
    else:
        print("No folders found or there was an error fetching folders.")
        return None

def fetch_lists(folder_id):
    url = f"{CLICKUP_BASE_URL}/folder/{folder_id}/list"
    return make_request(url)

def list_lists(lists):
    if lists and 'lists' in lists and lists['lists']:
        print("\nLists in the selected folder:")
        for index, list in enumerate(lists['lists']):
            print(f"{index + 1}. List Name: {list['name']}")
        return lists['lists']
    else:
        print("No lists found or there was an error fetching lists.")
        return None

def fetch_tasks(list_id):
    url = f"{CLICKUP_BASE_URL}/list/{list_id}/task"
    return make_request(url)

def list_tasks(tasks):
    if tasks and 'tasks' in tasks and tasks['tasks']:
        print("\nTasks in the selected list:")
        for index, task in enumerate(tasks['tasks']):
            print(f"{index + 1}. Task Name: {task['name']} - Task ID: {task['id']}")
        return tasks['tasks']
    else:
        print("No tasks found or there was an error fetching tasks.")
        return None

def fetch_task_details(task_id):
    url = f"{CLICKUP_BASE_URL}/task/{task_id}"
    return make_request(url)

def display_custom_fields(task):
    if 'custom_fields' in task and task['custom_fields']:
        print("\nCustom Fields:")
        for index, field in enumerate(task['custom_fields']):
            value = field.get('value', 'Not set')
            print(f"{index + 1}. {field['name']}: {value}")
        return task['custom_fields']
    else:
        print("No custom fields found for this task.")
        return None

def update_custom_field(task_id, field_id, value, value_type):
    url = f"{CLICKUP_BASE_URL}/task/{task_id}/field/{field_id}"
    payload = {"value": value}
    if value_type == "date":
        # Convert user input date in format 'YYYY-MM-DD' to Unix timestamp in milliseconds
        try:
            dt = datetime.strptime(value, '%Y-%m-%d')
            payload['value'] = int(dt.timestamp()) * 1000
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

    response = make_request(url, 'post', payload)
    if response is not None:  # Checking if response exists
        print("Field updated successfully.")
    else:
        print("Failed to update field. Please try again later.")

def edit_custom_fields(custom_fields, task):
    """Allows the user to edit multiple custom fields without exiting."""
    task_name = task.get('name', 'Unknown Task')

    # Find the 'Website URL' in the custom fields to use for WHOIS lookup
    website_url = next((field.get('value') for field in custom_fields if field['name'].lower() == 'website url'), None)

    while True:
        print(f"\n{task_name} - Custom Fields:")
        for index, field in enumerate(custom_fields):
            print(f"{index + 1}. {field['name']}: {field.get('value', 'Not set')}")

        print("\nEnter the number to edit a field, 'b' to go back, or 'q' to quit.")
        choice = input("Choice: ").strip().lower()

        if choice.isdigit():
            field_index = int(choice) - 1
            if 0 <= field_index < len(custom_fields):
                field = custom_fields[field_index]
                field_name = field['name'].lower()
                field_type = field.get('type', 'text')

                if field_name == "domain expiration" and field_type == "date":
                    new_value = input(f"Enter the domain URL for {field_name} (or press Enter to fetch current expiration from {website_url}): ").strip()
                    if not new_value:  # If user presses Enter, perform WHOIS lookup
                        if website_url:
                            domain = get_domain_name(website_url)
                            new_value = get_dns_expiry(domain)
                            print(f"Fetched expiration date from WHOIS for {website_url}: {new_value}")
                        else:
                            print("No website URL provided. Cannot fetch domain expiration.")
                    else:
                        new_value = input(f"Enter new expiration date (YYYY-MM-DD) for {field_name}: ").strip()

                else:
                    new_value = input(f"Enter new value for {field_name}: ").strip()

                if new_value:
                    update_custom_field(task['id'], field['id'], new_value, field_type)
                else:
                    print(f"Skipping update for {field_name}.")
            else:
                print("Invalid selection. Please enter a valid number.")
        elif choice == 'b':
            return  # Exit back to task selection
        elif choice == 'q':
            exit("Exiting program...")
        else:
            print("Invalid option. Please try again.")




def navigation_menu(items, level):
    if not items:
        print("Nothing here to display.")
        return None
    while True:
        choice = input("\nEnter number to select, 'b' to start over, or 'q' to quit: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(items):
            return items[int(choice) - 1]
        elif choice.lower() == 'b' and level > 0:
            return None
        elif choice.lower() == 'q':
            exit("Exiting program...")
        else:
            print("Invalid option, please try again.")

def main():
    #confirm_connection()
    while True:
        folders = fetch_folders(CLICKUP_SPACE_ID)
        folder_list = list_folders(folders)
        selected_folder = navigation_menu(folder_list, 0)
        if selected_folder:
            lists = fetch_lists(selected_folder['id'])
            list_list = list_lists(lists)
            selected_list = navigation_menu(list_list, 1)
            if selected_list:
                tasks = fetch_tasks(selected_list['id'])
                task_list = list_tasks(tasks)
                selected_task = navigation_menu(task_list, 2)
                if selected_task:
                    task_details = fetch_task_details(selected_task['id'])
                    custom_fields = display_custom_fields(task_details)
                    if custom_fields:
                        edit_custom_fields(custom_fields, task_details)

if __name__ == "__main__":
    main()
