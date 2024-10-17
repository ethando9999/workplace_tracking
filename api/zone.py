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
zone_router = APIRouter()


# Define API route to add a zone
@zone_router.post("/add_zone/")
async def add_zone(
    staff_id: str = Form(...),  # Change type to str for alphanumeric staff IDs
    x1: float = Form(...),
    y1: float = Form(...),
    x2: float = Form(...),
    y2: float = Form(...),
    x3: float = Form(...),
    y3: float = Form(...),
    x4: float = Form(...),
    y4: float = Form(...)
):
    try:
        # Save zone data into SQLite
        cursor.execute('''INSERT INTO zone (staff_id, x1, y1, x2, y2, x3, y3, x4, y4) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (staff_id, x1, y1, x2, y2, x3, y3, x4, y4))

        # Commit to the SQLite database
        sqlite_conn.commit()

        # Add zone data to Qdrant zone collection
        qdrant_client.upsert(
            collection_name="zone_collection",
            points=[
                models.PointStruct(
                    id=staff_id,  # Use the staff_id directly
                    vector=[x1, y1, x2, y2, x3, y3, x4, y4],
                    payload={"staff_id": staff_id}
                )
            ]
        )

        return JSONResponse(content={"message": "Zone added successfully!", "staff_id": staff_id}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)