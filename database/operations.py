from .connect_db import cursor
import pickle

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
