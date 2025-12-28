import sqlite3
import hashlib
import os

DB_NAME = "refundops.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            gmail_email TEXT,
            gmail_app_pass TEXT
        )
    ''')
    # Stats Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            key TEXT PRIMARY KEY,
            value INTEGER
        )
    ''')
    # Initialize 'refund_count' if not exists
    c.execute("INSERT OR IGNORE INTO stats (key, value) VALUES ('refund_count', 0)")
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, gmail, app_pass):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        hashed = hash_password(password)
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, hashed, gmail, app_pass))
        conn.commit()
        conn.close()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, str(e)

def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("SELECT gmail_email, gmail_app_pass FROM users WHERE username=? AND password_hash=?", (username, hashed))
    result = c.fetchone()
    conn.close()
    if result:
        return True, result[0], result[1] # Return gmail, app_pass
    return False, None, None

def increment_refund_count():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE stats SET value = value + 1 WHERE key = 'refund_count'")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"DB Error: {e}")
        return False

def get_stats():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT value FROM stats WHERE key = 'refund_count'")
        result = c.fetchone()
        conn.close()
        count = result[0] if result else 0
        return {
            "refunds_processed": count,
            "time_saved_minutes": count * 8,  # Assume 8 mins per refund
            "money_saved_inr": count * 4500   # Assume ₹4,500 per refund
        }
    except Exception as e:
        return {"refunds_processed": 0, "time_saved_minutes": 0, "money_saved_usd": 0}
