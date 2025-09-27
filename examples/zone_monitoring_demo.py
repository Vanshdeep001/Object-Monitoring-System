"""
Simple Zone Monitoring Demo
Quick demo of zone monitoring capabilities
"""

import cv2
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zone_monitoring import CompleteZoneMonitor


def main():
    """Simple zone monitoring demo"""
    print("🚨 Zone Monitoring Demo")
    print("=" * 30)
    
    # Initialize complete zone monitor
    monitor = CompleteZoneMonitor(enable_logging=False)
    
    # Setup default zones
    monitor.setup_default_zones()
    
    print("\n🎥 Starting demo...")
    print("Controls:")
    print("  'q' - Quit")
    print("  'z' - Add zones")
    print("  'c' - Clear zones")
    print("  'r' - Reset to default zones")
    
    # Start monitoring
    monitor.monitor_webcam(camera_index=0)


if __name__ == "__main__":
    main()