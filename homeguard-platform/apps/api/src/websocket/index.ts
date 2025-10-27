import { Server as HttpServer } from 'http';
import { Server, Socket } from 'socket.io';
import { logger } from '@/utils/logger';
import { handleESP32Connection } from './esp32.handler';
import { handleAIEngineConnection } from './ai-engine.handler';
import { handleWebClientConnection } from './client.handler';
import { initializeMessageRouter } from './message-router';

let io: Server;

export const createWebSocketServer = (httpServer: HttpServer) => {
  io = new Server(httpServer, {
    cors: {
      origin: process.env.CORS_ORIGIN || '*',
      methods: ['GET', 'POST'],
      credentials: true,
    },
    pingTimeout: 60000,
    pingInterval: 25000,
  });

  // Initialize message router
  initializeMessageRouter(io);

  io.on('connection', (socket: Socket) => {
    const clientId = socket.id;
    const clientType = socket.handshake.query.type as string;

    logger.info({
      event: 'client_connected',
      clientId,
      clientType,
      address: socket.handshake.address,
    });

    // Handle client type registration
    if (clientType === 'esp32') {
      handleESP32Connection(socket);
    } else if (clientType === 'ai-engine') {
      handleAIEngineConnection(socket);
    } else if (clientType === 'web-client') {
      handleWebClientConnection(socket);
    } else {
      logger.warn(`Unknown client type: ${clientType}`);
      socket.disconnect();
    }

    // Common disconnect handler
    socket.on('disconnect', (reason) => {
      logger.info({
        event: 'client_disconnected',
        clientId,
        clientType,
        reason,
      });
    });

    // Error handler
    socket.on('error', (error) => {
      logger.error({
        event: 'socket_error',
        clientId,
        error,
      });
    });
  });

  return io;
};

export const getIO = () => {
  if (!io) {
    throw new Error('WebSocket server not initialized');
  }
  return io;
};

export const broadcastToAll = (event: string, data: any) => {
  if (io) {
    io.emit(event, data);
  }
};

export const broadcastToRoom = (room: string, event: string, data: any) => {
  if (io) {
    io.to(room).emit(event, data);
  }
};