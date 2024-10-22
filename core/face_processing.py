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

            # Convert byte image to numpy array if necessary
            if byte_image:
                image_pil = Image.open(io.BytesIO(cropped_frame_rgb))
            else:
                image_pil = Image.fromarray(cropped_frame_rgb)

            # # Detect faces using extract_faces instead of the deprecated detectFace
            # faces = DeepFace.extract_faces(
            #     np.array(image_pil),  # Convert the PIL image to numpy array
            #     detector_backend='opencv',
            #     enforce_detection=False
            # )

            # if len(faces) == 0:
            #     raise ValueError("No face detected.")

            # print("Face detected!")

            # Extract the face image
            # detected_face = faces[0]['face']

            # Ensure detected_face is a valid numpy array
        #     if isinstance(detected_face, np.ndarray):
        #         # Generate the embedding using DeepFace
        #         face_embedding = DeepFace.represent(
        #             img_path=np.array(image_pil),  # Directly pass numpy array as input
        #             model_name=self.model_name,
        #             enforce_detection=False
        #         )[0]["embedding"]

        #         print("Successful embedding face!")
        #     else:
        #         raise ValueError("Detected face is not a valid numpy array.")
        # except ValueError as v:
        #     print(v)
        #     return 
            face_embedding = DeepFace.represent(
                img_path=np.array(image_pil),  # Directly pass numpy array as input
                model_name=self.model_name,
                enforce_detection=True # # Eable strict face detection
            )[0]["embedding"]

        except Exception as e:
            print(f"Error: {e}")
            return str(e)

        return face_embedding
    
    def tracking_face(self, cropped_frame_rgb, zone_id):

        query_embedding = self.embedding_face(cropped_frame_rgb)
        if type(query_embedding) == str:
            print("No face detected")
            return
        
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
                print("Face does not exist in the database!")
                break

            # Insert tracking information
            current_datetime = datetime.now()
            print(f"Track logged: Staff ID {staff_id}, Zone ID {zone_id}, Timestamp {current_datetime}")
            insert_track(staff_id, zone_id, current_datetime)
            print("TRACKING SUCCESSFULLY!")       
        
         
