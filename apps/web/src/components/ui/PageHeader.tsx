import React from 'react';
import { Sparkles } from 'lucide-react';

interface PageHeaderProps {
  title: string;
  description: string;
  moduleBadge?: string;
  keyTakeaway?: string;
  actions?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  moduleBadge,
  keyTakeaway,
  actions,
}) => {
  return (
    <div className="space-y-3 pb-5 border-b border-slate-200 dark:border-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
              {title}
            </h1>
            {moduleBadge && (
              <span className="text-[11px] font-mono px-2 py-0.5 rounded font-medium bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                {moduleBadge}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {description}
          </p>
        </div>

        {actions && <div className="flex items-center gap-2.5">{actions}</div>}
      </div>

      {keyTakeaway && (
        <div className="flex items-start gap-2 px-3.5 py-2.5 rounded-lg bg-slate-100/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300">
          <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-slate-900 dark:text-slate-100 mr-1.5">Key takeaway:</span>
            <span>{keyTakeaway}</span>
          </div>
        </div>
      )}
    </div>
  );
};
