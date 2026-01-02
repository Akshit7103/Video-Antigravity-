"""
InsightFace detection and recognition service
Provides better accuracy and performance than dlib
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from loguru import logger
import insightface
from insightface.app import FaceAnalysis


class InsightFaceDetectionService:
    """Service for detecting and encoding faces using InsightFace"""

    def __init__(self, detection_model: str = "buffalo_l", use_gpu: bool = False):
        """
        Initialize InsightFace detection service

        Args:
            detection_model: Model name ('buffalo_l', 'buffalo_m', 'buffalo_s')
                - buffalo_l: Large model (most accurate, slower)
                - buffalo_m: Medium model (balanced)
                - buffalo_s: Small model (fastest)
            use_gpu: Whether to use GPU acceleration
        """
        self.detection_model = detection_model
        self.use_gpu = use_gpu

        # Initialize FaceAnalysis
        ctx_id = 0 if use_gpu else -1  # 0 for GPU, -1 for CPU

        try:
            self.app = FaceAnalysis(
                name=detection_model,
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_gpu else ['CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))
            logger.info(f"InsightFace initialized with model: {detection_model}, GPU: {use_gpu}")
        except Exception as e:
            logger.error(f"Error initializing InsightFace: {e}")
            raise

    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """
        Detect faces in an image

        Args:
            image: RGB image as numpy array

        Returns:
            List of face detection results with bboxes and landmarks
        """
        try:
            faces = self.app.get(image)
            return faces
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []

    def encode_face(self, image: np.ndarray, face: Dict = None) -> Optional[np.ndarray]:
        """
        Generate face encoding from image

        Args:
            image: RGB image as numpy array
            face: Optional face detection result

        Returns:
            512-dimensional face embedding (InsightFace uses 512-D vs dlib's 128-D)
        """
        try:
            if face is not None:
                # Face already detected
                return face.embedding
            else:
                # Detect and encode
                faces = self.detect_faces(image)
                if len(faces) > 0:
                    return faces[0].embedding
                else:
                    logger.warning("No face encoding generated")
                    return None
        except Exception as e:
            logger.error(f"Error encoding face: {e}")
            return None

    def detect_and_encode(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all faces and generate embeddings

        Args:
            image: RGB image as numpy array

        Returns:
            List of dicts with 'location', 'embedding', 'bbox', 'landmarks', 'age', 'gender'
        """
        results = []

        try:
            # Detect faces
            faces = self.detect_faces(image)

            if not faces:
                return results

            for face in faces:
                # Get bounding box
                bbox = face.bbox.astype(int)  # [x1, y1, x2, y2]

                # Convert to our format: (x, y, width, height)
                x1, y1, x2, y2 = bbox
                bbox_formatted = (x1, y1, x2 - x1, y2 - y1)

                # Convert to location format: (top, right, bottom, left)
                location = (y1, x2, y2, x1)

                # Get embedding (512-D vector)
                embedding = face.embedding

                # Additional InsightFace features
                age = face.age if hasattr(face, 'age') else None
                gender = face.gender if hasattr(face, 'gender') else None
                landmarks = face.landmark_2d_106 if hasattr(face, 'landmark_2d_106') else None

                results.append({
                    'location': location,
                    'embedding': embedding,
                    'bbox': bbox_formatted,
                    'landmarks': landmarks,
                    'age': age,
                    'gender': gender,
                    'confidence': face.det_score
                })

        except Exception as e:
            logger.error(f"Error in detect_and_encode: {e}")

        return results

    def compare_faces(self,
                     known_embeddings: List[np.ndarray],
                     face_embedding: np.ndarray,
                     tolerance: float = 0.5) -> Tuple[List[bool], List[float]]:
        """
        Compare face embedding against known embeddings using cosine similarity

        Args:
            known_embeddings: List of known face embeddings (512-D)
            face_embedding: Face embedding to compare (512-D)
            tolerance: Matching threshold (default 0.5)
                      Lower = stricter matching
                      InsightFace uses cosine similarity (higher is better)

        Returns:
            Tuple of (matches list, similarities list)
        """
        try:
            if not known_embeddings:
                return [], []

            # Normalize embeddings
            face_embedding_norm = face_embedding / np.linalg.norm(face_embedding)

            similarities = []
            for known_embedding in known_embeddings:
                known_norm = known_embedding / np.linalg.norm(known_embedding)
                # Cosine similarity
                similarity = np.dot(face_embedding_norm, known_norm)
                similarities.append(float(similarity))

            # Higher similarity = better match (opposite of dlib's distance)
            matches = [sim >= tolerance for sim in similarities]

            return matches, similarities
        except Exception as e:
            logger.error(f"Error comparing faces: {e}")
            return [], []

    def find_best_match(self,
                       known_embeddings: List[np.ndarray],
                       face_embedding: np.ndarray,
                       tolerance: float = 0.5) -> Tuple[Optional[int], float]:
        """
        Find best matching face from known embeddings

        Args:
            known_embeddings: List of known face embeddings
            face_embedding: Face embedding to match
            tolerance: Matching threshold (cosine similarity)

        Returns:
            Tuple of (best_match_index, similarity) or (None, 0.0) if no match
        """
        if not known_embeddings:
            return None, 0.0

        matches, similarities = self.compare_faces(known_embeddings, face_embedding, tolerance)

        if not any(matches):
            return None, 0.0

        # Find best match (highest similarity)
        best_match_idx = int(np.argmax(similarities))
        best_similarity = similarities[best_match_idx]

        return best_match_idx, best_similarity

    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load image from file path

        Args:
            image_path: Path to image file

        Returns:
            RGB image as numpy array or None if failed
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image_rgb
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None

    def assess_face_quality(self, image: np.ndarray, face: Dict) -> Dict:
        """
        Assess quality of detected face

        Args:
            image: RGB image
            face: Face detection result from InsightFace

        Returns:
            Dict with quality metrics
        """
        bbox = face['bbox']
        x, y, w, h = bbox

        # Calculate face area
        face_area = w * h
        image_area = image.shape[0] * image.shape[1]
        area_ratio = face_area / image_area

        # Check if face is good size
        is_good_size = 0.05 < area_ratio < 0.8

        # Check aspect ratio
        aspect_ratio = w / max(h, 1)
        is_good_aspect = 0.7 < aspect_ratio < 1.3

        # Extract face region for brightness check
        face_region = image[y:y+h, x:x+w]
        brightness = np.mean(face_region)
        is_good_brightness = 50 < brightness < 230

        # Use detection confidence from InsightFace
        detection_confidence = face.get('confidence', 0.0)
        is_good_confidence = detection_confidence > 0.5

        # Calculate overall quality score
        quality_score = 0.0
        if is_good_size:
            quality_score += 0.3
        if is_good_aspect:
            quality_score += 0.2
        if is_good_brightness:
            quality_score += 0.2
        if is_good_confidence:
            quality_score += 0.3

        return {
            'score': quality_score,
            'size_ok': is_good_size,
            'aspect_ok': is_good_aspect,
            'brightness_ok': is_good_brightness,
            'confidence_ok': is_good_confidence,
            'face_size': (w, h),
            'area_ratio': area_ratio,
            'brightness': brightness,
            'detection_confidence': detection_confidence
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
