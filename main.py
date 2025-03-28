from ClickupTest.clickupConnect import test_clickup_connection
from GoogleTest.googleConnect import test_google_sheet_connection

print("NLS Maintenance Terminal Started.")

while True:
    # Display the options to the user
    print("\nChoose an option:")
    print("1: Test ClickUp Connection")
    print("2: Test Google Connection (Will overwrite Cell A:1)")
    print("3: Start Maintenance")
    print("Type 'exit' to stop the program.")

    user_input = input("Enter your choice: ")  # Prompt for input

    if user_input.lower() == "exit":
        print("Stopping the program.")
        break  # Exit the loop and end the program if the user types 'exit'
    elif user_input == "1":
        test_clickup_connection()  # Call the clickup function
    elif user_input == "2":
        test_google_sheet_connection()  # Call the google function
    elif user_input == "3":
        print("Start Maintenance")
    else:
        print("Invalid input. Please enter 1, 2, 3, or 'exit'.")