import React, { useState, useEffect } from 'react';
import './App.css';
import VideoStream from './components/VideoStream';
import ControlPanel from './components/ControlPanel';
import StatisticsPanel from './components/StatisticsPanel';
import ZoneManagement from './components/ZoneManagement';
import { MonitoringType } from './types';

function App() {
  const [activeMonitoring, setActiveMonitoring] = useState<MonitoringType | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [statistics, setStatistics] = useState<any>({});
  const [zones, setZones] = useState<any[]>([]);

  useEffect(() => {
    // Check connection status
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/status');
        if (response.ok) {
          setIsConnected(true);
          const data = await response.json();
          if (data.monitoring_active) setActiveMonitoring('object_detection');
          if (data.zone_monitoring_active) setActiveMonitoring('zone_monitoring');
          if (data.clean_detection_active) setActiveMonitoring('clean_detection');
        }
      } catch (error) {
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleMonitoringStart = (type: MonitoringType) => {
    setActiveMonitoring(type);
  };

  const handleMonitoringStop = () => {
    setActiveMonitoring(null);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎯 Object Monitoring Dashboard</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
        </div>
      </header>

      <main className="app-main">
        <div className="dashboard-grid">
          {/* Video Stream */}
          <div className="video-section">
            <VideoStream 
              activeMonitoring={activeMonitoring}
              onMonitoringChange={setActiveMonitoring}
            />
          </div>

          {/* Control Panel */}
          <div className="control-section">
            <ControlPanel
              activeMonitoring={activeMonitoring}
              onStart={handleMonitoringStart}
              onStop={handleMonitoringStop}
              isConnected={isConnected}
            />
          </div>

          {/* Statistics */}
          <div className="stats-section">
            <StatisticsPanel 
              statistics={statistics}
              activeMonitoring={activeMonitoring}
            />
          </div>

          {/* Zone Management */}
          <div className="zones-section">
            <ZoneManagement 
              zones={zones}
              onZonesChange={setZones}
              isConnected={isConnected}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

