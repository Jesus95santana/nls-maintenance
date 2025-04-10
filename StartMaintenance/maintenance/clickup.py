import os
from dotenv import load_dotenv
from ClickupTest.clickupConnect import make_request, CLICKUP_BASE_URL

load_dotenv()

# Constants
USER = os.getenv("CLICKUP_USER_ID")


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
    Fetches tasks from a specific ClickUp list filtered by assignee IDs.
    :param list_id: The ID of the list in ClickUp.
    :param assignee_ids: List of assignee IDs to filter tasks.
    :return: None
    """
    assignees = "&".join([f"assignees[]={id}" for id in assignee_ids])
    url = f"{CLICKUP_BASE_URL}/list/{list_id}/task?{assignees}&statuses[]=due this month&statuses[]=send expiration notice&statuses[]=ready for report"  # Hardcoded to only show 3 status
    response = make_request(url)
    if response and "tasks" in response:
        # print(f"    Tasks for List ID {list_id}:")
        for task in response["tasks"]:
            # Extract the status details
            task_status = task.get("status", {}).get("status", "No status found")
            print(f"      - {task['name']} (Status: {task_status})")
    else:
        print("    No tasks found or failed to fetch tasks for List ID:", list_id)
