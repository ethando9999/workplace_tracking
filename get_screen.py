from moviepy.editor import VideoFileClip

def get_video_corners(video_path):
    # Load the video
    video = VideoFileClip(video_path)
    
    # Get the size (width, height)
    width, height = video.size

    # Define corner coordinates based on the width and height
    # Bottom-left corner (0, height - 1)
    x1, y1 = 0, height - 1
    # Bottom-right corner (width - 1, height - 1)
    x2, y2 = width - 1, height - 1
    # Top-right corner (width - 1, 0)
    x3, y3 = width - 1, 0
    # Top-left corner (0, 0)
    x4, y4 = 0, 0

    return x1, y1, x2, y2, x3, y3, x4, y4

# Example usage
video_path = r'C:\Users\TrisNguyen\Desktop\API_Zone_Staff\workplace_detection\test.mp4'  # Replace with your video file path
x1, y1, x2, y2, x3, y3, x4, y4 = get_video_corners(video_path)

# Calculate Top-left and Bottom-right coordinates
top_left = (int(min(x4, x1)), int(min(y4, y1)))  # Top-left corner
bottom_right = (int(max(x2, x3)), int(max(y2, y3)))  # Bottom-right corner

print(f"Top-left corner: {top_left}")       # Should be (0, 0)
print(f"Bottom-right corner: {bottom_right}")  # Should be (width-1, height-1)
