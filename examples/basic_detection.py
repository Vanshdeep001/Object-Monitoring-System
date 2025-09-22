"""
Basic Object Detection Example
"""

import cv2
import numpy as np
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from object_detector import ObjectDetector

def main():
    """Basic object detection example"""
    print("Basic Object Detection Example")
    print("=" * 40)
    
    # Initialize detector
    detector = ObjectDetector()
    
    # Create a sample image (in real usage, you would load an actual image)
    sample_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some shapes to simulate objects
    cv2.rectangle(sample_image, (100, 100), (200, 200), (255, 0, 0), -1)  # Blue rectangle
    cv2.circle(sample_image, (400, 150), 50, (0, 255, 0), -1)  # Green circle
    cv2.putText(sample_image, "Sample Image", (250, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Detect objects
    detections, annotated_image = detector.detect_objects(sample_image)
    
    # Display results
    print(f"Detected {len(detections)} objects:")
    for i, detection in enumerate(detections):
        print(f"  {i+1}. {detection['class_name']} (confidence: {detection['confidence']:.3f})")
    
    # Count objects
    counts = detector.count_objects(detections)
    print(f"\nObject counts: {counts}")
    
    # Save annotated image
    cv2.imwrite("output/basic_detection_result.jpg", annotated_image)
    print("\nAnnotated image saved to: output/basic_detection_result.jpg")

if __name__ == "__main__":
    main()
