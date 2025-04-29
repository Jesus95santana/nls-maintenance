import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()  # Make sure to load the .env file, assumes .env is in the root or environment path is set

# Constants
CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")
CLICKUP_BASE_URL = os.getenv("CLICKUP_BASE_URL")

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": CLICKUP_TOKEN,
}


def make_request(url, method="get", data=None, files=None):
    """Handles making HTTP requests and error management for GET, POST, and PUT methods."""
    try:
        methods = {"get": requests.get, "post": requests.post, "put": requests.put}
        method_func = methods.get(method.lower())

        if method_func is None:
            raise ValueError("Invalid HTTP method provided.")

        if method == "get":
            response = method_func(url, headers=HEADERS)
        elif files:
            # Modify headers for multipart/form-data, let requests handle 'Content-Type'
            multipart_headers = {key: value for key, value in HEADERS.items() if key.lower() != "content-type"}
            response = method_func(url, headers=multipart_headers, files=files, data=data)
        else:
            response = method_func(url, headers=HEADERS, json=data)

        response.raise_for_status()
        return response.json() if response.content else None

    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code} {e.response.reason}")
        if e.response.content:
            try:
                print("Error details:", e.response.json())
            except ValueError:
                print("Error reading error details, raw content:", e.response.text)
        return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except ValueError as e:
        print(f"A ValueError occurred: {e}")
        return None


def test_clickup_connection():
    """Check if connection to ClickUp is successful using the API token."""
    url = f"{CLICKUP_BASE_URL}/user"
    url2 = f"{CLICKUP_BASE_URL}/team"
    response = make_request(url)
    response2 = make_request(url2)
    user_id = response["user"]["id"]
    team_id = response2["teams"][0]["id"]
    if response:
        print("Connection confirmed. User data received successfully.")
        print("User ID is " + str(user_id))
        print("Team ID is " + str(team_id))
    else:
        print("Failed to establish a connection. Check your API token and network settings.")


def main():
    test_clickup_connection()


if __name__ == "__main__":
    main()
