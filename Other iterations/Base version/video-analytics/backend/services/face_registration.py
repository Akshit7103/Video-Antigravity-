"""
Face registration service
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from loguru import logger
from PIL import Image

from .face_detection import FaceDetectionService
from ..database.models import Person
from ..utils.helpers import serialize_encoding, sanitize_filename, get_timestamp_string


class FaceRegistrationService:
    """Service for registering new persons"""

    def __init__(self, face_detector: FaceDetectionService, storage_path: Path):
        """
        Initialize registration service

        Args:
            face_detector: Face detection service instance
            storage_path: Path to store face images
        """
        self.face_detector = face_detector
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Face registration service initialized with storage: {storage_path}")

    def register_from_images(self,
                            name: str,
                            image_paths: List[str],
                            email: str = None,
                            employee_id: str = None,
                            **kwargs) -> Optional[Person]:
        """
        Register person from multiple image files

        Args:
            name: Person's name
            image_paths: List of image file paths
            email: Person's email (optional)
            employee_id: Employee ID (optional)
            **kwargs: Additional person attributes (phone, department, designation, notes)

        Returns:
            Person object if successful, None otherwise
        """
        logger.info(f"Registering person: {name} from {len(image_paths)} images")

        # Load and process images
        face_encodings = []
        valid_image_paths = []
        quality_scores = []

        for img_path in image_paths:
            # Load image
            image = self.face_detector.load_image(img_path)
            if image is None:
                logger.warning(f"Could not load image: {img_path}")
                continue

            # Detect and encode face
            results = self.face_detector.detect_and_encode(image)

            if not results:
                logger.warning(f"No face detected in image: {img_path}")
                continue

            if len(results) > 1:
                logger.warning(f"Multiple faces detected in image: {img_path}, using first one")

            # Use first detected face
            face_data = results[0]

            # Assess quality
            quality = self.face_detector.assess_face_quality(image, face_data)
            quality_scores.append(quality['score'])

            if quality['score'] < 0.5:
                logger.warning(f"Low quality face in image: {img_path} (score: {quality['score']:.2f})")
                continue

            face_encodings.append(face_data['embedding'])
            valid_image_paths.append(img_path)

        if not face_encodings:
            logger.error(f"No valid face encodings found for {name}")
            return None

        logger.info(f"Generated {len(face_encodings)} valid face encodings with avg quality: {np.mean(quality_scores):.2f}")

        # Calculate average encoding
        avg_encoding = np.mean(face_encodings, axis=0)

        # Copy images to storage
        person_folder = self._create_person_folder(name)
        saved_paths = []

        for idx, img_path in enumerate(valid_image_paths):
            saved_path = self._save_face_image(img_path, person_folder, f"sample_{idx+1}")
            if saved_path:
                saved_paths.append(str(saved_path.relative_to(self.storage_path.parent)))

        # Create Person object
        person = Person(
            name=name,
            email=email,
            employee_id=employee_id,
            face_encoding=serialize_encoding(avg_encoding),
            registration_date=datetime.utcnow(),
            is_active=True,
            sample_images=saved_paths,
            profile_image=saved_paths[0] if saved_paths else None,
            phone=kwargs.get('phone'),
            department=kwargs.get('department'),
            designation=kwargs.get('designation'),
            notes=kwargs.get('notes')
        )

        logger.success(f"Successfully registered: {name}")
        return person

    def register_from_frames(self,
                           name: str,
                           frames: List[np.ndarray],
                           email: str = None,
                           employee_id: str = None,
                           **kwargs) -> Optional[Person]:
        """
        Register person from captured video frames

        Args:
            name: Person's name
            frames: List of RGB image frames
            email: Person's email (optional)
            employee_id: Employee ID (optional)
            **kwargs: Additional person attributes

        Returns:
            Person object if successful, None otherwise
        """
        logger.info(f"Registering person: {name} from {len(frames)} frames")

        # Process frames
        face_encodings = []
        person_folder = self._create_person_folder(name)
        saved_paths = []
        quality_scores = []

        for idx, frame in enumerate(frames):
            # Detect and encode face
            results = self.face_detector.detect_and_encode(frame)

            if not results:
                logger.warning(f"No face detected in frame {idx}")
                continue

            if len(results) > 1:
                logger.warning(f"Multiple faces detected in frame {idx}, using first one")

            face_data = results[0]

            # Assess quality
            quality = self.face_detector.assess_face_quality(frame, face_data)
            quality_scores.append(quality['score'])

            if quality['score'] < 0.5:
                logger.warning(f"Low quality face in frame {idx} (score: {quality['score']:.2f})")
                continue

            # Save frame
            frame_path = person_folder / f"sample_{idx+1}.jpg"
            cv2.imwrite(str(frame_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            saved_paths.append(str(frame_path.relative_to(self.storage_path.parent)))

            face_encodings.append(face_data['embedding'])

        if not face_encodings:
            logger.error(f"No valid face encodings found for {name}")
            return None

        logger.info(f"Generated {len(face_encodings)} valid encodings with avg quality: {np.mean(quality_scores):.2f}")

        # Calculate average encoding
        avg_encoding = np.mean(face_encodings, axis=0)

        # Create Person object
        person = Person(
            name=name,
            email=email,
            employee_id=employee_id,
            face_encoding=serialize_encoding(avg_encoding),
            registration_date=datetime.utcnow(),
            is_active=True,
            sample_images=saved_paths,
            profile_image=saved_paths[0] if saved_paths else None,
            phone=kwargs.get('phone'),
            department=kwargs.get('department'),
            designation=kwargs.get('designation'),
            notes=kwargs.get('notes')
        )

        logger.success(f"Successfully registered: {name}")
        return person

    def register_single_image(self,
                            name: str,
                            image: np.ndarray,
                            email: str = None,
                            employee_id: str = None,
                            **kwargs) -> Optional[Person]:
        """
        Register person from a single image

        Args:
            name: Person's name
            image: RGB image as numpy array
            email: Person's email
            employee_id: Employee ID
            **kwargs: Additional person attributes

        Returns:
            Person object if successful, None otherwise
        """
        # Detect and encode face
        results = self.face_detector.detect_and_encode(image)

        if not results:
            logger.error(f"No face detected in image for {name}")
            return None

        if len(results) > 1:
            logger.warning(f"Multiple faces detected, using first one")

        face_data = results[0]

        # Assess quality
        quality = self.face_detector.assess_face_quality(image, face_data)

        if quality['score'] < 0.5:
            logger.warning(f"Low quality face detected (score: {quality['score']:.2f})")

        # Save image
        person_folder = self._create_person_folder(name)
        frame_path = person_folder / "profile.jpg"
        cv2.imwrite(str(frame_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        saved_path = str(frame_path.relative_to(self.storage_path.parent))

        # Create Person object
        person = Person(
            name=name,
            email=email,
            employee_id=employee_id,
            face_encoding=serialize_encoding(face_data['embedding']),
            registration_date=datetime.utcnow(),
            is_active=True,
            sample_images=[saved_path],
            profile_image=saved_path,
            phone=kwargs.get('phone'),
            department=kwargs.get('department'),
            designation=kwargs.get('designation'),
            notes=kwargs.get('notes')
        )

        logger.success(f"Successfully registered: {name}")
        return person

    def _create_person_folder(self, name: str) -> Path:
        """
        Create folder for person's images

        Args:
            name: Person's name

        Returns:
            Path to person's folder
        """
        # Sanitize name for folder
        folder_name = sanitize_filename(name)
        timestamp = get_timestamp_string()
        folder_path = self.storage_path / f"{folder_name}_{timestamp}"

        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path

    def _save_face_image(self, source_path: str, dest_folder: Path, filename: str) -> Optional[Path]:
        """
        Copy image to destination folder

        Args:
            source_path: Source image path
            dest_folder: Destination folder
            filename: Filename without extension

        Returns:
            Path to saved image or None if failed
        """
        try:
            source = Path(source_path)
            dest = dest_folder / f"{filename}{source.suffix}"

            # Copy file
            img = Image.open(source)
            img.save(dest)

            logger.debug(f"Saved image: {dest}")
            return dest
        except Exception as e:
            logger.error(f"Error saving image {source_path}: {e}")
            return None
