from .connect_db import cursor, sqlite_conn

def get_all_zone():
    # Fetch all zones from the database
    cursor.execute("SELECT id, x1, y1, x2, y2, x3, y3, x4, y4 FROM zone")
    zones = cursor.fetchall()
    return zones

def delete_zone(id):
    # Delete the zone with the given id from the database
    cursor.execute("DELETE FROM zone WHERE id = ?", (id,))
    sqlite_conn.commit()  # Commit the transaction to the database
