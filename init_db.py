# init_db.py

import sqlite3

# Connect or create the SQLite database
conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

# Insert a default admin user (if not already inserted)
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('admin', 'admin123'))

# Commit and close
conn.commit()
conn.close()

print("✅ Database and table initialized!")
