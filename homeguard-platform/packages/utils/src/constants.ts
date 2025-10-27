// WebSocket constants
export const WS_RECONNECT_INTERVAL = 5000; // 5 seconds
export const WS_MAX_RECONNECT_ATTEMPTS = 10;
export const WS_PING_INTERVAL = 30000; // 30 seconds

// API constants
export const API_TIMEOUT = 30000; // 30 seconds
export const API_RATE_LIMIT = 100; // requests per minute

// Sensor constants
export const SENSOR_UPDATE_INTERVAL = 1000; // 1 second
export const SENSOR_HISTORY_LIMIT = 100;

export const SENSOR_UNITS = {
  temperature: '°C',
  humidity: '%',
  light: 'lux',
  distance: 'cm',
  gas: 'ppm',
  sound: 'dB',
} as const;

// Robot constants
export const ROBOT_BATTERY_WARNING = 20; // %
export const ROBOT_BATTERY_CRITICAL = 10; // %
export const ROBOT_MAX_SPEED = 100; // units
export const ROBOT_STATUS_INTERVAL = 2000; // 2 seconds

// Camera constants
export const CAMERA_FPS = 30;
export const CAMERA_RESOLUTION = '1280x720';
export const FACE_DETECTION_CONFIDENCE = 0.7;

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

// Validation
export const MIN_PASSWORD_LENGTH = 8;
export const MAX_USERNAME_LENGTH = 50;
export const MAX_MESSAGE_LENGTH = 1000;

// Error codes
export const ERROR_CODES = {
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  WS_CONNECTION_FAILED: 'WS_CONNECTION_FAILED',
  DEVICE_OFFLINE: 'DEVICE_OFFLINE',
} as const;