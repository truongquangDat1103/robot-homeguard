'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Square } from 'lucide-react';

interface RobotControlProps {
  onCommand: (command: string) => void;
  disabled?: boolean;
}

export function RobotControl({ onCommand, disabled = false }: RobotControlProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Điều khiển Robot</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-2 max-w-xs mx-auto">
          <div></div>
          <Button
            variant="outline"
            size="lg"
            onClick={() => onCommand('forward')}
            disabled={disabled}
            className="h-16"
          >
            <ArrowUp className="h-6 w-6" />
          </Button>
          <div></div>

          <Button
            variant="outline"
            size="lg"
            onClick={() => onCommand('left')}
            disabled={disabled}
            className="h-16"
          >
            <ArrowLeft className="h-6 w-6" />
          </Button>
          <Button
            variant="destructive"
            size="lg"
            onClick={() => onCommand('stop')}
            disabled={disabled}
            className="h-16"
          >
            <Square className="h-6 w-6" />
          </Button>
          <Button
            variant="outline"
            size="lg"
            onClick={() => onCommand('right')}
            disabled={disabled}
            className="h-16"
          >
            <ArrowRight className="h-6 w-6" />
          </Button>

          <div></div>
          <Button
            variant="outline"
            size="lg"
            onClick={() => onCommand('backward')}
            disabled={disabled}
            className="h-16"
          >
            <ArrowDown className="h-6 w-6" />
          </Button>
          <div></div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2">
          <Button variant="secondary" onClick={() => onCommand('scan')} disabled={disabled}>
            Quét
          </Button>
          <Button variant="secondary" onClick={() => onCommand('home')} disabled={disabled}>
            Về nhà
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}