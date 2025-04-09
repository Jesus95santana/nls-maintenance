from ClickupTest.clickupConnect import make_request, CLICKUP_BASE_URL


def list_sites(list_id, assignee_ids):
    """
    Fetches tasks from a specific ClickUp list filtered by assignee IDs.
    :param list_id: The ID of the list in ClickUp.
    :param assignee_ids: List of assignee IDs to filter tasks.
    :return: None
    """
    assignees = "&".join([f"assignees[]={id}" for id in assignee_ids])
    url = f"{CLICKUP_BASE_URL}/list/{list_id}/task?{assignees}"
    response = make_request(url)
    if response and "tasks" in response:
        print(f"List of tasks for list ID {list_id}:")
        for task in response["tasks"]:
            print(f"- {task['name']} (ID: {task['id']})")
    else:
        print("No tasks found or failed to fetch tasks.")
