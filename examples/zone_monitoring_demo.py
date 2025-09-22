"""
Zone Monitoring Demo with Interactive Zone Selection
"""

import cv2
import numpy as np
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zone_monitor import ZoneMonitor, InteractiveZoneSelector
from object_detector import ObjectDetector

def create_test_image():
    """Create a test image with some objects"""
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some objects
    cv2.rectangle(image, (100, 100), (200, 200), (255, 0, 0), -1)  # Blue rectangle
    cv2.circle(image, (400, 150), 50, (0, 255, 0), -1)  # Green circle
    cv2.rectangle(image, (300, 300), (400, 400), (0, 0, 255), -1)  # Red rectangle
    
    # Add text
    cv2.putText(image, "Test Image for Zone Monitoring", (150, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    return image

def main():
    """Zone monitoring demonstration"""
    print("Zone Monitoring Demo")
    print("=" * 40)
    
    # Create test image
    test_image = create_test_image()
    cv2.imwrite("output/test_image.jpg", test_image)
    
    # Initialize components
    detector = ObjectDetector()
    zone_monitor = ZoneMonitor()
    
    # Add some predefined zones
    print("Adding predefined zones...")
    zone_monitor.add_rectangular_zone(50, 50, 250, 250, "Zone 1")
    zone_monitor.add_polygonal_zone([(300, 100), (500, 150), (450, 300), (250, 250)], "Zone 2")
    
    # Detect objects
    print("Detecting objects...")
    detections, detection_image = detector.detect_objects(test_image)
    
    print(f"Detected {len(detections)} objects:")
    for i, detection in enumerate(detections):
        print(f"  {i+1}. {detection['class_name']} at {detection['bbox']}")
    
    # Check for zone violations
    print("\nChecking zone violations...")
    violations = zone_monitor.check_zone_violations(detections)
    
    if violations:
        print(f"Found {len(violations)} zone violations:")
        for violation in violations:
            print(f"  - {violation['object_class']} in {violation['zone_name']}")
    else:
        print("No zone violations detected")
    
    # Draw zones and violations
    annotated_image = detection_image.copy()
    annotated_image = zone_monitor.draw_zones(annotated_image)
    if violations:
        annotated_image = zone_monitor.draw_violations(annotated_image, violations)
    
    # Save results
    cv2.imwrite("output/zone_monitoring_result.jpg", annotated_image)
    
    print("\nResults saved to:")
    print("  - output/test_image.jpg (original)")
    print("  - output/zone_monitoring_result.jpg (with zones and violations)")
    
    # Interactive zone selection demo
    print("\nInteractive Zone Selection Demo")
    print("You can now interactively select zones on the image.")
    print("Instructions:")
    print("  - Left click to draw zones")
    print("  - Right click to finish polygon")
    print("  - Press 'r' for rectangle mode")
    print("  - Press 'p' for polygon mode")
    print("  - Press 'c' to clear zones")
    print("  - Press 'q' to quit")
    
    selector = InteractiveZoneSelector()
    selected_zones = selector.select_zones_interactive(test_image)
    
    print(f"\nSelected {len(selected_zones)} zones interactively:")
    for zone in selected_zones:
        print(f"  - {zone['name']} ({zone['type']})")

if __name__ == "__main__":
    main()

