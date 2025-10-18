import React from 'react';
import { cn } from '@/utils/cn';
import type { InputProps } from '@/types';

const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  className,
  label,
  error,
  description,
  id,
  ...props
}, ref) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="label mb-2 block text-gray-900">
          {label}
        </label>
      )}
      <input
        id={inputId}
        ref={ref}
        className={cn(
          'input',
          error && 'border-danger-500 focus-visible:ring-danger-500',
          className
        )}
        {...props}
      />
      {description && !error && (
        <p className="mt-1 text-sm text-gray-600">{description}</p>
      )}
      {error && (
        <p className="mt-1 text-sm text-danger-600">{error}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;