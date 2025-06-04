import sqlite3
import bcrypt

# Connect to SQLite database
conn = sqlite3.connect("users.db")
c = conn.cursor()

# Ensure the users table exists
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")

# Define the test user credentials
username = "test_user"
plain_password = "test_password"

# Hash the password before storing it
hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Insert the test user into the database
try:
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    print("✅ Test user added successfully.")
except sqlite3.IntegrityError:
    print("⚠️ Username already exists.")

# Close database connection
conn.close()