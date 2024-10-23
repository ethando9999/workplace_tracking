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
        """
        Extract the face embedding from a cropped RGB image.

        :param cropped_frame_rgb: Numpy array or byte representation of the cropped face image.
        :param byte_image: Whether the input is a byte image.
        :return: Face embedding vector or error message.
        """
        try:
            print("Analyzing face...")

            # Convert byte image to numpy array if necessary
            if byte_image:
                image_pil = Image.open(io.BytesIO(cropped_frame_rgb))
                image_np = np.array(image_pil)
            else:
                image_np = cropped_frame_rgb

            # Generate face embedding directly using represent
            face_embedding = DeepFace.represent(
                image_np,  # Pass the image array directly
                model_name=self.model_name,
                detector_backend ='yolo',
                enforce_detection=True  # If no face is detected in an image, raise an exception.
            )[0]["embedding"]

        except ValueError as ve:
            print(f"Value error: {ve}")
            return str(ve)
        except Exception as e:
            print(f"Error in face embedding: {e}")
            return str(e)

        return face_embedding

    
    def tracking_face(self, cropped_frame_rgb, zone_id):
        """
        Track the face within a specific zone by matching it against the vector database.

        :param cropped_frame_rgb: Cropped face image as a numpy array.
        :param zone_id: Identifier for the zone where the face was detected.
        """
        query_embedding = self.embedding_face(cropped_frame_rgb)

        if isinstance(query_embedding, str):  # Check if embedding failed
            print("No face detected or error in embedding.")
            return

        # Search for similar faces in the vector database

        search_result = self.vector_db.search_vectors(
            collection_name="staff_collection",
            query_vector=query_embedding,
            top_k=1  # Get the top 1 similar vector
        )

        if not search_result:
            print("No matching face found in the vector database.")
            return

        for point in search_result:
            staff_id = point.id
            score = point.score
            print(f"Similarity score: {score}")

            # Check if the score meets the threshold
            if score < self.threshold:
                print("Face does not exist in the database or threshold not met.")
                break

            # Insert tracking information
            current_datetime = datetime.now()
            print(f"Track logged: Staff ID {staff_id}, Zone ID {zone_id}, Timestamp {current_datetime}")
            insert_track(staff_id, zone_id, current_datetime)
            print("TRACKING SUCCESSFULLY!")      

# class FaceTracker:
#     def __init__(self, vector_db, model_name=None, threshold=0.3):
#         """
#         Initialize the FaceTracker with a vector database, face recognition model, and threshold for similarity.
        
#         :param vector_db: Vector database instance (e.g., Qdrant)
#         :param model_name: Name of the embedding model. If not provided, it is fetched from the environment variable 'EMBEDDING_MODEL'.
#         :param threshold: Threshold for face similarity score (default is 0.3)
#         """
#         self.vector_db = vector_db
#         self.model_name = model_name if model_name else os.getenv('EMBEDDING_MODEL')
#         self.threshold = threshold

#     def embedding_face(self, cropped_frame_rgb, byte_image=False):
#         """
#         Extract the face embedding from a cropped RGB image.

#         :param cropped_frame_rgb: Numpy array or byte representation of the cropped face image.
#         :param byte_image: Whether the input is a byte image.
#         :return: Face embedding vector or error message.
#         """
#         try:
#             print("Analyzing face...")

#             # Convert byte image to numpy array if necessary
#             if byte_image:
#                 image_pil = Image.open(io.BytesIO(cropped_frame_rgb))
#                 image_np = np.array(image_pil)
#             else:
#                 image_np = cropped_frame_rgb

#             # Detect faces using extract_faces
#             detected_faces = DeepFace.extract_faces(
#                 image_np,
#                 detector_backend='opencv',
#                 enforce_detection=False  # Allow images with no face to be processed
#             )

#             # Check if any faces were detected
#             if detected_faces:
#                 # Access the detected face array using the 'face' key
#                 detected_face = detected_faces[0]['face']

#                 # Convert to uint8
#                 detected_face = (detected_face * 255).astype(np.uint8)

#                 # Display the detected face using cv2_imshow
#                 cv2.imshow('Detected Face', detected_face)

#                 # Generate face embedding for the detected face
#                 face_embedding = DeepFace.represent(
#                     detected_face,  # Pass the cropped face numpy array
#                     model_name=self.model_name,
#                     enforce_detection=False  # Already detected face, no need to enforce again
#                 )[0]["embedding"]
#             else:
#                 return "No face detected or error in embedding."

#         except ValueError as ve:
#             print(f"Value error: {ve}")
#             return str(ve)
#         except Exception as e:
#             print(f"Error in face embedding: {e}")
#             return str(e)

#         return face_embedding

#     def tracking_face(self, cropped_frame_rgb, zone_id):
#         """
#         Track the face within a specific zone by matching it against the vector database.

#         :param cropped_frame_rgb: Cropped face image as a numpy array.
#         :param zone_id: Identifier for the zone where the face was detected.
#         """
#         query_embedding = self.embedding_face(cropped_frame_rgb)

#         if isinstance(query_embedding, str):  # Check if embedding failed
#             print("No face detected or error in embedding.")
#             return

#         # Search for similar faces in the vector database

#         search_result = self.vector_db.search_vectors(
#             collection_name="staff_collection",
#             query_vector=query_embedding,
#             top_k=1  # Get the top 1 similar vector
#         )

#         if not search_result:
#             print("No matching face found in the database.")
#             return

#         for point in search_result:
#             staff_id = point.id
#             score = point.score
#             print(f"Similarity score: {score}")

#             # Check if the score meets the threshold
#             if score < self.threshold:
#                 print("Face does not exist in the database or threshold not met.")
#                 break

#             # Insert tracking information
#             current_datetime = datetime.now()
#             print(f"Track logged: Staff ID {staff_id}, Zone ID {zone_id}, Timestamp {current_datetime}")
#             insert_track(staff_id, zone_id, current_datetime)

