def nls_maintenance():
    while True:
        # === FOLDER MENU ===
        print("\n📁 FOLDER MENU:")
        print("Type 'exit' to return to Main Menu.")
        folders = list_folders()  # Maintenance Plan | Canceled
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
            print("Type 'r' to refresh folders.")
            print("Type 'exit' to return to Main Menu.")
            lists = list_lists(folder_id)  # Hosting Name
            if not lists:
                print("No Lists")
                break

            list_input = input("Choose a list number: ").strip()
            if list_input == ".":
                break
            if folder_input == "refresh":
                continue
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
                print("Type 'r' to refresh List Menu.")
                print("Type 'exit' to return to Main Menu.")
                sites = list_sites_maintenance(list_id)  # List sites
                if not sites:
                    print("No Sites")
                    print(sites)
                    break

                site_input = input("Choose a site number: ").strip()
                if site_input == ".":
                    break
                if folder_input == "refresh":
                    continue
                if site_input.lower() == "exit":
                    return
                if not site_input.isdigit() or int(site_input) not in range(1, len(sites) + 1):
                    print("Invalid site selection.")
                    continue

                selected_site = sites[int(site_input) - 1]
                site_name = selected_site["name"]
                site_id = selected_site["id"]

                # while True:
                #     # === UPDATE MENU ===
                #     task = get_task(site_id)
                #     # Uncomment to see data coming in
                #     # print(task["custom_fields"])
                #     task_id = task["id"]
                #     print("\n🛠️ UPDATE MENU for " + site_name + ":")

                #     display_task_details(task)
                #     print("9. Updage Google Sheet Status")
                #     print("0. Change Clickup Status")
                #     print("==================================")
                #     print("Type '.' to go back to Site Menu.")
                #     print("Type 'r' to refresh Site Menu.")
                #     print("Type 'exit' to return to Main Menu.")
                #     print("==================================")

                #     update_input = input("Enter your choice: ").strip()

                #     if update_input == ".":
                #         break
                #     if folder_input == "refresh":
                #         continue
                #     if update_input.lower() == "exit":
                #         return

                #     if update_input == "1":
                #         field_id = get_field_id_by_name(task, "Broken Links Report")
                #         file_path = select_file_gui()
                #         if file_path:
                #             upload_file_to_clickup(task_id, field_id, file_path)
                #         else:
                #             print("No file selected.")

                #     elif update_input == "2":
                #         field_id = get_field_id_by_name(task, "Date Completed")
                #         date_completed(task_id, field_id)

                #     elif update_input == "3":
                #         field_id = get_field_id_by_name(task, "Date for Email Subject Line (Month & Year)")
                #         date_email_subject_line(task_id, field_id)

                #     elif update_input == "4":
                #         print("website_url: not built")
                #         # website_url()

                #     elif update_input == "5":
                #         field_id = get_field_id_by_name(task, "WordPress Version")
                #         wordpress_version(task_id, field_id)

                #     elif update_input == "6":
                #         text = get_custom_field_value(task, "Notes for Maintenance Report")
                #         field_id = get_field_id_by_name(task, "Notes for Maintenance Report")
                #         maintenance_notes(site_name, task_id, field_id, text)

                #     elif update_input == "6.1":
                #         text = get_custom_field_value(task, "Notes for Maintenance Report")
                #         field_id = get_field_id_by_name(task, "Notes for Maintenance Report")
                #         update_footer(site_name, task_id, field_id, text)

                #     elif update_input == "6.2":
                #         text = get_custom_field_value(task, "Notes for Maintenance Report")
                #         field_id = get_field_id_by_name(task, "Notes for Maintenance Report")
                #         update_slider(site_name, task_id, field_id, text)

                #     elif update_input == "7":
                #         field_id = get_field_id_by_name(task, "Number of Plugins Updated")
                #         update_plugins(site_name, task_id, field_id)

                #     elif update_input == "8":
                #         field_id = get_field_id_by_name(task, "Domain Expiration")
                #         domain_exp(site_name, task, task_id, field_id)

                #     elif update_input == "9":
                #         print("Syncing status to Google Sheets...")
                #         clickup_sync_google(site_name, task)
                #         print("Sync completed!")

                #     elif update_input == "0":
                #         change_clickup_status(site_name, task_id)

                #     else:
                #         print("Invalid choice.")
