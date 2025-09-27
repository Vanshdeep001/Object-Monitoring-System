import React, { useState, useEffect } from 'react';
import './App.css';
import { HorizonHeroSection } from './components/ui/horizon-hero-section';
import { MonitoringType } from './types';

function App() {
  const [activeMonitoring, setActiveMonitoring] = useState<MonitoringType | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [statistics] = useState<any>({});
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
        }
      } catch (error) {
        console.error('Backend connection failed:', error);
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStartMonitoring = (type: MonitoringType) => {
    setActiveMonitoring(type);
  };

  const handleStopMonitoring = () => {
    setActiveMonitoring(null);
  };

  const handleZonesChange = (newZones: any[]) => {
    setZones(newZones);
  };

  return (
    <div className="App">
      <HorizonHeroSection
        activeMonitoring={activeMonitoring}
        isConnected={isConnected}
        statistics={statistics}
        zones={zones}
        onStartMonitoring={handleStartMonitoring}
        onStopMonitoring={handleStopMonitoring}
        onZonesChange={handleZonesChange}
        onMonitoringChange={setActiveMonitoring}
      />
    </div>
  );
}

export default App;
