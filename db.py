import sqlite3

def get_conn():
    return sqlite3.connect("users.db")

def init_db():
    conn = get_conn()
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
        is_admin INTEGER DEFAULT 0,
        email TEXT DEFAULT NULL,
        reset_token TEXT DEFAULT NULL,
        reset_expiry INTEGER DEFAULT NULL
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
    
    # Appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        service_id INTEGER,
        phone_number TEXT DEFAULT NULL,
        FOREIGN KEY(username) REFERENCES users(username),
        FOREIGN KEY(service_id) REFERENCES services(id)
    )
    """)
    
    conn.commit()
    conn.close()

def seed_admin():
    conn = get_conn()
    cursor = conn.cursor()
    admin_username = "admin"
    admin_password = "1234"  # Default password; hash in auth.py if needed

    cursor.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            (admin_username, admin_password, 1)
        )
        conn.commit()
    conn.close()

def is_admin(username):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

def promote_to_admin(current_user):
    if not is_admin(current_user):
        print("You do not have permission to promote users.")
        return

    target = input("Enter username to promote: ")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (target,))
    if cursor.rowcount > 0:
        print(f"{target} is now an admin.")
    else:
        print("No such user.")
    conn.commit()
    conn.close()
