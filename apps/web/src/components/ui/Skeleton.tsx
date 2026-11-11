import React from 'react';

interface SkeletonProps {
  className?: string;
  rows?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = 'h-4 w-full', rows = 1 }) => {
  return (
    <div aria-busy="true" aria-live="polite" className="space-y-2.5 animate-pulse">
      {Array.from({ length: rows }).map((_, idx) => (
        <div
          key={idx}
          className={`bg-slate-200/80 dark:bg-slate-800 rounded-md ${className}`}
        />
      ))}
    </div>
  );
};

export const KPISkeletonRow: React.FC = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 h-28 space-y-3"
        >
          <div className="h-3 w-24 bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="h-7 w-32 bg-slate-300 dark:bg-slate-700 rounded" />
          <div className="h-3 w-40 bg-slate-200 dark:bg-slate-800 rounded" />
        </div>
      ))}
    </div>
  );
};
