import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Shield,
  UserCheck,
  Search,
  Sun,
  Moon,
  Database,
  WifiOff,
  Printer,
  Globe,
  DollarSign,
  Palette,
  Bookmark,
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useThemeStore } from '../../stores/themeStore';
import { useDatasetStore } from '../../stores/datasetStore';
import { useFilterStore } from '../../stores/filterStore';
import { useSavedViewsStore } from '../../stores/savedViewsStore';
import { useCurrencyStore, SupportedLocale, CurrencyCode, GroupingStyle } from '../../stores/currencyStore';
import { useTranslation } from '../../utils/i18n';
import { PALETTES, PaletteKey } from '../../design/tokens';

interface TopBarProps {
  onOpenCommandPalette: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onOpenCommandPalette }) => {
  const { role, setRole, fetchDemoToken } = useAuthStore();
  const { theme, toggleTheme, setTheme, palette, setPalette } = useThemeStore();
  const { activeDataset, isOffline } = useDatasetStore();
  const { setAllFilters } = useFilterStore();
  const { savedViews, activeViewId, loadView } = useSavedViewsStore();
  const {
    currency,
    setCurrency,
    applyFxConversion,
    setApplyFxConversion,
    grouping,
    setGrouping,
    locale,
    setLocale,
  } = useCurrencyStore();
  const { t } = useTranslation();

  const [showConfigModal, setShowConfigModal] = useState(false);

  useEffect(() => {
    fetchDemoToken(role);
  }, [role, fetchDemoToken]);

  const toggleRole = () => {
    const newRole = role === 'analyst' ? 'admin' : 'analyst';
    setRole(newRole);
    fetchDemoToken(newRole);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <>
      <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md sticky top-0 z-40 px-4 md:px-6 flex items-center justify-between transition-colors print:hidden">
        {/* Brand & Title */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-xs">
            P
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-semibold text-slate-900 dark:text-slate-100 text-xs tracking-tight">
                PARCL BUYER INTELLIGENCE
              </h1>
              <span className="text-[10px] font-mono uppercase bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                Model B3
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 hidden sm:block">
              Enterprise Client Segmentation & Allocation
            </p>
          </div>
        </div>

        {/* Center Search / Command Palette shortcut */}
        <div className="flex items-center gap-2">
          <button
            onClick={onOpenCommandPalette}
            className="hidden md:flex items-center gap-2 px-3 py-1.5 text-xs text-slate-500 dark:text-slate-400 bg-slate-100/80 dark:bg-slate-800/80 hover:bg-slate-200/60 dark:hover:bg-slate-750 border border-slate-200 dark:border-slate-700 rounded-md transition-colors"
            aria-label="Open command palette (Ctrl+K)"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Search navigation, clients, modules...</span>
            <kbd className="font-mono text-[10px] bg-white dark:bg-slate-900 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700 text-slate-500">
              ⌘K
            </kbd>
          </button>

          {/* Saved Views Selector */}
          <div className="hidden xl:flex items-center gap-1.5 bg-slate-100/80 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-md px-2.5 py-1 text-xs">
            <Bookmark className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
            <select
              value={activeViewId || ''}
              onChange={(e) => {
                const filters = loadView(e.target.value);
                if (filters) setAllFilters(filters);
              }}
              className="bg-transparent border-none text-xs text-slate-700 dark:text-slate-300 focus:outline-none cursor-pointer"
              aria-label="Saved views selector"
            >
              <option value="" disabled>Saved Views...</option>
              {savedViews.map((v) => (
                <option key={v.id} value={v.id} className="dark:bg-slate-900 text-slate-800 dark:text-slate-200">
                  {v.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-2 sm:gap-2.5">
          {/* Export Board Pack Print Button */}
          <button
            onClick={handlePrint}
            className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-md border border-slate-200 dark:border-slate-700 transition-colors"
            title="Export high-resolution Board Pack (PDF)"
            aria-label="Export Board Pack (PDF)"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>{t('exportBoardPack')}</span>
          </button>

          {/* Currency / i18n Config Button */}
          <button
            onClick={() => setShowConfigModal(true)}
            className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md border border-slate-200 dark:border-slate-700 transition-colors"
            title="Configure Currency, FX rate, and Language"
            aria-label="Localization and Currency Settings"
          >
            <Globe className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
            <span className="font-mono uppercase text-[11px] font-semibold">{currency}</span>
            <span className="text-[10px] text-slate-400 uppercase">({locale})</span>
          </button>

          {/* Offline Badge */}
          {isOffline && (
            <div
              className="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-medium bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800"
              title="Backend is unreachable. Displaying cached verified snapshot."
              aria-label="Offline mode active"
            >
              <WifiOff className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Offline Mode</span>
            </div>
          )}

          {/* Dataset Badge (Click to open Data Source page) */}
          <Link
            to="/data"
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium border transition-colors cursor-pointer hover:border-blue-500 hover:shadow-2xs ${
              activeDataset === 'sample'
                ? 'bg-amber-50 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300 border-amber-200 dark:border-amber-800'
                : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700'
            }`}
            title={`Active: ${activeDataset === 'sample' ? 'Sample (200 buyers)' : 'Production (2,000 buyers)'}. Click to switch datasets or upload CSV in Data Source.`}
            aria-label={activeDataset === 'sample' ? 'Using sample data. Click to manage.' : 'Using production data. Click to manage.'}
          >
            <Database className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
            <span className="hidden sm:inline">
              {activeDataset === 'sample' ? 'Sample (200)' : 'Production (2,000)'}
            </span>
            <span className="sm:hidden">
              {activeDataset === 'sample' ? 'Sample' : 'Prod'}
            </span>
          </Link>

          {/* Theme Toggle (Light / Dark) */}
          <button
            onClick={toggleTheme}
            className="p-1.5 rounded-md text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-300 dark:border-slate-700 transition-colors shadow-2xs cursor-pointer"
            aria-label={`Current theme: ${theme}. Click to switch.`}
            title={theme === 'dark' ? 'Current theme: Dark. Click to switch to Light mode' : 'Current theme: Light. Click to switch to Dark mode'}
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-slate-700" />
            )}
          </button>

          {/* Role Toggle */}
          <button
            onClick={toggleRole}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border transition-colors ${
              role === 'admin'
                ? 'bg-amber-50 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300 border-amber-200 dark:border-amber-800 hover:bg-amber-100'
                : 'bg-blue-50 text-blue-800 dark:bg-blue-950/50 dark:text-blue-300 border-blue-200 dark:border-blue-800 hover:bg-blue-100'
            }`}
            title="Click to toggle between Analyst (masked PII) and Admin (unmasked PII & export)"
            aria-label={`Current role: ${role}. Click to switch.`}
          >
            {role === 'admin' ? (
              <>
                <Shield className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                <span className="hidden sm:inline">Admin</span>
                <span className="text-[10px] font-mono uppercase text-amber-600 dark:text-amber-400">(Unmasked)</span>
              </>
            ) : (
              <>
                <UserCheck className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                <span className="hidden sm:inline">Analyst</span>
                <span className="text-[10px] font-mono uppercase text-blue-600 dark:text-blue-400">(Masked)</span>
              </>
            )}
          </button>
        </div>
      </header>

      {/* Localization, Currency & Palettes Settings Dialog */}
      {showConfigModal && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 print:hidden"
        >
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl max-w-md w-full p-6 text-slate-900 dark:text-slate-100">
            <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
              <Globe className="w-4 h-4 text-blue-600" />
              Enterprise Localization & Display Settings
            </h2>

            {/* Currency Selector */}
            <div className="mb-4">
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5">
                Accounting Currency
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['INR', 'USD', 'EUR'] as CurrencyCode[]).map((c) => (
                  <button
                    key={c}
                    onClick={() => setCurrency(c)}
                    className={`py-1.5 px-3 rounded-lg text-xs font-semibold border transition-colors ${
                      currency === c
                        ? 'bg-blue-50 dark:bg-blue-950/60 border-blue-500 text-blue-600 dark:text-blue-300'
                        : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    {c === 'INR' ? '₹ INR' : c === 'USD' ? '$ USD' : '€ EUR'}
                  </button>
                ))}
              </div>
            </div>

            {/* FX Conversion Toggle */}
            <div className="mb-4 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs font-medium">Mathematical FX Conversion</div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">
                    Apply configured conversion rates (as of 2026-11-10: ₹83.50/USD, ₹90.20/EUR)
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={applyFxConversion}
                  onChange={(e) => setApplyFxConversion(e.target.checked)}
                  className="rounded text-blue-600 focus:ring-blue-500 w-4 h-4"
                />
              </div>
            </div>

            {/* Number Grouping */}
            <div className="mb-4">
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5">
                Number Grouping
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setGrouping('indian')}
                  className={`py-1.5 px-3 rounded-lg text-xs font-medium border transition-colors ${
                    grouping === 'indian'
                      ? 'bg-blue-50 dark:bg-blue-950/60 border-blue-500 text-blue-600 dark:text-blue-300'
                      : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'
                  }`}
                >
                  Indian (Lakh/Crore)
                </button>
                <button
                  onClick={() => setGrouping('international')}
                  className={`py-1.5 px-3 rounded-lg text-xs font-medium border transition-colors ${
                    grouping === 'international'
                      ? 'bg-blue-50 dark:bg-blue-950/60 border-blue-500 text-blue-600 dark:text-blue-300'
                      : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'
                  }`}
                >
                  International (M / B)
                </button>
              </div>
            </div>

            {/* Language Selector */}
            <div className="mb-4">
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5">
                Language
              </label>
              <div className="grid grid-cols-4 gap-2">
                {[
                  { code: 'en' as SupportedLocale, name: 'English' },
                  { code: 'hi' as SupportedLocale, name: 'हिन्दी' },
                  { code: 'de' as SupportedLocale, name: 'Deutsch' },
                  { code: 'ar' as SupportedLocale, name: 'العربية' },
                ].map((l) => (
                  <button
                    key={l.code}
                    onClick={() => setLocale(l.code)}
                    className={`py-1.5 px-2 rounded-lg text-xs font-medium border text-center transition-colors ${
                      locale === l.code
                        ? 'bg-blue-50 dark:bg-blue-950/60 border-blue-500 text-blue-600 dark:text-blue-300'
                        : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    {l.name}
                  </button>
                ))}
              </div>
              <div className="text-[10px] text-slate-400 dark:text-slate-500 mt-1.5 italic">
                * Non-English locales (hi, de, ar) are machine-translated, pending native linguistic review.
              </div>
            </div>

            {/* Theme Mode Selector */}
            <div className="mb-4">
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Sun className="w-3.5 h-3.5 text-slate-400" />
                Color Theme Mode
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { key: 'light' as const, label: 'Light' },
                  { key: 'dark' as const, label: 'Dark' },
                  { key: 'high-contrast' as const, label: 'High Contrast' },
                ].map((th) => (
                  <button
                    key={th.key}
                    type="button"
                    onClick={() => setTheme(th.key)}
                    className={`py-1.5 px-2 rounded-lg text-xs font-medium border text-center transition-colors ${
                      theme === th.key
                        ? 'bg-blue-50 dark:bg-blue-950/60 border-blue-500 text-blue-600 dark:text-blue-300 font-semibold'
                        : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    {th.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Data-Viz Palette */}
            <div className="mb-6">
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Palette className="w-3.5 h-3.5 text-slate-400" />
                Data-Viz Color Palette (8 Palettes)
              </label>
              <select
                value={palette}
                onChange={(e) => setPalette(e.target.value as PaletteKey)}
                className="w-full text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2 text-slate-900 dark:text-slate-100"
              >
                {Object.entries(PALETTES).map(([k, p]) => (
                  <option key={k} value={k}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={() => setShowConfigModal(false)}
              className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors"
            >
              Apply & Close
            </button>
          </div>
        </div>
      )}
    </>
  );
};
