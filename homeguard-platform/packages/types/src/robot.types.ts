export enum RobotState {
  IDLE = 'idle',
  MOVING = 'moving',
  SCANNING = 'scanning',
  ALERT = 'alert',
  CHARGING = 'charging',
  ERROR = 'error',
}

export enum RobotEmotion {
  HAPPY = 'happy',
  SAD = 'sad',
  SURPRISED = 'surprised',
  ANGRY = 'angry',
  NEUTRAL = 'neutral',
  CURIOUS = 'curious',
}

export enum MovementDirection {
  FORWARD = 'forward',
  BACKWARD = 'backward',
  LEFT = 'left',
  RIGHT = 'right',
  STOP = 'stop',
}

export interface RobotStatus {
  id: string;
  state: RobotState;
  emotion: RobotEmotion;
  battery: number;
  position: {
    x: number;
    y: number;
    rotation: number;
  };
  isConnected: boolean;
  lastUpdate: Date;
}

export interface RobotCommand {
  id: string;
  type: 'movement' | 'emotion' | 'action';
  command: string;
  parameters?: Record<string, unknown>;
  timestamp: Date;
}

export interface BehaviorLog {
  id: string;
  robotId: string;
  behavior: string;
  description: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}