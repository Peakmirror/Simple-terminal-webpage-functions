#Imports necessary libraries

import hashlib
import webbrowser
import time
import string
import sqlite3
import datetime
import os


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

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        failed_attempts INTEGER DEFAULT 0,
        lock_until INTEGER DEFAULT NULL,
        created_at INTEGER DEFAULT (strftime('%s','now')),
        last_login INTEGER DEFAULT NULL
    )
    """)

    #Appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        FOREIGN KEY(username) REFERENCES users(username)
    )
    """)

init_db()

# Registration function

def register():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    minimum_length = 8

    # Asks the user for a username and checks if it already exists
    username = input("Enter a username: ")
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return ("Username already exists.")

        # Asks the user for a password and checks if it is strong enough or if it exists in rockyou.txt
    print("Password must be at least 8 characters long, contain at least one digit, one uppercase letter, and one special character.")
    while True:
        password = input("Enter a password (minimum 8 characters): ")
        hashed_password = hash_password(password)
        if len(password) < minimum_length:
            print("Password is too short, enter a longer password.")
        elif not any(char.isdigit() for char in password):
            print("Password must contain at least one digit.")
        elif not any(char.isupper() for char in password):
            print("Password must contain at least one uppercase letter.")
        elif not has_special_char(password):
            print("Password must contain at least one special character.")
        else:
            break
    with open(os.path.join(os.path.dirname(__file__), "rockyou.txt"), "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    if password in content:
        print("Your password is too weak, enter a stronger password.")
        while True:
            password = input("Enter your password: ")
            if password not in content:
                print("Your password is strong enough.")
                break
            print("Your password is too weak, enter a stronger password.")
    else:
        print("Your password is strong enough.")

    hashed_password = hash_password(password)

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    print("Registration successful.")

# Login function

def login():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    while True:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        login_attempts = 3
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        hashed_password = hash_password(password)
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and result[1] == hash_password(password):
            print("Login successful.")
            webbrowser.open("D:/projekt/thumbsup.webp")
            cursor.execute("UPDATE users SET last_login = strftime('%s','now') WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return username
        else:
            print("Invalid username or password.")
            login_attempts -= 1
            if login_attempts > 0:
                print(f"You have {login_attempts} attempts left.")
            elif login_attempts == 0:
                print("Too many failed attempts. Try again in 2 minutes.")
                time.sleep(120)
conn.close()
            

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
        with open("D:/projekt/rockyou.txt", "r", encoding="utf-8", errors="ignore") as f:
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
    username = login()  # This will run your existing login function
    # Continue with appointment booking after successful login
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    print(f"Available dates in {calendar.month_name[month]} {year}:")
    month_days = calendar.monthcalendar(year,month)
    available_dates = []
    for week in month_days:
        for day in week:
            if day != 0:
                available_dates.append(day)
    print(available_dates)
    day = int(input("Choose a date (day number): "))
    hour = int(input("Choose an hour (10-18): "))
    if day in available_dates and 10 <= hour <= 18:
        appointment_time = datetime.datetime(year, month, day, hour)
        print(f"Appointment booked for {appointment_time}.")
    elif day not in available_dates:
        print("Invalid date selected.")
    else:
        print("Invalid hour selected.")
    cursor.execute("INSERT INTO appointments (username, appointment_time) VALUES (?, ?)", (username, appointment_time))
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
            calendar_appointment()
        elif next_choice == "q":
            print("Goodbye!")
    elif choice == "l":
        login()
        next_choice = input("What do you wish to do next? [m]anage account, [b]ook appointment or [q]uit: ")
        if next_choice == "m":
            manage_account()
        elif next_choice == "b":
            calendar_appointment()
        elif next_choice == "q":
            print("Goodbye!")
    elif next_choice == "q":
        print("Goodbye!")
    else:
        print("Invalid choice.")
main_menu()