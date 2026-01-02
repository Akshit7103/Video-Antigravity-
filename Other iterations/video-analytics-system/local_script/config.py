import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    # Camera Configuration
    CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
    DETECTION_FPS = int(os.getenv("DETECTION_FPS", "30"))

    # Model Configuration
    YOLO_MODEL = "yolov8n.pt"  # YOLOv8 nano for speed on CPU
    YOLO_CONF_THRESHOLD = 0.5
    YOLO_IOU_THRESHOLD = 0.45

    # Phone Detection
    PHONE_CLASS_ID = 67  # COCO dataset class ID for cell phone

    # Face Detection/Recognition
    FACE_DETECTION_THRESHOLD = 0.5
    FACE_SIZE = (112, 112)  # Standard size for ArcFace

    # Tracking Configuration
    TRACK_BUFFER = 30  # Frames to keep lost tracks
    MATCH_THRESHOLD = 0.8  # IoU threshold for matching

    # Display Configuration
    DISPLAY_VIDEO = True
    DISPLAY_WIDTH = 1280
    DISPLAY_HEIGHT = 720


config = Config()
