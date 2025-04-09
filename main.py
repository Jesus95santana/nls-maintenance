import os
import logging
from dotenv import load_dotenv

from ClickupTest.clickupConnect import test_clickup_connection
from GoogleTest.googleConnect import test_google_sheet_connection
from StartMaintenance.nls_maintenance.nls_maintenance import nls_maintenance
from StartMaintenance.maintenance.google import create_or_notify_sheet
from StartMaintenance.maintenance.clickup import list_sites

load_dotenv()

# Constants
TOMO360_MONTHLY = os.getenv("CLICKUP_T3_MONTHLY_ID")
NLS = os.getenv("CLICKUP_USER_ID")

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main_menu():
    logging.info("NLS Maintenance Terminal Started.")
    while True:
        print("\nMain Menu:")
        print("1: Test ClickUp Connection")
        print("2: Test Google Connection (Will overwrite Cell A:1)")
        print("3: Start Maintenance")
        print("Type 'exit' to stop the program.")

        user_input = input("Enter your choice: ").strip()

        if user_input.lower() == "exit":
            logging.info("Stopping the program.")
            break

        elif user_input == "1":  # Test Clickup
            test_clickup_connection()
        elif user_input == "2":  # Test Google
            test_google_sheet_connection()
        elif user_input == "3":
            print("1: NLS Maintenance")
            print("2: Maintenance")

            user_input = input("Choose the type of maintenance to work on: ").strip()
            if user_input == "1":  # NLS Maintenance
                nls_maintenance()
            elif user_input == "2":  # Maintenance
                print("1: Create Sheet for Current Month Maintenance from Template")
                print("2: List Sites that are assigned")
                print("3: Execute Maintenance")
                print("4: Exit Program")

                user_input = input("Choose the type of maintenance to work on: ").strip()

                if user_input == "1":
                    create_or_notify_sheet()
                elif user_input == "2":
                    list_sites(TOMO360_MONTHLY, [NLS])
                elif user_input == "3":
                    print("Executing Maintenance")
                elif user_input == "4":
                    print("Exiting the program.")
                else:
                    print("Invalid input. Restarting...")
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
