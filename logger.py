"""
Logging System for Object Detection and Monitoring
"""

import csv
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from config import *

# Set up logging
logger = logging.getLogger(__name__)


class DetectionLogger:
    """
    Logs object detection results to CSV and JSON files
    """
    
    def __init__(self, log_file: str = LOG_FILE, json_log_file: Optional[str] = None):
        """
        Initialize the detection logger
        
        Args:
            log_file: Path to CSV log file
            json_log_file: Path to JSON log file (optional)
        """
        self.csv_log_file = log_file
        self.json_log_file = json_log_file or log_file.replace('.csv', '.json')
        
        # Initialize CSV file with headers if it doesn't exist
        self._initialize_csv_file()
        
        logger.info(f"DetectionLogger initialized. CSV: {self.csv_log_file}, JSON: {self.json_log_file}")
    
    def _initialize_csv_file(self):
        """Initialize CSV file with headers"""
        if not os.path.exists(self.csv_log_file):
            with open(self.csv_log_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp', 'frame_number', 'object_id', 'class_name', 'confidence',
                    'bbox_x1', 'bbox_y1', 'bbox_x2', 'bbox_y2', 'center_x', 'center_y',
                    'zone_violation', 'zone_name', 'track_length', 'movement_status'
                ])
    
    def log_detection(self, detection_data: Dict[str, Any]):
        """
        Log a single detection
        
        Args:
            detection_data: Dictionary containing detection information
        """
        try:
            # Prepare CSV row
            csv_row = [
                detection_data.get('timestamp', datetime.now().isoformat()),
                detection_data.get('frame_number', 0),
                detection_data.get('object_id', ''),
                detection_data.get('class_name', ''),
                detection_data.get('confidence', 0.0),
                detection_data.get('bbox', [0, 0, 0, 0])[0],
                detection_data.get('bbox', [0, 0, 0, 0])[1],
                detection_data.get('bbox', [0, 0, 0, 0])[2],
                detection_data.get('bbox', [0, 0, 0, 0])[3],
                detection_data.get('center', (0, 0))[0],
                detection_data.get('center', (0, 0))[1],
                detection_data.get('zone_violation', False),
                detection_data.get('zone_name', ''),
                detection_data.get('track_length', 0),
                detection_data.get('movement_status', '')
            ]
            
            # Write to CSV
            with open(self.csv_log_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(csv_row)
            
            # Write to JSON (append to array)
            self._append_to_json(detection_data)
            
        except Exception as e:
            logger.error(f"Error logging detection: {e}")
    
    def log_frame_detections(self, frame_number: int, detections: List[Dict], 
                           tracked_objects: List[Dict] = None, 
                           violations: List[Dict] = None):
        """
        Log all detections from a frame
        
        Args:
            frame_number: Frame number
            detections: List of detection dictionaries
            tracked_objects: List of tracked objects (optional)
            violations: List of zone violations (optional)
        """
        timestamp = datetime.now().isoformat()
        
        # Create violation lookup
        violation_lookup = {}
        if violations:
            for violation in violations:
                bbox = violation['bbox']
                center = violation['center']
                violation_lookup[(center[0], center[1])] = violation
        
        # Create track lookup
        track_lookup = {}
        if tracked_objects:
            for track in tracked_objects:
                center = track['center']
                track_lookup[(center[0], center[1])] = track
        
        # Log each detection
        for detection in detections:
            center = detection.get('center', (0, 0))
            
            # Check for violations
            violation = violation_lookup.get(center, None)
            zone_violation = violation is not None
            zone_name = violation['zone_name'] if violation else ''
            
            # Check for tracking info
            track = track_lookup.get(center, None)
            object_id = track['track_id'] if track else ''
            track_length = track.get('track_length', 0) if track else 0
            
            detection_data = {
                'timestamp': timestamp,
                'frame_number': frame_number,
                'object_id': object_id,
                'class_name': detection['class_name'],
                'confidence': detection['confidence'],
                'bbox': detection['bbox'],
                'center': center,
                'zone_violation': zone_violation,
                'zone_name': zone_name,
                'track_length': track_length,
                'movement_status': ''
            }
            
            self.log_detection(detection_data)
    
    def _append_to_json(self, detection_data: Dict[str, Any]):
        """Append detection data to JSON log file"""
        try:
            # Read existing data
            if os.path.exists(self.json_log_file):
                with open(self.json_log_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                data = []
            
            # Append new data
            data.append(detection_data)
            
            # Write back to file
            with open(self.json_log_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error writing to JSON log: {e}")
    
    def get_detection_summary(self, start_time: Optional[str] = None, 
                           end_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary statistics from logged detections
        
        Args:
            start_time: Start time filter (ISO format)
            end_time: End time filter (ISO format)
            
        Returns:
            Summary statistics dictionary
        """
        try:
            # Read CSV data
            df = pd.read_csv(self.csv_log_file)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Apply time filters
            if start_time:
                df = df[df['timestamp'] >= pd.to_datetime(start_time)]
            if end_time:
                df = df[df['timestamp'] <= pd.to_datetime(end_time)]
            
            # Calculate statistics
            total_detections = len(df)
            unique_objects = df['object_id'].nunique() if 'object_id' in df.columns else 0
            class_counts = df['class_name'].value_counts().to_dict()
            zone_violations = df['zone_violation'].sum() if 'zone_violation' in df.columns else 0
            
            # Calculate average confidence
            avg_confidence = df['confidence'].mean() if 'confidence' in df.columns else 0
            
            # Get time range
            time_range = {
                'start': df['timestamp'].min().isoformat() if len(df) > 0 else None,
                'end': df['timestamp'].max().isoformat() if len(df) > 0 else None
            }
            
            return {
                'total_detections': total_detections,
                'unique_objects': unique_objects,
                'class_counts': class_counts,
                'zone_violations': zone_violations,
                'average_confidence': avg_confidence,
                'time_range': time_range
            }
            
        except Exception as e:
            logger.error(f"Error generating detection summary: {e}")
            return {}
    
    def export_to_excel(self, output_file: str, start_time: Optional[str] = None,
                       end_time: Optional[str] = None) -> bool:
        """
        Export logged data to Excel file
        
        Args:
            output_file: Path to output Excel file
            start_time: Start time filter (ISO format)
            end_time: End time filter (ISO format)
            
        Returns:
            True if successful
        """
        try:
            # Read CSV data
            df = pd.read_csv(self.csv_log_file)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Apply time filters
            if start_time:
                df = df[df['timestamp'] >= pd.to_datetime(start_time)]
            if end_time:
                df = df[df['timestamp'] <= pd.to_datetime(end_time)]
            
            # Export to Excel
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name='Detections', index=False)
                
                # Summary sheet
                summary = self.get_detection_summary(start_time, end_time)
                summary_df = pd.DataFrame([summary])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Class counts sheet
                if 'class_name' in df.columns:
                    class_counts = df['class_name'].value_counts().reset_index()
                    class_counts.columns = ['Class', 'Count']
                    class_counts.to_excel(writer, sheet_name='Class_Counts', index=False)
            
            logger.info(f"Data exported to Excel: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return False


class ActivityLogger:
    """
    Logs system activity and events
    """
    
    def __init__(self, activity_log_file: str = None):
        """
        Initialize activity logger
        
        Args:
            activity_log_file: Path to activity log file
        """
        self.activity_log_file = activity_log_file or os.path.join(LOG_DIR, "activity_log.txt")
        
        # Set up file handler
        self.file_handler = logging.FileHandler(self.activity_log_file)
        self.file_handler.setLevel(logging.INFO)
        
        # Set up formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger = logging.getLogger('activity')
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)
        
        logger.info(f"ActivityLogger initialized: {self.activity_log_file}")
    
    def log_system_start(self, config: Dict[str, Any]):
        """Log system startup"""
        self.logger.info("=== SYSTEM STARTED ===")
        self.logger.info(f"Configuration: {json.dumps(config, indent=2)}")
    
    def log_system_stop(self):
        """Log system shutdown"""
        self.logger.info("=== SYSTEM STOPPED ===")
    
    def log_zone_alert(self, violation: Dict[str, Any]):
        """Log zone violation alert"""
        self.logger.warning(f"ZONE ALERT: {violation}")
    
    def log_tracking_event(self, event: str, track_id: int, details: Dict[str, Any] = None):
        """Log tracking events"""
        message = f"TRACKING EVENT: {event} - Track ID: {track_id}"
        if details:
            message += f" - Details: {details}"
        self.logger.info(message)
    
    def log_error(self, error_message: str, exception: Exception = None):
        """Log errors"""
        message = f"ERROR: {error_message}"
        if exception:
            message += f" - Exception: {str(exception)}"
        self.logger.error(message)


if __name__ == "__main__":
    # Example usage
    detection_logger = DetectionLogger()
    activity_logger = ActivityLogger()
    
    # Test logging
    test_detection = {
        'timestamp': datetime.now().isoformat(),
        'frame_number': 1,
        'object_id': '1',
        'class_name': 'person',
        'confidence': 0.95,
        'bbox': [100, 100, 200, 300],
        'center': (150, 200),
        'zone_violation': False,
        'zone_name': '',
        'track_length': 1,
        'movement_status': 'moving'
    }
    
    detection_logger.log_detection(test_detection)
    
    # Get summary
    summary = detection_logger.get_detection_summary()
    print("Detection Summary:", summary)
    
    print("Logging system initialized and tested")
