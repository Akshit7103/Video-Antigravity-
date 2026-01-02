import numpy as np
from collections import defaultdict
from typing import List, Tuple, Dict


class BoTSORTTracker:
    """
    Simplified BoT-SORT tracker implementation
    For production, consider using the official BoT-SORT implementation
    """

    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold

        self.tracks: Dict[int, dict] = {}
        self.next_id = 1
        self.frame_count = 0

    def update(self, detections: List[Tuple[int, int, int, int, float]]) -> Dict[int, Tuple[int, int, int, int]]:
        """
        Update tracker with new detections
        Args:
            detections: List of (x1, y1, x2, y2, confidence)
        Returns:
            Dict of {track_id: (x1, y1, x2, y2)}
        """
        self.frame_count += 1

        # Convert detections to numpy array
        if len(detections) == 0:
            det_boxes = np.empty((0, 4))
        else:
            det_boxes = np.array([det[:4] for det in detections])

        # Get existing track boxes
        track_ids = list(self.tracks.keys())
        if len(track_ids) == 0:
            track_boxes = np.empty((0, 4))
        else:
            track_boxes = np.array([self.tracks[tid]['bbox'] for tid in track_ids])

        # Match detections to tracks using IoU
        matches, unmatched_dets, unmatched_tracks = self._match(det_boxes, track_boxes)

        # Update matched tracks
        for det_idx, track_idx in matches:
            track_id = track_ids[track_idx]
            self.tracks[track_id]['bbox'] = det_boxes[det_idx]
            self.tracks[track_id]['hits'] += 1
            self.tracks[track_id]['age'] = 0

        # Create new tracks for unmatched detections
        for det_idx in unmatched_dets:
            self.tracks[self.next_id] = {
                'bbox': det_boxes[det_idx],
                'hits': 1,
                'age': 0,
                'id': self.next_id
            }
            self.next_id += 1

        # Update age of unmatched tracks
        for track_idx in unmatched_tracks:
            track_id = track_ids[track_idx]
            self.tracks[track_id]['age'] += 1

        # Remove old tracks
        to_remove = []
        for track_id, track in self.tracks.items():
            if track['age'] > self.max_age:
                to_remove.append(track_id)

        for track_id in to_remove:
            del self.tracks[track_id]

        # Return active tracks
        active_tracks = {}
        for track_id, track in self.tracks.items():
            if track['hits'] >= self.min_hits:
                active_tracks[track_id] = tuple(map(int, track['bbox']))

        return active_tracks

    def _match(self, detections: np.ndarray, tracks: np.ndarray) -> Tuple[List, List, List]:
        """
        Match detections to tracks using IoU
        Returns: (matches, unmatched_detections, unmatched_tracks)
        """
        if len(detections) == 0:
            return [], [], list(range(len(tracks)))

        if len(tracks) == 0:
            return [], list(range(len(detections))), []

        # Compute IoU matrix
        iou_matrix = self._iou_batch(detections, tracks)

        # Simple greedy matching
        matches = []
        unmatched_dets = list(range(len(detections)))
        unmatched_tracks = list(range(len(tracks)))

        # Find best matches
        while len(unmatched_dets) > 0 and len(unmatched_tracks) > 0:
            # Find maximum IoU
            max_iou = 0
            max_det = -1
            max_track = -1

            for i in unmatched_dets:
                for j in unmatched_tracks:
                    if iou_matrix[i, j] > max_iou:
                        max_iou = iou_matrix[i, j]
                        max_det = i
                        max_track = j

            if max_iou < self.iou_threshold:
                break

            matches.append((max_det, max_track))
            unmatched_dets.remove(max_det)
            unmatched_tracks.remove(max_track)

        return matches, unmatched_dets, unmatched_tracks

    def _iou_batch(self, boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
        """
        Compute IoU between two sets of boxes
        """

        def box_area(box):
            return (box[2] - box[0]) * (box[3] - box[1])

        area_a = np.array([box_area(box) for box in boxes_a])
        area_b = np.array([box_area(box) for box in boxes_b])

        iou_matrix = np.zeros((len(boxes_a), len(boxes_b)))

        for i, box_a in enumerate(boxes_a):
            for j, box_b in enumerate(boxes_b):
                xx1 = max(box_a[0], box_b[0])
                yy1 = max(box_a[1], box_b[1])
                xx2 = min(box_a[2], box_b[2])
                yy2 = min(box_a[3], box_b[3])

                w = max(0, xx2 - xx1)
                h = max(0, yy2 - yy1)

                intersection = w * h
                union = area_a[i] + area_b[j] - intersection

                if union > 0:
                    iou_matrix[i, j] = intersection / union

        return iou_matrix

    def get_active_track_ids(self) -> List[int]:
        """Get list of currently active track IDs"""
        return [tid for tid, track in self.tracks.items() if track['hits'] >= self.min_hits]
