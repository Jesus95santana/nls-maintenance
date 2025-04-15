import os
import logging
from dotenv import load_dotenv

from ClickupTest.clickupConnect import test_clickup_connection
from GoogleTest.googleConnect import test_google_sheet_connection
from StartMaintenance.nls_maintenance.nls_maintenance import nls_maintenance
from StartMaintenance.maintenance.google import create_or_update_sheet, google_list_formatter
from StartMaintenance.maintenance.clickup import fetch_shared_folders, fetch_all_tasks_by_folder, return_fetch_all_tasks_by_folder
from StartMaintenance.maintenance.maintenance import maintenance

load_dotenv()

# Constants
TOMO360_MONTHLY = os.getenv("CLICKUP_T3_MONTHLY_ID")
TEAM = os.getenv("CLICKUP_TEAM_ID")
USER = os.getenv("CLICKUP_USER_ID")

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main_menu():
    logging.info("NLS Maintenance Terminal Started.")
    while True:
        # Menu 1
        print("\nMain Menu:")
        print("1: Test ClickUp Connection")
        print("2: Test Google Connection (Will overwrite Cell A:1)")
        print("3: Start Maintenance")
        print("Type 'exit' to stop the program.")
        user_input = input("Enter your choice: ").strip()
        if user_input.lower() == "exit":
            logging.info("Stopping the program.")
            break

        # Menu 1.1 Test Clickup
        elif user_input == "1":
            test_clickup_connection()

        # Menu 1.2 Test Google
        elif user_input == "2":
            test_google_sheet_connection()

        # Menu 1.3 Which Maintenance
        elif user_input == "3":
            # Menu 2
            print("1: Maintenance")
            print("2: NLS Maintenance")
            user_input = input("Choose the type of maintenance to work on: ").strip()

            #
            #
            #
            #
            # Menu 2.1 Maintenance
            if user_input == "1":
                # Menu 3
                print("1: Create/Update Google Sheet")
                print("2: List Sites that are assigned")
                print("3: Execute Maintenance")
                print("4: Exit Program")
                user_input = input("Choose the type of maintenance to work on: ").strip()

                # Menu 3.1 Create/Update New Spreadsheet
                if user_input == "1":
                    # Fetch all tasks from ClickUp
                    raw_data = return_fetch_all_tasks_by_folder(TEAM)
                    # Format the fetched data for Google Sheets
                    formatted_data = google_list_formatter(raw_data)
                    # Create or update the Google Sheet with formatted data
                    create_or_update_sheet(formatted_data)

                # Menu 3.2 List All Sites + Status
                elif user_input == "2":
                    fetch_all_tasks_by_folder(TEAM)

                # Menu 3.3 Executing Maintenance
                elif user_input == "3":
                    maintenance()

                # Exit
                elif user_input == "4":
                    print("Exiting the program.")
                else:
                    print("Invalid input. Restarting...")

            #
            #
            #
            #
            # Menu 2.2 NLS Maintenance
            elif user_input == "2":
                # Menu 4
                nls_maintenance()
                print("1: Create Sheet for Current Month Maintenance from Template")
                print("3: Execute Maintenance")
                print("4: Exit Program")
                user_input = input("Choose the type of maintenance to work on: ").strip()
            else:
                print("Invalid input. Restarting...")
        else:
            logging.warning("Invalid input. Please enter 1, 2, 3, or 'exit'.")


if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        exit(1)
