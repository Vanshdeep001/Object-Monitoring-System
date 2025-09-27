import React from 'react';
import { MonitoringType } from '../types';
import StarBorder from './StarBorder';

interface ControlPanelProps {
  activeMonitoring: MonitoringType | null;
  onStart: (type: MonitoringType) => void;
  onStop: () => void;
  isConnected: boolean;
}

const ControlPanel: React.FC<ControlPanelProps> = ({
  activeMonitoring,
  onStart,
  onStop,
  isConnected
}) => {
  const handleStart = async (type: MonitoringType) => {
    if (!isConnected) return;

    try {
      const endpoint = type === 'object_detection' ? 'object-detection' :
                      type === 'zone_monitoring' ? 'zone-monitoring' : 'clean-detection';
      
      const response = await fetch(`http://localhost:8000/api/start/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log(`${type} started:`, data);
        onStart(type);
      } else {
        console.error('Failed to start monitoring');
        const errorData = await response.json();
        console.error('Error details:', errorData);
      }
    } catch (error) {
      console.error('Error starting monitoring:', error);
    }
  };

  const handleStop = async () => {
    if (!isConnected) return;

    try {
      const response = await fetch('http://localhost:8000/api/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Monitoring stopped:', data);
        onStop();
      } else {
        console.error('Failed to stop monitoring');
        const errorData = await response.json();
        console.error('Error details:', errorData);
      }
    } catch (error) {
      console.error('Error stopping monitoring:', error);
    }
  };

  const monitoringOptions = [
    {
      type: 'object_detection' as MonitoringType,
      title: 'Object Detection',
      description: 'Detect and track objects with bounding boxes',
      icon: '🎯',
      color: '#3b82f6'
    },
    {
      type: 'zone_monitoring' as MonitoringType,
      title: 'Zone Monitoring',
      description: 'Monitor restricted zones for violations',
      icon: '🚫',
      color: '#ef4444'
    },
    {
      type: 'clean_detection' as MonitoringType,
      title: 'Clean Detection',
      description: 'High-quality object detection without clutter',
      icon: '✨',
      color: '#10b981'
    }
  ];

  return (
    <div className="control-panel">
      <h2>🎮 Control Panel</h2>
      
      <div className="control-section">
        <h3>Start Monitoring</h3>
        <div className="monitoring-options">
          {monitoringOptions.map((option) => (
            <div
              key={option.type}
              className={`monitoring-option ${
                activeMonitoring === option.type ? 'active' : ''
              } ${!isConnected ? 'disabled' : ''}`}
              style={{ borderColor: option.color }}
            >
              <div className="option-header">
                <span className="option-icon">{option.icon}</span>
                <h4>{option.title}</h4>
              </div>
              <p className="option-description">{option.description}</p>
              <StarBorder
                className="start-button"
                color={option.color}
                speed="5s"
                onClick={() => handleStart(option.type)}
                disabled={!isConnected || activeMonitoring === option.type}
              >
                {activeMonitoring === option.type ? 'Running' : 'Start'}
              </StarBorder>
            </div>
          ))}
        </div>
      </div>

      <div className="control-section">
        <h3>System Control</h3>
        <div className="system-controls">
          <StarBorder
            className="stop-button"
            color="#ef4444"
            speed="5s"
            onClick={handleStop}
            disabled={!isConnected || !activeMonitoring}
          >
            🛑 Stop All Monitoring
          </StarBorder>
        </div>
      </div>

      {!isConnected && (
        <div className="connection-warning">
          <p>⚠️ Backend not connected. Please start the FastAPI server.</p>
        </div>
      )}
    </div>
  );
};

export default ControlPanel;



