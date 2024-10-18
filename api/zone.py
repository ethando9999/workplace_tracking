import os
import cv2
import numpy as np
import threading
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from database import cursor, sqlite_conn

# Create FastAPI instance and router
app = FastAPI()
zone_router = APIRouter()

# Specify a temporary directory for video files
TEMP_DIR = "temp_video_files"
os.makedirs(TEMP_DIR, exist_ok=True)  # Create the directory if it doesn't exist

# Initialize a variable to hold the latest frame captured from the camera
latest_frame = None

# Start capturing video from the camera in a separate thread
def capture_video():
    global latest_frame
    cap = cv2.VideoCapture(0)  # Use the first camera
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        latest_frame = frame
        cv2.waitKey(30)  # Capture at approximately 30 FPS
    cap.release()

# Start the camera capture thread
threading.Thread(target=capture_video, daemon=True).start()

# Utility function to upload video file
async def upload_video_file(video_file: UploadFile) -> str:
    """Save the uploaded video file to a temporary path."""
    try:
        temp_video_path = os.path.join(TEMP_DIR, "temp_video.mp4")
        with open(temp_video_path, "wb") as temp_video:
            temp_video.write(await video_file.read())
        return temp_video_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")

# Function to fetch zones from the database
def fetch_zones():
    """Fetch all zones from the database."""
    cursor.execute("SELECT x1, y1, x2, y2, x3, y3, x4, y4 FROM zone")
    zones = cursor.fetchall()
    if not zones:
        raise HTTPException(status_code=404, detail="No zones found in the database.")
    return zones

# Function to process video stream and draw bounding boxes
def process_video(video_path: str, draw_bounding: bool = True) -> str:
    """Process the video by drawing bounding boxes or cutting zones based on the input."""
    cap = cv2.VideoCapture(video_path)

    # Create an output video file
    output_path = os.path.join(TEMP_DIR, "temp_video_output.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    # Fetch all zones from the database
    zones = fetch_zones()

    # Process each frame of the video
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if draw_bounding:
            # Draw bounding boxes for each zone
            for zone in zones:
                x1, y1, x2, y2, x3, y3, x4, y4 = zone
                top_left = (int(min(x1, x3)), int(min(y1, y2)))
                bottom_right = (int(max(x2, x4)), int(max(y3, y4)))
                cv2.rectangle(frame, top_left, bottom_right, color=(0, 255, 0), thickness=2)
        else:
            # Create a mask for cropping based on zones
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            for zone in zones:
                x1, y1, x2, y2, x3, y3, x4, y4 = zone
                top_left = (int(min(x1, x3)), int(min(y1, y2)))
                bottom_right = (int(max(x2, x4)), int(max(y3, y4)))
                cv2.rectangle(mask, top_left, bottom_right, 255, thickness=cv2.FILLED)

            # Crop the frame to keep only the area within the bounding box
            frame = cv2.bitwise_and(frame, frame, mask=mask)

        # Write the modified frame to the output video
        out.write(frame)

    # Release resources
    cap.release()
    out.release()
    return output_path

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

# Endpoint to draw bounding boxes on a video
@zone_router.post("/draw_bounding/")
async def draw_bounding(video_file: UploadFile = File(...)):
    """Upload a video, draw bounding boxes based on zones from the database, and return the processed video."""
    try:
        video_path = await upload_video_file(video_file)
        processed_video_path = process_video(video_path, draw_bounding=True)
        return StreamingResponse(
            open(processed_video_path, "rb"),
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=temp_video_output.mp4"}
        )
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

# Endpoint to cut zones from a video
@zone_router.post("/cut_zone/")
async def cut_zone(video_file: UploadFile = File(...)):
    """Upload a video, cut out zones based on the database, and return the processed video."""
    try:
        video_path = await upload_video_file(video_file)
        processed_video_path = process_video(video_path, draw_bounding=False)
        return StreamingResponse(
            open(processed_video_path, "rb"),
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=temp_video_output.mp4"}
        )
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

# Endpoint to capture a frame from the live camera
@app.get("/capture_frame/")
async def capture_frame():
    """Capture a frame from the live camera."""
    global latest_frame
    if latest_frame is None:
        raise HTTPException(status_code=404, detail="No frame captured yet.")
    
    # Save the captured frame as an image
    frame_path = os.path.join(TEMP_DIR, "captured_frame.jpg")
    cv2.imwrite(frame_path, latest_frame)

    return StreamingResponse(
        open(frame_path, "rb"),
        media_type="image/jpeg",
        headers={"Content-Disposition": "attachment; filename=captured_frame.jpg"}
    )
