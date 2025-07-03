# init_db.py

import sqlite3

conn = sqlite3.connect('db.sqlite')  # Makes/opens db.sqlite in current directory
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
''')

cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'admin123')")
conn.commit()
conn.close()

print("✅ Database and table initialized!")
