import io
from PIL import Image
from deepface import DeepFace
from vector_db import qdrant_client
from database import insert_track
from datetime import datetime

def track_processing(zone_image_file, zone_id):
    try:
        print("Analyzing face...")
        # Generate the embedding using DeepFace with Facenet model
        query_embedding = DeepFace.represent(zone_image_file, model_name="Facenet512")[0]["embedding"]

        # Search for similar faces in Qdrant
        search_result = qdrant_client.search(
            collection_name="staff_collection",
            query_vector=query_embedding,
            limit=1  # Get top 1 similar vector (change if needed)
        )

        for point in search_result:
            staff_id = point.id
            current_datetime = datetime.now()
            insert_track(staff_id, zone_id, current_datetime)

    except ValueError as e:
        return "Face could not be detected."
    except Exception as e:
        return str(e)
    
    return "Face detected!"