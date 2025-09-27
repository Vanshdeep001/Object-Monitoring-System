"""
Core Object Detection Module using YOLOv8
"""

import cv2
import numpy as np
import torch
from ultralytics import YOLO
from typing import List, Tuple, Dict, Optional
import logging
from config import *

# Set up logging
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class ObjectDetector:
    """
    YOLOv8-based object detector with enhanced features
    """
    
    def __init__(self, model_path: str = MODEL_PATH, custom_model: bool = False):
        """
        Initialize the object detector
        
        Args:
            model_path: Path to the YOLO model
            custom_model: Whether to use a custom trained model
        """
        self.model_path = model_path
        self.custom_model = custom_model
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load model
        self._load_model()
        
        logger.info(f"ObjectDetector initialized with device: {self.device}")
    
    def _load_model(self):
        """Load the YOLO model"""
        try:
            # Fix PyTorch weights_only issue by setting weights_only=False
            import torch
            original_load = torch.load
            
            def patched_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return original_load(*args, **kwargs)
            
            torch.load = patched_load
            
            if self.custom_model and CUSTOM_MODEL_PATH:
                self.model = YOLO(CUSTOM_MODEL_PATH)
                logger.info(f"Loaded custom model: {CUSTOM_MODEL_PATH}")
            else:
                self.model = YOLO(self.model_path)
                logger.info(f"Loaded pre-trained model: {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def detect_objects(self, image: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Detect objects in an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (detections, annotated_image)
        """
        try:
            # Run inference
            results = self.model(image, conf=CONFIDENCE_THRESHOLD, iou=IOU_THRESHOLD)
            
            detections = []
            annotated_image = image.copy()
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        # Extract box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Get class name
                        class_name = COCO_CLASSES[class_id] if class_id < len(COCO_CLASSES) else f"class_{class_id}"
                        
                        detection = {
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': class_name
                        }
                        detections.append(detection)
                        
                        # Draw bounding box
                        color = COLORS[class_id % len(COLORS)]
                        cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        
                        # Draw label
                        label = f"{class_name}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                        cv2.rectangle(annotated_image, (int(x1), int(y1) - label_size[1] - 10),
                                    (int(x1) + label_size[0], int(y1)), color, -1)
                        cv2.putText(annotated_image, label, (int(x1), int(y1) - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            return detections, annotated_image
            
        except Exception as e:
            logger.error(f"Error in object detection: {e}")
            return [], image
    
    def count_objects(self, detections: List[Dict]) -> Dict[str, int]:
        """
        Count objects by class
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Dictionary with class names as keys and counts as values
        """
        counts = {}
        for detection in detections:
            class_name = detection['class_name']
            counts[class_name] = counts.get(class_name, 0) + 1
        return counts
    
    def detect_video(self, video_path: str, output_path: Optional[str] = None) -> List[Dict]:
        """
        Detect objects in a video file
        
        Args:
            video_path: Path to input video
            output_path: Path to save annotated video (optional)
            
        Returns:
            List of detection results for each frame
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Error opening video file: {video_path}")
            return []
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer if output path is provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        all_detections = []
        frame_count = 0
        
        logger.info(f"Processing video: {video_path}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect objects in frame
            detections, annotated_frame = self.detect_objects(frame)
            
            # Count objects
            counts = self.count_objects(detections)
            
            # Add count information to frame
            y_offset = 30
            for class_name, count in counts.items():
                count_text = f"{class_name}: {count}"
                cv2.putText(annotated_frame, count_text, (10, y_offset),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_offset += 30
            
            # Store detection results
            frame_result = {
                'frame_number': frame_count,
                'detections': detections,
                'counts': counts
            }
            all_detections.append(frame_result)
            
            # Write frame if output video is requested
            if writer:
                writer.write(annotated_frame)
            
            frame_count += 1
            
            # Show progress
            if frame_count % 100 == 0:
                logger.info(f"Processed {frame_count} frames")
        
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        
        logger.info(f"Video processing completed. Total frames: {frame_count}")
        return all_detections
    
    def detect_webcam(self, camera_index: int = 0, show_window: bool = True) -> None:
        """
        Detect objects in live webcam feed
        
        Args:
            camera_index: Camera index (default: 0)
            show_window: Whether to display the video window
        """
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            logger.error(f"Error opening camera {camera_index}")
            return
        
        logger.info("Starting webcam detection. Press 'q' to quit.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("Error reading from camera")
                break
            
            # Detect objects
            detections, annotated_frame = self.detect_objects(frame)
            
            # Count objects
            counts = self.count_objects(detections)
            
            # Display counts
            y_offset = 30
            for class_name, count in counts.items():
                count_text = f"{class_name}: {count}"
                cv2.putText(annotated_frame, count_text, (10, y_offset),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_offset += 30
            
            # Show frame
            if show_window:
                cv2.imshow('Object Detection', annotated_frame)
                
                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Webcam detection stopped")


if __name__ == "__main__":
    # Example usage
    detector = ObjectDetector()
    
    # Test with webcam
    detector.detect_webcam()
