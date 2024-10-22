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

    def embedding_face(self, cropped_frame_rgb, byte_image=False):
        try:
            print("Analyzing face...")

            if byte_image:
                # Open the image and convert it to a numpy array
                image_pil = Image.open(io.BytesIO(cropped_frame_rgb))
            else:
                # Convert the image from numpy array to PIL Image for real-time processing
                image_pil = Image.fromarray(cropped_frame_rgb)

            detected_face = DeepFace.detectFace(
                np.array(image_pil),  # Directly pass numpy array as input
                detector_backend='opencv'
            )
            print(self.model_name)
            print("Face detected!")

            # Ensure detected_face is in the correct format (numpy array)
            if isinstance(detected_face, np.ndarray):
                # Generate the embedding using DeepFace
                face_embedding = DeepFace.represent(
                    img_path=detected_face,  # Pass the numpy array directly
                    model_name=self.model_name,
                    enforce_detection=False  # Disable strict face detection
                )[0]["embedding"]

                print("Successful embedding face!")
            else:
                raise ValueError("Detected face is not a valid numpy array.")

        except Exception as e:
            print(e)
            return str(e)

        return face_embedding
    
    def tracking_face(self, cropped_frame_rgb, zone_id):
        try:
            query_embedding = self.embedding_face(cropped_frame_rgb)
            
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
    
        except Exception as e:
            return str(e)
        
        return "TRACKING SUCCESSFULLY!"
