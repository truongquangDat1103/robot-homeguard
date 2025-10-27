export enum WebSocketEvent {
  // Connection events
  CONNECT = 'connect',
  DISCONNECT = 'disconnect',
  ERROR = 'error',
  
  // Sensor events
  SENSOR_DATA = 'sensor:data',
  SENSOR_ALERT = 'sensor:alert',
  
  // Robot events
  ROBOT_STATUS = 'robot:status',
  ROBOT_COMMAND = 'robot:command',
  ROBOT_BEHAVIOR = 'robot:behavior',
  
  // Camera events
  CAMERA_FRAME = 'camera:frame',
  FACE_DETECTED = 'face:detected',
  MOTION_DETECTED = 'motion:detected',
  
  // AI Engine events
  AI_RESULT = 'ai:result',
  AI_STATUS = 'ai:status',
  
  // ESP32 events
  ESP32_CONNECTED = 'esp32:connected',
  ESP32_DISCONNECTED = 'esp32:disconnected',
  
  // Client events
  CLIENT_SUBSCRIBE = 'client:subscribe',
  CLIENT_UNSUBSCRIBE = 'client:unsubscribe',
}

export interface WebSocketMessage<T = unknown> {
  event: WebSocketEvent;
  data: T;
  timestamp: Date;
  sender?: string;
}

export interface WebSocketError {
  code: string;
  message: string;
  details?: unknown;
}

export interface SubscriptionRequest {
  channels: string[];
  clientId: string;
}