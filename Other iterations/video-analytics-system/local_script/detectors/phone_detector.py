from ultralytics import YOLO
import numpy as np
from typing import List, Tuple
from config import config


class PhoneDetector:
    def __init__(self):
        """Initialize YOLOv8 for phone detection"""
        print("Loading YOLOv8 model for phone detection...")
        self.model = YOLO(config.YOLO_MODEL)
        print("Phone detector loaded successfully!")

    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect phones in frame
        Returns: List of (x1, y1, x2, y2, confidence)
        """
        results = self.model(
            frame,
            conf=config.YOLO_CONF_THRESHOLD,
            iou=config.YOLO_IOU_THRESHOLD,
            classes=[config.PHONE_CLASS_ID],  # Only detect cell phones
            verbose=False
        )

        detections = []
        if len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                confidence = float(box.conf[0].cpu().numpy())
                detections.append((x1, y1, x2, y2, confidence))

        return detections
