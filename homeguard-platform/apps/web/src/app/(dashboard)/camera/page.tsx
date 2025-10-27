'use client';

import { LiveStream } from '@/components/features/camera/LiveStream';
import { FaceRecognition } from '@/components/features/camera/FaceRecognition';

export default function CameraPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Camera & AI</h2>
        <p className="text-muted-foreground">Giám sát camera và nhận diện khuôn mặt</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <LiveStream />
        </div>
        <div>
          <FaceRecognition />
        </div>
      </div>
    </div>
  );
}