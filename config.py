"""
Configuration file for the Object Detection and Monitoring System
"""

import os

# Model Configuration
MODEL_PATH = "yolov8n.pt"  # Default YOLOv8 nano model
CUSTOM_MODEL_PATH = None  # Path to custom trained model

# Detection Configuration
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45
MAX_DETECTIONS = 1000

# COCO Class Names (80 classes)
COCO_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
    'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
    'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
    'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
    'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
    'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

# Colors for bounding boxes (BGR format)
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255),
    (0, 255, 255), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0),
    (128, 0, 128), (0, 128, 128), (192, 192, 192), (128, 128, 128), (255, 165, 0)
]

# Zone Monitoring Configuration
RESTRICTED_ZONE_COLOR = (0, 0, 255)  # Red color for restricted zone
ALERT_COLOR = (0, 255, 255)  # Yellow color for alerts

# File Paths
OUTPUT_DIR = "output"
LOG_DIR = "logs"
MODELS_DIR = "models"

# Create directories if they don't exist
for directory in [OUTPUT_DIR, LOG_DIR, MODELS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(LOG_DIR, "detection_log.csv")

# Streamlit Configuration
STREAMLIT_TITLE = "Real-time Object Detection & Monitoring System"
STREAMLIT_SIDEBAR_TITLE = "Configuration"
