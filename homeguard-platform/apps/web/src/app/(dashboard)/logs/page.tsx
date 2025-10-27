'use client';

import { LogsList } from '@/components/features/logs/LogsList';

export default function LogsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Nhật ký</h2>
        <p className="text-muted-foreground">Theo dõi hoạt động của hệ thống</p>
      </div>

      <LogsList />
    </div>
  );
}