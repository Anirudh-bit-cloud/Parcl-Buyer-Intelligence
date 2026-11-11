import React, { useState } from 'react';
import { HelpCircle } from 'lucide-react';

interface InfoTooltipProps {
  content: string;
  term?: string;
}

export const InfoTooltip: React.FC<InfoTooltipProps> = ({ content, term }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <span className="relative inline-flex items-center ml-1 align-middle">
      <button
        type="button"
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        onFocus={() => setIsOpen(true)}
        onBlur={() => setIsOpen(false)}
        className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 focus:outline-none transition-colors"
        aria-label={term ? `Learn more about ${term}` : 'Information'}
      >
        <HelpCircle className="w-3.5 h-3.5" />
      </button>

      {isOpen && (
        <span
          role="tooltip"
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-2.5 bg-slate-900 text-slate-100 dark:bg-slate-800 dark:text-slate-200 text-xs rounded-lg shadow-lg border border-slate-700/50 z-50 pointer-events-none leading-relaxed transition-opacity"
        >
          {term && <strong className="block text-blue-400 mb-0.5 font-semibold">{term}</strong>}
          {content}
        </span>
      )}
    </span>
  );
};
