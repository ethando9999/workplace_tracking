import io
from PIL import Image
from deepface import DeepFace
from vector_db import qdrant_client
from database import insert_track
from datetime import datetime
import numpy as np


class TrackLogger:
    @staticmethod
    def insert_track(staff_id, zone_id, timestamp):
        # This function should log tracking information in the database
        print(f"Track logged: Staff ID {staff_id}, Zone ID {zone_id}, Timestamp {timestamp}")
        # Add the actual database insertion logic here.


class FaceTracker:
    def __init__(self, qdrant_db, model_name="Facenet512", threshold=0.3):
        self.qdrant_db = qdrant_db
        self.model_name = model_name
        self.threshold = threshold
    
    def process_face(self, cropped_frame_rgb, zone_id):
        try:
            print("Analyzing face...")
            
            # Convert the image from numpy array to PIL Image
            image_pil = Image.fromarray(cropped_frame_rgb)
            
            # Generate the embedding using DeepFace with enforce_detection=False
            query_embedding = DeepFace.represent(
                img_path=np.array(image_pil),  # Directly pass numpy array as input
                model_name=self.model_name,
                enforce_detection=False  # Disable strict face detection
            )[0]["embedding"]
            
            # Search for similar faces in Qdrant
            search_result = self.qdrant_db.search_face(
                collection_name="staff_collection",
                query_embedding=query_embedding,
                limit=1  # Get top 1 similar vector
            )
            
            # Process search result
            for point in search_result:
                staff_id = point.id
                score = point.score
                print(f"Similarity score: {score}")
                
                # Check if the score meets the threshold
                if score < self.threshold:
                    return "Face does not exist in the database!"
                
                # Insert tracking information
                current_datetime = datetime.now()
                TrackLogger.insert_track(staff_id, zone_id, current_datetime)
        
        except ValueError:
            return "Face could not be detected."
        except Exception as e:
            return str(e)
        
        return "Face detected and recorded!"