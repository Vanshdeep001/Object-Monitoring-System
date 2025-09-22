"""
Object Tracking Module using DeepSORT
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from config import *

try:
    from deep_sort_realtime import DeepSort
    DEEPSORT_AVAILABLE = True
except ImportError:
    DEEPSORT_AVAILABLE = False
    print("Warning: deep-sort-realtime not available. Tracking will use basic centroid tracking.")

logger = logging.getLogger(__name__)


class ObjectTracker:
    """
    Object tracking using DeepSORT algorithm
    """
    
    def __init__(self, max_age: int = 30, n_init: int = 3, max_cosine_distance: float = 0.2):
        """
        Initialize the object tracker
        
        Args:
            max_age: Maximum number of frames to keep a track without detections
            n_init: Number of consecutive detections before a track is confirmed
            max_cosine_distance: Maximum cosine distance for association
        """
        if DEEPSORT_AVAILABLE:
            self.tracker = DeepSort(
                max_age=max_age,
                n_init=n_init,
                max_cosine_distance=max_cosine_distance
            )
        else:
            self.tracker = None
            # Fallback to simple centroid tracking
            self.next_id = 1
            self.tracks = {}
            self.max_disappeared = max_age
        
        self.track_history = {}  # Store track history
        self.frame_count = 0
        
        if DEEPSORT_AVAILABLE:
            logger.info("ObjectTracker initialized with DeepSORT")
        else:
            logger.info("ObjectTracker initialized with basic centroid tracking")
    
    def update_tracks(self, detections: List[Dict], frame: np.ndarray) -> List[Dict]:
        """
        Update tracks with new detections
        
        Args:
            detections: List of detection dictionaries
            frame: Current frame image
            
        Returns:
            List of tracked objects with IDs
        """
        self.frame_count += 1
        
        if DEEPSORT_AVAILABLE:
            return self._update_tracks_deepsort(detections, frame)
        else:
            return self._update_tracks_centroid(detections, frame)
    
    def _update_tracks_deepsort(self, detections: List[Dict], frame: np.ndarray) -> List[Dict]:
        """Update tracks using DeepSORT"""
        # Convert detections to DeepSORT format
        detection_list = []
        for detection in detections:
            bbox = detection['bbox']
            x1, y1, x2, y2 = bbox
            
            # DeepSORT expects [x1, y1, width, height]
            width = x2 - x1
            height = y2 - y1
            
            detection_list.append(([x1, y1, width, height], detection['confidence'], detection['class_name']))
        
        # Update tracker
        tracks = self.tracker.update_tracks(detection_list, frame=frame)
        
        # Convert tracks back to our format
        tracked_objects = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            # Get track ID
            track_id = track.track_id
            
            # Get bounding box
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = ltrb
            
            # Find corresponding detection
            class_name = "unknown"
            confidence = 0.0
            
            for detection in detections:
                det_bbox = detection['bbox']
                det_x1, det_y1, det_x2, det_y2 = det_bbox
                
                # Check if this detection corresponds to the track
                if (abs(x1 - det_x1) < 10 and abs(y1 - det_y1) < 10 and
                    abs(x2 - det_x2) < 10 and abs(y2 - det_y2) < 10):
                    class_name = detection['class_name']
                    confidence = detection['confidence']
                    break
            
            tracked_object = {
                'track_id': track_id,
                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                'class_name': class_name,
                'confidence': confidence,
                'center': (int((x1 + x2) / 2), int((y1 + y2) / 2))
            }
            
            tracked_objects.append(tracked_object)
            
            # Update track history
            if track_id not in self.track_history:
                self.track_history[track_id] = []
            
            self.track_history[track_id].append({
                'frame': self.frame_count,
                'center': tracked_object['center'],
                'bbox': tracked_object['bbox'],
                'class_name': class_name
            })
            
            # Keep only recent history (last 50 frames)
            if len(self.track_history[track_id]) > 50:
                self.track_history[track_id] = self.track_history[track_id][-50:]
        
        return tracked_objects
    
    def _update_tracks_centroid(self, detections: List[Dict], frame: np.ndarray) -> List[Dict]:
        """Update tracks using simple centroid tracking"""
        # Calculate centroids for current detections
        centroids = []
        for detection in detections:
            bbox = detection['bbox']
            x1, y1, x2, y2 = bbox
            centroid = ((x1 + x2) / 2, (y1 + y2) / 2)
            centroids.append(centroid)
        
        # If no existing tracks, create new ones
        if len(self.tracks) == 0:
            for i, (centroid, detection) in enumerate(zip(centroids, detections)):
                self.tracks[self.next_id] = {
                    'centroid': centroid,
                    'bbox': detection['bbox'],
                    'class_name': detection['class_name'],
                    'confidence': detection['confidence'],
                    'disappeared': 0
                }
                self.next_id += 1
        else:
            # Match existing tracks with new detections
            track_ids = list(self.tracks.keys())
            track_centroids = [self.tracks[tid]['centroid'] for tid in track_ids]
            
            # Simple distance-based matching
            used_detection_indices = set()
            used_track_indices = set()
            
            for i, track_centroid in enumerate(track_centroids):
                if i in used_track_indices:
                    continue
                    
                min_distance = float('inf')
                best_detection_idx = None
                
                for j, detection_centroid in enumerate(centroids):
                    if j in used_detection_indices:
                        continue
                    
                    distance = np.sqrt((track_centroid[0] - detection_centroid[0])**2 + 
                                     (track_centroid[1] - detection_centroid[1])**2)
                    
                    if distance < min_distance and distance < 50:  # Max distance threshold
                        min_distance = distance
                        best_detection_idx = j
                
                if best_detection_idx is not None:
                    # Update existing track
                    track_id = track_ids[i]
                    detection = detections[best_detection_idx]
                    
                    self.tracks[track_id]['centroid'] = centroids[best_detection_idx]
                    self.tracks[track_id]['bbox'] = detection['bbox']
                    self.tracks[track_id]['class_name'] = detection['class_name']
                    self.tracks[track_id]['confidence'] = detection['confidence']
                    self.tracks[track_id]['disappeared'] = 0
                    
                    used_detection_indices.add(best_detection_idx)
                    used_track_indices.add(i)
            
            # Add new tracks for unmatched detections
            for j, detection in enumerate(detections):
                if j not in used_detection_indices:
                    self.tracks[self.next_id] = {
                        'centroid': centroids[j],
                        'bbox': detection['bbox'],
                        'class_name': detection['class_name'],
                        'confidence': detection['confidence'],
                        'disappeared': 0
                    }
                    self.next_id += 1
            
            # Remove tracks that have disappeared for too long
            tracks_to_remove = []
            for track_id, track in self.tracks.items():
                if track_id not in [track_ids[i] for i in used_track_indices]:
                    track['disappeared'] += 1
                    if track['disappeared'] > self.max_disappeared:
                        tracks_to_remove.append(track_id)
            
            for track_id in tracks_to_remove:
                del self.tracks[track_id]
        
        # Convert tracks to our format
        tracked_objects = []
        for track_id, track in self.tracks.items():
            bbox = track['bbox']
            tracked_object = {
                'track_id': track_id,
                'bbox': bbox,
                'class_name': track['class_name'],
                'confidence': track['confidence'],
                'center': track['centroid']
            }
            tracked_objects.append(tracked_object)
            
            # Update track history
            if track_id not in self.track_history:
                self.track_history[track_id] = []
            
            self.track_history[track_id].append({
                'frame': self.frame_count,
                'center': track['centroid'],
                'bbox': bbox,
                'class_name': track['class_name']
            })
            
            # Keep only recent history (last 50 frames)
            if len(self.track_history[track_id]) > 50:
                self.track_history[track_id] = self.track_history[track_id][-50:]
        
        return tracked_objects
    
    def draw_tracks(self, frame: np.ndarray, tracked_objects: List[Dict]) -> np.ndarray:
        """
        Draw tracks on the frame
        
        Args:
            frame: Input frame
            tracked_objects: List of tracked objects
            
        Returns:
            Frame with tracks drawn
        """
        annotated_frame = frame.copy()
        
        for obj in tracked_objects:
            track_id = obj['track_id']
            bbox = obj['bbox']
            class_name = obj['class_name']
            confidence = obj['confidence']
            
            x1, y1, x2, y2 = bbox
            
            # Ensure coordinates are integers
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Choose color based on track ID
            color = COLORS[track_id % len(COLORS)]
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw track ID and class label
            label = f"ID:{track_id} {class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Draw label background
            cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10),
                        (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(annotated_frame, label, (x1, y1 - 5),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw track trail
            if track_id in self.track_history and len(self.track_history[track_id]) > 1:
                trail_points = [point['center'] for point in self.track_history[track_id][-10:]]
                for i in range(1, len(trail_points)):
                    # Convert coordinates to integers for OpenCV
                    pt1 = (int(trail_points[i-1][0]), int(trail_points[i-1][1]))
                    pt2 = (int(trail_points[i][0]), int(trail_points[i][1]))
                    cv2.line(annotated_frame, pt1, pt2, color, 2)
        
        return annotated_frame
    
    def get_track_statistics(self) -> Dict:
        """
        Get tracking statistics
        
        Returns:
            Dictionary with tracking statistics
        """
        total_tracks = len(self.track_history)
        active_tracks = len([track for track in self.track_history.values() if track])
        
        track_lengths = [len(history) for history in self.track_history.values()]
        avg_track_length = np.mean(track_lengths) if track_lengths else 0
        
        return {
            'total_tracks': total_tracks,
            'active_tracks': active_tracks,
            'average_track_length': avg_track_length,
            'frame_count': self.frame_count
        }
    
    def get_track_by_id(self, track_id: int) -> Optional[Dict]:
        """
        Get track information by ID
        
        Args:
            track_id: Track ID
            
        Returns:
            Track information or None if not found
        """
        if track_id in self.track_history:
            history = self.track_history[track_id]
            if history:
                latest = history[-1]
                return {
                    'track_id': track_id,
                    'current_position': latest['center'],
                    'current_bbox': latest['bbox'],
                    'class_name': latest['class_name'],
                    'track_length': len(history),
                    'first_seen': history[0]['frame'],
                    'last_seen': latest['frame']
                }
        return None
    
    def clear_tracks(self):
        """Clear all tracks and reset tracker"""
        self.track_history.clear()
        self.tracker = DeepSort()
        self.frame_count = 0
        logger.info("All tracks cleared")


class TrackAnalyzer:
    """
    Analyze tracking data for insights
    """
    
    def __init__(self):
        self.movement_threshold = 10  # Minimum movement in pixels
        self.stationary_threshold = 30  # Frames to consider stationary
    
    def analyze_movement(self, track_history: List[Dict]) -> Dict:
        """
        Analyze movement patterns of a track
        
        Args:
            track_history: List of track history points
            
        Returns:
            Movement analysis dictionary
        """
        if len(track_history) < 2:
            return {'status': 'insufficient_data'}
        
        # Calculate total distance traveled
        total_distance = 0
        for i in range(1, len(track_history)):
            prev_center = track_history[i-1]['center']
            curr_center = track_history[i]['center']
            distance = np.sqrt((curr_center[0] - prev_center[0])**2 + 
                            (curr_center[1] - prev_center[1])**2)
            total_distance += distance
        
        # Calculate average speed (pixels per frame)
        avg_speed = total_distance / len(track_history) if len(track_history) > 1 else 0
        
        # Determine movement status
        if avg_speed < self.movement_threshold:
            status = 'stationary'
        elif avg_speed < self.movement_threshold * 2:
            status = 'slow_moving'
        else:
            status = 'fast_moving'
        
        # Calculate direction (if moving)
        direction = None
        if len(track_history) >= 2:
            start_center = track_history[0]['center']
            end_center = track_history[-1]['center']
            
            dx = end_center[0] - start_center[0]
            dy = end_center[1] - start_center[1]
            
            if abs(dx) > abs(dy):
                direction = 'horizontal'
            elif abs(dy) > abs(dx):
                direction = 'vertical'
            else:
                direction = 'diagonal'
        
        return {
            'status': status,
            'total_distance': total_distance,
            'average_speed': avg_speed,
            'direction': direction,
            'track_length': len(track_history)
        }
    
    def detect_loitering(self, track_history: List[Dict]) -> bool:
        """
        Detect if an object is loitering in an area
        
        Args:
            track_history: List of track history points
            
        Returns:
            True if loitering detected
        """
        if len(track_history) < self.stationary_threshold:
            return False
        
        # Check if object has been in a small area for too long
        recent_points = track_history[-self.stationary_threshold:]
        centers = [point['center'] for point in recent_points]
        
        # Calculate bounding box of recent positions
        x_coords = [center[0] for center in centers]
        y_coords = [center[1] for center in centers]
        
        bbox_width = max(x_coords) - min(x_coords)
        bbox_height = max(y_coords) - min(y_coords)
        
        # If bounding box is small, object is loitering
        return bbox_width < 50 and bbox_height < 50


if __name__ == "__main__":
    # Example usage
    tracker = ObjectTracker()
    analyzer = TrackAnalyzer()
    
    print("ObjectTracker and TrackAnalyzer initialized")
