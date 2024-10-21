from fastapi import FastAPI, File, UploadFile, Form, APIRouter
from database import get_staff_info, insert_staff
from deepface import DeepFace
from PIL import Image
import numpy as np
from vector_db import qdrant_client, models
import uuid
from fastapi.responses import JSONResponse
import io

# Create routers
staff_router = APIRouter()

# Helper function: process image and return embedding
def generate_face_embedding(image_data):
    try:
        # Open the image and convert it to a numpy array
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)

        # Generate the face embedding
        embedding = DeepFace.represent(
            img_path=image_np,  # Use the numpy array as input
            model_name="Facenet512",
            enforce_detection=False  # Set enforce_detection to False
        )[0]["embedding"]

        return embedding
    except Exception as e:
        raise ValueError(f"Failed to generate embedding: {str(e)}")

# Define API route to add a staff member
@staff_router.post("/add_staff/")
async def add_staff(
    name: str = Form(...),
    age: int = Form(...),
    position: str = Form(...),
    face_image: UploadFile = File(...)
):
    try:
        # Read image data and generate face embedding
        image_data = await face_image.read()
        embedding = generate_face_embedding(image_data)

        # Generate a UUID for the Qdrant point ID
        staff_id = str(uuid.uuid4())  # Generate a UUID

        # Save staff data into SQLite
        insert_staff(staff_id, name, age, position)

        # Add face embedding to Qdrant staff collection
        qdrant_client.upsert(
            collection_name="staff_collection",
            points=[
                models.PointStruct(
                    id=staff_id,
                    vector=embedding,  # Face embedding
                )
            ]
        )

        # Return success response
        return JSONResponse(content={"message": "Staff added successfully!", "staff_id": staff_id}, status_code=200)

    except ValueError as ve:
        return JSONResponse(content={"message": str(ve)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

# Define API route for querying similar face images
async def query_image_face(image_face: UploadFile = File(...)):
    try:
        # Load image from uploaded file
        image_data = await image_face.read()
        image = Image.open(io.BytesIO(image_data))

        # Save image to a file
        output_file = "tmp_image.jpg"
        image.save(output_file)

        # Generate the embedding using DeepFace with enforce_detection=False
        query_embedding = DeepFace.represent(
            img_path=output_file,
            model_name="Facenet512",
            enforce_detection=False  # Set enforce_detection to False
        )[0]["embedding"]

        # Search for similar faces in Qdrant
        search_result = qdrant_client.search(
            collection_name="staff_collection",
            query_vector=query_embedding,
            limit=1  # Get top 1 similar vector (change if needed)
        )

        # Prepare the result
        similar_faces = []
        for point in search_result:
            staff_info = get_staff_info(point.id)
            similar_faces.append({
                "score": point.score,  # Similarity score
                "staff_info": staff_info
            })

        return JSONResponse(content={"similar_faces": similar_faces}, status_code=200)

    except ValueError as e:
        return JSONResponse(content={"message": "Face could not be detected."})
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

    
# Define API route for querying similar face images
# @staff_router.post("/query_face_image/")
# async def query_image_face(image_face: UploadFile = File(...)):
#     try:
#         # Load image from uploaded file
#         image_data = await image_face.read()
#         image = Image.open(io.BytesIO(image_data))

#         # Save image to a file
#         output_file = "tmp_image.jpg"  # Đường dẫn và tên file
#         image.save(output_file)

#         # Generate the embedding using DeepFace with Facenet model
#         query_embedding = DeepFace.represent(output_file, model_name="Facenet512")[0]["embedding"]

#         # Search for similar faces in Qdrant
#         search_result = qdrant_client.search(
#             collection_name="staff_collection",
#             query_vector=query_embedding,
#             limit=1  # Get top 1 similar vector (change if needed)
#         )

#         # Prepare the result
#         similar_faces = []
#         for point in search_result:
#             staff_info = get_staff_info(point.id)
#             print(staff_info)
#             similar_faces.append({
#                 "score": point.score, # Similarity score
#                 "staff_info": staff_info
#             })

#         return JSONResponse(content={"similar_faces": similar_faces}, status_code=200)

#     except ValueError as e:
#         return JSONResponse(content={"message": "Face could not be detected."})
#     except Exception as e:
#         return JSONResponse(content={"message": str(e)}, status_code=500)
    
