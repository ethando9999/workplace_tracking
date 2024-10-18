import cv2
import numpy as np
import time
import requests
from database import get_all_zone
from .zone_procesing import draw_bounding_box
from .face_processing import track_processing

def camera_streamming_processing(interval=2, stream_url='http://192.168.1.201/640x480.mjpeg'):
    # Gửi yêu cầu GET để nhận dữ liệu từ stream
    stream = requests.get(stream_url, stream=True)
    
    # Biến để chứa dữ liệu hình ảnh
    bytes_data = b''
    start_time = time.time()

    for chunk in stream.iter_content(chunk_size=1024):
        # Thêm dữ liệu mới vào bytes_data
        bytes_data += chunk

        # Tìm kiếm ký tự EOI của frame JPEG
        a = bytes_data.find(b'\xff\xd8')  # SOI (Start of Image)
        b = bytes_data.find(b'\xff\xd9')  # EOI (End of Image)

        # Nếu tìm thấy cả SOI và EOI, xử lý frame JPEG
        if a != -1 and b != -1:
            # Extract frame JPEG
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]

            # Chuyển đổi dữ liệu JPEG thành frame
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)        

            if frame is not None: 

                start = False # flag to starting time   

                # Get all zones from database
                zones = get_all_zone()

                # Fill the mask for all zones
                for zone in zones:
                    # Extract points for the bounding box
                    zone_id, x1, y1, x2, y2, x3, y3, x4, y4 = zone

                    # Calculate the bounding box's top-left and bottom-right coordinates
                    top_left = (int(min(x1, x3)), int(min(y1, y2)))  # Top-left corner
                    bottom_right = (int(max(x2, x4)), int(max(y3, y4)))  # Bottom-right corner

                    # Draw a bounding box on the frame.
                    frame = draw_bounding_box(frame, top_left, bottom_right)

                    # Kiểm tra thời gian đã trôi qua
                    elapsed_time = time.time() - start_time

                    # Cứ 30 giây (hoặc thời gian interval) thì crop frame 1 lần
                    if elapsed_time >= interval:
                        # Create a mask for cropping based on zones
                        mask = np.zeros(frame.shape[:2], dtype=np.uint8)

                        # Create a rectangle on the mask
                        cv2.rectangle(mask, top_left, bottom_right, 255, thickness=cv2.FILLED)

                        # Crop the frame to keep only the area within the bounding box
                        cropped_frame = cv2.bitwise_and(frame, frame, mask=mask)

                        # Save the cropped frame to a file
                        output_file = "tmp_image.jpg"
                        cv2.imwrite(output_file, cropped_frame)
                        print("Cropped frame saved at tmp_image.jpg")

                        # track processing
                        track = track_processing(output_file, zone_id)
                        print(track)
                        
                        start = True # start to count down time

                if start:    
                    start_time = time.time()       
                # Hiển thị frame hiện tại
                cv2.imshow('Video Frame', frame)
                
                # Thoát khi nhấn phím 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cv2.destroyAllWindows()

def webcam_processing(interval=5):
    cap = cv2.VideoCapture(0)  # Open webcam stream (0 is default webcam)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting live webcam stream. Capturing a frame every 5 seconds...")
    start_time = time.time()  # Record the starting time


    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame from webcam. Exiting...")
            cap.release()
            break

        if frame is not None: 
            # flag to starting time       
            start = False              
            # Get all zones from database
            zones = get_all_zone()

            # Fill the mask for all zones
            for zone in zones:
                # Extract points for the bounding box
                zone_id, x1, y1, x2, y2, x3, y3, x4, y4 = zone

                # Calculate the bounding box's top-left and bottom-right coordinates
                top_left = (int(min(x1, x3)), int(min(y1, y2)))  # Top-left corner
                bottom_right = (int(max(x2, x4)), int(max(y3, y4)))  # Bottom-right corner

                # Draw a bounding box on the frame.
                frame = draw_bounding_box(frame, top_left, bottom_right)

                # Kiểm tra thời gian đã trôi qua
                elapsed_time = time.time() - start_time

                # Cứ 30 giây (hoặc thời gian interval) thì crop frame 1 lần
                if elapsed_time >= interval:
                    # Create a mask for cropping based on zones
                    mask = np.zeros(frame.shape[:2], dtype=np.uint8)

                    # Create a rectangle on the mask
                    cv2.rectangle(mask, top_left, bottom_right, 255, thickness=cv2.FILLED)

                    # Crop the frame to keep only the area within the bounding box
                    cropped_frame = cv2.bitwise_and(frame, frame, mask=mask)

                    # Save the cropped frame to a file
                    output_file = "tmp_image.jpg"
                    cv2.imwrite(output_file, cropped_frame)
                    print("Cropped frame saved at tmp_image.jpg")

                    # track processing
                    track = track_processing(output_file, zone_id)
                    print(track)

                    start = True # start to count down time

            if start:    
                start_time = time.time() 

            # Hiển thị frame hiện tại
            cv2.imshow('Video Frame', frame)
            
            # Thoát khi nhấn phím 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                break

    # Release resources
    cv2.destroyAllWindows()
