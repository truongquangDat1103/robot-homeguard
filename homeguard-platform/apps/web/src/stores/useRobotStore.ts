import { create } from 'zustand';
import { RobotStatus, RobotState, RobotEmotion } from '@homeguard/types';

interface RobotStore {
  robotStatus: Record<string, RobotStatus>;
  updateRobotStatus: (deviceId: string, status: RobotStatus) => void;
  getRobotStatus: (deviceId: string) => RobotStatus | null;
  isRobotConnected: (deviceId: string) => boolean;
}

export const useRobotStore = create<RobotStore>((set, get) => ({
  robotStatus: {},

  updateRobotStatus: (deviceId, status) => {
    set((state) => ({
      robotStatus: {
        ...state.robotStatus,
        [deviceId]: status,
      },
    }));
  },

  getRobotStatus: (deviceId) => {
    return get().robotStatus[deviceId] || null;
  },

  isRobotConnected: (deviceId) => {
    const status = get().robotStatus[deviceId];
    return status?.isConnected || false;
  },
}));