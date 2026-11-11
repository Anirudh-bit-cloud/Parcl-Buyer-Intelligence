import React from 'react';
import { InfoTooltip } from './InfoTooltip';

interface KPICardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  tooltip?: string;
  badge?: {
    text: string;
    variant?: 'default' | 'success' | 'warning' | 'accent';
  };
}

export const KPICard: React.FC<KPICardProps> = ({
  label,
  value,
  subtitle,
  icon,
  tooltip,
  badge,
}) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
        <span className="text-xs font-medium flex items-center">
          {label}
          {tooltip && <InfoTooltip content={tooltip} term={label} />}
        </span>
        {icon && (
          <div className="p-1.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-2 flex items-baseline justify-between gap-2">
        <div className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50 tabular-nums">
          {value}
        </div>
        {badge && (
          <span
            className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-medium ${
              badge.variant === 'success'
                ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400'
                : badge.variant === 'warning'
                ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400'
                : badge.variant === 'accent'
                ? 'bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400'
                : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
            }`}
          >
            {badge.text}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400 truncate">
          {subtitle}
        </p>
      )}
    </div>
  );
};
