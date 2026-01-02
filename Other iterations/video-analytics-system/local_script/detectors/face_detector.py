import numpy as np
from insightface.app import FaceAnalysis
from typing import List, Optional
from config import config


class FaceDetector:
    def __init__(self):
        """Initialize SCRFD face detector from InsightFace"""
        print("Loading SCRFD face detector...")
        self.app = FaceAnalysis(
            name='buffalo_l',  # Using buffalo_l model which includes SCRFD
            providers=['CPUExecutionProvider']  # CPU only
        )
        self.app.prepare(ctx_id=-1, det_size=(640, 640))
        print("SCRFD face detector loaded successfully!")

    def detect_faces(self, frame: np.ndarray, person_bbox: Optional[tuple] = None):
        """
        Detect faces in frame or within person bounding box
        Args:
            frame: Input frame
            person_bbox: Optional (x1, y1, x2, y2) to crop to person region
        Returns:
            List of face objects with bounding boxes and embeddings
        """
        # If person bbox provided, crop the region
        if person_bbox:
            x1, y1, x2, y2 = person_bbox
            # Add padding and ensure within bounds
            h, w = frame.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            if x2 <= x1 or y2 <= y1:
                return []

            crop = frame[y1:y2, x1:x2]
            faces = self.app.get(crop)

            # Adjust coordinates back to full frame
            for face in faces:
                face.bbox[0] += x1
                face.bbox[1] += y1
                face.bbox[2] += x1
                face.bbox[3] += y1
        else:
            faces = self.app.get(frame)

        return faces

    def get_largest_face(self, faces):
        """Get the largest face from detected faces"""
        if not faces:
            return None

        largest_face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        return largest_face
