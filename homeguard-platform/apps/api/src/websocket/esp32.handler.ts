import { Socket } from 'socket.io';
import { logger } from '@/utils/logger';
import { WebSocketEvent, SensorReading, RobotStatus } from '@homeguard/types';
import { saveSensorData, saveRobotStatus } from '@/services/esp32.service';
import { broadcastToRoom } from './index';

export const handleESP32Connection = (socket: Socket) => {
  const deviceId = socket.handshake.query.deviceId as string;
  
  if (!deviceId) {
    logger.warn('ESP32 connected without deviceId');
    socket.disconnect();
    return;
  }

  logger.info(`ESP32 device connected: ${deviceId} (${socket.id})`);

  // Join device-specific room
  socket.join(`esp32:${deviceId}`);
  socket.join('esp32');

  // Handle sensor data
  socket.on(WebSocketEvent.SENSOR_DATA, async (data: SensorReading | SensorReading[]) => {
    try {
      logger.debug({ event: 'sensor_data', deviceId, data });

      // Save to database
      await saveSensorData(data);

      // Broadcast to web clients
      broadcastToRoom('web-clients', WebSocketEvent.SENSOR_DATA, {
        deviceId,
        data,
        timestamp: new Date(),
      });
    } catch (error) {
      logger.error('Error handling sensor data:', error);
      socket.emit(WebSocketEvent.ERROR, {
        code: 'SENSOR_DATA_ERROR',
        message: 'Failed to process sensor data',
      });
    }
  });

  // Handle robot status updates
  socket.on(WebSocketEvent.ROBOT_STATUS, async (status: RobotStatus) => {
    try {
      logger.debug({ event: 'robot_status', deviceId, status });

      // Save to database
      await saveRobotStatus(deviceId, status);

      // Broadcast to web clients
      broadcastToRoom('web-clients', WebSocketEvent.ROBOT_STATUS, {
        deviceId,
        status,
        timestamp: new Date(),
      });
    } catch (error) {
      logger.error('Error handling robot status:', error);
    }
  });

  // Handle robot behavior events
  socket.on(WebSocketEvent.ROBOT_BEHAVIOR, async (behavior: any) => {
    try {
      logger.debug({ event: 'robot_behavior', deviceId, behavior });

      // Broadcast to web clients
      broadcastToRoom('web-clients', WebSocketEvent.ROBOT_BEHAVIOR, {
        deviceId,
        behavior,
        timestamp: new Date(),
      });
    } catch (error) {
      logger.error('Error handling robot behavior:', error);
    }
  });

  // Handle commands from server to ESP32
  socket.on(WebSocketEvent.ROBOT_COMMAND, (command: any) => {
    logger.debug({ event: 'robot_command_ack', deviceId, command });
    // Command acknowledgment from ESP32
  });

  // Heartbeat
  socket.on('heartbeat', () => {
    socket.emit('heartbeat_ack', { timestamp: Date.now() });
  });

  // Disconnection
  socket.on('disconnect', (reason) => {
    logger.info(`ESP32 device disconnected: ${deviceId} - ${reason}`);
    
    // Notify web clients
    broadcastToRoom('web-clients', WebSocketEvent.ESP32_DISCONNECTED, {
      deviceId,
      timestamp: new Date(),
    });
  });
};

// Send command to specific ESP32 device
export const sendCommandToESP32 = (socket: Socket, deviceId: string, command: any) => {
  socket.to(`esp32:${deviceId}`).emit(WebSocketEvent.ROBOT_COMMAND, command);
  logger.debug({ event: 'command_sent_to_esp32', deviceId, command });
};