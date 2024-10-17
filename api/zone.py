from fastapi import FastAPI, File, UploadFile, Form, APIRouter
from database import cursor, sqlite_conn
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
import os
import cv2

# Create routers
zone_router = APIRouter()

# Define API route to add a zone
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
    try:
        # Insert the zone data into SQLite database without specifying the zone_id (it will auto-increment)
        cursor.execute('''INSERT INTO zone (x1, y1, x2, y2, x3, y3, x4, y4) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (x1, y1, x2, y2, x3, y3, x4, y4))

        # Commit the transaction
        sqlite_conn.commit()

        # Retrieve the last inserted zone_id
        zone_id = cursor.lastrowid

        return JSONResponse(content={"message": "Zone added successfully!", "zone_id": zone_id}, status_code=200)

    except Exception as e:
        # Handle any errors and return a message
        return JSONResponse(content={"message": str(e)}, status_code=500)


# Specify a temporary directory for video files
TEMP_DIR = "temp_video_files"
os.makedirs(TEMP_DIR, exist_ok=True)  # Create the directory if it doesn't exist


@zone_router.post("/process_video/")
async def process_video(video_file: UploadFile = File(...)):
    try:
        # Load the video file into a temporary directory
        temp_video_path = os.path.join(TEMP_DIR, "temp_video.mp4")
        with open(temp_video_path, "wb") as temp_video_file:
            temp_video_file.write(await video_file.read())

        # Open the video using OpenCV
        cap = cv2.VideoCapture(temp_video_path)

        # Create a temporary output video file
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_path = os.path.join(TEMP_DIR, "temp_video_output.mp4")
        out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), 
                              (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        # Fetch all zones from the database
        cursor.execute("SELECT x1, y1, x2, y2, x3, y3, x4, y4 FROM zone")
        zones = cursor.fetchall()

        if not zones:
            raise HTTPException(status_code=404, detail="No zones found in the database.")

        # Loop through the video frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Draw bounding boxes based on all zones
            for zone in zones:
                # Extract points for the bounding box
                x1, y1, x2, y2, x3, y3, x4, y4 = zone

                # Calculate the bounding box's top-left and bottom-right coordinates
                top_left = (int(min(x1, x3)), int(min(y1, y2)))  # Top-left corner
                bottom_right = (int(max(x2, x4)), int(max(y3, y4)))  # Bottom-right corner

                # Draw the bounding box
                cv2.rectangle(frame, top_left, bottom_right, color=(0, 255, 0), thickness=2)

            # Write the modified frame to the output video
            out.write(frame)

        # Release resources
        cap.release()
        out.release()

        # Return the processed video file as a streaming response for download
        return StreamingResponse(
            open(output_path, "rb"),
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=temp_video_output.mp4"}
        )

    except Exception as e:
        return {"message": str(e)}