"""
Main Monitoring System integrating all components
"""

import cv2
import numpy as np
import logging
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from object_detector import ObjectDetector
from object_tracker import ObjectTracker, TrackAnalyzer
from image_enhancer import ImageEnhancer
from logger import DetectionLogger, ActivityLogger
from config import *

logger = logging.getLogger(__name__)


class MonitoringSystem:
    """
    Main monitoring system that integrates all components
    """
    
    def __init__(self, model_path: str = MODEL_PATH, enable_tracking: bool = True,
                 enable_enhancement: bool = True, enable_logging: bool = True):
        """
        Initialize the monitoring system
        
        Args:
            model_path: Path to YOLO model
            enable_tracking: Whether to enable object tracking
            enable_enhancement: Whether to enable image enhancement
            enable_logging: Whether to enable logging
        """
        # Initialize components
        self.detector = ObjectDetector(model_path)
        self.tracker = ObjectTracker() if enable_tracking else None
        self.enhancer = ImageEnhancer() if enable_enhancement else None
        self.detection_logger = DetectionLogger() if enable_logging else None
        self.activity_logger = ActivityLogger() if enable_logging else None
        
        # System state
        self.is_running = False
        self.frame_count = 0
        self.start_time = None
        
        # Statistics
        self.total_detections = 0
        self.object_counts = {}
        
        logger.info("MonitoringSystem initialized")
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Process a single frame through the monitoring system
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (annotated_frame, results_dict)
        """
        self.frame_count += 1
        
        # Enhance image if enabled
        if self.enhancer:
            enhanced_frame = self.enhancer.enhance_image(frame, 'auto')
        else:
            enhanced_frame = frame
        
        # Detect objects
        detections, detection_frame = self.detector.detect_objects(enhanced_frame)
        
        # Update object counts
        counts = self.detector.count_objects(detections)
        for class_name, count in counts.items():
            self.object_counts[class_name] = self.object_counts.get(class_name, 0) + count
        
        # Track objects if enabled
        tracked_objects = []
        if self.tracker:
            tracked_objects = self.tracker.update_tracks(detections, enhanced_frame)
        
        # Update statistics
        self.total_detections += len(detections)
        
        # Create annotated frame
        annotated_frame = detection_frame.copy()
        
        # Draw tracks
        if self.tracker and tracked_objects:
            annotated_frame = self.tracker.draw_tracks(annotated_frame, tracked_objects)
        
        # Draw statistics
        annotated_frame = self._draw_statistics(annotated_frame, counts)
        
        # Log detections if enabled
        if self.detection_logger:
            self.detection_logger.log_frame_detections(
                self.frame_count, detections, tracked_objects, []
            )
        
        # Prepare results
        results = {
            'frame_number': self.frame_count,
            'detections': detections,
            'tracked_objects': tracked_objects,
            'counts': counts,
            'total_detections': self.total_detections
        }
        
        return annotated_frame, results
    
    def _draw_statistics(self, frame: np.ndarray, counts: Dict[str, int]) -> np.ndarray:
        """
        Draw statistics on the frame
        
        Args:
            frame: Input frame
            counts: Object counts
            
        Returns:
            Frame with statistics drawn
        """
        annotated_frame = frame.copy()
        
        # Draw frame info
        info_text = f"Frame: {self.frame_count} | Detections: {self.total_detections}"
        cv2.putText(annotated_frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw object counts
        y_offset = 60
        for class_name, count in counts.items():
            count_text = f"{class_name}: {count}"
            cv2.putText(annotated_frame, count_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25
        
        return annotated_frame
    
    def monitor_webcam(self, camera_index: int = 0, show_window: bool = True):
        """
        Monitor live webcam feed
        
        Args:
            camera_index: Camera index
            show_window: Whether to show video window
        """
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            logger.error(f"Error opening camera {camera_index}")
            return
        
        self.is_running = True
        self.start_time = time.time()
        
        # Log system start
        if self.activity_logger:
            config = {
                'model_path': self.detector.model_path,
                'tracking_enabled': self.tracker is not None,
                'enhancement_enabled': self.enhancer is not None,
                'logging_enabled': self.detection_logger is not None
            }
            self.activity_logger.log_system_start(config)
        
        logger.info("Starting webcam monitoring. Press 'q' to quit.")
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                logger.error("Error reading from camera")
                break
            
            # Process frame
            annotated_frame, results = self.process_frame(frame)
            
            # Show frame
            if show_window:
                cv2.imshow('Object Monitoring System', annotated_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        self.is_running = False
        
        # Log system stop
        if self.activity_logger:
            self.activity_logger.log_system_stop()
        
        logger.info("Webcam monitoring stopped")
    
    def monitor_video(self, video_path: str, output_path: Optional[str] = None):
        """
        Monitor video file
        
        Args:
            video_path: Path to input video
            output_path: Path to save annotated video
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Error opening video file: {video_path}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer if output path is provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        self.is_running = True
        self.start_time = time.time()
        
        # Log system start
        if self.activity_logger:
            config = {
                'input_video': video_path,
                'output_video': output_path,
                'tracking_enabled': self.tracker is not None,
                'enhancement_enabled': self.enhancer is not None,
                'logging_enabled': self.detection_logger is not None
            }
            self.activity_logger.log_system_start(config)
        
        logger.info(f"Processing video: {video_path}")
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            annotated_frame, results = self.process_frame(frame)
            
            # Write frame if output video is requested
            if writer:
                writer.write(annotated_frame)
            
            # Show progress
            if self.frame_count % 100 == 0:
                logger.info(f"Processed {self.frame_count} frames")
        
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        
        self.is_running = False
        
        # Log system stop
        if self.activity_logger:
            self.activity_logger.log_system_stop()
        
        logger.info(f"Video processing completed. Total frames: {self.frame_count}")
    
    def get_system_statistics(self) -> Dict:
        """
        Get system statistics
        
        Returns:
            Dictionary with system statistics
        """
        runtime = time.time() - self.start_time if self.start_time else 0
        
        stats = {
            'runtime_seconds': runtime,
            'frame_count': self.frame_count,
            'fps': self.frame_count / runtime if runtime > 0 else 0,
            'total_detections': self.total_detections,
            'object_counts': self.object_counts.copy()
        }
        
        # Add tracking statistics if enabled
        if self.tracker:
            track_stats = self.tracker.get_track_statistics()
            stats['tracking'] = track_stats
        
        return stats
    
    def export_logs(self, output_file: str) -> bool:
        """
        Export logs to Excel file
        
        Args:
            output_file: Path to output Excel file
            
        Returns:
            True if successful
        """
        if self.detection_logger:
            return self.detection_logger.export_to_excel(output_file)
        return False
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_running = False
        logger.info("Monitoring system stopped")


if __name__ == "__main__":
    # Example usage
    system = MonitoringSystem()
    
    # Start monitoring
    system.monitor_webcam()
