'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SensorReading } from '@homeguard/types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

interface SensorChartProps {
  readings: SensorReading[];
  title: string;
  color?: string;
}

export function SensorChart({ readings, title, color = '#3b82f6' }: SensorChartProps) {
  const chartData = readings.map((reading) => ({
    time: format(new Date(reading.timestamp), 'HH:mm:ss'),
    value: reading.value,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            Chưa có dữ liệu
          </div>
        )}
      </CardContent>
    </Card>
  );
}