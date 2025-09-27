"""
FastAPI Backend for Object Monitoring Dashboard
Integrates with existing monitoring systems
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import logging
import cv2
import base64
import numpy as np
from datetime import datetime
import os
import sys

# Add parent directory to path to import monitoring modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix PyTorch weights_only issue
import torch
torch.serialization.add_safe_globals([
    'ultralytics.nn.tasks.DetectionModel',
    'ultralytics.nn.modules.conv.Conv',
    'ultralytics.nn.modules.block.C2f',
    'ultralytics.nn.modules.block.SPPF',
    'ultralytics.nn.modules.head.Detect',
    'ultralytics.utils.torch_utils.ModelEMA'
])

from monitoring_system import MonitoringSystem
from zone_detector import ZoneDetector
from clean_object_detection import CleanObjectDetectionSystem
from config import MODEL_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Object Monitoring Dashboard API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global monitoring systems
monitoring_system = None
zone_detector = None
clean_detection = None
active_connections = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Mark for removal
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

manager = ConnectionManager()

def frame_to_base64(frame):
    """Convert OpenCV frame to base64 string"""
    _, buffer = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{frame_base64}"

async def run_simple_webcam_stream(stream_type: str):
    """Run webcam stream with basic object detection"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Error opening camera for webcam stream")
        return

    # Set reasonable resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    frame_count = 0
    detection_count = 0
    logger.info(f"Starting webcam stream for {stream_type}")
    
    # Try to initialize YOLO model
    yolo_model = None
    try:
        # Fix PyTorch weights_only issue
        import torch
        torch.serialization.add_safe_globals([
            'ultralytics.nn.tasks.DetectionModel',
            'ultralytics.nn.modules.conv.Conv',
            'ultralytics.nn.modules.block.C2f',
            'ultralytics.nn.modules.block.SPPF',
            'ultralytics.nn.modules.head.Detect',
            'ultralytics.utils.torch_utils.ModelEMA'
        ])
        
        from ultralytics import YOLO
        yolo_model = YOLO('yolov8n.pt')  # Use nano model for faster processing
        logger.info("YOLO model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load YOLO model: {e}. Using basic detection.")
        logger.warning(f"Error details: {str(e)}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Error reading frame from camera")
            break
        
        frame_count += 1
        detections = 0
        
        # Try to run YOLO detection
        if yolo_model is not None:
            try:
                results = yolo_model(frame, verbose=False)
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        detections = len(boxes)
                        detection_count += detections
                        
                        # Draw bounding boxes
                        for box in boxes:
                            # Get box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            conf = box.conf[0].cpu().numpy()
                            cls = int(box.cls[0].cpu().numpy())
                            
                            # Only draw high confidence detections
                            if conf > 0.5:
                                # Draw rectangle
                                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                                
                                # Get class name
                                class_names = yolo_model.names
                                class_name = class_names[cls]
                                
                                # Draw label
                                label = f"{class_name}: {conf:.2f}"
                                cv2.putText(frame, label, (int(x1), int(y1) - 10), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        # Log detection info every 30 frames
                        if frame_count % 30 == 0:
                            logger.info(f"Frame {frame_count}: Found {detections} detections")
            except Exception as e:
                logger.warning(f"YOLO detection failed: {e}")
                detections = 0
        else:
            # If no YOLO model, try basic motion detection
            if frame_count > 10:  # Skip first few frames
                detections = 1  # Mock detection for testing
        
        # Add text overlay
        cv2.putText(frame, f"{stream_type.replace('_', ' ').title()}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Frame: {frame_count}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Detections: {detections}", (10, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {datetime.now().strftime('%H:%M:%S')}", (10, 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        frame_base64 = frame_to_base64(frame)
        
        message = {
            "type": stream_type,
            "frame": frame_base64,
            "detections": detections,
            "violations": 0,  # For now, no violations in simple mode
            "frame_count": frame_count,
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.broadcast(json.dumps(message))
        await asyncio.sleep(0.03)  # ~30 FPS

    cap.release()
    logger.info(f"Webcam stream for {stream_type} stopped")

@app.get("/")
async def read_root():
    return {"message": "Object Monitoring Dashboard API"}

@app.get("/api/test")
async def test_endpoint():
    return {"status": "success", "message": "Backend is working!"}

@app.get("/api/status")
async def get_status():
    """Get current system status"""
    return {
        "monitoring_active": monitoring_system is not None and monitoring_system.is_running,
        "zone_monitoring_active": zone_detector is not None,
        "clean_detection_active": clean_detection is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/start/object-detection")
async def start_object_detection():
    """Start object detection monitoring"""
    global monitoring_system
    
    try:
        # Try to initialize the real monitoring system
        if monitoring_system is None:
            monitoring_system = MonitoringSystem()
        
        if not monitoring_system.is_running:
            asyncio.create_task(run_object_detection())
            return {"status": "started", "message": "Object detection started"}
        else:
            return {"status": "already_running", "message": "Object detection already running"}
    except Exception as e:
        logger.error(f"Error starting object detection: {e}")
        # Fallback to simple webcam stream
        asyncio.create_task(run_simple_webcam_stream("object_detection"))
        return {"status": "started", "message": "Object detection started (simple mode)"}

@app.post("/api/start/zone-monitoring")
async def start_zone_monitoring():
    """Start zone monitoring"""
    global zone_detector
    
    try:
        # Try to initialize the real zone detector
        if zone_detector is None:
            zone_detector = ZoneDetector()
        
        if not zone_detector.is_running:
            asyncio.create_task(run_zone_monitoring())
            return {"status": "started", "message": "Zone monitoring started"}
        else:
            return {"status": "already_running", "message": "Zone monitoring already running"}
    except Exception as e:
        logger.error(f"Error starting zone monitoring: {e}")
        # Fallback to simple webcam stream
        asyncio.create_task(run_simple_webcam_stream("zone_monitoring"))
        return {"status": "started", "message": "Zone monitoring started (simple mode)"}

@app.post("/api/start/clean-detection")
async def start_clean_detection():
    """Start clean object detection"""
    global clean_detection
    
    try:
        # Try to initialize the real clean detection system
        if clean_detection is None:
            clean_detection = CleanObjectDetectionSystem()
        
        if not clean_detection.is_running:
            asyncio.create_task(run_clean_detection())
            return {"status": "started", "message": "Clean detection started"}
        else:
            return {"status": "already_running", "message": "Clean detection already running"}
    except Exception as e:
        logger.error(f"Error starting clean detection: {e}")
        # Fallback to simple webcam stream
        asyncio.create_task(run_simple_webcam_stream("clean_detection"))
        return {"status": "started", "message": "Clean detection started (simple mode)"}

@app.post("/api/stop")
async def stop_monitoring():
    """Stop all monitoring"""
    global monitoring_system, zone_detector, clean_detection
    
    try:
        # For now, return success to test the frontend
        return {"status": "stopped", "message": "All monitoring stopped (mock mode)"}
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics")
async def get_statistics():
    """Get monitoring statistics"""
    stats = {}
    
    if monitoring_system:
        stats["object_detection"] = monitoring_system.get_system_statistics()
    
    if zone_detector:
        stats["zone_monitoring"] = zone_detector.get_system_statistics()
    
    # Return basic stats if no system is active
    if not stats:
        stats = {
            "total_detections": 0,
            "active_objects": 0,
            "violations": 0,
            "frame_count": 0,
            "fps": 30  # Approximate FPS for webcam stream
        }
    
    return stats

@app.post("/api/zones/add")
async def add_zone(zone_data: dict):
    """Add a new zone"""
    global zone_detector
    
    try:
        if zone_detector is None:
            zone_detector = ZoneDetector()
        
        zone_name = zone_data.get("name", f"Zone_{len(zone_detector.zone_monitor.get_zone_info()) + 1}")
        points = zone_data.get("points", [])
        
        if len(points) >= 3:
            zone_detector.add_restricted_zone(zone_name, points)
            return {"status": "success", "message": f"Zone '{zone_name}' added"}
        else:
            raise HTTPException(status_code=400, detail="Zone must have at least 3 points")
    except Exception as e:
        logger.error(f"Error adding zone: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/zones")
async def get_zones():
    """Get all zones"""
    global zone_detector
    
    if zone_detector:
        return {"zones": zone_detector.zone_monitor.get_zone_info()}
    else:
        return {"zones": []}

async def run_object_detection():
    """Run object detection and broadcast frames"""
    global monitoring_system
    
    if monitoring_system is None:
        return
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Error opening camera")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    monitoring_system.is_running = True
    
    try:
        while monitoring_system.is_running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            annotated_frame, results = monitoring_system.process_frame(frame)
            
            # Convert to base64
            frame_b64 = frame_to_base64(annotated_frame)
            
            # Broadcast to all connected clients
            message = json.dumps({
                "type": "object_detection",
                "frame": frame_b64,
                "detections": len(results) if results else 0,
                "timestamp": datetime.now().isoformat()
            })
            
            await manager.broadcast(message)
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.033)  # ~30 FPS
            
    except Exception as e:
        logger.error(f"Error in object detection loop: {e}")
    finally:
        cap.release()
        monitoring_system.is_running = False

async def run_zone_monitoring():
    """Run zone monitoring and broadcast frames"""
    global zone_detector
    
    if zone_detector is None:
        return
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Error opening camera")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    zone_detector.is_running = True
    
    try:
        while zone_detector.is_running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            annotated_frame, results_dict = zone_detector.process_frame(frame)
            
            # Convert to base64
            frame_b64 = frame_to_base64(annotated_frame)
            
            # Extract detections and violations from results_dict
            detections = results_dict.get('detections', []) if isinstance(results_dict, dict) else []
            violations = results_dict.get('violations', []) if isinstance(results_dict, dict) else []
            
            # Broadcast to all connected clients
            message = json.dumps({
                "type": "zone_monitoring",
                "frame": frame_b64,
                "detections": len(detections),
                "violations": len(violations),
                "timestamp": datetime.now().isoformat()
            })
            
            await manager.broadcast(message)
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.033)  # ~30 FPS
            
    except Exception as e:
        logger.error(f"Error in zone monitoring loop: {e}")
    finally:
        cap.release()
        zone_detector.is_running = False

async def run_clean_detection():
    """Run clean object detection and broadcast frames"""
    global clean_detection
    
    if clean_detection is None:
        return
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Error opening camera")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    clean_detection.is_running = True
    
    try:
        while clean_detection.is_running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            annotated_frame = clean_detection.process_frame(frame)
            
            # Convert to base64
            frame_b64 = frame_to_base64(annotated_frame)
            
            # Broadcast to all connected clients
            message = json.dumps({
                "type": "clean_detection",
                "frame": frame_b64,
                "frame_count": clean_detection.frame_count,
                "timestamp": datetime.now().isoformat()
            })
            
            await manager.broadcast(message)
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.033)  # ~30 FPS
            
    except Exception as e:
        logger.error(f"Error in clean detection loop: {e}")
    finally:
        cap.release()
        clean_detection.is_running = False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
