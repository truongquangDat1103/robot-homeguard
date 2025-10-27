export enum SensorType {
  TEMPERATURE = 'temperature',
  HUMIDITY = 'humidity',
  LIGHT = 'light',
  MOTION = 'motion',
  DISTANCE = 'distance',
  GAS = 'gas',
  SOUND = 'sound',
}

export interface SensorReading {
  id: string;
  type: SensorType;
  value: number;
  unit: string;
  timestamp: Date;
  deviceId: string;
}

export interface SensorData {
  temperature?: number;
  humidity?: number;
  light?: number;
  motion?: boolean;
  distance?: number;
  gas?: number;
  sound?: number;
}

export interface SensorThreshold {
  id: string;
  sensorType: SensorType;
  minValue?: number;
  maxValue?: number;
  alertEnabled: boolean;
}

export interface SensorAlert {
  id: string;
  sensorId: string;
  sensorType: SensorType;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  acknowledged: boolean;
}