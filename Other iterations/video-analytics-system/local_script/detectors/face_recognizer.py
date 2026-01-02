import numpy as np
from typing import Optional, Tuple


class FaceRecognizer:
    def __init__(self):
        """
        Face recognizer using ArcFace embeddings from InsightFace
        The actual embedding extraction is done by FaceDetector
        This class handles the matching logic
        """
        print("Face recognizer initialized (using ArcFace from InsightFace)")

    def get_embedding(self, face) -> np.ndarray:
        """
        Get face embedding (already computed by InsightFace)
        Args:
            face: Face object from InsightFace
        Returns:
            512-dimensional embedding vector
        """
        return face.embedding

    def normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Normalize embedding to unit length"""
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
