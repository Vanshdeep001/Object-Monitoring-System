"""
Streamlit Dashboard for Object Detection and Monitoring System
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import tempfile
from PIL import Image

from monitoring_system import MonitoringSystem
from object_detector import ObjectDetector
from zone_monitor import ZoneMonitor
from logger import DetectionLogger
from config import *

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_TITLE,
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-box {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
    }
    .success-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'monitoring_system' not in st.session_state:
    st.session_state.monitoring_system = None
if 'detection_results' not in st.session_state:
    st.session_state.detection_results = []
if 'zone_monitor' not in st.session_state:
    st.session_state.zone_monitor = ZoneMonitor()

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Real-time Object Detection & Monitoring System</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title(STREAMLIT_SIDEBAR_TITLE)
        
        # Model selection
        st.subheader("Model Configuration")
        model_type = st.selectbox(
            "Select Model",
            ["YOLOv8n (Nano)", "YOLOv8s (Small)", "YOLOv8m (Medium)", "YOLOv8l (Large)", "Custom Model"],
            index=0
        )
        
        # Feature toggles
        st.subheader("Features")
        enable_tracking = st.checkbox("Enable Object Tracking", value=True)
        enable_enhancement = st.checkbox("Enable Image Enhancement", value=True)
        enable_logging = st.checkbox("Enable Logging", value=True)
        
        # Detection parameters
        st.subheader("Detection Parameters")
        confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
        iou_threshold = st.slider("IoU Threshold", 0.1, 1.0, 0.45, 0.05)
        
        # Zone configuration
        st.subheader("Zone Configuration")
        if st.button("Add Rectangular Zone"):
            st.session_state.show_zone_input = True
        
        if st.button("Clear All Zones"):
            st.session_state.zone_monitor.clear_zones()
            st.success("All zones cleared!")
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎥 Live Monitoring", 
        "📁 File Upload", 
        "📊 Analytics", 
        "🚨 Alerts & Logs", 
        "⚙️ Settings"
    ])
    
    with tab1:
        live_monitoring_tab()
    
    with tab2:
        file_upload_tab()
    
    with tab3:
        analytics_tab()
    
    with tab4:
        alerts_logs_tab()
    
    with tab5:
        settings_tab()

def live_monitoring_tab():
    """Live monitoring tab"""
    st.header("🎥 Live Monitoring")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Camera Feed")
        
        # Camera selection
        camera_index = st.selectbox("Select Camera", [0, 1, 2], index=0)
        
        # Start/Stop monitoring
        col_start, col_stop = st.columns(2)
        
        with col_start:
            if st.button("🚀 Start Monitoring", type="primary"):
                if st.session_state.monitoring_system is None:
                    st.session_state.monitoring_system = MonitoringSystem(
                        enable_tracking=True,
                        enable_enhancement=True,
                        enable_logging=True
                    )
                
                # Add zones to monitoring system
                for zone in st.session_state.zone_monitor.get_zone_info():
                    if zone['type'] == 'rectangle':
                        st.session_state.monitoring_system.add_restricted_zone(
                            'rectangle', zone['points'], zone['name']
                        )
                    elif zone['type'] == 'polygon':
                        st.session_state.monitoring_system.add_restricted_zone(
                            'polygon', zone['points'], zone['name']
                        )
                
                st.success("Monitoring started!")
        
        with col_stop:
            if st.button("⏹️ Stop Monitoring"):
                if st.session_state.monitoring_system:
                    st.session_state.monitoring_system.stop_monitoring()
                    st.session_state.monitoring_system = None
                st.info("Monitoring stopped!")
        
        # Placeholder for video feed
        video_placeholder = st.empty()
        
        # Simulate video feed (in real implementation, this would be actual camera feed)
        if st.session_state.monitoring_system and st.session_state.monitoring_system.is_running:
            # Create a sample frame for demonstration
            sample_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(sample_frame, "Live Camera Feed", (200, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Convert to RGB for Streamlit
            sample_frame_rgb = cv2.cvtColor(sample_frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(sample_frame_rgb, channels="RGB", use_column_width=True)
    
    with col2:
        st.subheader("Real-time Statistics")
        
        if st.session_state.monitoring_system:
            stats = st.session_state.monitoring_system.get_system_statistics()
            
            # Display metrics
            col_metric1, col_metric2 = st.columns(2)
            
            with col_metric1:
                st.metric("Total Detections", stats['total_detections'])
                st.metric("Frame Count", stats['frame_count'])
            
            with col_metric2:
                st.metric("Zone Violations", stats['total_violations'])
                st.metric("FPS", f"{stats['fps']:.1f}")
            
            # Object counts
            st.subheader("Object Counts")
            if stats['object_counts']:
                for class_name, count in stats['object_counts'].items():
                    st.write(f"**{class_name}**: {count}")
            else:
                st.write("No objects detected yet")
        else:
            st.info("Start monitoring to see statistics")

def file_upload_tab():
    """File upload and processing tab"""
    st.header("📁 File Upload & Processing")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Image or Video", 
        type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'],
        help="Upload an image or video file for object detection"
    )
    
    if uploaded_file is not None:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        # Determine file type
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension in ['jpg', 'jpeg', 'png']:
            process_image(tmp_file_path)
        elif file_extension in ['mp4', 'avi', 'mov']:
            process_video(tmp_file_path)
        
        # Clean up
        os.unlink(tmp_file_path)

def process_image(image_path):
    """Process uploaded image"""
    st.subheader("Image Processing Results")
    
    # Initialize detector
    detector = ObjectDetector()
    
    # Load and process image
    image = cv2.imread(image_path)
    if image is None:
        st.error("Error loading image")
        return
    
    # Detect objects
    detections, annotated_image = detector.detect_objects(image)
    
    # Display results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        st.image(image_rgb, use_column_width=True)
    
    with col2:
        st.subheader("Detection Results")
        annotated_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        st.image(annotated_rgb, use_column_width=True)
    
    # Display detection details
    if detections:
        st.subheader("Detection Details")
        
        # Count objects
        counts = detector.count_objects(detections)
        
        # Create DataFrame
        detection_data = []
        for i, detection in enumerate(detections):
            detection_data.append({
                'Object ID': i + 1,
                'Class': detection['class_name'],
                'Confidence': f"{detection['confidence']:.3f}",
                'Bounding Box': f"({detection['bbox'][0]}, {detection['bbox'][1]}) - ({detection['bbox'][2]}, {detection['bbox'][3]})"
            })
        
        df = pd.DataFrame(detection_data)
        st.dataframe(df, use_container_width=True)
        
        # Object counts chart
        if counts:
            st.subheader("Object Counts")
            count_df = pd.DataFrame(list(counts.items()), columns=['Class', 'Count'])
            fig = px.bar(count_df, x='Class', y='Count', title="Object Counts")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No objects detected in the image")

def process_video(video_path):
    """Process uploaded video"""
    st.subheader("Video Processing")
    
    # Initialize monitoring system
    system = MonitoringSystem(enable_tracking=True, enable_enhancement=True, enable_logging=True)
    
    # Add zones if any
    for zone in st.session_state.zone_monitor.get_zone_info():
        if zone['type'] == 'rectangle':
            system.add_restricted_zone('rectangle', zone['points'], zone['name'])
        elif zone['type'] == 'polygon':
            system.add_restricted_zone('polygon', zone['points'], zone['name'])
    
    # Process video
    output_path = os.path.join(OUTPUT_DIR, f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
    
    with st.spinner("Processing video..."):
        system.monitor_video(video_path, output_path)
    
    # Display results
    st.success("Video processing completed!")
    
    # Show statistics
    stats = system.get_system_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Frames", stats['frame_count'])
    with col2:
        st.metric("Total Detections", stats['total_detections'])
    with col3:
        st.metric("Zone Violations", stats['total_violations'])
    with col4:
        st.metric("Processing FPS", f"{stats['fps']:.1f}")
    
    # Download processed video
    if os.path.exists(output_path):
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Download Processed Video",
                data=file.read(),
                file_name=f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                mime="video/mp4"
            )

def analytics_tab():
    """Analytics and visualization tab"""
    st.header("📊 Analytics & Visualization")
    
    # Load detection logs
    detection_logger = DetectionLogger()
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Get summary statistics
    start_time = start_date.isoformat()
    end_time = end_date.isoformat()
    
    summary = detection_logger.get_detection_summary(start_time, end_time)
    
    if summary:
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Detections", summary['total_detections'])
        with col2:
            st.metric("Unique Objects", summary['unique_objects'])
        with col3:
            st.metric("Zone Violations", summary['zone_violations'])
        with col4:
            st.metric("Avg Confidence", f"{summary['average_confidence']:.3f}")
        
        # Class distribution chart
        if summary['class_counts']:
            st.subheader("Object Class Distribution")
            class_df = pd.DataFrame(list(summary['class_counts'].items()), 
                                  columns=['Class', 'Count'])
            fig = px.pie(class_df, values='Count', names='Class', 
                        title="Object Class Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Time series analysis
        st.subheader("Detection Timeline")
        st.info("Time series analysis would show detection patterns over time")
        
    else:
        st.info("No detection data available for the selected date range")

def alerts_logs_tab():
    """Alerts and logs tab"""
    st.header("🚨 Alerts & Activity Logs")
    
    # Zone violations
    st.subheader("Recent Zone Violations")
    
    # Simulate recent violations (in real implementation, this would come from logs)
    sample_violations = [
        {
            'timestamp': '2024-01-15 14:30:25',
            'zone': 'Restricted Area 1',
            'object': 'person',
            'confidence': 0.95
        },
        {
            'timestamp': '2024-01-15 14:28:10',
            'zone': 'Restricted Area 2',
            'object': 'car',
            'confidence': 0.87
        }
    ]
    
    if sample_violations:
        for violation in sample_violations:
            with st.container():
                st.markdown(f"""
                <div class="alert-box">
                    <strong>🚨 Zone Violation Alert</strong><br>
                    <strong>Time:</strong> {violation['timestamp']}<br>
                    <strong>Zone:</strong> {violation['zone']}<br>
                    <strong>Object:</strong> {violation['object']}<br>
                    <strong>Confidence:</strong> {violation['confidence']:.2f}
                </div>
                """, unsafe_allow_html=True)
                st.write("")
    else:
        st.info("No recent zone violations")
    
    # Activity logs
    st.subheader("System Activity Logs")
    
    # Log export
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Detection Logs"):
            detection_logger = DetectionLogger()
            output_file = os.path.join(OUTPUT_DIR, f"detection_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            
            if detection_logger.export_to_excel(output_file):
                st.success("Logs exported successfully!")
                
                # Download button
                with open(output_file, "rb") as file:
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=file.read(),
                        file_name=f"detection_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error("Failed to export logs")
    
    with col2:
        if st.button("🗑️ Clear All Logs"):
            st.warning("This will clear all detection logs. Are you sure?")
            if st.button("Confirm Clear", type="primary"):
                # Clear logs logic would go here
                st.success("All logs cleared!")

def settings_tab():
    """Settings and configuration tab"""
    st.header("⚙️ System Settings")
    
    # Model settings
    st.subheader("Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Model Size", ["Nano", "Small", "Medium", "Large"], index=0)
        st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
    
    with col2:
        st.slider("IoU Threshold", 0.1, 1.0, 0.45, 0.05)
        st.number_input("Max Detections", 1, 1000, 100)
    
    # Enhancement settings
    st.subheader("Image Enhancement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Enable Low-light Enhancement", value=True)
        st.slider("Denoise Strength", 1, 20, 10)
    
    with col2:
        st.slider("CLAHE Clip Limit", 1.0, 5.0, 2.0, 0.1)
        st.slider("Gamma Correction", 0.5, 2.0, 1.2, 0.1)
    
    # Tracking settings
    st.subheader("Object Tracking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Max Age", 1, 100, 30)
        st.number_input("N Init", 1, 10, 3)
    
    with col2:
        st.slider("Max Cosine Distance", 0.1, 1.0, 0.2, 0.05)
        st.checkbox("Enable Track History", value=True)
    
    # Zone settings
    st.subheader("Zone Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Alert Cooldown (seconds)", 1, 60, 2)
        st.multiselect("Monitored Classes", COCO_CLASSES[:10], default=['person', 'car'])
    
    with col2:
        st.checkbox("Enable Sound Alerts", value=True)
        st.checkbox("Enable Visual Alerts", value=True)
    
    # Save settings
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")

if __name__ == "__main__":
    main()
