from .connect_db import cursor, sqlite_conn

def insert_track(staff_id, zone_id, time):
    # Insert a track into sqlite
    cursor.execute('''INSERT INTO track (staff_id, zone_id, time)
                        VALUES (?, ?, ?)''', (staff_id, zone_id, time))
    sqlite_conn.commit()
    print("Insert track successfully!")
