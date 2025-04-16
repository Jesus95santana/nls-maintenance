import os
from dotenv import load_dotenv
import requests
import json
import whois
from urllib.parse import urlparse
from datetime import datetime

from StartMaintenance.maintenance.clickup import (
    list_folders,
    list_lists,
    list_sites_maintenance,
    get_task,
    display_task_details,
)


def maintenance():
    while True:
        # === FOLDER MENU ===
        print("\n📁 FOLDER MENU:")
        print("Type 'exit' to return to Main Menu.")
        folders = list_folders()
        if not folders:
            print("No Folders")
            return

        folder_input = input("Choose a folder number: ").strip()
        if folder_input.lower() == "exit":
            break
        if not folder_input.isdigit() or int(folder_input) not in range(1, len(folders) + 1):
            print("Invalid folder selection.")
            continue

        selected_folder = folders[int(folder_input) - 1]
        folder_id = selected_folder["id"]

        while True:
            # === LIST MENU ===
            print("\n📋 LIST MENU:")
            print("Type '.' to go back to Folder Menu.")
            print("Type 'exit' to return to Main Menu.")
            lists = list_lists(folder_id)
            if not lists:
                print("No Lists")
                break

            list_input = input("Choose a list number: ").strip()
            if list_input == ".":
                break
            if list_input.lower() == "exit":
                return
            if not list_input.isdigit() or int(list_input) not in range(1, len(lists) + 1):
                print("Invalid list selection.")
                continue

            selected_list = lists[int(list_input) - 1]
            list_id = selected_list["id"]

            while True:
                # === SITE MENU ===
                print("\n🌐 SITE MENU:")
                print("Type '.' to go back to List Menu.")
                print("Type 'exit' to return to Main Menu.")
                sites = list_sites_maintenance(list_id)
                if not sites:
                    print("No Sites")
                    print(sites)
                    break

                site_input = input("Choose a site number: ").strip()
                if site_input == ".":
                    break
                if site_input.lower() == "exit":
                    return
                if not site_input.isdigit() or int(site_input) not in range(1, len(sites) + 1):
                    print("Invalid site selection.")
                    continue

                selected_site = sites[int(site_input) - 1]
                site_name = selected_site["name"]
                site_id = selected_site["id"]

                while True:
                    # === UPDATE MENU ===
                    task = get_task(site_id)
                    print("\n🛠️ UPDATE MENU for " + site_name + ":")

                    display_task_details(task)

                    print("Type '.' to go back to Site Menu.")
                    print("Type 'exit' to return to Main Menu.")

                    update_input = input("Enter your choice: ").strip()

                    if update_input == ".":
                        break
                    if update_input.lower() == "exit":
                        return

                    if update_input == "1":
                        print("broken_links: not built")
                        # broken_links()

                    elif update_input == "2":
                        print("date_completed: not built")
                        # date_completed()

                    elif update_input == "3":
                        print("date_email_subject_line: not built")
                        # date_email_subject_line()

                    elif update_input == "4":
                        print("website_url: not built")
                        # website_url()

                    elif update_input == "5":
                        print("wordpress_version: not built")
                        # wordpress_version()

                    elif update_input == "6":
                        print("maintenance_notes: not built")
                        # maintenance_notes()

                    elif update_input == "7":
                        print("update_plugins: not built")
                        # update_plugins()

                    elif update_input == "8":
                        print("domain_exp: not built")
                        # domain_exp()

                    else:
                        print("Invalid choice.")


# def get_domain_name(url):
#     """Extract the domain name from a URL."""
#     if not urlparse(url).scheme:
#         url = "http://" + url
#     parsed_url = urlparse(url)
#     return parsed_url.netloc


# def get_dns_expiry(domain):
#     """Retrieve the domain expiration date using WHOIS."""
#     try:
#         domain_info = whois.whois(domain)
#         if isinstance(domain_info.expiration_date, list):
#             expiration_date = domain_info.expiration_date[0]
#         else:
#             expiration_date = domain_info.expiration_date
#         return expiration_date.strftime("%Y-%m-%d") if expiration_date else "No expiration date found"
#     except Exception as e:
#         return f"Error retrieving information for {domain}: {e}"


# def fetch_task_details(task_id):
#     url = f"{CLICKUP_BASE_URL}/task/{task_id}"
#     return make_request(url)


# def display_custom_fields(task):
#     if "custom_fields" in task and task["custom_fields"]:
#         print("\nCustom Fields:")
#         for index, field in enumerate(task["custom_fields"]):
#             value = field.get("value", "Not set")
#             print(f"{index + 1}. {field['name']}: {value}")
#         return task["custom_fields"]
#     else:
#         print("No custom fields found for this task.")
#         return None


# def update_custom_field(task_id, field_id, value, value_type):
#     url = f"{CLICKUP_BASE_URL}/task/{task_id}/field/{field_id}"
#     payload = {"value": value}
#     if value_type == "date":
#         # Convert user input date in format 'YYYY-MM-DD' to Unix timestamp in milliseconds
#         try:
#             dt = datetime.strptime(value, "%Y-%m-%d")
#             payload["value"] = int(dt.timestamp()) * 1000
#         except ValueError:
#             print("Invalid date format. Please use YYYY-MM-DD.")
#             return

#     response = make_request(url, "post", payload)
#     if response is not None:  # Checking if response exists
#         print("Field updated successfully.")
#     else:
#         print("Failed to update field. Please try again later.")


# def edit_custom_fields(custom_fields, task):
#     """Allows the user to edit multiple custom fields without exiting."""
#     task_name = task.get("name", "Unknown Task")

#     # Find the 'Website URL' in the custom fields to use for WHOIS lookup
#     website_url = next((field.get("value") for field in custom_fields if field["name"].lower() == "website url"), None)

#     while True:
#         print(f"\n{task_name} - Custom Fields:")
#         for index, field in enumerate(custom_fields):
#             print(f"{index + 1}. {field['name']}: {field.get('value', 'Not set')}")

#         print("\nEnter the number to edit a field, 'b' to go back, or 'q' to quit.")
#         choice = input("Choice: ").strip().lower()

#         if choice.isdigit():
#             field_index = int(choice) - 1
#             if 0 <= field_index < len(custom_fields):
#                 field = custom_fields[field_index]
#                 field_name = field["name"].lower()
#                 field_type = field.get("type", "text")

#                 if field_name == "domain expiration" and field_type == "date":
#                     new_value = input(
#                         f"Enter the domain URL for {field_name} (or press Enter to fetch current expiration from {website_url}): "
#                     ).strip()
#                     if not new_value:  # If user presses Enter, perform WHOIS lookup
#                         if website_url:
#                             domain = get_domain_name(website_url)
#                             new_value = get_dns_expiry(domain)
#                             print(f"Fetched expiration date from WHOIS for {website_url}: {new_value}")
#                         else:
#                             print("No website URL provided. Cannot fetch domain expiration.")
#                     else:
#                         new_value = input(f"Enter new expiration date (YYYY-MM-DD) for {field_name}: ").strip()

#                 else:
#                     new_value = input(f"Enter new value for {field_name}: ").strip()

#                 if new_value:
#                     update_custom_field(task["id"], field["id"], new_value, field_type)
#                 else:
#                     print(f"Skipping update for {field_name}.")
#             else:
#                 print("Invalid selection. Please enter a valid number.")
#         elif choice == "b":
#             return  # Exit back to task selection
#         elif choice == "q":
#             exit("Exiting program...")
#         else:
#             print("Invalid option. Please try again.")
