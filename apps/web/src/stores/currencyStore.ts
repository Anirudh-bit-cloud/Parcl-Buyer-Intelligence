import { create } from 'zustand';

export type CurrencyCode = 'INR' | 'USD' | 'EUR';
export type GroupingStyle = 'indian' | 'international';
export type SupportedLocale = 'en' | 'hi' | 'de' | 'ar';

interface CurrencyState {
  currency: CurrencyCode;
  applyFxConversion: boolean;
  fxRateUsdToInr: number;
  fxRateEurToInr: number;
  grouping: GroupingStyle;
  locale: SupportedLocale;
  setCurrency: (currency: CurrencyCode) => void;
  setApplyFxConversion: (apply: boolean) => void;
  setGrouping: (grouping: GroupingStyle) => void;
  setLocale: (locale: SupportedLocale) => void;
}

const getStored = <T>(key: string, fallback: T): T => {
  try {
    if (typeof window !== 'undefined' && typeof window.localStorage?.getItem === 'function') {
      const val = window.localStorage.getItem(key);
      if (val !== null) return JSON.parse(val);
    }
  } catch {
    // fallback
  }
  return fallback;
};

const setStored = (key: string, val: unknown) => {
  try {
    if (typeof window !== 'undefined' && typeof window.localStorage?.setItem === 'function') {
      window.localStorage.setItem(key, JSON.stringify(val));
    }
  } catch {
    // ignore
  }
};

const applyRTL = (locale: SupportedLocale) => {
  if (typeof document === 'undefined') return;
  if (locale === 'ar') {
    document.documentElement.setAttribute('dir', 'rtl');
    document.documentElement.setAttribute('lang', 'ar');
  } else {
    document.documentElement.setAttribute('dir', 'ltr');
    document.documentElement.setAttribute('lang', locale);
  }
};

export const useCurrencyStore = create<CurrencyState>((set) => ({
  currency: getStored<CurrencyCode>('parcl_currency', 'INR'),
  applyFxConversion: getStored<boolean>('parcl_apply_fx', false),
  fxRateUsdToInr: 83.50,
  fxRateEurToInr: 90.20,
  grouping: getStored<GroupingStyle>('parcl_grouping', 'indian'),
  locale: getStored<SupportedLocale>('parcl_locale', 'en'),

  setCurrency: (currency) => {
    setStored('parcl_currency', currency);
    set({ currency });
  },

  setApplyFxConversion: (applyFxConversion) => {
    setStored('parcl_apply_fx', applyFxConversion);
    set({ applyFxConversion });
  },

  setGrouping: (grouping) => {
    setStored('parcl_grouping', grouping);
    set({ grouping });
  },

  setLocale: (locale) => {
    setStored('parcl_locale', locale);
    applyRTL(locale);
    set({ locale });
  },
}));
