import io
from PIL import Image
from deepface import DeepFace
from database import insert_track
from datetime import datetime
import numpy as np
import os



class FaceTracker:
    def __init__(self, vector_db, model_name= None, threshold=0.3):
        self.vector_db = vector_db
        self.model_name = model_name if model_name else os.getenv('EMBEDDING_MODEL')
        self.threshold = threshold
    
    def process_face(self, cropped_frame_rgb, zone_id):
        try:
            print("Analyzing face...")

            # Convert the image from numpy array to PIL Image for realtime processing
            image_pil = Image.fromarray(cropped_frame_rgb)

            detected_faces = DeepFace.detectFace(
                np.array(image_pil), # Directly pass numpy array as input 
                detector_backend='opencv'
            )

            # Generate the embedding using DeepFace with enforce_detection=False
            query_embedding = DeepFace.represent(
                img_path=detected_faces,  
                model_name=self.model_name,
                enforce_detection=False  # Disable strict face detection
            )[0]["embedding"]

            print(query_embedding)
            
            # Search for similar faces in Qdrant
            search_result = self.vector_db.search_vectors(
                collection_name="staff_collection",
                query_vector=query_embedding,
                top_k=1  # Get top 1 similar vector
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
                print(f"Track logged: Staff ID {staff_id}, Zone ID {zone_id}, Timestamp {current_datetime}")
                insert_track(staff_id, zone_id, current_datetime)
    
        except ValueError:
            return "Face could not be detected."
        except Exception as e:
            return str(e)
        
        return "Face detected and recorded!"
