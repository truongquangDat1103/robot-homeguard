'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SensorReading, SensorType } from '@homeguard/types';
import { formatSensorValue, formatRelativeTime } from '@homeguard/utils';
import { Thermometer, Droplets, Sun, Activity } from 'lucide-react';

interface SensorCardProps {
  reading: SensorReading | null;
  sensorType: SensorType;
}

const getSensorIcon = (type: SensorType) => {
  switch (type) {
    case SensorType.TEMPERATURE:
      return <Thermometer className="h-5 w-5" />;
    case SensorType.HUMIDITY:
      return <Droplets className="h-5 w-5" />;
    case SensorType.LIGHT:
      return <Sun className="h-5 w-5" />;
    default:
      return <Activity className="h-5 w-5" />;
  }
};

const getSensorLabel = (type: SensorType) => {
  switch (type) {
    case SensorType.TEMPERATURE:
      return 'Nhiệt độ';
    case SensorType.HUMIDITY:
      return 'Độ ẩm';
    case SensorType.LIGHT:
      return 'Ánh sáng';
    case SensorType.MOTION:
      return 'Chuyển động';
    case SensorType.DISTANCE:
      return 'Khoảng cách';
    case SensorType.GAS:
      return 'Khí gas';
    case SensorType.SOUND:
      return 'Âm thanh';
    default:
      return type;
  }
};

export function SensorCard({ reading, sensorType }: SensorCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{getSensorLabel(sensorType)}</CardTitle>
        {getSensorIcon(sensorType)}
      </CardHeader>
      <CardContent>
        {reading ? (
          <>
            <div className="text-2xl font-bold">
              {formatSensorValue(reading.value, reading.unit)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {formatRelativeTime(reading.timestamp)}
            </p>
          </>
        ) : (
          <div className="text-sm text-muted-foreground">Chưa có dữ liệu</div>
        )}
      </CardContent>
    </Card>
  );
}