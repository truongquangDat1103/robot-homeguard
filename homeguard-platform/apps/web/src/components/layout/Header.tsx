'use client';

import { useWebSocket } from '@/hooks/useWebSocket';
import { Circle } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Header() {
  const { isConnected } = useWebSocket();

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">HomeGuard Dashboard</h1>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Circle
              className={cn(
                'h-3 w-3 fill-current',
                isConnected ? 'text-green-500' : 'text-red-500'
              )}
            />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {isConnected ? 'Đã kết nối' : 'Mất kết nối'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}