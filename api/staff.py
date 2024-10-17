from fastapi import FastAPI, File, UploadFile, Form, APIRouter
from database import cursor, sqlite_conn
from deepface import DeepFace
from PIL import Image
import numpy as np
from vector_db import qdrant_client, models
import pickle
from fastapi.responses import JSONResponse
import io

# Create routers
staff_router = APIRouter()

# Helper function: process image and return embedding
def generate_face_embedding(image_data):
    image = Image.open(io.BytesIO(image_data))
    image_np = np.array(image)
    embedding = DeepFace.represent(image_np, model_name="Facenet")[0]["embedding"]
    return embedding

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

        # Serialize the embedding to bytes
        embedding_bytes = pickle.dumps(embedding)
        
        # Get the next available ID for staff, as alphanumeric (e.g., BE001)
        cursor.execute("SELECT COUNT(*) FROM staff")
        staff_count = cursor.fetchone()[0]
        staff_id = f"BE{staff_count + 1:03d}"  # Generate alphanumeric ID (e.g., BE001, BE002)

        # Save staff data into SQLite
        cursor.execute('''INSERT INTO staff (id, name, age, position, face_image) 
                          VALUES (?, ?, ?, ?, ?)''', (staff_id, name, age, position, embedding_bytes))

        # Commit to the SQLite database
        sqlite_conn.commit()

        # Add face embedding to Qdrant staff collection
        qdrant_client.upsert(
            collection_name="staff_collection",
            points=[
                models.PointStruct(
                    id=staff_id,
                    vector=embedding,  # Face embedding
                    payload={"name": name, "position": position}
                )
            ]
        )

        # Return success response
        return JSONResponse(content={"message": "Staff added successfully!", "staff_id": staff_id}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
# Define API route for querying similar face images
@staff_router.post("/query_image_face/")
async def query_image_face(image_face: UploadFile = File(...)):
    try:
        # Load image from uploaded file
        image_data = await image_face.read()
        image = Image.open(io.BytesIO(image_data))

        # Convert image to numpy array as required by DeepFace
        image_np = np.array(image)

        # Generate the embedding using DeepFace with Facenet model
        query_embedding = DeepFace.represent(image_np, model_name="Facenet")[0]["embedding"]

        # Search for similar faces in Qdrant
        search_result = qdrant_client.search(
            collection_name="staff_collection",
            query_vector=query_embedding,
            top=1  # Get top 5 similar vectors
        )

        # Prepare the result
        similar_faces = []
        for point in search_result:
            similar_faces.append({
                "staff_id": point.id,
                "payload": point.payload,
                "score": point.score  # Similarity score
            })

        return JSONResponse(content={"similar_faces": similar_faces}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
