import React from 'react';
import { cn } from '@/utils/cn';
import type { ProgressProps } from '@/types';

const Progress: React.FC<ProgressProps> = ({
  value,
  max,
  className,
  showLabel = false,
}) => {
  const percentage = Math.round((value / max) * 100);

  return (
    <div className={cn('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Progress</span>
          <span className="text-sm text-gray-600">{percentage}%</span>
        </div>
      )}
      <div className="progress">
        <div
          className="progress-bar"
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
};

export default Progress;