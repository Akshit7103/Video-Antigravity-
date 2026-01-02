from ultralytics import YOLO
import numpy as np
from typing import List, Tuple, Dict
from config import config


class PersonDetector:
    def __init__(self):
        """Initialize YOLOv8 for person AND phone detection (combined for efficiency)"""
        print("Loading YOLOv8 model...")
        self.model = YOLO(config.YOLO_MODEL)
        self.person_class_id = 0  # COCO class ID for person
        self.phone_class_id = 67  # COCO class ID for cell phone
        print("YOLOv8 model loaded successfully!")

    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect persons in frame
        Returns: List of (x1, y1, x2, y2, confidence)
        """
        results = self.model(
            frame,
            conf=config.YOLO_CONF_THRESHOLD,
            iou=config.YOLO_IOU_THRESHOLD,
            classes=[self.person_class_id],  # Only detect persons
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

    def detect_all(self, frame: np.ndarray) -> Dict[str, List[Tuple[int, int, int, int, float]]]:
        """
        Detect BOTH persons AND phones in a single YOLOv8 pass (optimized)
        Returns: {
            'persons': [(x1, y1, x2, y2, confidence), ...],
            'phones': [(x1, y1, x2, y2, confidence), ...]
        }
        """
        results = self.model(
            frame,
            conf=config.YOLO_CONF_THRESHOLD,
            iou=config.YOLO_IOU_THRESHOLD,
            classes=[self.person_class_id, self.phone_class_id],  # Detect BOTH in one pass
            verbose=False
        )

        person_detections = []
        phone_detections = []

        if len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())

                if class_id == self.person_class_id:
                    person_detections.append((x1, y1, x2, y2, confidence))
                elif class_id == self.phone_class_id:
                    phone_detections.append((x1, y1, x2, y2, confidence))

        return {
            'persons': person_detections,
            'phones': phone_detections
        }
