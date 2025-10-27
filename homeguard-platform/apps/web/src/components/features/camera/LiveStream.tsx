'use client';

import { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useWebSocket } from '@/hooks/useWebSocket';
import { WebSocketEvent } from '@homeguard/types';

export function LiveStream() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe(WebSocketEvent.CAMERA_FRAME, (data) => {
      if (data.frame && canvasRef.current) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        
        if (ctx) {
          const img = new Image();
          img.onload = () => {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            setIsStreaming(true);
          };
          img.src = `data:image/jpeg;base64,${data.frame}`;
        }
      }
    });

    return () => unsubscribe?.();
  }, [subscribe]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Camera trực tiếp</span>
          <span className={`text-sm ${isStreaming ? 'text-green-500' : 'text-gray-400'}`}>
            {isStreaming ? '● LIVE' : '○ Offline'}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden">
          <canvas
            ref={canvasRef}
            width={640}
            height={480}
            className="w-full h-full object-contain"
          />
          {!isStreaming && (
            <div className="absolute inset-0 flex items-center justify-center text-gray-400">
              Đang chờ video stream...
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}