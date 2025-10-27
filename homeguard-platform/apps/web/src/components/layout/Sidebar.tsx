'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Activity, Camera, Bot, FileText, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Tổng quan', href: '/', icon: Home },
  { name: 'Cảm biến', href: '/sensors', icon: Activity },
  { name: 'Camera', href: '/camera', icon: Camera },
  { name: 'Robot', href: '/robot', icon: Bot },
  { name: 'Logs', href: '/logs', icon: FileText },
  { name: 'Cài đặt', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      <div className="p-6">
        <h2 className="text-xl font-bold text-primary">🏠 HomeGuard</h2>
      </div>
      
      <nav className="px-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}