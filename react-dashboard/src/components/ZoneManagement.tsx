import React, { useEffect, useState } from 'react';
import { Zone } from '../types';

interface ZoneManagementProps {
  zones: Zone[];
  onZonesChange: (zones: Zone[]) => void;
  isConnected: boolean;
}

const ZoneManagement: React.FC<ZoneManagementProps> = ({
  zones,
  onZonesChange,
  isConnected
}) => {
  const [isAddingZone, setIsAddingZone] = useState(false);
  const [newZoneName, setNewZoneName] = useState('');

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/zones');
        if (response.ok) {
          const data = await response.json();
          onZonesChange(data.zones || []);
        }
      } catch (error) {
        console.error('Error fetching zones:', error);
      }
    };

    if (isConnected) {
      fetchZones();
    }
  }, [isConnected, onZonesChange]);

  const handleAddZone = async () => {
    if (!newZoneName.trim() || !isConnected) return;

    try {
      // For demo purposes, create a default rectangular zone
      const defaultPoints = [
        [100, 100],
        [200, 100],
        [200, 200],
        [100, 200]
      ];

      const response = await fetch('http://localhost:8000/api/zones/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newZoneName,
          points: defaultPoints
        }),
      });

      if (response.ok) {
        setNewZoneName('');
        setIsAddingZone(false);
        // Refresh zones
        const zonesResponse = await fetch('http://localhost:8000/api/zones');
        if (zonesResponse.ok) {
          const data = await zonesResponse.json();
          onZonesChange(data.zones || []);
        }
      } else {
        console.error('Failed to add zone');
      }
    } catch (error) {
      console.error('Error adding zone:', error);
    }
  };

  return (
    <div className="zone-management">
      <h2>🎯 Zone Management</h2>
      
      <div className="zone-controls">
        <button
          className="add-zone-button"
          onClick={() => setIsAddingZone(true)}
          disabled={!isConnected}
        >
          ➕ Add Zone
        </button>
      </div>

      {isAddingZone && (
        <div className="add-zone-form">
          <input
            type="text"
            placeholder="Zone name"
            value={newZoneName}
            onChange={(e) => setNewZoneName(e.target.value)}
            className="zone-name-input"
          />
          <div className="form-actions">
            <button
              className="save-zone-button"
              onClick={handleAddZone}
              disabled={!newZoneName.trim()}
            >
              Save
            </button>
            <button
              className="cancel-zone-button"
              onClick={() => {
                setIsAddingZone(false);
                setNewZoneName('');
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="zones-list">
        <h3>Active Zones ({zones.length})</h3>
        {zones.length > 0 ? (
          <div className="zones-grid">
            {zones.map((zone, index) => (
              <div key={index} className="zone-card">
                <div className="zone-header">
                  <span className="zone-icon">🎯</span>
                  <h4>{zone.name}</h4>
                </div>
                <div className="zone-info">
                  <div className="zone-detail">
                    <span className="detail-label">Type:</span>
                    <span className="detail-value">{zone.type}</span>
                  </div>
                  <div className="zone-detail">
                    <span className="detail-label">Points:</span>
                    <span className="detail-value">{zone.points?.length || 0}</span>
                  </div>
                </div>
                <div className="zone-status">
                  <span className="status-indicator active">🟢 Active</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-zones">
            <div className="no-zones-icon">🎯</div>
            <p>No zones configured</p>
            <p className="no-zones-subtitle">Add zones to monitor restricted areas</p>
          </div>
        )}
      </div>

      {!isConnected && (
        <div className="connection-warning">
          <p>⚠️ Backend not connected. Zone management unavailable.</p>
        </div>
      )}
    </div>
  );
};

export default ZoneManagement;



