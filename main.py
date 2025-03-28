from ClickupTest.clickupConnect import test_clickup_connection
from GoogleTest.googleConnect import google

print("NLS Maintenance Terminal-Exec Started.")

while True:
    # Display the options to the user
    print("\nChoose an option:")
    print("1: ClickUp")
    print("2: Google")
    print("3: Hello World")
    print("Type 'exit' to stop the program.")

    user_input = input("Enter your choice: ")  # Prompt for input

    if user_input.lower() == "exit":
        print("Stopping the program.")
        break  # Exit the loop and end the program if the user types 'exit'
    elif user_input == "1":
        test_clickup_connection()  # Call the clickup function
    elif user_input == "2":
        google()  # Call the google function
    elif user_input == "3":
        print("Hello World")  # Print Hello World
    else:
        print("Invalid input. Please enter 1, 2, 3, or 'exit'.")