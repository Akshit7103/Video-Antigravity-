"""
Face detection and recognition service
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from loguru import logger
import time


class FaceDetectionService:
    """Service for detecting and encoding faces"""

    def __init__(self, detection_model: str = "hog", upsample_times: int = 1):
        """
        Initialize face detection service

        Args:
            detection_model: 'hog' (faster, CPU) or 'cnn' (accurate, GPU)
            upsample_times: How many times to upsample image for detection
        """
        self.detection_model = detection_model
        self.upsample_times = upsample_times
        logger.info(f"Face detection service initialized with model: {detection_model}")

    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image

        Args:
            image: RGB image as numpy array

        Returns:
            List of face bounding boxes [(top, right, bottom, left), ...]
        """
        try:
            face_locations = face_recognition.face_locations(
                image,
                number_of_times_to_upsample=self.upsample_times,
                model=self.detection_model
            )
            return face_locations
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []

    def encode_face(self, image: np.ndarray, face_location: Tuple[int, int, int, int] = None) -> Optional[np.ndarray]:
        """
        Generate face encoding from image

        Args:
            image: RGB image as numpy array
            face_location: Optional face bounding box (top, right, bottom, left)

        Returns:
            128-dimensional face encoding or None if failed
        """
        try:
            if face_location:
                encodings = face_recognition.face_encodings(
                    image,
                    known_face_locations=[face_location]
                )
            else:
                encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                return encodings[0]
            else:
                logger.warning("No face encoding generated")
                return None
        except Exception as e:
            logger.error(f"Error encoding face: {e}")
            return None

    def detect_and_encode(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all faces and generate encodings

        Args:
            image: RGB image as numpy array

        Returns:
            List of dicts with 'location' and 'encoding' keys
        """
        results = []

        try:
            # Detect faces
            face_locations = self.detect_faces(image)

            if not face_locations:
                return results

            # Generate encodings for all detected faces
            encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)

            for location, encoding in zip(face_locations, encodings):
                results.append({
                    'location': location,  # (top, right, bottom, left)
                    'encoding': encoding,
                    'bbox': self._location_to_bbox(location)  # (x, y, width, height)
                })

        except Exception as e:
            logger.error(f"Error in detect_and_encode: {e}")

        return results

    def compare_faces(self,
                     known_encodings: List[np.ndarray],
                     face_encoding: np.ndarray,
                     tolerance: float = 0.6) -> Tuple[List[bool], List[float]]:
        """
        Compare face encoding against known encodings

        Args:
            known_encodings: List of known face encodings
            face_encoding: Face encoding to compare
            tolerance: Matching threshold (default 0.6)

        Returns:
            Tuple of (matches list, distances list)
        """
        try:
            # Calculate distances
            distances = face_recognition.face_distance(known_encodings, face_encoding)

            # Determine matches
            matches = list(distances <= tolerance)

            return matches, distances.tolist()
        except Exception as e:
            logger.error(f"Error comparing faces: {e}")
            return [], []

    def find_best_match(self,
                       known_encodings: List[np.ndarray],
                       face_encoding: np.ndarray,
                       tolerance: float = 0.6) -> Tuple[Optional[int], float]:
        """
        Find best matching face from known encodings

        Args:
            known_encodings: List of known face encodings
            face_encoding: Face encoding to match
            tolerance: Matching threshold

        Returns:
            Tuple of (best_match_index, distance) or (None, inf) if no match
        """
        if not known_encodings:
            return None, float('inf')

        matches, distances = self.compare_faces(known_encodings, face_encoding, tolerance)

        if not any(matches):
            return None, float('inf')

        # Find best match (lowest distance)
        best_match_idx = int(np.argmin(distances))
        best_distance = distances[best_match_idx]

        return best_match_idx, best_distance

    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load image from file path

        Args:
            image_path: Path to image file

        Returns:
            RGB image as numpy array or None if failed
        """
        try:
            image = face_recognition.load_image_file(image_path)
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None

    def assess_face_quality(self, image: np.ndarray, face_location: Tuple[int, int, int, int]) -> Dict:
        """
        Assess quality of detected face

        Args:
            image: RGB image
            face_location: Face bounding box

        Returns:
            Dict with quality metrics
        """
        top, right, bottom, left = face_location
        face_width = right - left
        face_height = bottom - top

        # Calculate face area
        face_area = face_width * face_height
        image_area = image.shape[0] * image.shape[1]
        area_ratio = face_area / image_area

        # Check if face is too small or too large
        is_good_size = 0.05 < area_ratio < 0.8

        # Check aspect ratio (should be close to 1:1 for frontal faces)
        aspect_ratio = face_width / max(face_height, 1)
        is_good_aspect = 0.7 < aspect_ratio < 1.3

        # Extract face region for brightness check
        face_region = image[top:bottom, left:right]
        brightness = np.mean(face_region)
        is_good_brightness = 50 < brightness < 230

        # Calculate overall quality score
        quality_score = 0.0
        if is_good_size:
            quality_score += 0.4
        if is_good_aspect:
            quality_score += 0.3
        if is_good_brightness:
            quality_score += 0.3

        return {
            'score': quality_score,
            'size_ok': is_good_size,
            'aspect_ok': is_good_aspect,
            'brightness_ok': is_good_brightness,
            'face_size': (face_width, face_height),
            'area_ratio': area_ratio,
            'brightness': brightness
        }

    @staticmethod
    def _location_to_bbox(location: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """
        Convert face_recognition location to standard bbox format

        Args:
            location: (top, right, bottom, left)

        Returns:
            (x, y, width, height)
        """
        top, right, bottom, left = location
        return (left, top, right - left, bottom - top)

    @staticmethod
    def _bbox_to_location(bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """
        Convert standard bbox to face_recognition location format

        Args:
            bbox: (x, y, width, height)

        Returns:
            (top, right, bottom, left)
        """
        x, y, width, height = bbox
        return (y, x + width, y + height, x)
