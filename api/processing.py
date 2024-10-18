import io
from PIL import Image
from deepface import DeepFace
from vector_db import qdrant_client
from database import get_staff_info, insert_track
import cv2
import numpy as np
from database import get_all_zone
from datetime import datetime
import time

def face_processing(frame, zone_id):
    try:
        # Load image from uploaded file
        # image_data = await image_face.read()
        image = Image.open(io.BytesIO(frame))

        # Save image to a file
        output_file = "tmp_image.jpg"  # Đường dẫn và tên file
        image.save(output_file)

        # Generate the embedding using DeepFace with Facenet model
        query_embedding = DeepFace.represent(output_file, model_name="Facenet512")[0]["embedding"]

        # Search for similar faces in Qdrant
        search_result = qdrant_client.search(
            collection_name="staff_collection",
            query_vector=query_embedding,
            limit=1  # Get top 1 similar vector (change if needed)
        )

        for point in search_result:
            staff_id = point.id
            current_datetime = datetime.now()
            insert_track(staff_id, zone_id, current_datetime)

    except ValueError as e:
        return "Face could not be detected."
    except Exception as e:
        return str(e)


def streamming_processing(interval=2, stream_url='http://192.168.1.201/640x480.mjpeg'):
    # Đọc stream video (có thể thay '0' bằng đường dẫn URL hoặc file video)
    video_capture = cv2.VideoCapture(stream_url)  # Nếu dùng webcam thì đặt '0'
    frame_index = 0
    print('Frame', frame_index)

    # Lưu thời gian bắt đầu
    start_time = time.time()

    while True:
        # Đọc từng frame từ video stream
        ret, frame = video_capture.read()

        # Kiểm tra nếu không đọc được frame
        if not ret:
            print("Không đọc được frame")
            break

        # Hiển thị frame hiện tại
        cv2.imshow('Video Frame', frame)

        # Kiểm tra thời gian đã trôi qua
        elapsed_time = time.time() - start_time

        # Cứ 30 giây (hoặc thời gian interval) thì crop frame 1 lần
        if elapsed_time >= interval:
            # Reset thời gian bắt đầu
            start_time = time.time()

            # Create a mask for cropping based on zones
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)

            # Get all zones from database
            zones = get_all_zone()

            # Fill the mask for all zones
            for zone in zones:
                # Extract points for the bounding box
                id, x1, y1, x2, y2, x3, y3, x4, y4 = zone

                # Calculate the bounding box's top-left and bottom-right coordinates
                top_left = (int(min(x1, x3)), int(min(y1, y2)))  # Top-left corner
                bottom_right = (int(max(x2, x4)), int(max(y3, y4)))  # Bottom-right corner

                # Create a rectangle on the mask
                cv2.rectangle(mask, top_left, bottom_right, 255, thickness=cv2.FILLED)

                # Crop the frame to keep only the area within the bounding box
                cropped_frame = cv2.bitwise_and(frame, frame, mask=mask)

                face_processing(cropped_frame, id)
            
                # Hiển thị frame hiện tại
                cv2.imshow('Video Frame', cropped_frame)

                # Lưu frame thành file ảnh
                cv2.imwrite('tmp_image.jpg', frame)
                frame_index += 1
                print(frame_index)

            # Nhấn 'q' để thoát
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            

    # Giải phóng video và đóng các cửa sổ
    video_capture.release()
    cv2.destroyAllWindows()
