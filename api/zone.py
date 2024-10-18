import os
import cv2
import numpy as np
import threading
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from database import cursor, sqlite_conn

# Create FastAPI instance and router
zone_router = APIRouter()

# Endpoint to add a zone
@zone_router.post("/add_zone/")
async def add_zone(
    x1: float = Form(...),
    y1: float = Form(...),
    x2: float = Form(...),
    y2: float = Form(...),
    x3: float = Form(...),
    y3: float = Form(...),
    x4: float = Form(...),
    y4: float = Form(...)
):
    """Add a new zone to the database."""
    try:
        cursor.execute('''INSERT INTO zone (x1, y1, x2, y2, x3, y3, x4, y4) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (x1, y1, x2, y2, x3, y3, x4, y4))
        sqlite_conn.commit()
        zone_id = cursor.lastrowid
        return JSONResponse(content={"message": "Zone added successfully!", "zone_id": zone_id}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)