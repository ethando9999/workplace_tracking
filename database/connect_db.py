import sqlite3

# Initialize SQLite database
sqlite_conn = sqlite3.connect('database.db')
cursor = sqlite_conn.cursor()


# Create tables for staff and zone
cursor.execute('''CREATE TABLE IF NOT EXISTS staff (
    id TEXT PRIMARY KEY,  -- Change id type to TEXT for alphanumeric IDs
    name TEXT,
    age INTEGER,
    position TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS zone (
    id INTEGER PRIMARY KEY,
    x1 REAL, y1 REAL, 
    x2 REAL, y2 REAL, 
    x3 REAL, y3 REAL, 
    x4 REAL, y4 REAL
)''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS track (
        staff_id TEXT,
        zone_id INTEGER,
        time DATETIME,
        FOREIGN KEY (staff_id) REFERENCES staff(id),
        FOREIGN KEY (zone_id) REFERENCES zone(id)
    )
''')
sqlite_conn.commit()