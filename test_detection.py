"""
Simple test script to verify object detection is working
"""

import cv2
import numpy as np
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_yolo_loading():
    """Test if YOLO model can be loaded"""
    try:
        # Fix PyTorch weights_only issue by setting weights_only=False
        import torch
        original_load = torch.load
        
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        
        torch.load = patched_load
        
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        logger.info("✅ YOLO model loaded successfully!")
        return model
    except Exception as e:
        logger.error(f"❌ Could not load YOLO model: {e}")
        return None

def test_camera():
    """Test if camera can be opened"""
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                logger.info("✅ Camera working successfully!")
                cap.release()
                return True
            else:
                logger.error("❌ Could not read from camera")
                cap.release()
                return False
        else:
            logger.error("❌ Could not open camera")
            return False
    except Exception as e:
        logger.error(f"❌ Camera test failed: {e}")
        return False

def test_detection():
    """Test object detection on a simple image"""
    try:
        # Create a simple test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_image, "Test Image", (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        # Load YOLO model
        model = test_yolo_loading()
        if model is None:
            return False
        
        # Run detection
        results = model(test_image, verbose=False)
        logger.info("✅ Detection test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Detection test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🧪 Running detection system tests...")
    
    # Test 1: YOLO model loading
    logger.info("\n1. Testing YOLO model loading...")
    yolo_ok = test_yolo_loading() is not None
    
    # Test 2: Camera access
    logger.info("\n2. Testing camera access...")
    camera_ok = test_camera()
    
    # Test 3: Detection functionality
    logger.info("\n3. Testing detection functionality...")
    detection_ok = test_detection()
    
    # Summary
    logger.info("\n📊 Test Results:")
    logger.info(f"   YOLO Model: {'✅ PASS' if yolo_ok else '❌ FAIL'}")
    logger.info(f"   Camera: {'✅ PASS' if camera_ok else '❌ FAIL'}")
    logger.info(f"   Detection: {'✅ PASS' if detection_ok else '❌ FAIL'}")
    
    if yolo_ok and camera_ok and detection_ok:
        logger.info("\n🎉 All tests passed! Detection system is ready.")
        return True
    else:
        logger.info("\n⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    main()
