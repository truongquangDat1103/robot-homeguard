import { io, Socket } from 'socket.io-client';
import { WebSocketEvent } from '@homeguard/types';

export class WebSocketClient {
  private socket: Socket | null = null;
  private serverUrl: string;
  private engineId: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectInterval = 5000;

  constructor(serverUrl: string, engineId: string) {
    this.serverUrl = serverUrl;
    this.engineId = engineId;
  }

  connect() {
    console.log(`Connecting to server: ${this.serverUrl}`);

    this.socket = io(this.serverUrl, {
      query: {
        type: 'ai-engine',
        engineId: this.engineId,
      },
      reconnection: true,
      reconnectionDelay: this.reconnectInterval,
      reconnectionAttempts: this.maxReconnectAttempts,
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('✓ Connected to server:', this.socket?.id);
      this.reconnectAttempts = 0;

      // Send initial status
      this.sendStatus({
        status: 'online',
        engineId: this.engineId,
        capabilities: ['face_detection', 'motion_detection', 'object_detection'],
      });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error.message);
      this.reconnectAttempts++;

      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
      }
    });

    this.socket.on('error', (error) => {
      console.error('Socket error:', error);
    });

    // Heartbeat
    this.socket.on('heartbeat_ack', (data) => {
      console.log('Heartbeat acknowledged:', data);
    });

    // Handle commands from server (if needed)
    this.socket.on(WebSocketEvent.ROBOT_COMMAND, (command) => {
      console.log('Received command:', command);
      // AI Engine can process commands if needed
    });
  }

  // Send face detection result
  sendFaceDetection(data: any) {
    if (!this.socket?.connected) {
      console.warn('Socket not connected, cannot send face detection');
      return;
    }

    this.socket.emit(WebSocketEvent.FACE_DETECTED, {
      ...data,
      engineId: this.engineId,
      timestamp: new Date(),
    });

    console.log('Sent face detection:', data);
  }

  // Send motion detection result
  sendMotionDetection(data: any) {
    if (!this.socket?.connected) {
      console.warn('Socket not connected, cannot send motion detection');
      return;
    }

    this.socket.emit(WebSocketEvent.MOTION_DETECTED, {
      ...data,
      engineId: this.engineId,
      timestamp: new Date(),
    });

    console.log('Sent motion detection:', data);
  }

  // Send generic AI result
  sendAIResult(data: any) {
    if (!this.socket?.connected) {
      console.warn('Socket not connected, cannot send AI result');
      return;
    }

    this.socket.emit(WebSocketEvent.AI_RESULT, {
      ...data,
      engineId: this.engineId,
      timestamp: new Date(),
    });

    console.log('Sent AI result:', data);
  }

  // Send camera frame (for live preview)
  sendCameraFrame(frameData: string) {
    if (!this.socket?.connected) {
      return;
    }

    this.socket.emit(WebSocketEvent.CAMERA_FRAME, {
      frame: frameData,
      engineId: this.engineId,
    });
  }

  // Send status update
  sendStatus(status: any) {
    if (!this.socket?.connected) {
      console.warn('Socket not connected, cannot send status');
      return;
    }

    this.socket.emit(WebSocketEvent.AI_STATUS, status);
    console.log('Sent status:', status);
  }

  // Send heartbeat
  sendHeartbeat() {
    if (!this.socket?.connected) return;
    this.socket.emit('heartbeat');
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      console.log('Disconnected from server');
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}