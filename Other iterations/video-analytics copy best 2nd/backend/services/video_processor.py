"""
Video processing and real-time face recognition service
"""
import cv2
import numpy as np
from typing import List, Dict, Optional, Callable
from datetime import datetime
from threading import Thread, Event
from queue import Queue
import time
from loguru import logger

from .face_detection import FaceDetectionService
from ..database.models import Person, Detection
from ..utils.helpers import deserialize_encoding, is_within_dedup_window


class VideoProcessor:
    """Processes video streams for face detection and recognition"""

    def __init__(self,
                 face_detector: FaceDetectionService,
                 known_persons: List[Person],
                 recognition_threshold: float = 0.6,
                 frame_skip: int = 2,
                 dedup_window: int = 30):
        """
        Initialize video processor

        Args:
            face_detector: Face detection service
            known_persons: List of registered persons
            recognition_threshold: Matching threshold
            frame_skip: Process every Nth frame
            dedup_window: Deduplication window in seconds
        """
        self.face_detector = face_detector
        self.recognition_threshold = recognition_threshold
        self.frame_skip = frame_skip
        self.dedup_window = dedup_window

        # Load known face encodings
        self.known_encodings = []
        self.known_persons = []
        self._load_known_persons(known_persons)

        # Tracking
        self.last_detections = {}  # person_id: timestamp
        self.frame_count = 0

        # Threading
        self.stop_event = Event()
        self.detection_queue = Queue(maxsize=100)

        logger.info(f"Video processor initialized with {len(self.known_persons)} known persons")

    def _load_known_persons(self, persons: List[Person]):
        """Load face encodings from registered persons"""
        self.known_encodings = []
        self.known_persons = []

        for person in persons:
            if person.is_active and person.face_encoding:
                try:
                    encoding = deserialize_encoding(person.face_encoding)
                    self.known_encodings.append(encoding)
                    self.known_persons.append(person)
                except Exception as e:
                    logger.error(f"Error loading encoding for {person.name}: {e}")

        logger.info(f"Loaded {len(self.known_encodings)} face encodings")

    def reload_persons(self, persons: List[Person]):
        """Reload known persons (call when database is updated)"""
        logger.info("Reloading known persons...")
        self._load_known_persons(persons)

    def process_frame(self, frame: np.ndarray, camera_id: str) -> List[Dict]:
        """
        Process a single frame for face detection and recognition

        Args:
            frame: BGR image from OpenCV
            camera_id: Camera identifier

        Returns:
            List of detection results
        """
        self.frame_count += 1

        # Skip frames for performance
        if self.frame_count % self.frame_skip != 0:
            logger.debug(f"Skipping frame {self.frame_count} (frame_skip={self.frame_skip})")
            return []

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        logger.info(f"Processing frame {self.frame_count}, shape: {rgb_frame.shape}")

        # Detect and encode faces
        detected_faces = self.face_detector.detect_and_encode(rgb_frame)

        logger.info(f"Face detection returned {len(detected_faces)} faces")

        if not detected_faces:
            logger.info("No faces detected in this frame")
            return []

        results = []
        current_time = datetime.utcnow()

        for face_data in detected_faces:
            face_encoding = face_data['embedding']
            location = face_data['location']
            bbox = face_data['bbox']

            # Match against known persons
            match_result = self._match_face(face_encoding, camera_id, current_time)

            if match_result:
                # Add detection info
                match_result['location'] = location
                match_result['bbox'] = bbox
                match_result['timestamp'] = current_time
                results.append(match_result)

        return results

    def _match_face(self, face_encoding: np.ndarray, camera_id: str, current_time: datetime) -> Optional[Dict]:
        """
        Match face encoding against known persons

        Args:
            face_encoding: Face encoding to match
            camera_id: Camera ID
            current_time: Current timestamp

        Returns:
            Match result dict or None if no match or within dedup window
        """
        if not self.known_encodings:
            return None

        # Find best match (returns similarity score, not distance!)
        best_idx, similarity = self.face_detector.find_best_match(
            self.known_encodings,
            face_encoding,
            self.recognition_threshold
        )

        if best_idx is None:
            # Unknown person
            return {
                'matched': False,
                'person': None,
                'confidence': 0.0,
                'distance': 1.0 - similarity if similarity else 1.0,
                'is_unknown': True
            }

        # Get matched person
        person = self.known_persons[best_idx]

        # Check deduplication window
        last_detection_key = f"{person.id}_{camera_id}"
        if last_detection_key in self.last_detections:
            last_detection = self.last_detections[last_detection_key]
            if is_within_dedup_window(last_detection, current_time, self.dedup_window):
                # Skip - too soon after last detection
                return None

        # Update last detection time
        self.last_detections[last_detection_key] = current_time

        # Confidence is the cosine similarity (higher = better match)
        confidence = float(similarity)
        distance = 1.0 - similarity  # Convert similarity to distance for compatibility

        logger.debug(f"Match found: {person.name}, similarity={similarity:.3f}, confidence={confidence:.3f}")

        return {
            'matched': True,
            'person': person,
            'person_id': person.id,
            'person_name': person.name,
            'confidence': confidence,
            'distance': distance,
            'is_unknown': False
        }

    def process_stream(self,
                      camera_id: str,
                      camera_url: str,
                      detection_callback: Callable[[List[Dict]], None] = None):
        """
        Process video stream continuously

        Args:
            camera_id: Camera identifier
            camera_url: Camera URL or device ID
            detection_callback: Callback function for detections
        """
        logger.info(f"Starting video stream processing: {camera_id} ({camera_url})")

        # Open video capture
        if camera_url.isdigit():
            cap = cv2.VideoCapture(int(camera_url))
        else:
            cap = cv2.VideoCapture(camera_url)

        if not cap.isOpened():
            logger.error(f"Could not open camera: {camera_id}")
            return

        fps_counter = FPSCounter()

        try:
            while not self.stop_event.is_set():
                ret, frame = cap.read()

                if not ret:
                    logger.warning(f"Failed to read frame from {camera_id}")
                    time.sleep(1)
                    continue

                # Process frame
                detections = self.process_frame(frame, camera_id)

                # Call callback if provided
                if detections and detection_callback:
                    detection_callback(detections)

                # Update FPS
                fps_counter.update()

                # Log FPS periodically
                if fps_counter.frame_count % 100 == 0:
                    logger.debug(f"Camera {camera_id} - FPS: {fps_counter.get_fps():.2f}")

        except Exception as e:
            logger.error(f"Error processing stream {camera_id}: {e}")
        finally:
            cap.release()
            logger.info(f"Video stream stopped: {camera_id}")

    def start_stream_thread(self,
                           camera_id: str,
                           camera_url: str,
                           detection_callback: Callable[[List[Dict]], None] = None) -> Thread:
        """
        Start processing stream in a separate thread

        Args:
            camera_id: Camera identifier
            camera_url: Camera URL or device ID
            detection_callback: Callback function for detections

        Returns:
            Thread object
        """
        thread = Thread(
            target=self.process_stream,
            args=(camera_id, camera_url, detection_callback),
            daemon=True
        )
        thread.start()
        return thread

    def stop(self):
        """Stop all video processing"""
        logger.info("Stopping video processor...")
        self.stop_event.set()

    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw detection boxes and labels on frame

        Args:
            frame: BGR image
            detections: List of detection results

        Returns:
            Annotated frame
        """
        annotated = frame.copy()

        for detection in detections:
            bbox = detection['bbox']
            x, y, w, h = bbox

            # Determine color and label
            if detection['matched']:
                color = (0, 255, 0)  # Green for known
                label = f"{detection['person_name']} ({detection['confidence']:.2f})"
            else:
                color = (0, 0, 255)  # Red for unknown
                label = "Unknown"

            # Draw box
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

            # Draw label background
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x, y - 25), (x + label_size[0], y), color, -1)

            # Draw label text
            cv2.putText(annotated, label, (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        return annotated


class FPSCounter:
    """Simple FPS counter"""

    def __init__(self):
        self.start_time = time.time()
        self.frame_count = 0

    def update(self):
        """Update frame count"""
        self.frame_count += 1

    def get_fps(self) -> float:
        """Get current FPS"""
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        return self.frame_count / elapsed

    def reset(self):
        """Reset counter"""
        self.start_time = time.time()
        self.frame_count = 0


class CameraManager:
    """Manages multiple camera streams"""

    def __init__(self, video_processor: VideoProcessor):
        """
        Initialize camera manager

        Args:
            video_processor: Video processor instance
        """
        self.video_processor = video_processor
        self.active_streams = {}  # camera_id: thread
        logger.info("Camera manager initialized")

    def start_camera(self,
                    camera_id: str,
                    camera_url: str,
                    detection_callback: Callable[[List[Dict]], None] = None):
        """
        Start processing a camera stream

        Args:
            camera_id: Camera identifier
            camera_url: Camera URL or device ID
            detection_callback: Callback for detections
        """
        if camera_id in self.active_streams:
            logger.warning(f"Camera {camera_id} is already running")
            return

        thread = self.video_processor.start_stream_thread(
            camera_id,
            camera_url,
            detection_callback
        )

        self.active_streams[camera_id] = thread
        logger.info(f"Started camera: {camera_id}")

    def stop_camera(self, camera_id: str):
        """
        Stop a camera stream

        Args:
            camera_id: Camera identifier
        """
        if camera_id not in self.active_streams:
            logger.warning(f"Camera {camera_id} is not running")
            return

        # Thread will stop when video_processor.stop_event is set
        # Remove from active streams
        del self.active_streams[camera_id]
        logger.info(f"Stopped camera: {camera_id}")

    def stop_all(self):
        """Stop all camera streams"""
        logger.info("Stopping all cameras...")
        self.video_processor.stop()
        self.active_streams.clear()

    def get_active_cameras(self) -> List[str]:
        """Get list of active camera IDs"""
        return list(self.active_streams.keys())
