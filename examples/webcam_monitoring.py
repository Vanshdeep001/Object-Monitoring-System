"""
Webcam Monitoring Example with Zone Detection
"""

import cv2
import time
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitoring_system import MonitoringSystem

def main():
    """Webcam monitoring with zone detection example"""
    print("Webcam Monitoring Example")
    print("=" * 40)
    
    # Initialize monitoring system
    system = MonitoringSystem(
        enable_tracking=True,
        enable_enhancement=True,
        enable_logging=True
    )
    
    # Add some example restricted zones
    print("Adding restricted zones...")
    system.add_restricted_zone('rectangle', [(100, 100), (300, 200)], "Restricted Area 1")
    system.add_restricted_zone('polygon', [(400, 100), (500, 150), (450, 250), (350, 200)], "Restricted Area 2")
    
    print("Starting webcam monitoring...")
    print("Press 'q' to quit, 'z' to add zone interactively")
    
    # Start monitoring
    system.monitor_webcam(camera_index=0, show_window=True)
    
    # Display final statistics
    stats = system.get_system_statistics()
    print("\nFinal Statistics:")
    print(f"  Total frames processed: {stats['frame_count']}")
    print(f"  Total detections: {stats['total_detections']}")
    print(f"  Zone violations: {stats['total_violations']}")
    print(f"  Average FPS: {stats['fps']:.2f}")
    
    # Export logs
    if system.detection_logger:
        output_file = "output/webcam_monitoring_logs.xlsx"
        if system.export_logs(output_file):
            print(f"Logs exported to: {output_file}")

if __name__ == "__main__":
    main()

