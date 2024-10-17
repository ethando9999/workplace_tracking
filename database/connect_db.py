import sqlite3

# Initialize SQLite database
sqlite_conn = sqlite3.connect('database.db')
cursor = sqlite_conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        position TEXT,
        face_image BLOB
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS zone (
        id INTEGER PRIMARY KEY,
        x1 REAL,
        y1 REAL,
        x2 REAL,
        y2 REAL
    )
''')

sqlite_conn.commit()