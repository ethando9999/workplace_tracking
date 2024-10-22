import cv2
import numpy as np
import requests
import time
from database import get_all_zone

class RT_Tracking:
    def __init__(self, face_tracker, cam_device='webcam', interval=5, stream_url=None):
        """
        Initialize the RT_Tracking object.
        :param cam_device: Type of camera device ('camera' for stream, 'webcam' for local webcam).
        :param interval: Time interval in seconds for cropping frames.
        :param stream_url: URL for the camera stream (Only used if cam_device is 'camera').
        """
        self.face_tracker = face_tracker
        self.cam_device = cam_device
        self.interval = interval
        self.stream_url = stream_url if cam_device == 'camera' else None
        self.start_time = time.time()

        if self.cam_device == 'camera' and not self.stream_url:
            raise ValueError("stream_url must be provided when cam_device is 'camera'.")

    def draw_bounding_box(self, frame, top_left, bottom_right):
        """
        Draw a bounding box on the frame.
        :param frame: The video frame.
        :param top_left: Top-left corner of the bounding box.
        :param bottom_right: Bottom-right corner of the bounding box.
        :return: Frame with bounding box drawn.
        """
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
        return frame

    def process_frame(self, frame, elapsed_time):
        """
        Process the frame by applying bounding boxes and cropping.
        :param frame: The current video frame.
        :param elapsed_time: Time elapsed since last capture.
        """
        start = False
        zones = get_all_zone()

        for zone in zones:
            zone_id, x1, y1, x2, y2, x3, y3, x4, y4 = zone
            top_left = (int(min(x1, x3)), int(min(y1, y2)))
            bottom_right = (int(max(x2, x4)), int(max(y3, y4)))

            # Draw bounding box
            frame = self.draw_bounding_box(frame, top_left, bottom_right)

            if elapsed_time >= self.interval:
                mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                cv2.rectangle(mask, top_left, bottom_right, 255, thickness=cv2.FILLED)
                cropped_frame = cv2.bitwise_and(frame, frame, mask=mask)

                # output_file = "tmp_image.jpg"
                # cv2.imwrite(output_file, cropped_frame)
                # print("Cropped frame saved at tmp_image.jpg")

                track = self.face_tracker.tracking_face(cropped_frame, zone_id)
                print(track)

                start = True

        return start

    def camera_streamming_processing(self):
        """
        Process video stream from a camera (e.g., IP camera).
        Only used if cam_device is 'camera'.
        """
        if self.cam_device != 'camera':
            raise ValueError("This method is only available for camera stream processing.")

        stream = requests.get(self.stream_url, stream=True)
        bytes_data = b''
        self.start_time = time.time()

        for chunk in stream.iter_content(chunk_size=1024):
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8')  # SOI
            b = bytes_data.find(b'\xff\xd9')  # EOI

            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                if frame is not None:
                    elapsed_time = time.time() - self.start_time
                    start = self.process_frame(frame, elapsed_time)

                    if start:
                        self.start_time = time.time()

                    cv2.imshow('Video Frame', frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

        cv2.destroyAllWindows()

    def webcam_processing(self):
        """
        Process frames from a local webcam.
        Only used if cam_device is 'webcam'.
        """
        if self.cam_device != 'webcam':
            raise ValueError("This method is only available for webcam processing.")

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        print("Starting live webcam stream...")
        self.start_time = time.time()

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Failed to capture frame from webcam. Exiting...")
                cap.release()
                break

            if frame is not None:
                elapsed_time = time.time() - self.start_time
                start = self.process_frame(frame, elapsed_time)

                if start:
                    self.start_time = time.time()

                cv2.imshow('Video Frame', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()

    def start_processing(self):
        """
        Start processing based on the cam_device attribute.
        """
        if self.cam_device == 'camera':
            self.camera_streamming_processing()
        elif self.cam_device == 'webcam':
            self.webcam_processing()
        else:
            raise ValueError(f"Unknown cam_device: {self.cam_device}. Must be 'camera' or 'webcam'.")

