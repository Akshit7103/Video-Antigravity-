"""
Duplicate Face Detection Service
"""
import numpy as np
from loguru import logger
from typing import Dict, Optional
from sqlalchemy.orm import Session

from ..database.models import Person
from ..utils.helpers import deserialize_encoding


class DuplicateFaceChecker:
    """Service for checking duplicate faces during registration"""

    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize duplicate checker

        Args:
            similarity_threshold: Minimum similarity to consider a duplicate (0.0-1.0)
                                Higher = stricter matching
                                Recommended: 0.7-0.8
        """
        self.similarity_threshold = similarity_threshold
        logger.info(f"Duplicate face checker initialized with threshold: {similarity_threshold}")

    def check_duplicate(
        self,
        new_encoding: np.ndarray,
        db_session: Session
    ) -> Dict:
        """
        Check if a face encoding matches any existing person

        Args:
            new_encoding: Face encoding to check (numpy array)
            db_session: Database session

        Returns:
            Dictionary with:
                - is_duplicate (bool): Whether a duplicate was found
                - person (Person): Matching person object if duplicate
                - similarity (float): Similarity score (0.0-1.0)
                - match_name (str): Name of matching person if duplicate
        """
        try:
            # Get all active registered persons
            persons = db_session.query(Person).filter(Person.is_active == True).all()

            if not persons:
                logger.debug("No registered persons found")
                return {
                    'is_duplicate': False,
                    'person': None,
                    'similarity': 0.0,
                    'match_name': None
                }

            best_match = None
            highest_similarity = 0.0

            # Compare with each registered person
            for person in persons:
                try:
                    # Deserialize stored encoding
                    stored_encoding = deserialize_encoding(person.face_encoding)

                    # Calculate cosine similarity
                    similarity = self._calculate_similarity(new_encoding, stored_encoding)

                    logger.debug(f"Similarity with {person.name}: {similarity:.3f}")

                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        best_match = person

                except Exception as e:
                    logger.warning(f"Error comparing with person {person.id} ({person.name}): {e}")
                    continue

            # Determine if duplicate
            is_duplicate = highest_similarity >= self.similarity_threshold

            if is_duplicate:
                logger.warning(
                    f"DUPLICATE DETECTED: New face matches {best_match.name} "
                    f"with {highest_similarity:.3f} similarity"
                )

            return {
                'is_duplicate': is_duplicate,
                'person': best_match if is_duplicate else None,
                'similarity': highest_similarity,
                'match_name': best_match.name if is_duplicate else None
            }

        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            # Return False on error to avoid blocking registration
            return {
                'is_duplicate': False,
                'person': None,
                'similarity': 0.0,
                'match_name': None,
                'error': str(e)
            }

    def _calculate_similarity(self, encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two face encodings

        Args:
            encoding1: First face encoding
            encoding2: Second face encoding

        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Normalize encodings
            encoding1_norm = encoding1 / np.linalg.norm(encoding1)
            encoding2_norm = encoding2 / np.linalg.norm(encoding2)

            # Calculate cosine similarity
            similarity = np.dot(encoding1_norm, encoding2_norm)

            # Ensure result is in [0, 1] range
            similarity = max(0.0, min(1.0, float(similarity)))

            return similarity

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def check_duplicate_batch(
        self,
        encodings: list,
        db_session: Session
    ) -> Dict:
        """
        Check multiple encodings for duplicates (for batch registration)

        Args:
            encodings: List of face encodings
            db_session: Database session

        Returns:
            Dictionary with overall duplicate status
        """
        results = []

        for idx, encoding in enumerate(encodings):
            result = self.check_duplicate(encoding, db_session)
            result['encoding_index'] = idx
            results.append(result)

        # Check if any encoding is a duplicate
        is_any_duplicate = any(r['is_duplicate'] for r in results)

        # Get the best match across all encodings
        if is_any_duplicate:
            best_result = max(results, key=lambda x: x['similarity'])
            return {
                'is_duplicate': True,
                'person': best_result['person'],
                'similarity': best_result['similarity'],
                'match_name': best_result['match_name'],
                'all_results': results
            }

        return {
            'is_duplicate': False,
            'person': None,
            'similarity': max(r['similarity'] for r in results),
            'match_name': None,
            'all_results': results
        }
