import os
from dotenv import load_dotenv
from ClickupTest.clickupConnect import make_request, CLICKUP_BASE_URL

load_dotenv()

# Constants
USER = os.getenv("CLICKUP_USER_ID")
STATUS = os.getenv("CLICKUP_STATUS_FILTER")


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
