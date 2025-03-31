import logging
from ClickupTest.clickupConnect import test_clickup_connection
from GoogleTest.googleConnect import test_google_sheet_connection
from StartMaintenance.start import start_maintenance

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main_menu():
    logging.info("NLS Maintenance Terminal Started.")
    while True:
        print("\nMain Menu:")
        print("1: Test ClickUp Connection")
        print("2: Test Google Connection (Will overwrite Cell A:1)")
        print("3: Start Maintenance")
        print("Type 'exit' to stop the program.")

        user_input = input("Enter your choice: ").strip()

        if user_input.lower() == 'exit':
            logging.info("Stopping the program.")
            break
        elif user_input == '1':
            test_clickup_connection()
        elif user_input == '2':
            test_google_sheet_connection()
        elif user_input == '3':
            start_maintenance()
        else:
            logging.warning("Invalid input. Please enter 1, 2, 3, or 'exit'.")

if __name__ == '__main__':
    try:
        main_menu()
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        exit(1)
