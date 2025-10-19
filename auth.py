from db import get_conn
from utils import hash_password, has_special_char, generate_token
import os
import time
import smtplib

# Registration
def register():
    conn = get_conn()
    cursor = conn.cursor()
    minimum_length = 8
    reserved = {"admin", "administrator", "root", "system"}

    email = input("Enter your email: ")
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        print("An account with this email already exists.")
        conn.close()
        return

    while True:
        username = input("Enter a username: ")
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print("Username already exists.")
        elif username.lower() in reserved:
            print("This username is reserved, please choose another one.")
        else:
            break

    print("Password must be at least 8 characters, contain a digit, uppercase letter, and special char.")
    while True:
        password = input("Enter a password: ")
        if len(password) < minimum_length:
            print("Password too short.")
        elif not any(char.isdigit() for char in password):
            print("Must contain a digit.")
        elif not any(char.isupper() for char in password):
            print("Must contain an uppercase letter.")
        elif not has_special_char(password):
            print("Must contain a special character.")
        else:
            # Weak password check
            filepath = os.path.join(os.path.dirname(__file__), "rockyou.txt")
            weak = False
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if password.strip() == line.strip():
                            weak = True
                            break
            except FileNotFoundError:
                pass
            if weak:
                print("Password too weak.")
                continue
            break

    hashed_password = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, password, is_admin, email) VALUES (?, ?, ?, ?)",
        (username, hashed_password, 0, email)
    )
    conn.commit()
    conn.close()
    print("Registration successful.")

# Login
def login():
    conn = get_conn()
    cursor = conn.cursor()
    login_attempts = 3
    while True:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        hashed_password = hash_password(password)
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and result[0] == hashed_password:
            cursor.execute("UPDATE users SET last_login = ? WHERE username = ?", (int(time.time()), username))
            conn.commit()
            conn.close()
            print("Login successful.")
            return username
        else:
            print("Invalid username or password.")
            login_attempts -= 1
            if login_attempts == 0:
                print("Too many failed attempts. Try again later.")
                time.sleep(120)
            conn.close()

# Password reset request

from email.mime.text import MIMEText

def send_email(email,token):
    sender = "senderemail"
    password = "code"
    reset_link = f"http://localhost:5000/reset_password?token={token}"
    msg = MIMEText(f"Click on the link to reset your password: {reset_link}")
    msg["Subject"] = "Password Reset"
    msg["From"] = sender
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
      
# Password reset request

def request_password_reset():

    email = input("Enter your registered email: ")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    if not result:
        print("No account associated with this email.")
        conn.close()
        return
    token = secrets.token_urlsafe(32)
    expiry = int(time.time()) + 3600  # 1 hour expiry
    cursor.execute("UPDATE users SET reset_token = ?, reset_expiry = ? WHERE email = ?", (token, expiry, email))
    conn.commit()
    conn.close()
    send_email(email, token)
    print("Password reset link has been sent to your email.")

def reset_password(token):
    get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT email, reset_expiry FROM users WHERE reset_token = ?", (token,))
    result = cursor.fetchone()

    if not result:
        print("Invalid token.")
        return
    email, expiry = result
    if int(time.time()) > expiry:
        print("Reset link expired.")
        return
    
    new_password = input("Enter your new password: ")
    hashed = hash_password(new_password)
    cursor.execute("UPDATE users SET password = ?, reset_token = NULL, reset_expiry = NULL WHERE email = ?", (hashed, email))
    conn.commit()
    conn.close()
    print("Password reset successful.")


