from .maintenance.maintenance import maintenance
from .nls_maintenance.nls_maintenance import nls_maintenance

def start_maintenance():
    print("1: NLS Maintenance")
    print("2: Maintenance")

    user_input = input("Choose the type of maintenance to work on: ").strip()

    if user_input == '1':
        nls_maintenance()
    elif user_input == '2':
        maintenance()
    else:
        print("Invalid input. Restarting...")