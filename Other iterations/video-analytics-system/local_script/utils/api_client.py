import requests
import json
import numpy as np
from typing import Optional, Tuple
from config import config


class APIClient:
    def __init__(self):
        self.base_url = config.API_BASE_URL

    def find_matching_person(self, face_embedding: np.ndarray) -> Tuple[Optional[str], Optional[float]]:
        """
        Send face embedding to backend to find matching person
        Returns: (person_name, confidence) or (None, None)
        """
        try:
            # Convert embedding to list for JSON serialization
            embedding_list = face_embedding.tolist()

            response = requests.post(
                f"{self.base_url}/api/faces/match",
                json={"embedding": embedding_list},
                timeout=2
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("name"), data.get("confidence")
            else:
                return None, None

        except Exception as e:
            print(f"Error matching face: {e}")
            return None, None

    def log_person_detection(self, person_name: str, is_authorized: bool, confidence: Optional[float], track_id: int):
        """Log person detection event"""
        try:
            response = requests.post(
                f"{self.base_url}/api/logs/person",
                json={
                    "person_name": person_name,
                    "is_authorized": is_authorized,
                    "confidence": confidence,
                    "track_id": track_id
                },
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error logging person detection: {e}")
            return False

    def log_phone_detection(self):
        """Log phone detection event"""
        try:
            response = requests.post(
                f"{self.base_url}/api/logs/phone",
                json={},
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error logging phone detection: {e}")
            return False

    def get_all_face_embeddings(self):
        """Get all registered face embeddings from backend (for local caching)"""
        try:
            response = requests.get(
                f"{self.base_url}/api/faces/embeddings",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching embeddings: {e}")
            return []
