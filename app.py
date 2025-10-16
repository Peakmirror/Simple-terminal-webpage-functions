# app.py
from auth import register, login
from services import list_services
from db import init_db, seed_admin, is_admin

def main_menu():
    choice = input("Do you want to [r]egister, [l]ogin or [q]uit: ")
    if choice == "r":
        register()
        next_choice = input("What do you wish to do next? [m]anage account, [b]ook appointment or [q]uit: ")
        if next_choice == "m":
            manage_account()
        elif next_choice == "b":
            sub_choice = input("Do you wish to see the list of services or proceed to book an appointment? [s]ee services or [b]ook appointment: ")
            if sub_choice == "s":
                list_services()
            else:
                calendar_appointment()
        elif next_choice == "q":
            print("Goodbye!")
    elif choice == "l":
        username = login()
        if not username:
            return
        if is_admin(username):
            print("\nAdmin Options:")
            print("[a] Add service")
            print("[r] Remove service")
            print("[p] Promote user")
            admin_choice = input("Choose an admin action (or press Enter to skip): ")
            if admin_choice == "a":
                add_service()
            elif admin_choice == "r":
                remove_service()
            elif admin_choice == "p":
                promote_to_admin(username)
        next_choice = input("What do you wish to do next? [m]anage account, [b]ook appointment or [q]uit: ")
        if next_choice == "m":
            manage_account()
        elif next_choice == "b":
            calendar_appointment()
        elif next_choice == "q":
            print("Goodbye!")

main_menu()