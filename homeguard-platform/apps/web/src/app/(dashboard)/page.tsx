'use client';

import { useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useSensorStore } from '@/stores/useSensorStore';
import { useRobotStore } from '@/stores/useRobotStore';
import { SensorCard } from '@/components/features/sensors/SensorCard';
import { SensorChart } from '@/components/features/sensors/SensorChart';
import { RobotStatusCard } from '@/components/features/robot/RobotStatusCard';
import { RobotControl } from '@/components/features/robot/RobotControl';
import { WebSocketEvent, SensorType } from '@homeguard/types';

const DEVICE_ID = 'esp32-test-1';

export default function DashboardPage() {
  const { subscribe, sendRobotCommand, isConnected } = useWebSocket();
  const { addSensorReading, getLatestReading, getSensorHistory } = useSensorStore();
  const { updateRobotStatus, getRobotStatus } = useRobotStore();

  useEffect(() => {
    // Subscribe to sensor data
    const unsubSensor = subscribe(WebSocketEvent.SENSOR_DATA, (data) => {
      console.log('Received sensor data:', data);

      if (data.data) {
        if (Array.isArray(data.data)) {
          data.data.forEach((reading: any) => addSensorReading(reading));
        } else {
          addSensorReading(data.data);
        }
      }
    });

    // Subscribe to robot status
    const unsubRobot = subscribe(WebSocketEvent.ROBOT_STATUS, (data) => {
      console.log('Received robot status:', data);
      if (data.status) {
        updateRobotStatus(data.deviceId || DEVICE_ID, data.status);
      }
    });

    return () => {
      unsubSensor?.();
      unsubRobot?.();
    };
  }, [subscribe, addSensorReading, updateRobotStatus]);

  const handleRobotCommand = (command: string) => {
    console.log('Sending command:', command);
    sendRobotCommand(DEVICE_ID, command);
  };

  const tempReading = getLatestReading(DEVICE_ID, SensorType.TEMPERATURE);
  const humidityReading = getLatestReading(DEVICE_ID, SensorType.HUMIDITY);
  const lightReading = getLatestReading(DEVICE_ID, SensorType.LIGHT);
  const distanceReading = getLatestReading(DEVICE_ID, SensorType.DISTANCE);

  const tempHistory = getSensorHistory(DEVICE_ID, SensorType.TEMPERATURE);
  const humidityHistory = getSensorHistory(DEVICE_ID, SensorType.HUMIDITY);

  const robotStatus = getRobotStatus(DEVICE_ID);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Tổng quan</h2>
        <p className="text-muted-foreground">Giám sát hệ thống HomeGuard real-time</p>
      </div>

      {/* Sensor Cards Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <SensorCard reading={tempReading} sensorType={SensorType.TEMPERATURE} />
        <SensorCard reading={humidityReading} sensorType={SensorType.HUMIDITY} />
        <SensorCard reading={lightReading} sensorType={SensorType.LIGHT} />
        <SensorCard reading={distanceReading} sensorType={SensorType.DISTANCE} />
      </div>

      {/* Charts */}
      <div className="grid gap-6 md:grid-cols-2">
        <SensorChart readings={tempHistory} title="Nhiệt độ theo thời gian" color="#ef4444" />
        <SensorChart readings={humidityHistory} title="Độ ẩm theo thời gian" color="#3b82f6" />
      </div>

      {/* Robot Section */}
      <div className="grid gap-6 md:grid-cols-2">
        <RobotStatusCard status={robotStatus} />
        <RobotControl onCommand={handleRobotCommand} disabled={!isConnected} />
      </div>
    </div>
  );
}