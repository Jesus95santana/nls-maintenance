from clickup import clickup
from google import google

print("NLS Maintenance Terminal Started.")

while True:
    user_input = input("Type 'exit' to stop the program: ")  # Prompt for input
    if user_input.lower() == "exit":
        print("Stopping the program.")
        break  # Exit the loop and end the program if the user types 'exit'
    elif user_input == "clickup":
        clickup()
    elif user_input == "google":
        google()
