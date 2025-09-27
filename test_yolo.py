"""
YOLO Test Script
This script tests if YOLO is working properly.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_yolo():
    """Test YOLO model loading"""
    try:
        # Fix PyTorch weights_only issue
        import torch
        logger.info("✅ PyTorch imported successfully")
        
        torch.serialization.add_safe_globals([
            'ultralytics.nn.tasks.DetectionModel',
            'ultralytics.nn.modules.conv.Conv',
            'ultralytics.nn.modules.block.C2f',
            'ultralytics.nn.modules.block.SPPF',
            'ultralytics.nn.modules.head.Detect',
            'ultralytics.utils.torch_utils.ModelEMA'
        ])
        logger.info("✅ PyTorch safe globals added")
        
        from ultralytics import YOLO
        logger.info("✅ Ultralytics imported successfully")
        
        # Load model
        model = YOLO('yolov8n.pt')
        logger.info("✅ YOLO model loaded successfully!")
        
        # Test detection on a dummy image
        import numpy as np
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = model(dummy_image, verbose=False)
        logger.info("✅ YOLO detection test passed!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ YOLO test failed: {e}")
        logger.error("Please install ultralytics: pip install ultralytics")
        return False

if __name__ == "__main__":
    logger.info("🧪 Testing YOLO installation...")
    success = test_yolo()
    if success:
        logger.info("🎉 YOLO is working correctly!")
    else:
        logger.info("💥 YOLO test failed. Please check installation.")



