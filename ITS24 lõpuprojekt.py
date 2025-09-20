#Imports necessary libraries

import hashlib
import webbrowser

#Function to hash passwords using SHA-256

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Registration function

def register():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    with open("D:/projekt/users.txt", "a+", encoding="utf-8", errors="ignore") as f:
        f.seek(0)
        users = [line.strip().split(":")[0] for line in f.readlines()]
        if username in users:
            print("Username already exists.")
            return
    with open("D:/projekt/rockyou.txt", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    if password in content:
        print("Your password is too weak, enter a stronger password.")
        password = input("Enter your password: ")
    else:
        print("Your password is strong enough.")

    password = hash_password(password)

    with open("D:/projekt/users.txt", "a", encoding="utf-8", errors="ignore") as f:
        f.write(f"{username}:{password}\n")

    print("Registration successful.") 
register()

# Login function

def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    with open("D:/projekt/users.txt", "r", encoding="utf-8", errors="ignore") as f:
        users = dict(line.strip().split(":") for line in f if ":" in line)

    hashed_password = hash_password(password)

    if username in users and users[username] == hashed_password:
        print("Login successful.")

        webbrowser.open("D:/projekt/thumbsup.webp")
    else:
        print("Invalid username or password.")
login()

# Change password function

def change_password():
    username = input("Enter your username: ")
    old_password = input("Enter your old password:")
    new_password = input("Enter your new password: ")

    with open("D:/projekt/users.txt", "r", encoding="utf-8", errors="ignore") as f:
        users = dict(line.strip().split(":") for line in f if ":" in line)

    if username in users and users[username] == hash_password(old_password):
        with open("D:/projekt/rockyou.txt", "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if new_password in content:
            print("Your new password is too weak, enter a stronger password.")
            new_password = input("Enter your new password: ")
        else:
            users[username] = hash_password(new_password)
            with open("D:/projekt/users.txt", "w", encoding="utf-8", errors="ignore") as f:
                for user, pwd in users.items():
                    f.write(f"{user}:{pwd}\n")
            print("Password changed successfully.")
change_password()

# Main menu function

def main_menu():
    choice = input("Do you want to [r]egister, [l]ogin, [q]uit or [c]hange password?: ")
    if choice == "r":
        register()
    elif choice == "l":
        login()
    elif choice == "q":
        print("Goodbye!")
    elif choice == "c":
        change_password()
    else:
        print("Invalid choice.")
main_menu()


        
















        