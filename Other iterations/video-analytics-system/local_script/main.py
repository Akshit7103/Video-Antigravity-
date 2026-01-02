import cv2
import numpy as np
import time
from collections import defaultdict
from datetime import datetime

from config import config
from detectors.person_detector import PersonDetector
from detectors.phone_detector import PhoneDetector
from detectors.face_detector import FaceDetector
from detectors.face_recognizer import FaceRecognizer
from tracking.tracker import BoTSORTTracker
from utils.api_client import APIClient


class VideoAnalyticsSystem:
    def __init__(self):
        print("Initializing Video Analytics System...")

        # Initialize detectors
        self.person_detector = PersonDetector()  # Handles both person AND phone detection
        self.face_detector = FaceDetector()
        self.face_recognizer = FaceRecognizer()

        # Initialize trackers
        self.person_tracker = BoTSORTTracker(max_age=30, min_hits=1, iou_threshold=0.3)
        self.phone_tracker = BoTSORTTracker(max_age=15, min_hits=1, iou_threshold=0.3)

        # Initialize API client
        self.api_client = APIClient()

        # Track logged persons (track_id -> {name, logged, frames_tracked, attempt_count, face_detected_count})
        self.tracked_persons = {}

        # Track logged phones (track_id -> logged)
        self.tracked_phones = {}
        self.phone_log_cooldown = 2  # seconds

        # Performance metrics
        self.fps_history = []
        self.frame_count = 0

        # Frame skip for face detection (reduce lag significantly)
        self.face_detection_interval = 10  # Try face detection every 10 frames (much less lag)

        # Grace period before marking as Unknown
        self.grace_period_frames = 45  # Wait 45 frames (~1.5 seconds) before marking as Unknown
        self.min_face_attempts = 5  # Must detect face at least 5 times before marking Unknown

        print("System initialized successfully!")

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process a single frame and return annotated frame"""
        start_time = time.time()

        # 1. Detect BOTH persons AND phones in single YOLOv8 pass (optimized!)
        all_detections = self.person_detector.detect_all(frame)
        person_detections = all_detections['persons']
        phone_detections = all_detections['phones']

        # 2. Update trackers (track both people AND phones)
        tracked_persons = self.person_tracker.update(person_detections)
        tracked_phones = self.phone_tracker.update(phone_detections)

        # 3. Process each tracked person
        for track_id, bbox in tracked_persons.items():
            x1, y1, x2, y2 = bbox

            # Initialize track if new
            if track_id not in self.tracked_persons:
                self.tracked_persons[track_id] = {
                    'name': None,
                    'logged': False,
                    'confidence': None,
                    'frames_tracked': 0,
                    'attempt_count': 0,
                    'face_detected_count': 0,
                    'no_face_count': 0,
                    'identification_complete': False  # Stop face detection after first identification
                }

            # Increment frame counter
            self.tracked_persons[track_id]['frames_tracked'] += 1

            # Only process face if not yet identified (skip if already processed)
            if not self.tracked_persons[track_id]['identification_complete']:
                # Only try face detection every N frames to reduce lag
                if self.tracked_persons[track_id]['frames_tracked'] % self.face_detection_interval == 1:
                    self.tracked_persons[track_id]['attempt_count'] += 1

                    # Detect face within person bbox
                    faces = self.face_detector.detect_faces(frame, bbox)

                    if faces:
                        # Face detected!
                        self.tracked_persons[track_id]['face_detected_count'] += 1

                        # Get largest face
                        face = self.face_detector.get_largest_face(faces)
                        embedding = self.face_recognizer.get_embedding(face)
                        embedding = self.face_recognizer.normalize_embedding(embedding)

                        # Match against database
                        person_name, confidence = self.match_face_local(embedding)

                        if person_name:
                            # Authorized person - log immediately
                            self.tracked_persons[track_id]['name'] = person_name
                            self.tracked_persons[track_id]['confidence'] = confidence
                            self.tracked_persons[track_id]['logged'] = True
                            self.tracked_persons[track_id]['identification_complete'] = True  # Stop face detection

                            # Log to backend
                            self.api_client.log_person_detection(
                                person_name=person_name,
                                is_authorized=True,
                                confidence=confidence,
                                track_id=track_id
                            )
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Authorized: {person_name} (confidence: {confidence:.2f})")
                        else:
                            # Face detected but not recognized
                            # Only mark as Unknown if we've detected face multiple times AND waited grace period
                            if (self.tracked_persons[track_id]['face_detected_count'] >= self.min_face_attempts and
                                self.tracked_persons[track_id]['frames_tracked'] >= self.grace_period_frames):
                                # Unknown person after multiple face detections
                                self.tracked_persons[track_id]['name'] = "Unknown"
                                self.tracked_persons[track_id]['logged'] = True
                                self.tracked_persons[track_id]['identification_complete'] = True  # Stop face detection

                                # Log to backend
                                self.api_client.log_person_detection(
                                    person_name="Unknown",
                                    is_authorized=False,
                                    confidence=None,
                                    track_id=track_id
                                )
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ Unauthorized: Unknown person detected")
                    else:
                        # No face detected - keep trying, DON'T mark as Unknown
                        # This handles cases where person is turned away or face not visible
                        self.tracked_persons[track_id]['no_face_count'] += 1

                        # Only if person has been in frame for VERY long without ANY face detection
                        # then we might consider them suspicious
                        if (self.tracked_persons[track_id]['frames_tracked'] >= self.grace_period_frames * 2 and
                            self.tracked_persons[track_id]['face_detected_count'] == 0):
                            # Person in frame for 3+ seconds with NO face ever detected
                            self.tracked_persons[track_id]['name'] = "Unknown"
                            self.tracked_persons[track_id]['logged'] = True
                            self.tracked_persons[track_id]['identification_complete'] = True  # Stop face detection

                            # Log to backend
                            self.api_client.log_person_detection(
                                person_name="Unknown",
                                is_authorized=False,
                                confidence=None,
                                track_id=track_id
                            )
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ Unauthorized: Person detected (face not visible)")

            # Draw bounding box and label
            name = self.tracked_persons[track_id]['name'] or "Identifying..."
            confidence = self.tracked_persons[track_id]['confidence']

            # Color: Green for authorized, Red for unknown, Yellow for identifying
            if name == "Unknown":
                color = (0, 0, 255)  # Red
            elif name == "Identifying...":
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 255, 0)  # Green

            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label background
            label = f"ID:{track_id} {name}"
            if confidence:
                label += f" ({confidence:.2f})"

            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)

            # Draw label text
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 4. Track and draw phones (continuous tracking with bounding boxes)
        for phone_track_id, phone_bbox in tracked_phones.items():
            x1, y1, x2, y2 = phone_bbox

            # Initialize phone track if new
            if phone_track_id not in self.tracked_phones:
                self.tracked_phones[phone_track_id] = {
                    'logged': False,
                    'first_seen': time.time()
                }

                # Log phone detection (only once per track)
                self.api_client.log_phone_detection()
                self.tracked_phones[phone_track_id]['logged'] = True
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 📱 Phone detected (Track ID: {phone_track_id})")

            # Draw phone bounding box (continuously)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)  # Magenta, thicker

            # Draw label
            label = f"Phone #{phone_track_id}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - label_h - 10), (x1 + label_w, y1), (255, 0, 255), -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Clean up lost phone tracks
        active_phone_track_ids = set(tracked_phones.keys())
        lost_phone_tracks = set(self.tracked_phones.keys()) - active_phone_track_ids
        for phone_track_id in lost_phone_tracks:
            del self.tracked_phones[phone_track_id]

        # Clean up lost tracks
        active_track_ids = set(tracked_persons.keys())
        lost_tracks = set(self.tracked_persons.keys()) - active_track_ids
        for track_id in lost_tracks:
            del self.tracked_persons[track_id]

        # Calculate FPS
        elapsed = time.time() - start_time
        fps = 1 / elapsed if elapsed > 0 else 0
        self.fps_history.append(fps)
        if len(self.fps_history) > 30:
            self.fps_history.pop(0)
        avg_fps = sum(self.fps_history) / len(self.fps_history)

        # Draw FPS and info
        info_text = f"FPS: {avg_fps:.1f} | Persons: {len(tracked_persons)} | Phones: {len(tracked_phones)}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        self.frame_count += 1
        return frame

    def match_face_local(self, embedding: np.ndarray):
        """
        Match face embedding against database
        For now, uses API. Could implement local caching later.
        """
        return self.api_client.find_matching_person(embedding)

    def run(self):
        """Main loop for video analytics"""
        print(f"\nStarting camera (index: {config.CAMERA_INDEX})...")
        cap = cv2.VideoCapture(config.CAMERA_INDEX)

        if not cap.isOpened():
            print("Error: Could not open camera!")
            return

        print("Camera opened successfully!")
        print("\nControls:")
        print("  - Press 'q' to quit")
        print("  - Press 's' to take screenshot")
        print("\nSystem is running...\n")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to read frame")
                    break

                # Resize frame if needed
                if config.DISPLAY_VIDEO:
                    frame = cv2.resize(frame, (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))

                # Process frame
                annotated_frame = self.process_frame(frame)

                # Display
                if config.DISPLAY_VIDEO:
                    cv2.imshow("Video Analytics System", annotated_frame)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nShutting down...")
                    break
                elif key == ord('s'):
                    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, annotated_frame)
                    print(f"Screenshot saved: {filename}")

        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("System stopped.")


if __name__ == "__main__":
    system = VideoAnalyticsSystem()
    system.run()
