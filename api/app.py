from deepface import DeepFace
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from qdrant_client import QdrantClient, models
from PIL import Image
import numpy as np
from database import cursor, fetch_staff_embeddings
from staff_router import staff_router
from zone_router import zone_router

# Initialize FastAPI app
app = FastAPI()
# Add routers to the main FastAPI app
app.include_router(staff_router)
app.include_router(zone_router)

# Create Qdrant Client (in-memory database for this example)
qdrant_client = QdrantClient(":memory:")

# Create collections for Staff and Zone tables in Qdrant
qdrant_client.create_collection(
    collection_name="staff_collection",
    vectors_config=models.VectorParams(
        size=128,  # Facenet typically outputs 128-dimensional vectors
        distance=models.Distance.COSINE,
    ),
)

qdrant_client.create_collection(
    collection_name="zone_collection",
    vectors_config=models.VectorParams(
        size=4,  # Zone has 4 coordinates: x1, y1, x2, y2
        distance=models.Distance.EUCLID,  # Euclidean distance for zones
    ),
)

@app.post("/tracking_changes/")
async def track_changes():
    try:
        # Fetch staff data from SQLite
        cursor.execute("SELECT * FROM staff")
        staff_rows = cursor.fetchall()
        
        staff_data = []
        for staff in staff_rows:
            staff_id, name, age, position, face_image = staff
            
            # Fetch zones for the current staff member
            cursor.execute("SELECT * FROM zone WHERE staff_id = ?", (staff_id,))
            zone_rows = cursor.fetchall()
            zones = [
                {
                    "id": zone[0],
                    "staff_id": zone[1],
                    "coordinates": zone[2:10]  # x1, y1, x2, y2, x3, y3, x4, y4
                }
                for zone in zone_rows
            ]
            
            staff_data.append({
                "id": staff_id,
                "name": name,
                "age": age,
                "position": position,
                "zones": zones
            })

        # Fetch staff embeddings
        staff_embeddings = fetch_staff_embeddings()

        # Combine staff data with embeddings
        for staff in staff_data:
            # Find the corresponding embedding for the current staff member
            embedding = next((emb for emb_id, emb in staff_embeddings if emb_id == staff['id']), None)
            staff['face_img'] = embedding  # Add the embedding to the staff data

        return JSONResponse(content={"staff_data": staff_data}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)