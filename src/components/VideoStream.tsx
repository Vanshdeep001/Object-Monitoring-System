import React, { useEffect, useRef, useState } from 'react';
import { MonitoringType, WebSocketMessage } from '../types';

interface VideoStreamProps {
  activeMonitoring: MonitoringType | null;
  onMonitoringChange: (type: MonitoringType | null) => void;
}

const VideoStream: React.FC<VideoStreamProps> = ({ activeMonitoring, onMonitoringChange }) => {
  const videoRef = useRef<HTMLImageElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [currentFrame, setCurrentFrame] = useState<string>('');
  const [stats, setStats] = useState({
    detections: 0,
    violations: 0,
    frameCount: 0,
    timestamp: ''
  });

  useEffect(() => {
    if (activeMonitoring) {
      connectWebSocket();
    } else {
      disconnectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [activeMonitoring]);

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        if (message.frame) {
          setCurrentFrame(message.frame);
        }

        setStats({
          detections: message.detections || 0,
          violations: message.violations || 0,
          frameCount: message.frame_count || 0,
          timestamp: message.timestamp
        });
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setCurrentFrame('');
  };

  const getMonitoringTitle = () => {
    switch (activeMonitoring) {
      case 'object_detection':
        return 'Object Detection';
      case 'zone_monitoring':
        return 'Zone Monitoring';
      case 'clean_detection':
        return 'Clean Detection';
      default:
        return 'No Active Monitoring';
    }
  };

  return (
    <div className="video-stream">
      <div className="video-header">
        <h2>📹 {getMonitoringTitle()}</h2>
        <div className="video-status">
          <span className={`status ${isConnected ? 'active' : 'inactive'}`}>
            {isConnected ? '🟢 Live' : '🔴 Offline'}
          </span>
        </div>
      </div>

      <div className="video-container">
        {currentFrame ? (
          <img
            ref={videoRef}
            src={currentFrame}
            alt="Live Video Stream"
            className="video-frame"
          />
        ) : (
          <div className="video-placeholder">
            <div className="placeholder-content">
              <div className="placeholder-icon">📹</div>
              <p>No video stream</p>
              <p className="placeholder-subtitle">Start monitoring to see live feed</p>
            </div>
          </div>
        )}
      </div>

      {activeMonitoring && (
        <div className="video-stats">
          <div className="stat-item">
            <span className="stat-label">Detections:</span>
            <span className="stat-value">{stats.detections}</span>
          </div>
          {activeMonitoring === 'zone_monitoring' && (
            <div className="stat-item">
              <span className="stat-label">Violations:</span>
              <span className="stat-value">{stats.violations}</span>
            </div>
          )}
          {activeMonitoring === 'clean_detection' && (
            <div className="stat-item">
              <span className="stat-label">Frames:</span>
              <span className="stat-value">{stats.frameCount}</span>
            </div>
          )}
          <div className="stat-item">
            <span className="stat-label">Last Update:</span>
            <span className="stat-value">
              {stats.timestamp ? new Date(stats.timestamp).toLocaleTimeString() : 'N/A'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoStream;



