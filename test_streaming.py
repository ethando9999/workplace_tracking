# from api.processing import streamming_processing
from core import RT_Tracking, face_tracker
import os

stream_url = os.getenv('STREAM_URL')

if __name__ == "__main__":
    # rt_tracker_camera = RT_Tracking(face_tracker, cam_device="camera", interval=5, stream_url=stream_url)
    # rt_tracker_camera.start_processing()
    rt_tracker_webcam = RT_Tracking(face_tracker, cam_device='webcam', interval=5)
    rt_tracker_webcam.start_processing()