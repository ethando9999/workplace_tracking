import os
import cv2
import numpy as np
import sqlite3
import time

# Specify a temporary directory for processed frame files
TEMP_DIR = "temp_video_files"
os.makedirs(TEMP_DIR, exist_ok=True)  # Create the directory if it doesn't exist

# Initialize database connection (adjust the path to your local database)
db_path = 'database.db'  # Replace with your actual database path
sqlite_conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = sqlite_conn.cursor()

# Function to fetch zones from the database
def fetch_zones():
    """Fetch all zones from the database."""
    cursor.execute("SELECT x1, y1, x2, y2, x3, y3, x4, y4 FROM zone")
    zones = cursor.fetchall()
    if not zones:
        print("No zones found in the database.")
    return zones

# Function to create a mask for the zones
def create_zone_mask(frame):
    """Create a mask for the zones to be used for capturing only the areas within the zones."""
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    zones = fetch_zones()

    for zone in zones:
        x1, y1, x2, y2, x3, y3, x4, y4 = zone
        top_left = (int(min(x1, x3)), int(min(y1, y2)))
        bottom_right = (int(max(x2, x4)), int(max(y3, y4)))
        cv2.rectangle(mask, top_left, bottom_right, 255, thickness=cv2.FILLED)

    return mask

# Function to process a frame by drawing bounding boxes
def process_frame(frame):
    # Fetch all zones from the database
    zones = fetch_zones()

    if not zones:
        return frame

    # Draw bounding boxes for each zone
    for zone in zones:
        x1, y1, x2, y2, x3, y3, x4, y4 = zone
        top_left = (int(min(x1, x3)), int(min(y1, y2)))
        bottom_right = (int(max(x2, x4)), int(max(y3, y4)))
        cv2.rectangle(frame, top_left, bottom_right, color=(0, 255, 0), thickness=2)

    return frame

def start_webcam_processing():
    cap = cv2.VideoCapture(0)  # Open webcam stream (0 is default webcam)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting live webcam stream. Capturing a frame every 5 seconds...")
    start_time = time.time()  # Record the starting time
    capture_interval = 5  # Time interval in seconds to capture frames

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from webcam. Exiting...")
            break

        # Process the frame to draw bounding boxes
        processed_frame = process_frame(frame)

        # Display the processed frame
        cv2.imshow('Live Webcam Processing', processed_frame)

        # Capture a frame every 5 seconds
        if time.time() - start_time >= capture_interval:
            print("Capturing frame...")

            # Create a mask for the zones
            mask = create_zone_mask(frame)

            # Apply the mask to the processed frame to get only the zone areas
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

            # Save the masked frame with zones only
            filename = os.path.join(TEMP_DIR, f"captured_frame_{int(time.time())}.png")  # Unique filename
            cv2.imwrite(filename, masked_frame)
            print("Frame with zones captured and saved to", filename)

            start_time = time.time()  # Reset the start time for the next capture

        # Wait for 'q' key to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

