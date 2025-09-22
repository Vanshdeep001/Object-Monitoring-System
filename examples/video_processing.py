"""
Video Processing Example with Full Monitoring Features
"""

import os
import cv2
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitoring_system import MonitoringSystem

def main():
    """Video processing with full monitoring features"""
    print("Video Processing Example")
    print("=" * 40)
    
    # Check if sample video exists
    sample_video = "sample_video.mp4"
    if not os.path.exists(sample_video):
        print(f"Sample video '{sample_video}' not found.")
        print("Please provide a video file or create a sample video.")
        return
    
    # Initialize monitoring system
    system = MonitoringSystem(
        enable_tracking=True,
        enable_enhancement=True,
        enable_logging=True
    )
    
    # Add restricted zones
    print("Adding restricted zones...")
    system.add_restricted_zone('rectangle', [(50, 50), (200, 150)], "Entry Zone")
    system.add_restricted_zone('polygon', [(300, 100), (400, 150), (350, 250), (250, 200)], "Parking Area")
    
    # Process video
    output_video = "output/processed_video.mp4"
    print(f"Processing video: {sample_video}")
    print(f"Output will be saved to: {output_video}")
    
    system.monitor_video(sample_video, output_video)
    
    # Display statistics
    stats = system.get_system_statistics()
    print("\nProcessing Statistics:")
    print(f"  Total frames: {stats['frame_count']}")
    print(f"  Total detections: {stats['total_detections']}")
    print(f"  Zone violations: {stats['total_violations']}")
    print(f"  Processing FPS: {stats['fps']:.2f}")
    
    # Object counts
    if stats['object_counts']:
        print("\nObject Counts:")
        for class_name, count in stats['object_counts'].items():
            print(f"  {class_name}: {count}")
    
    # Export logs
    if system.detection_logger:
        log_file = "output/video_processing_logs.xlsx"
        if system.export_logs(log_file):
            print(f"\nLogs exported to: {log_file}")

if __name__ == "__main__":
    main()

