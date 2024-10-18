from .connect_db import cursor, sqlite_conn

def insert_track(staff_id, zone_id, time):
    # Insert a track into sqlite
    cursor.execute('''INSERT INTO track (staff_id, zone_id, time)
                        VALUES (?, ?, ?)''', (staff_id, zone_id, time))
    sqlite_conn.commit()
    print("Insert track successfully!")

def get_all_track():
    # Fetch all zones from the database
    cursor.execute("SELECT * FROM track")
    tracks = cursor.fetchall()
    return tracks