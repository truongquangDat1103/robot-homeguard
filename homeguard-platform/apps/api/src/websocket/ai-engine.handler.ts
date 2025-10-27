import { Socket } from 'socket.io';
import { logger } from '@/utils/logger';
import { WebSocketEvent } from '@homeguard/types';
import { processFaceDetection, processMotionDetection, processAIResult } from '@/services/ai-engine.service';
import { broadcastToRoom } from './index';

export const handleAIEngineConnection = (socket: Socket) => {
  const engineId = socket.handshake.query.engineId as string || socket.id;
  
  logger.info(`AI Engine connected: ${engineId} (${socket.id})`);

  // Join AI engine room
  socket.join('ai-engine');
  socket.join(`ai-engine:${engineId}`);

  // Notify connection
  broadcastToRoom('web-clients', WebSocketEvent.AI_STATUS, {
    engineId,
    status: 'connected',
    timestamp: new Date(),
  });

  // Handle face detection results
  socket.on(WebSocketEvent.FACE_DETECTED, async (data: any) => {
    try {
      logger.debug({ event: 'face_detected', engineId, data });

      // Process face detection
      const result = await processFaceDetection(data);

      // Broadcast to web clients
      broadcastToRoom('web-clients', WebSocketEvent.FACE_DETECTED, {
        engineId,
        ...result,
        timestamp: new Date(),
      });

      // Send to ESP32 if action needed
      if (result.actionRequired) {
        broadcastToRoom('esp32', WebSocketEvent.ROBOT_COMMAND, {
          type: 'action',
          command: result.action,
          parameters: result.parameters,
        });
      }
    } catch (error) {
      logger.error('Error handling face detection:', error);
    }
  });

  // Handle motion detection results
  socket.on(WebSocketEvent.MOTION_DETECTED, async (data: any) => {
    try {
      logger.debug({ event: 'motion_detected', engineId, data });

      // Process motion detection
      const result = await processMotionDetection(data);

      // Broadcast to web clients
      broadcastToRoom('web-clients', WebSocketEvent.MOTION_DETECTED, {
        engineId,
        ...result,
        timestamp: new Date(),
      });
    } catch (error) {
      logger.error('Error handling motion detection:', error);
    }
  });

  // Handle generic AI results
  socket.on(WebSocketEvent.AI_RESULT, async (data: any) => {
    try {
      logger.debug({ event: 'ai_result', engineId, data });

      // Process AI result
      const result = await processAIResult(data);

      // Broadcast to web clients
      broadcastToRoom('web-clients', WebSocketEvent.AI_RESULT, {
        engineId,
        ...result,
        timestamp: new Date(),
      });
    } catch (error) {
      logger.error('Error handling AI result:', error);
    }
  });

  // Handle camera frames (if needed for streaming)
  socket.on(WebSocketEvent.CAMERA_FRAME, (data: any) => {
    // Forward to web clients (for live preview)
    broadcastToRoom('web-clients', WebSocketEvent.CAMERA_FRAME, {
      engineId,
      frame: data.frame,
      timestamp: Date.now(),
    });
  });

  // AI Engine status updates
  socket.on(WebSocketEvent.AI_STATUS, (status: any) => {
    logger.debug({ event: 'ai_status', engineId, status });
    
    broadcastToRoom('web-clients', WebSocketEvent.AI_STATUS, {
      engineId,
      status,
      timestamp: new Date(),
    });
  });

  // Heartbeat
  socket.on('heartbeat', () => {
    socket.emit('heartbeat_ack', { timestamp: Date.now() });
  });

  // Disconnection
  socket.on('disconnect', (reason) => {
    logger.info(`AI Engine disconnected: ${engineId} - ${reason}`);
    
    broadcastToRoom('web-clients', WebSocketEvent.AI_STATUS, {
      engineId,
      status: 'disconnected',
      reason,
      timestamp: new Date(),
    });
  });
};