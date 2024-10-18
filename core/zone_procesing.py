import cv2

def draw_bounding_box(frame, top_left, bottom_right, color=(0, 255, 0), thickness=2):
    """
    Draw a bounding box on the given frame.

    Parameters:
        frame (numpy array): The video frame where the bounding box will be drawn.
        top_left (tuple): Coordinates (x, y) of the top-left corner of the bounding box.
        bottom_right (tuple): Coordinates (x, y) of the bottom-right corner of the bounding box.
        color (tuple): The color of the bounding box in BGR format (default is green).
        thickness (int): Thickness of the bounding box lines (default is 2).
    
    Returns:
        frame (numpy array): The frame with the bounding box drawn.
    """
    cv2.rectangle(frame, top_left, bottom_right, color, thickness)
    return frame