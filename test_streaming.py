# from api.processing import streamming_processing
from core import camera_streamming_processing, webcam_processing

if __name__ == "__main__":
    # camera_streamming_processing(interval=5)
    webcam_processing(interval=3)