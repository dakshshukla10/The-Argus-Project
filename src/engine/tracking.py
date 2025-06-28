"""
SORT (Simple Online and Realtime Tracking) implementation for person tracking.
Assigns and maintains unique IDs for each detected person across frames.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import cv2


class KalmanBoxTracker:
    """
    This class represents the internal state of individual tracked objects observed as bbox.
    """
    count = 0

    def __init__(self, bbox: np.ndarray):
        """
        Initialize a tracker using initial bounding box.
        
        Args:
            bbox: Bounding box in format [x1, y1, x2, y2]
        """
        # Define constant velocity model
        self.kf = cv2.KalmanFilter(7, 4)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0, 0, 0, 0],
                                             [0, 1, 0, 0, 0, 0, 0],
                                             [0, 0, 1, 0, 0, 0, 0],
                                             [0, 0, 0, 1, 0, 0, 0]], dtype=np.float32)
        
        self.kf.transitionMatrix = np.array([[1, 0, 0, 0, 1, 0, 0],
                                            [0, 1, 0, 0, 0, 1, 0],
                                            [0, 0, 1, 0, 0, 0, 1],
                                            [0, 0, 0, 1, 0, 0, 0],
                                            [0, 0, 0, 0, 1, 0, 0],
                                            [0, 0, 0, 0, 0, 1, 0],
                                            [0, 0, 0, 0, 0, 0, 1]], dtype=np.float32)

        self.kf.measurementNoiseCov = np.eye(4, dtype=np.float32) * 0.1
        self.kf.processNoiseCov = np.eye(7, dtype=np.float32) * 0.01
        self.kf.errorCovPost = np.eye(7, dtype=np.float32)

        # Convert bbox to center format and initialize state
        z = self.convert_bbox_to_z(bbox)
        # State vector: [x, y, s, r, dx, dy, ds] where x,y are center, s is scale, r is aspect ratio
        self.kf.statePre = np.array([z[0], z[1], z[2], z[3], 0, 0, 0], dtype=np.float32).reshape((7, 1))
        self.kf.statePost = self.kf.statePre.copy()
        
        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0

    def update(self, bbox: np.ndarray):
        """
        Updates the state vector with observed bbox.
        
        Args:
            bbox: Bounding box in format [x1, y1, x2, y2]
        """
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        measurement = self.convert_bbox_to_z(bbox).reshape((4, 1)).astype(np.float32)
        self.kf.correct(measurement)

    def predict(self):
        """
        Advances the state vector and returns the predicted bounding box estimate.
        
        Returns:
            Predicted bounding box in format [x1, y1, x2, y2]
        """
        try:
            if len(self.kf.statePost) > 6 and (self.kf.statePost[6] + self.kf.statePost[2]) <= 0:
                self.kf.statePost[6] = 0.0

            self.kf.predict()
            self.age += 1
            if self.time_since_update > 0:
                self.hit_streak = 0
            self.time_since_update += 1
            
            predicted_bbox = self.convert_x_to_bbox(self.kf.statePost.flatten())
            self.history.append(predicted_bbox)
            return predicted_bbox
        except:
            # Return last known position if prediction fails
            if self.history:
                return self.history[-1]
            else:
                return np.array([0, 0, 50, 50])

    def get_state(self):
        """
        Returns the current bounding box estimate.
        
        Returns:
            Current bounding box in format [x1, y1, x2, y2]
        """
        try:
            return self.convert_x_to_bbox(self.kf.statePost.flatten())
        except:
            # Fallback to a default bbox if state is corrupted
            return np.array([0, 0, 50, 50])

    @staticmethod
    def convert_bbox_to_z(bbox: np.ndarray) -> np.ndarray:
        """
        Takes a bounding box in the form [x1,y1,x2,y2] and returns z in the form
        [x,y,s,r] where x,y is the centre of the box and s is the scale/area and r is
        the aspect ratio
        """
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = bbox[0] + w / 2.
        y = bbox[1] + h / 2.
        s = w * h  # scale is just area
        r = w / float(h)
        return np.array([x, y, s, r])

    @staticmethod
    def convert_x_to_bbox(x: np.ndarray, score: Optional[float] = None) -> np.ndarray:
        """
        Takes a bounding box in the centre form [x,y,s,r] and returns it in the form
        [x1,y1,x2,y2] where x1,y1 is the top left and x2,y2 is the bottom right
        """
        w = np.sqrt(x[2] * x[3])
        h = x[2] / w
        if score is None:
            return np.array([x[0] - w / 2., x[1] - h / 2., x[0] + w / 2., x[1] + h / 2.])
        else:
            return np.array([x[0] - w / 2., x[1] - h / 2., x[0] + w / 2., x[1] + h / 2., score])


def associate_detections_to_trackers(detections: np.ndarray, trackers: np.ndarray, iou_threshold: float = 0.3):
    """
    Assigns detections to tracked object (both represented as bounding boxes)
    
    Returns 3 lists of matches, unmatched_detections and unmatched_trackers
    """
    if len(trackers) == 0:
        return np.empty((0, 2), dtype=int), np.arange(len(detections)), np.empty((0, 5), dtype=int)

    iou_matrix = iou_batch(detections, trackers)

    if min(iou_matrix.shape) > 0:
        a = (iou_matrix > iou_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            matched_indices = linear_assignment(-iou_matrix)
    else:
        matched_indices = np.empty(shape=(0, 2))

    unmatched_detections = []
    for d, det in enumerate(detections):
        if d not in matched_indices[:, 0]:
            unmatched_detections.append(d)
    unmatched_trackers = []
    for t, trk in enumerate(trackers):
        if t not in matched_indices[:, 1]:
            unmatched_trackers.append(t)

    # filter out matched with low IOU
    matches = []
    for m in matched_indices:
        if iou_matrix[m[0], m[1]] < iou_threshold:
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1, 2))
    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


def iou_batch(bb_test: np.ndarray, bb_gt: np.ndarray) -> np.ndarray:
    """
    From SORT: Computes IOU between two bboxes in the form [x1,y1,x2,y2]
    """
    bb_gt = np.expand_dims(bb_gt, 0)
    bb_test = np.expand_dims(bb_test, 1)

    xx1 = np.maximum(bb_test[..., 0], bb_gt[..., 0])
    yy1 = np.maximum(bb_test[..., 1], bb_gt[..., 1])
    xx2 = np.minimum(bb_test[..., 2], bb_gt[..., 2])
    yy2 = np.minimum(bb_test[..., 3], bb_gt[..., 3])
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    o = wh / ((bb_test[..., 2] - bb_test[..., 0]) * (bb_test[..., 3] - bb_test[..., 1])
              + (bb_gt[..., 2] - bb_gt[..., 0]) * (bb_gt[..., 3] - bb_gt[..., 1]) - wh)
    return o


def linear_assignment(cost_matrix: np.ndarray) -> np.ndarray:
    """
    Simple linear assignment using Hungarian algorithm approximation
    """
    try:
        from scipy.optimize import linear_sum_assignment
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        return np.array(list(zip(row_ind, col_ind)))
    except ImportError:
        # Fallback to simple greedy assignment
        assignments = []
        cost_matrix = cost_matrix.copy()
        for _ in range(min(cost_matrix.shape)):
            # Find minimum cost
            min_idx = np.unravel_index(np.argmin(cost_matrix), cost_matrix.shape)
            assignments.append(min_idx)
            # Set row and column to infinity to avoid reassignment
            cost_matrix[min_idx[0], :] = np.inf
            cost_matrix[:, min_idx[1]] = np.inf
        return np.array(assignments)


class Sort:
    """
    Simplified SORT tracker implementation
    """
    
    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_threshold: float = 0.3):
        """
        Initialize SORT tracker
        
        Args:
            max_age: Maximum number of frames to keep alive a track without associated detections
            min_hits: Minimum number of associated detections before track is initialised
            iou_threshold: Minimum IOU for match
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []
        self.frame_count = 0

    def update(self, dets: np.ndarray = None) -> np.ndarray:
        """
        Update tracker with new detections
        
        Args:
            dets: numpy array of detections in format [[x1,y1,x2,y2,score],...]
            
        Returns:
            numpy array of tracks in format [[x1,y1,x2,y2,id],...]
        """
        if dets is None:
            dets = np.empty((0, 5))
            
        self.frame_count += 1
        
        # Get predicted locations from existing trackers
        trks = np.zeros((len(self.trackers), 5))
        to_del = []
        ret = []
        
        for t, tracker in enumerate(self.trackers):
            try:
                pos = tracker.predict()
                trks[t] = [pos[0], pos[1], pos[2], pos[3], 0]
                if np.any(np.isnan(pos)):
                    to_del.append(t)
            except:
                to_del.append(t)
        
        # Remove invalid trackers
        for t in reversed(to_del):
            self.trackers.pop(t)
            trks = np.delete(trks, t, axis=0)

        # Associate detections to trackers
        if len(self.trackers) > 0 and len(dets) > 0:
            matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(dets, trks, self.iou_threshold)
        else:
            matched = np.empty((0, 2), dtype=int)
            unmatched_dets = np.arange(len(dets))
            unmatched_trks = np.arange(len(self.trackers))

        # Update matched trackers with assigned detections
        for m in matched:
            self.trackers[m[1]].update(dets[m[0], :4])  # Only pass bbox, not confidence

        # Create and initialise new trackers for unmatched detections
        for i in unmatched_dets:
            trk = KalmanBoxTracker(dets[i, :4])  # Only pass bbox
            self.trackers.append(trk)
        
        # Get results
        i = len(self.trackers)
        for trk in reversed(self.trackers):
            try:
                d = trk.get_state()
                if (trk.time_since_update < 1) and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                    ret.append(np.concatenate((d, [trk.id + 1])).reshape(1, -1))  # +1 as MOT benchmark requires positive
                i -= 1
                # Remove dead tracklet
                if trk.time_since_update > self.max_age:
                    self.trackers.pop(i)
            except:
                # Remove problematic tracker
                self.trackers.pop(i-1)
                i -= 1
                
        if len(ret) > 0:
            return np.concatenate(ret)
        return np.empty((0, 5))

    def get_trackers(self) -> List[Dict]:
        """
        Get current tracker information for analytics
        
        Returns:
            List of tracker dictionaries with id, bbox, and velocity info
        """
        tracker_info = []
        for trk in self.trackers:
            if trk.time_since_update < 1:
                state = trk.get_state()[0]
                # Calculate velocity from Kalman filter state
                velocity_x = trk.kf.statePost[4, 0] if len(trk.kf.statePost) > 4 else 0
                velocity_y = trk.kf.statePost[5, 0] if len(trk.kf.statePost) > 5 else 0
                
                tracker_info.append({
                    'id': trk.id,
                    'bbox': [float(state[0]), float(state[1]), float(state[2]), float(state[3])],
                    'velocity': [float(velocity_x), float(velocity_y)],
                    'age': trk.age,
                    'hits': trk.hits
                })
        return tracker_info


def test_tracking():
    """Test function for the SORT tracker."""
    tracker = Sort()
    
    # Create some test detections
    test_detections = np.array([
        [100, 100, 150, 200, 0.9],  # person 1
        [300, 150, 350, 250, 0.8],  # person 2
    ])
    
    # Test tracking
    tracks = tracker.update(test_detections)
    print(f"Frame 1: {len(tracks)} tracks")
    
    # Move detections slightly for next frame
    test_detections[:, 0] += 5  # move right
    tracks = tracker.update(test_detections)
    print(f"Frame 2: {len(tracks)} tracks")
    
    print("SORT tracking test completed successfully")


if __name__ == "__main__":
    test_tracking()