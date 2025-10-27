import { Socket } from 'socket.io';
import { logger } from '@/utils/logger';
import { WebSocketEvent, SubscriptionRequest } from '@homeguard/types';
import { sendCommandToESP32 } from './esp32.handler';
import { getIO } from './index';

export const handleWebClientConnection = (socket: Socket) => {
  const clientId = socket.id;
  const userId = socket.handshake.query.userId as string;
  
  logger.info(`Web client connected: ${clientId}${userId ? ` (User: ${userId})` : ''}`);

  // Join web clients room
  socket.join('web-clients');
  if (userId) {
    socket.join(`user:${userId}`);
  }

  // Handle subscription requests
  socket.on(WebSocketEvent.CLIENT_SUBSCRIBE, (data: SubscriptionRequest) => {
    logger.debug({ event: 'client_subscribe', clientId, channels: data.channels });
    
    data.channels.forEach((channel) => {
      socket.join(channel);
    });

    socket.emit('subscribed', { channels: data.channels });
  });

  // Handle unsubscribe
  socket.on(WebSocketEvent.CLIENT_UNSUBSCRIBE, (data: { channels: string[] }) => {
    logger.debug({ event: 'client_unsubscribe', clientId, channels: data.channels });
    
    data.channels.forEach((channel) => {
      socket.leave(channel);
    });

    socket.emit('unsubscribed', { channels: data.channels });
  });

  // Handle robot commands from web client
  socket.on(WebSocketEvent.ROBOT_COMMAND, async (command: any) => {
    try {
      logger.debug({ event: 'robot_command', clientId, command });

      const { deviceId, type, command: cmd, parameters } = command;

      if (!deviceId) {
        socket.emit(WebSocketEvent.ERROR, {
          code: 'MISSING_DEVICE_ID',
          message: 'Device ID is required',
        });
        return;
      }

      // Send command to ESP32
      const io = getIO();
      io.to(`esp32:${deviceId}`).emit(WebSocketEvent.ROBOT_COMMAND, {
        type,
        command: cmd,
        parameters,
        timestamp: new Date(),
      });

      // Acknowledge
      socket.emit('command_sent', {
        deviceId,
        command: cmd,
        timestamp: new Date(),
      });
    } catch (error) {
      logger.error('Error handling robot command:', error);
      socket.emit(WebSocketEvent.ERROR, {
        code: 'COMMAND_ERROR',
        message: 'Failed to send command',
      });
    }
  });

  // Request current status
  socket.on('request_status', (data: { deviceId?: string } = {}) => {
    logger.debug({ event: 'request_status', clientId, deviceId: data.deviceId });
    
    const io = getIO();
    
    if (data.deviceId) {
      // Request from specific device
      io.to(`esp32:${data.deviceId}`).emit('status_request');
    } else {
      // Request from all devices
      io.to('esp32').emit('status_request');
    }
  });

  // Ping/Pong
  socket.on('ping', () => {
    socket.emit('pong', { timestamp: Date.now() });
  });

  // Disconnection
  socket.on('disconnect', (reason) => {
    logger.info(`Web client disconnected: ${clientId} - ${reason}`);
  });
};