"""
Zone Monitoring Module for Restricted Area Detection
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Optional
import time
import winsound  # For Windows sound alerts
from config import *

logger = logging.getLogger(__name__)


class ZoneMonitor:
    """
    Monitors restricted zones and triggers alerts when objects enter
    """
    
    def __init__(self):
        self.restricted_zones = []  # List of zone polygons
        self.alert_threshold = 0.5  # Minimum confidence for alerts
        self.alert_cooldown = 2.0  # Seconds between alerts for same zone
        self.last_alert_times = {}  # Track last alert time per zone
        self.monitored_classes = ['person', 'car', 'truck', 'motorcycle', 'bicycle']  # Classes to monitor
        
    def add_rectangular_zone(self, x1: int, y1: int, x2: int, y2: int, zone_name: str = None):
        """
        Add a rectangular restricted zone
        
        Args:
            x1, y1: Top-left corner coordinates
            x2, y2: Bottom-right corner coordinates
            zone_name: Optional name for the zone
        """
        zone = {
            'type': 'rectangle',
            'points': [(x1, y1), (x2, y2)],
            'name': zone_name or f"Zone_{len(self.restricted_zones) + 1}"
        }
        self.restricted_zones.append(zone)
        logger.info(f"Added rectangular zone: {zone['name']}")
    
    def add_polygonal_zone(self, points: List[Tuple[int, int]], zone_name: str = None):
        """
        Add a polygonal restricted zone
        
        Args:
            points: List of (x, y) coordinates defining the polygon
            zone_name: Optional name for the zone
        """
        if len(points) < 3:
            logger.error("Polygon must have at least 3 points")
            return
        
        zone = {
            'type': 'polygon',
            'points': points,
            'name': zone_name or f"Zone_{len(self.restricted_zones) + 1}"
        }
        self.restricted_zones.append(zone)
        logger.info(f"Added polygonal zone: {zone['name']}")
    
    def point_in_zone(self, point: Tuple[int, int], zone: Dict) -> bool:
        """
        Check if a point is inside a zone
        
        Args:
            point: (x, y) coordinates
            zone: Zone dictionary
            
        Returns:
            True if point is inside zone
        """
        x, y = point
        
        if zone['type'] == 'rectangle':
            (x1, y1), (x2, y2) = zone['points']
            return x1 <= x <= x2 and y1 <= y <= y2
        
        elif zone['type'] == 'polygon':
            points = np.array(zone['points'])
            return cv2.pointPolygonTest(points, (x, y), False) >= 0
        
        return False
    
    def check_zone_violations(self, detections: List[Dict]) -> List[Dict]:
        """
        Check for zone violations in detections
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        current_time = time.time()
        
        for detection in detections:
            # Only check monitored classes
            if detection['class_name'] not in self.monitored_classes:
                continue
            
            # Get center point of bounding box
            bbox = detection['bbox']
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            
            # Check each zone
            for zone in self.restricted_zones:
                if self.point_in_zone((center_x, center_y), zone):
                    # Check alert cooldown
                    zone_key = zone['name']
                    if zone_key in self.last_alert_times:
                        if current_time - self.last_alert_times[zone_key] < self.alert_cooldown:
                            continue
                    
                    violation = {
                        'zone_name': zone['name'],
                        'object_class': detection['class_name'],
                        'confidence': detection['confidence'],
                        'bbox': bbox,
                        'center': (center_x, center_y),
                        'timestamp': current_time
                    }
                    violations.append(violation)
                    
                    # Update last alert time
                    self.last_alert_times[zone_key] = current_time
                    
                    # Trigger alert
                    self._trigger_alert(violation)
        
        return violations
    
    def _trigger_alert(self, violation: Dict):
        """
        Trigger an alert for a zone violation
        
        Args:
            violation: Violation dictionary
        """
        alert_message = f"ALERT: {violation['object_class']} detected in {violation['zone_name']}!"
        logger.warning(alert_message)
        print(f"\n🚨 {alert_message}")
        
        # Play sound alert (Windows)
        try:
            winsound.Beep(1000, 500)  # 1000Hz for 500ms
        except:
            pass  # Ignore if sound not available
    
    def draw_zones(self, image: np.ndarray) -> np.ndarray:
        """
        Draw restricted zones on the image
        
        Args:
            image: Input image
            
        Returns:
            Image with zones drawn
        """
        annotated_image = image.copy()
        
        for zone in self.restricted_zones:
            if zone['type'] == 'rectangle':
                (x1, y1), (x2, y2) = zone['points']
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), RESTRICTED_ZONE_COLOR, 2)
                
                # Draw zone label
                label = zone['name']
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(annotated_image, (x1, y1 - label_size[1] - 10),
                            (x1 + label_size[0], y1), RESTRICTED_ZONE_COLOR, -1)
                cv2.putText(annotated_image, label, (x1, y1 - 5),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            elif zone['type'] == 'polygon':
                points = np.array(zone['points'], np.int32)
                cv2.polylines(annotated_image, [points], True, RESTRICTED_ZONE_COLOR, 2)
                
                # Draw zone label at centroid
                centroid = np.mean(points, axis=0).astype(int)
                label = zone['name']
                cv2.putText(annotated_image, label, tuple(centroid),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, RESTRICTED_ZONE_COLOR, 2)
        
        return annotated_image
    
    def draw_violations(self, image: np.ndarray, violations: List[Dict]) -> np.ndarray:
        """
        Draw violation indicators on the image
        
        Args:
            image: Input image
            violations: List of violation dictionaries
            
        Returns:
            Image with violations drawn
        """
        annotated_image = image.copy()
        
        for violation in violations:
            bbox = violation['bbox']
            x1, y1, x2, y2 = bbox
            
            # Draw alert box around violating object
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), ALERT_COLOR, 3)
            
            # Draw alert label
            alert_text = f"VIOLATION: {violation['object_class']}"
            label_size = cv2.getTextSize(alert_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(annotated_image, (x1, y1 - label_size[1] - 10),
                        (x1 + label_size[0], y1), ALERT_COLOR, -1)
            cv2.putText(annotated_image, alert_text, (x1, y1 - 5),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        return annotated_image
    
    def clear_zones(self):
        """Clear all restricted zones"""
        self.restricted_zones.clear()
        self.last_alert_times.clear()
        logger.info("All zones cleared")
    
    def get_zone_info(self) -> List[Dict]:
        """
        Get information about all zones
        
        Returns:
            List of zone information dictionaries
        """
        return [
            {
                'name': zone['name'],
                'type': zone['type'],
                'points': zone['points']
            }
            for zone in self.restricted_zones
        ]


class InteractiveZoneSelector:
    """
    Interactive zone selector for drawing zones on images/video
    """
    
    def __init__(self):
        self.drawing = False
        self.current_zone = []
        self.zones = []
        self.mode = 'rectangle'  # 'rectangle' or 'polygon'
        self.window_name = 'Zone Selector'
    
    def mouse_callback(self, event, x, y, flags, param):
        """Mouse callback for interactive zone drawing"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.mode == 'rectangle':
                if len(self.current_zone) == 0:
                    self.current_zone = [(x, y)]
                    self.drawing = True
                elif len(self.current_zone) == 1:
                    self.current_zone.append((x, y))
                    self.zones.append({
                        'type': 'rectangle',
                        'points': self.current_zone.copy(),
                        'name': f"Zone_{len(self.zones) + 1}"
                    })
                    self.current_zone = []
                    self.drawing = False
            
            elif self.mode == 'polygon':
                self.current_zone.append((x, y))
                self.drawing = True
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.mode == 'polygon' and len(self.current_zone) >= 3:
                self.zones.append({
                    'type': 'polygon',
                    'points': self.current_zone.copy(),
                    'name': f"Zone_{len(self.zones) + 1}"
                })
                self.current_zone = []
                self.drawing = False
    
    def select_zones_interactive(self, image: np.ndarray) -> List[Dict]:
        """
        Interactive zone selection on an image
        
        Args:
            image: Input image
            
        Returns:
            List of selected zones
        """
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print("Zone Selection Instructions:")
        print("- Left click to draw zones")
        print("- Right click to finish polygon")
        print("- Press 'r' to switch to rectangle mode")
        print("- Press 'p' to switch to polygon mode")
        print("- Press 'c' to clear all zones")
        print("- Press 'q' to quit")
        
        while True:
            display_image = image.copy()
            
            # Draw completed zones
            for zone in self.zones:
                if zone['type'] == 'rectangle':
                    (x1, y1), (x2, y2) = zone['points']
                    cv2.rectangle(display_image, (x1, y1), (x2, y2), RESTRICTED_ZONE_COLOR, 2)
                elif zone['type'] == 'polygon':
                    points = np.array(zone['points'], np.int32)
                    cv2.polylines(display_image, [points], True, RESTRICTED_ZONE_COLOR, 2)
            
            # Draw current zone being drawn
            if self.drawing:
                if self.mode == 'rectangle' and len(self.current_zone) == 1:
                    cv2.circle(display_image, self.current_zone[0], 5, RESTRICTED_ZONE_COLOR, -1)
                elif self.mode == 'polygon' and len(self.current_zone) > 0:
                    for point in self.current_zone:
                        cv2.circle(display_image, point, 5, RESTRICTED_ZONE_COLOR, -1)
                    if len(self.current_zone) > 1:
                        points = np.array(self.current_zone, np.int32)
                        cv2.polylines(display_image, [points], False, RESTRICTED_ZONE_COLOR, 2)
            
            cv2.imshow(self.window_name, display_image)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.mode = 'rectangle'
                self.current_zone = []
                self.drawing = False
                print("Switched to rectangle mode")
            elif key == ord('p'):
                self.mode = 'polygon'
                self.current_zone = []
                self.drawing = False
                print("Switched to polygon mode")
            elif key == ord('c'):
                self.zones.clear()
                self.current_zone = []
                self.drawing = False
                print("Cleared all zones")
        
        cv2.destroyAllWindows()
        return self.zones


if __name__ == "__main__":
    # Example usage
    monitor = ZoneMonitor()
    
    # Add some example zones
    monitor.add_rectangular_zone(100, 100, 300, 200, "Restricted Area 1")
    monitor.add_polygonal_zone([(400, 100), (500, 150), (450, 250), (350, 200)], "Restricted Area 2")
    
    print("Zone Monitor initialized with example zones")
