from .connect_db import cursor
import pickle
import json

# Example for querying and deserializing embeddings
def fetch_staff_embeddings():
    cursor.execute("SELECT id, face_image FROM staff")
    rows = cursor.fetchall()
    staff_embeddings = []
    for row in rows:
        staff_id = row[0]
        embedding_bytes = row[1]
        embedding = pickle.loads(embedding_bytes)  # Deserialize back to list
        staff_embeddings.append((staff_id, embedding))
    return staff_embeddings

def load_staff():
    cursor.execute("SELECT id, name, age, position FROM staff")
    rows = cursor.fetchall()
    return rows

def get_staff_info(id: str):
    query = "SELECT name, age, position FROM staff WHERE staff.id = ?"
    cursor.execute(query, (id,))
    row = cursor.fetchone()  # Fetch a single record

    if row:
        staff_info = {
            'name': row[0],
            'age': row[1],
            'position': row[2]
        }
        return staff_info  
    else:
        return {}  # Return an empty JSON if no record is found