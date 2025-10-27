'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useWebSocket } from '@/hooks/useWebSocket';
import { WebSocketEvent } from '@homeguard/types';
import { formatRelativeTime } from '@homeguard/utils';
import { UserCircle, AlertTriangle } from 'lucide-react';

interface FaceDetection {
  faces: Array<{
    name?: string;
    confidence: number;
    bbox: { x: number; y: number; width: number; height: number };
  }>;
  unknownCount: number;
  knownCount: number;
  timestamp: Date;
}

export function FaceRecognition() {
  const [detections, setDetections] = useState<FaceDetection[]>([]);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe(WebSocketEvent.FACE_DETECTED, (data) => {
      console.log('Face detected:', data);
      setDetections((prev) => [data, ...prev].slice(0, 10)); // Keep last 10
    });

    return () => unsubscribe?.();
  }, [subscribe]);

  const latestDetection = detections[0];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Nhận diện khuôn mặt</CardTitle>
      </CardHeader>
      <CardContent>
        {latestDetection ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="flex items-center gap-3">
                <UserCircle className="h-8 w-8 text-primary" />
                <div>
                  <p className="font-semibold">
                    {latestDetection.knownCount} người quen thuộc
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatRelativeTime(latestDetection.timestamp)}
                  </p>
                </div>
              </div>
              {latestDetection.unknownCount > 0 && (
                <div className="flex items-center gap-2 text-yellow-600">
                  <AlertTriangle className="h-5 w-5" />
                  <span className="font-semibold">
                    {latestDetection.unknownCount} người lạ
                  </span>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Danh sách phát hiện:</p>
              {latestDetection.faces.map((face, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <span className="font-medium">
                    {face.name || 'Người lạ'}
                  </span>
                  <span className="text-sm text-muted-foreground">
                    {(face.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center text-muted-foreground py-8">
            Chưa phát hiện khuôn mặt nào
          </div>
        )}
      </CardContent>
    </Card>
  );
}