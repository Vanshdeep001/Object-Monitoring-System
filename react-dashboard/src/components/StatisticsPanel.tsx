import React, { useEffect, useState } from 'react';
import { MonitoringType } from '../types';
import { CommitsGrid } from './ui/commits-grid';

interface StatisticsPanelProps {
  statistics: any;
  activeMonitoring: MonitoringType | null;
}

const StatisticsPanel: React.FC<StatisticsPanelProps> = ({
  statistics,
  activeMonitoring
}) => {
  const [stats, setStats] = useState({
    total_detections: 0,
    active_objects: 0,
    violations: 0,
    frame_count: 0,
    fps: 0
  });

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/statistics');
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    };

    if (activeMonitoring) {
      fetchStatistics();
      const interval = setInterval(fetchStatistics, 2000);
      return () => clearInterval(interval);
    }
  }, [activeMonitoring]);

  const getMonitoringStats = () => {
    if (!activeMonitoring) return null;

    switch (activeMonitoring) {
      case 'object_detection':
        return statistics.object_detection || {};
      case 'zone_monitoring':
        return statistics.zone_monitoring || {};
      case 'clean_detection':
        return statistics.clean_detection || {};
      default:
        return {};
    }
  };

  const currentStats = getMonitoringStats();

  const statCards = [
    {
      title: 'Total Detections',
      value: currentStats?.total_detections || 0,
      icon: '🎯',
      color: '#3b82f6'
    },
    {
      title: 'Active Objects',
      value: currentStats?.active_objects || 0,
      icon: '👥',
      color: '#10b981'
    },
    {
      title: 'Zone Violations',
      value: currentStats?.violations || 0,
      icon: '🚫',
      color: '#ef4444'
    },
    {
      title: 'Frames Processed',
      value: currentStats?.frame_count || 0,
      icon: '📊',
      color: '#8b5cf6'
    }
  ];

  return (
    <div className="statistics-panel">
      <h2>📊 Statistics</h2>
      
      <div className="stats-grid">
        {statCards.map((card, index) => (
          <div key={index} className="stat-card">
            <div className="stat-icon" style={{ color: card.color }}>
              {card.icon}
            </div>
            <div className="stat-content">
              <h3>{card.title}</h3>
              <div className="stat-value" style={{ color: card.color }}>
                {card.value.toLocaleString()}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* CommitsGrid Display for Statistics */}
      {activeMonitoring && (
        <div className="commits-grid-section">
          <h3>📈 Live Activity Display</h3>
          <div className="commits-grid-container">
            <CommitsGrid text={`${currentStats?.total_detections || 0}`} />
            <div className="commits-grid-label">Total Detections</div>
          </div>
        </div>
      )}

      {activeMonitoring && (
        <div className="monitoring-info">
          <h3>Current Monitoring</h3>
          <div className="info-item">
            <span className="info-label">Type:</span>
            <span className="info-value">
              {activeMonitoring === 'object_detection' ? 'Object Detection' :
               activeMonitoring === 'zone_monitoring' ? 'Zone Monitoring' :
               'Clean Detection'}
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Status:</span>
            <span className="info-value active">🟢 Active</span>
          </div>
          <div className="info-item">
            <span className="info-label">Last Update:</span>
            <span className="info-value">
              {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>
      )}

      {!activeMonitoring && (
        <div className="no-monitoring">
          <div className="no-monitoring-icon">📊</div>
          <p>No active monitoring</p>
          <p className="no-monitoring-subtitle">Start monitoring to see statistics</p>
        </div>
      )}
    </div>
  );
};

export default StatisticsPanel;

