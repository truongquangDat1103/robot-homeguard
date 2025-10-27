'use client';

import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { WebSocketEvent } from '@homeguard/types';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:4000';

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // Initialize socket connection
    const socket = io(WS_URL, {
      query: {
        type: 'web-client',
        userId: 'user-1', // TODO: Get from auth context
      },
      reconnection: true,
      reconnectionDelay: 5000,
      reconnectionAttempts: 10,
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('✓ WebSocket connected:', socket.id);
      setIsConnected(true);
      setConnectionError(null);

      // Subscribe to channels
      socket.emit(WebSocketEvent.CLIENT_SUBSCRIBE, {
        channels: ['sensors', 'robot', 'ai'],
        clientId: socket.id,
      });
    });

    socket.on('disconnect', (reason) => {
      console.log('✗ WebSocket disconnected:', reason);
      setIsConnected(false);
    });

    socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      setConnectionError(error.message);
      setIsConnected(false);
    });

    socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Cleanup
    return () => {
      socket.disconnect();
    };
  }, []);

  const subscribe = (event: WebSocketEvent, callback: (data: any) => void) => {
    if (!socketRef.current) return;

    socketRef.current.on(event, callback);

    // Return unsubscribe function
    return () => {
      socketRef.current?.off(event, callback);
    };
  };

  const emit = (event: WebSocketEvent, data: any) => {
    if (!socketRef.current?.connected) {
      console.warn('Socket not connected, cannot emit');
      return;
    }

    socketRef.current.emit(event, data);
  };

  const sendRobotCommand = (deviceId: string, command: string, parameters?: any) => {
    emit(WebSocketEvent.ROBOT_COMMAND, {
      deviceId,
      type: 'movement',
      command,
      parameters,
    });
  };

  return {
    isConnected,
    connectionError,
    subscribe,
    emit,
    sendRobotCommand,
    socket: socketRef.current,
  };
};