import { Server, Socket } from 'socket.io';
import { logger } from '@/utils/logger';
import { WebSocketEvent, WebSocketMessage } from '@homeguard/types';

export class MessageRouter {
  private io: Server;

  constructor(io: Server) {
    this.io = io;
  }

  // Route message from one client type to another
  routeMessage(
    from: 'esp32' | 'ai-engine' | 'web-client',
    to: 'esp32' | 'ai-engine' | 'web-client' | 'all',
    event: WebSocketEvent,
    data: any
  ) {
    const message: WebSocketMessage = {
      event,
      data,
      timestamp: new Date(),
      sender: from,
    };

    logger.debug({ event: 'route_message', from, to, message });

    switch (to) {
      case 'esp32':
        this.io.to('esp32').emit(event, message);
        break;
      case 'ai-engine':
        this.io.to('ai-engine').emit(event, message);
        break;
      case 'web-client':
        this.io.to('web-clients').emit(event, message);
        break;
      case 'all':
        this.io.emit(event, message);
        break;
    }
  }

  // Route to specific device
  routeToDevice(deviceId: string, event: WebSocketEvent, data: any) {
    const message: WebSocketMessage = {
      event,
      data,
      timestamp: new Date(),
    };

    this.io.to(`esp32:${deviceId}`).emit(event, message);
    logger.debug({ event: 'route_to_device', deviceId, message });
  }

  // Route to specific user
  routeToUser(userId: string, event: WebSocketEvent, data: any) {
    const message: WebSocketMessage = {
      event,
      data,
      timestamp: new Date(),
    };

    this.io.to(`user:${userId}`).emit(event, message);
    logger.debug({ event: 'route_to_user', userId, message });
  }

  // Broadcast to all except sender
  broadcastExcept(socket: Socket, event: WebSocketEvent, data: any) {
    const message: WebSocketMessage = {
      event,
      data,
      timestamp: new Date(),
    };

    socket.broadcast.emit(event, message);
  }

  // Get connected clients by type
  async getConnectedClients(type: 'esp32' | 'ai-engine' | 'web-clients') {
    const room = await this.io.in(type).fetchSockets();
    return room.map((socket) => ({
      id: socket.id,
      data: socket.data,
    }));
  }

  // Check if device is connected
  async isDeviceConnected(deviceId: string): Promise<boolean> {
    const room = await this.io.in(`esp32:${deviceId}`).fetchSockets();
    return room.length > 0;
  }
}

export let messageRouter: MessageRouter;

export const initializeMessageRouter = (io: Server) => {
  messageRouter = new MessageRouter(io);
  logger.info('Message router initialized');
  return messageRouter;
};