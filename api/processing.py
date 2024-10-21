import os
import cv2
import numpy as np
import sqlite3
import threading
from api import zone_tmp

# Specify a temporary directory for video files (optional)
TEMP_DIR = "temp_video_files"
os.makedirs(TEMP_DIR, exist_ok=True)  # Create the directory if it doesn't exist

# Initialize a variable to hold the latest frame captured from the camera
latest_frame = None

# Initialize database connection (adjust the path to your local database)
db_path = 'your_database.db'  # Replace with your actual database path
sqlite_conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = sqlite_conn.cursor()

# Start capturing video from the camera in a separate thread
def capture_video():
    global latest_frame
    cap = cv2.VideoCapture(0)  # Use the first camera (Webcam)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read from webcam.")
            break
        latest_frame = frame
        cv2.waitKey(30)  # Capture frame at ~30 FPS
    cap.release()

# Start the camera capture thread
threading.Thread(target=capture_video, daemon=True).start()

# Function to fetch zones from the database
def fetch_zones():
    """Fetch all zones from the database."""
    try:
        cursor.execute("SELECT x1, y1, x2, y2, x3, y3, x4, y4 FROM zone")
        zones = cursor.fetchall()
        if not zones:
            print("No zones found in the database.")
        return zones
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return []

# Function to process the frame and draw bounding boxes or cut zones
def process_frame(frame, draw_bounding=True):
    """Process the live frame by drawing bounding boxes or cutting zones."""
    zones = fetch_zones()
    if not zones:
        return frame

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

    return frame

# Function to capture and process the live webcam feed
def run_live_processing(draw_bounding=True):
    start_webcam_processing