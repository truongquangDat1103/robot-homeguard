import { create } from 'zustand';
import { SensorReading, SensorType } from '@homeguard/types';

interface SensorStore {
  sensorData: Record<string, SensorReading[]>;
  latestReadings: Record<string, SensorReading>;
  addSensorReading: (reading: SensorReading) => void;
  getLatestReading: (deviceId: string, sensorType: SensorType) => SensorReading | null;
  getSensorHistory: (deviceId: string, sensorType: SensorType) => SensorReading[];
  clearHistory: () => void;
}

export const useSensorStore = create<SensorStore>((set, get) => ({
  sensorData: {},
  latestReadings: {},

  addSensorReading: (reading) => {
    const key = `${reading.deviceId}:${reading.type}`;
    const latestKey = key;

    set((state) => {
      const currentData = state.sensorData[key] || [];
      const newData = [...currentData, reading].slice(-100); // Keep last 100 readings

      return {
        sensorData: {
          ...state.sensorData,
          [key]: newData,
        },
        latestReadings: {
          ...state.latestReadings,
          [latestKey]: reading,
        },
      };
    });
  },

  getLatestReading: (deviceId, sensorType) => {
    const key = `${deviceId}:${sensorType}`;
    return get().latestReadings[key] || null;
  },

  getSensorHistory: (deviceId, sensorType) => {
    const key = `${deviceId}:${sensorType}`;
    return get().sensorData[key] || [];
  },

  clearHistory: () => {
    set({ sensorData: {}, latestReadings: {} });
  },
}));