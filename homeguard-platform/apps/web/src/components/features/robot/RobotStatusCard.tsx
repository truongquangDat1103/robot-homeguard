'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RobotStatus } from '@homeguard/types';
import { Battery, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RobotStatusCardProps {
  status: RobotStatus | null;
}

const getStateColor = (state: string) => {
  switch (state) {
    case 'IDLE':
      return 'text-green-500';
    case 'MOVING':
      return 'text-blue-500';
    case 'ALERT':
      return 'text-red-500';
    case 'CHARGING':
      return 'text-yellow-500';
    default:
      return 'text-gray-500';
  }
};

const getStateName = (state: string) => {
  switch (state) {
    case 'IDLE':
      return 'Chờ';
    case 'MOVING':
      return 'Di chuyển';
    case 'SCANNING':
      return 'Quét';
    case 'ALERT':
      return 'Cảnh báo';
    case 'CHARGING':
      return 'Sạc pin';
    case 'ERROR':
      return 'Lỗi';
    default:
      return state;
  }
};

const getEmotionEmoji = (emotion: string) => {
  switch (emotion) {
    case 'HAPPY':
      return '😊';
    case 'SAD':
      return '😢';
    case 'SURPRISED':
      return '😮';
    case 'ANGRY':
      return '😠';
    case 'NEUTRAL':
      return '😐';
    case 'CURIOUS':
      return '🤔';
    default:
      return '🤖';
  }
};

export function RobotStatusCard({ status }: RobotStatusCardProps) {
  if (!status) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Trạng thái Robot</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">Robot chưa kết nối</div>
        </CardContent>
      </Card>
    );
  }

  const batteryLevel = status.battery;
  const batteryColor =
    batteryLevel > 60 ? 'text-green-500' : batteryLevel > 20 ? 'text-yellow-500' : 'text-red-500';

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Trạng thái Robot</span>
          <Circle
            className={cn('h-3 w-3 fill-current', status.isConnected ? 'text-green-500' : 'text-red-500')}
          />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Trạng thái:</span>
          <span className={cn('font-semibold', getStateColor(status.state))}>
            {getStateName(status.state)}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Cảm xúc:</span>
          <span className="text-2xl">{getEmotionEmoji(status.emotion)}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Pin:</span>
          <div className="flex items-center gap-2">
            <Battery className={cn('h-5 w-5', batteryColor)} />
            <span className={cn('font-semibold', batteryColor)}>{batteryLevel.toFixed(0)}%</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Vị trí:</span>
          <span className="text-sm font-mono">
            ({status.position.x.toFixed(1)}, {status.position.y.toFixed(1)})
          </span>
        </div>
      </CardContent>
    </Card>
  );
}