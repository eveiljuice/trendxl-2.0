import React from 'react';
import { LoadingSpinnerProps } from '../types';

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  const borderClasses = {
    sm: 'border-2',
    md: 'border-2',
    lg: 'border-3'
  };

  return (
    <div className={`inline-block ${className}`}>
      <div 
        className={`
          ${sizeClasses[size]} 
          ${borderClasses[size]} 
          border-primary-accent 
          border-t-transparent 
          rounded-full 
          animate-spin
        `}
      />
    </div>
  );
};

export default LoadingSpinner;
