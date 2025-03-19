import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

# Credentials and URL from .env
url = os.getenv('WP_ADMIN_URL')
user = os.getenv('WP_ADMIN_USER')
password = os.getenv('WP_ADMIN_PASS')

# Set up WebDriver
options = Options()
driver = webdriver.Firefox(options=options)

# Navigate to the WordPress admin login page
driver.get(url + "/wp-admin")

# Log in to WordPress admin
username_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "user_login"))
)
password_input = driver.find_element(By.ID, "user_pass")
login_button = driver.find_element(By.ID, "wp-submit")

username_input.send_keys(user)
password_input.send_keys(password)
login_button.click()

# Pause script for manual navigation
input("Navigate to the plugins page and press Enter to continue...")

# Find all plugins that need updating and list them
try:
    update_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "update now")
    plugins_to_update = []

    for link in update_links:
        plugin_row = link.find_element(By.XPATH, "./ancestor::tr[1]/preceding-sibling::tr[1]")  # Navigate to the previous <tr>
        plugin_name = plugin_row.find_element(By.XPATH, ".//strong").text
        plugin_description = plugin_row.find_element(By.XPATH, ".//p").text[:25]
        plugins_to_update.append((plugin_name, plugin_description))

    # Ask user for the preferred format
    format_choice = input("Choose the format for plugin list (m for Markdown, l for List): ").strip().lower()
    number_of_updates = len(plugins_to_update)

    # Display all plugins that need updating
    if format_choice == 'm':
        print(f"Plugins to be updated ({number_of_updates}):")
        print("| Plugin Name |")
        print("|-------------|")
        for name, _ in plugins_to_update:
            print(f"| {name} |")
    elif format_choice == 'l':
        print(f"Plugins to be updated ({number_of_updates}):")
        for name, desc in plugins_to_update:
            print(f"* {name}: {desc}")  # Bold plugin names with bullet list

    # Ask for confirmation before updating
    input("Press Enter to continue with updates...")

    # Update the plugins
    for link in update_links:
        link.click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "updated-message"))
        )

    print("All available updates have been applied.")

except Exception as e:
    print(f"An error occurred while updating plugins: {e}")

# Optionally, add more steps or close the browser
# driver.quit()
