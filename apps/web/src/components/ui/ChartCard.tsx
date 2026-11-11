import React from 'react';
import { Badge, type BadgeVariant } from './Badge';
import { InfoTooltip } from './InfoTooltip';
import { Skeleton } from './Skeleton';

export interface ChartCardProps {
  title: string;
  subtitle?: string;
  description?: string;
  tooltip?: string;
  badge?: {
    text: string;
    variant?: BadgeVariant;
  };
  icon?: React.ReactNode;
  action?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  loading?: boolean;
  minHeight?: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({
  title,
  subtitle,
  description,
  tooltip,
  badge,
  icon,
  action,
  footer,
  children,
  className = '',
  loading = false,
  minHeight = 'min-h-[260px]',
}) => {
  return (
    <div
      className={`bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-2xs flex flex-col justify-between transition-colors ${className}`}
      data-testid="chart-card"
    >
      <div>
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-start gap-2.5">
            {icon && (
              <div className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-blue-600 dark:text-blue-400 mt-0.5">
                {icon}
              </div>
            )}
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 leading-tight">
                  {title}
                </h3>
                {tooltip && <InfoTooltip content={tooltip} />}
                {badge && (
                  <Badge variant={badge.variant || 'default'} size="sm">
                    {badge.text}
                  </Badge>
                )}
              </div>
              {subtitle && (
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-mono">
                  {subtitle}
                </p>
              )}
              {description && (
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                  {description}
                </p>
              )}
            </div>
          </div>

          {action && <div className="flex items-center gap-2 shrink-0">{action}</div>}
        </div>

        {/* Chart Canvas Area */}
        <div className={`w-full ${minHeight} flex flex-col justify-center`}>
          {loading ? (
            <div className="space-y-3 w-full py-4">
              <Skeleton className="h-44 w-full rounded-lg" />
              <div className="flex justify-between">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-3 w-20" />
              </div>
            </div>
          ) : (
            children
          )}
        </div>
      </div>

      {/* Optional Card Footer */}
      {footer && (
        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
          {footer}
        </div>
      )}
    </div>
  );
};
