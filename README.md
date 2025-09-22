# 🎯 Real-time Object Detection and Monitoring System

A comprehensive Python-based surveillance and monitoring application that combines YOLOv8 object detection with advanced features like zone monitoring, object tracking, image enhancement, and real-time analytics.

## 🌟 Features

### Core Detection
- **YOLOv8 Integration**: Pre-trained COCO model for general object detection
- **Multi-format Support**: Images, video files, and live webcam feeds
- **Real-time Processing**: Optimized for live video streams
- **Custom Model Support**: Use your own trained YOLO models

### Object Counting & Tracking
- **Real-time Counting**: Count objects by class per frame
- **DeepSORT Tracking**: Assign unique IDs and track objects across frames
- **Movement Analysis**: Detect stationary, slow-moving, and fast-moving objects
- **Loitering Detection**: Identify objects staying in one area

### Zone Monitoring
- **Restricted Areas**: Define rectangular or polygonal restricted zones
- **Real-time Alerts**: Instant notifications when objects enter restricted areas
- **Interactive Zone Selection**: Draw zones directly on video feed
- **Sound & Visual Alerts**: Audio and visual notification system

### Image Enhancement
- **Low-light Enhancement**: CLAHE and gamma correction for dark conditions
- **Noise Reduction**: Advanced denoising algorithms
- **Adaptive Enhancement**: Automatically adjust parameters based on image content
- **Real-time Processing**: Enhance video frames on-the-fly

### Dashboard & Analytics
- **Streamlit Dashboard**: Modern web interface for monitoring
- **Real-time Statistics**: Live object counts and detection metrics
- **Historical Analytics**: Time-series analysis and trend visualization
- **Export Capabilities**: CSV, JSON, and Excel report generation

### Logging & Monitoring
- **Comprehensive Logging**: Detailed detection logs with timestamps
- **Activity Tracking**: System events and zone violations
- **Data Export**: Multiple format support for analysis
- **Performance Metrics**: FPS, processing time, and accuracy statistics

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd object-monitoring-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit dashboard**
   ```bash
   python run_streamlit.py
   ```

4. **Or run basic detection**
   ```bash
   python examples/basic_detection.py
   ```

### System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **GPU**: Optional but recommended for real-time processing
- **Camera**: USB webcam or built-in camera for live monitoring

## 📁 Project Structure

```
object-monitoring-system/
├── config.py                 # Configuration settings
├── object_detector.py        # Core YOLOv8 detection
├── zone_monitor.py          # Zone monitoring and alerts
├── object_tracker.py        # DeepSORT tracking
├── image_enhancer.py        # Image enhancement algorithms
├── monitoring_system.py     # Main system integration
├── logger.py               # Logging and data export
├── streamlit_app.py        # Web dashboard
├── run_streamlit.py        # Dashboard launcher
├── requirements.txt         # Dependencies
├── README.md              # This file
├── examples/              # Example scripts
│   ├── basic_detection.py
│   ├── webcam_monitoring.py
│   ├── video_processing.py
│   ├── image_enhancement_demo.py
│   └── zone_monitoring_demo.py
├── output/                # Generated outputs
├── logs/                  # Log files
└── models/                # Model files
```

## 🎮 Usage Examples

### 1. Basic Object Detection

```python
from object_detector import ObjectDetector
import cv2

# Initialize detector
detector = ObjectDetector()

# Load image
image = cv2.imread("sample.jpg")

# Detect objects
detections, annotated_image = detector.detect_objects(image)

# Count objects
counts = detector.count_objects(detections)
print(f"Detected objects: {counts}")

# Save result
cv2.imwrite("result.jpg", annotated_image)
```

### 2. Webcam Monitoring with Zones

```python
from monitoring_system import MonitoringSystem

# Initialize system
system = MonitoringSystem(
    enable_tracking=True,
    enable_enhancement=True,
    enable_logging=True
)

# Add restricted zones
system.add_restricted_zone('rectangle', [(100, 100), (300, 200)], "Restricted Area")
system.add_restricted_zone('polygon', [(400, 100), (500, 150), (450, 250)], "Parking Zone")

# Start monitoring
system.monitor_webcam(camera_index=0)
```

### 3. Video Processing

```python
from monitoring_system import MonitoringSystem

# Initialize system
system = MonitoringSystem()

# Process video file
system.monitor_video("input_video.mp4", "output_video.mp4")

# Get statistics
stats = system.get_system_statistics()
print(f"Processed {stats['frame_count']} frames")
print(f"Found {stats['total_detections']} objects")
```

### 4. Image Enhancement

```python
from image_enhancer import ImageEnhancer
import cv2

# Initialize enhancer
enhancer = ImageEnhancer()

# Load low-light image
image = cv2.imread("dark_image.jpg")

# Enhance image
enhanced = enhancer.enhance_image(image, 'low_light')

# Save enhanced image
cv2.imwrite("enhanced_image.jpg", enhanced)
```

## 🎛️ Configuration

### Model Settings
```python
# In config.py
MODEL_PATH = "yolov8n.pt"           # Model file
CONFIDENCE_THRESHOLD = 0.5          # Detection confidence
IOU_THRESHOLD = 0.45                # Intersection over Union
MAX_DETECTIONS = 1000               # Maximum detections per frame
```

### Zone Monitoring
```python
# Zone settings
RESTRICTED_ZONE_COLOR = (0, 0, 255)  # Red color for zones
ALERT_COOLDOWN = 2.0                 # Seconds between alerts
MONITORED_CLASSES = ['person', 'car', 'truck']  # Classes to monitor
```

### Enhancement Parameters
```python
# Image enhancement
DENOISE_STRENGTH = 10               # Noise reduction strength
CLAHE_CLIP_LIMIT = 2.0             # Contrast enhancement
GAMMA_CORRECTION = 1.2             # Brightness adjustment
```

## 📊 Dashboard Features

### Live Monitoring Tab
- Real-time camera feed
- Object detection visualization
- Zone violation alerts
- Live statistics display

### File Upload Tab
- Image and video processing
- Batch processing capabilities
- Download processed results
- Detection analysis

### Analytics Tab
- Historical data visualization
- Object class distribution
- Time-series analysis
- Performance metrics

### Alerts & Logs Tab
- Zone violation history
- System activity logs
- Data export options
- Log management

### Settings Tab
- Model configuration
- Enhancement parameters
- Tracking settings
- Zone monitoring options

## 🔧 Advanced Usage

### Custom Model Training

1. **Prepare dataset in YOLO format**
2. **Train model using Ultralytics**
3. **Update config.py with model path**
4. **Set custom_model=True in ObjectDetector**

### Custom Zone Shapes

```python
# Define custom polygon zones
custom_points = [(x1, y1), (x2, y2), (x3, y3), ...]
system.add_restricted_zone('polygon', custom_points, "Custom Zone")
```

### Integration with External Systems

```python
# Custom alert handler
def custom_alert_handler(violation):
    # Send email, SMS, or API call
    send_notification(violation)

# Override default alert method
system.zone_monitor._trigger_alert = custom_alert_handler
```

## 📈 Performance Optimization

### GPU Acceleration
- Install CUDA-compatible PyTorch
- Set device to 'cuda' in config
- Use larger YOLO models for better accuracy

### Memory Management
- Adjust batch sizes for video processing
- Use smaller models for real-time applications
- Enable frame skipping for long videos

### Real-time Optimization
- Reduce input resolution for faster processing
- Use YOLOv8n for maximum speed
- Disable unnecessary features for speed

## 🐛 Troubleshooting

### Common Issues

1. **Camera not detected**
   - Check camera permissions
   - Try different camera indices (0, 1, 2)
   - Verify camera is not used by other applications

2. **Low detection accuracy**
   - Increase confidence threshold
   - Use larger YOLO model
   - Enable image enhancement

3. **Performance issues**
   - Reduce input resolution
   - Use GPU acceleration
   - Disable tracking for faster processing

4. **Zone alerts not working**
   - Check zone coordinates
   - Verify monitored classes
   - Check alert cooldown settings

### Error Messages

- **"Error loading model"**: Check model file path and format
- **"Camera not accessible"**: Verify camera permissions and availability
- **"Out of memory"**: Reduce batch size or input resolution

## 📝 API Reference

### ObjectDetector Class
```python
detector = ObjectDetector(model_path, custom_model=False)
detections, annotated_image = detector.detect_objects(image)
counts = detector.count_objects(detections)
```

### ZoneMonitor Class
```python
monitor = ZoneMonitor()
monitor.add_rectangular_zone(x1, y1, x2, y2, name)
violations = monitor.check_zone_violations(detections)
```

### ObjectTracker Class
```python
tracker = ObjectTracker()
tracked_objects = tracker.update_tracks(detections, frame)
```

### ImageEnhancer Class
```python
enhancer = ImageEnhancer()
enhanced_image = enhancer.enhance_image(image, 'auto')
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLOv8
- [DeepSORT](https://github.com/nwojke/deep_sort) for object tracking
- [OpenCV](https://opencv.org/) for computer vision
- [Streamlit](https://streamlit.io/) for the web dashboard

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the documentation
- Review example scripts

---

**Made with ❤️ for the computer vision community**

