import React from 'react';
import { AlertCircle, ArrowRightLeft } from 'lucide-react';
import { useCurrencyStore } from '../../stores/currencyStore';
import { useTranslation } from '../../utils/i18n';

export const CurrencyNoticeBanner: React.FC = () => {
  const { currency, applyFxConversion, setApplyFxConversion } = useCurrencyStore();
  const { t } = useTranslation();

  if (currency !== 'INR' || applyFxConversion) {
    return null;
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className="bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-200 px-4 py-2.5 rounded-lg flex flex-wrap items-center justify-between gap-3 text-xs mb-4 print:hidden"
    >
      <div className="flex items-center gap-2">
        <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" aria-hidden="true" />
        <span className="font-medium">
          {t('relabeledNotice')}
        </span>
      </div>
      <button
        onClick={() => setApplyFxConversion(true)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-900 dark:text-amber-100 font-medium transition-colors cursor-pointer"
      >
        <ArrowRightLeft className="w-3.5 h-3.5" aria-hidden="true" />
        {t('applyFx')}
      </button>
    </div>
  );
};
