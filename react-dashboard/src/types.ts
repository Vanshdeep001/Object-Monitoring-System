export type MonitoringType = 'object_detection' | 'zone_monitoring' | 'clean_detection';

export interface DetectionResult {
  class: string;
  confidence: number;
  bbox: [number, number, number, number];
}

export interface Zone {
  id: string;
  name: string;
  points: [number, number][];
  type: 'rectangular' | 'polygonal';
}

export interface MonitoringStats {
  total_detections: number;
  active_objects: number;
  violations: number;
  frame_count: number;
  fps: number;
}

export interface WebSocketMessage {
  type: MonitoringType;
  frame: string;
  detections?: number;
  violations?: number;
  frame_count?: number;
  timestamp: string;
}



