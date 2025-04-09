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


def make_request(url, method="get", data=None):
    """Handles making HTTP requests and error management."""
    try:
        if method == "get":
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


def test_clickup_connection():
    """Check if connection to ClickUp is successful using the API token."""
    url = f"{CLICKUP_BASE_URL}/user"
    response = make_request(url)
    if response:
        print("Connection confirmed. User data received successfully.")
        print(response)
    else:
        print("Failed to establish a connection. Check your API token and network settings.")


def main():
    test_clickup_connection()


if __name__ == "__main__":
    main()
