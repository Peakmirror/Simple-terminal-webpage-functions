import hashlib
import webbrowser
import time
import string
import sqlite3
import datetime
import os
import calendar

#Function to hash passwords using SHA-256

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check for special characters in a password

def has_special_char(password: str) -> bool:
    special_characters = string.punctuation
    return any(char in special_characters for char in password)
# Initialize the database and create tables if they don't exist

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    failed_attempts INTEGER DEFAULT 0,
    lock_until INTEGER DEFAULT NULL,
    created_at INTEGER DEFAULT (strftime('%s','now')),
    last_login INTEGER DEFAULT NULL,
    is_admin INTEGER DEFAULT 0
)
""")

    # Services table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        price REAL NOT NULL
    )
    """)

    #Appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        service_id INTEGER,
        FOREIGN KEY(username) REFERENCES users(username),
        FOREIGN KEY(service_id) REFERENCES services(id)
    )
    """)

init_db()

# Seed an admin account if it doesn't exist
def seed_admin():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    admin_username = "admin"
    admin_password = hash_password("1234")  # Default admin password, change this

    cursor.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            (admin_username, admin_password, 1)
        )
        conn.commit()
        print("Admin account created.")
    conn.close()
seed_admin()

# Check if a user is an admin
def is_admin(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

# Promote a user to admin

def promote_to_admin(current_user):
    if not is_admin(current_user):
        print("You do not have permission to promote users.")
        return

    target = input("Enter username to promote: ")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (target,))
    if cursor.rowcount > 0:
        print(f"{target} is now an admin.")
    else:
        print("No such user.")
    conn.commit()
    conn.close()


# Registration function

def register():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    minimum_length = 8
    reserved = {"admin", "administrator", "root", "system"}

    # Ask for username
    while True:
        username = input("Enter a username: ")
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print("Username already exists.")
        elif username.lower() in reserved:
            print("This username is reserved, please choose another one.")
        else:
            break

    # Ask for password and check rules
    print("Password must be at least 8 characters long, contain at least one digit, one uppercase letter, and one special character.")
    while True:
        password = input("Enter a password: ")
        if len(password) < minimum_length:
            print("Password is too short, enter a longer password.")
        elif not any(char.isdigit() for char in password):
            print("Password must contain at least one digit.")
        elif not any(char.isupper() for char in password):
            print("Password must contain at least one uppercase letter.")
        elif not has_special_char(password):
            print("Password must contain at least one special character.")
        else:
            filepath = os.path.join(os.path.dirname(__file__), "rockyou.txt")
            weak = False
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if password.strip() == line.strip():
                            weak = True
                            break
            except FileNotFoundError:
                print("rockyou.txt not found. Skipping weak password check.")
            if weak:
                print("Your password is too weak, enter a stronger password.")
                continue
            break

    hashed_password = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
        (username, hashed_password, 0)
    )
    conn.commit()
    conn.close()
    print("Registration successful.")

# Login function

def login():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    login_attempts = 3
    while True:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        hashed_password = hash_password(password)
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and result[0] == hash_password(password):
            print("Login successful.")
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE username = ?",
                (int(time.time()), username)
            )
            conn.commit()
            conn.close()
            return username
        elif username not in [row[0] for row in cursor.execute("SELECT username FROM users").fetchall()]:
            print("Account does not exist or you have entered an incorrect username.")
            conn.close()
            continue 
        else:
            print("Invalid username or password.")
            login_attempts -= 1
            if login_attempts > 0:
                print(f"You have {login_attempts} attempts left.")
            elif login_attempts == 0:
                print("Too many failed attempts. Try again in 2 minutes.")
                time.sleep(120)

# Manage account function

def manage_account():
    action = input("What do you want to do? [c]hange password or [d]elete account?: ")

    if action == "c":
        change_password()
    elif action == "d":
        delete_account()
    else:
        print("Invalid action.")

# delete account function

def delete_account():

    username = login()
    if not username:
        return
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    password = input("Enter your password to confirm deletion: ")
    hashed_password = hash_password(password)
    if not result or result[0] != hash_password(password):
        print("Invalid password.")
        conn.close()
        return
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    print("Account deleted successfully.")
    conn.close()

# change password function
def change_password():
    username = login()
    if not username:
        return
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    old_password = input("Enter your old password: ")
    new_password = input("Enter your new password: ")
    hashed_password = hash_password(old_password)

    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    if result and result[0] == hash_password(old_password):
        with open(os.path.join(os.path.dirname(__file__), "rockyou.txt"), "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if new_password in content:
            print("Your new password is too weak, enter a stronger password.")
            conn.close()
            return
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hash_password(new_password), username))
        conn.commit()
        if cursor.rowcount > 0:
            print("Password changed successfully.")
        else:
            print("Password change failed.")
    else:
        print("Invalid username or password.")
    conn.close()

#Choosing an appointment time
def calendar_appointment():
    print("Please login to book an appointment.")
    username = login()
    if not username:
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    print(f"Available dates in {datetime.date(year, month, 1).strftime('%B')} {year}:")
    
    month_days = calendar.monthcalendar(year, month)
    available_dates = [day for week in month_days for day in week if day != 0]


    #Asks the user to choose a service
    service_id = list_services()
    if not service_id:
        return  # stop if invalid

    cursor.execute(
        "INSERT INTO appointments (username, appointment_time, service_id) VALUES (?, ?, ?)",
        (username, appointment_time_str, service_id)
    )

    print(available_dates)
    day = int(input("Choose a date (day number): "))
    hour = int(input("Choose an hour (10-18): "))

    if day in available_dates and 10 <= hour <= 18:
        appointment_time = datetime.datetime(year, month, day, hour)
        appointment_time_str = appointment_time.isoformat()  # <-- ✅ save as string
        print(f"Appointment booked for {appointment_time_str}.")
        cursor.execute(
            "INSERT INTO appointments (username, appointment_time) VALUES (?, ?)",
            (username, appointment_time_str)
        )
        conn.commit()
    else:
        print("Invalid date or hour selected.")
    conn.close()

def list_services():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM services")
    services = cursor.fetchall()
    conn.close()

    if not services:
        print("No services available.")
        return None

    print("Available Services:")
    for sid, name, price in services:
        print(f"{sid}. {name} - ${price}")

    choice = input("Select a service by entering the corresponding number: ")
    try:
        choice = int(choice)
    except ValueError:
        print("Invalid selection.")
        return None

    for sid, name, price in services:
        if sid == choice:
            print(f"You have selected: {name}")
            return sid  # return service_id for later use

    print("Invalid selection.")
    return None

#add services to the database if they don't exist
def add_service():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    name = input("Enter service name: ")
    price = input("Enter price: ")

    try:
        price = float(price)
    except ValueError:
        print("Invalid price.")
        conn.close()
        return

    try:
        cursor.execute("INSERT INTO services (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        print(f"Service '{name}' added successfully.")
    except sqlite3.IntegrityError:
        print("That service already exists.")
    conn.close()

def remove_service():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM services")
    services = cursor.fetchall()
    if not services:
        print("No services available.")
        conn.close()
        return

    print("Available services:")
    for sid, name in services:
        print(f"{sid}. {name}")

    choice = input("Enter the ID of the service to remove: ")
    try:
        choice = int(choice)
    except ValueError:
        print("Invalid choice.")
        conn.close()
        return

    cursor.execute("DELETE FROM services WHERE id = ?", (choice,))
    if cursor.rowcount > 0:
        print("Service removed successfully.")
    else:
        print("No service found with that ID.")
    conn.commit()
    conn.close()

# Main menu function

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
        next_choice = input("What do you wish to do next? [m]anage account, [b]ook appointment or [q]uit: ")
        if next_choice == "m":
            manage_account()
        elif next_choice == "b":
            calendar_appointment()
        elif next_choice == "q":
            print("Goodbye!")
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

main_menu()
