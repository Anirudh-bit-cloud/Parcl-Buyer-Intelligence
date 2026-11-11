import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';
import { FilterBar } from './FilterBar';
import { CommandPalette } from './CommandPalette';
import { CurrencyNoticeBanner } from '../ui/CurrencyNoticeBanner';
import { useDatasetStore } from '../../stores/datasetStore';
import { Database, AlertCircle } from 'lucide-react';

export const AppLayout: React.FC = () => {
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const { activeDataset, isOffline } = useDatasetStore();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      <TopBar onOpenCommandPalette={() => setIsCommandPaletteOpen(true)} />

      {/* Dataset Context Banner (Noticeable when sample dataset or offline fallback is active) */}
      {activeDataset === 'sample' && (
        <div className="bg-amber-50 dark:bg-amber-950/40 border-b border-amber-200 dark:border-amber-900/60 px-4 md:px-6 py-1.5 text-xs text-amber-800 dark:text-amber-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
            <span className="font-semibold">Active: Synthetic Sample Dataset</span>
            <span className="hidden sm:inline text-amber-700/80 dark:text-amber-300/80">
              — 200 anonymized test buyers & 500 properties. Model parameters reflect production baseline.
            </span>
          </div>
          <span className="text-[10px] font-mono uppercase bg-amber-100 dark:bg-amber-900/60 px-2 py-0.5 rounded border border-amber-300 dark:border-amber-800 font-semibold">
            Sample Mode
          </span>
        </div>
      )}

      {isOffline && (
        <div className="bg-rose-50 dark:bg-rose-950/40 border-b border-rose-200 dark:border-rose-900/60 px-4 md:px-6 py-1.5 text-xs text-rose-800 dark:text-rose-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" />
            <span className="font-semibold">Offline Snapshot Active:</span>
            <span>API backend unreachable. Using local verified sample responses.</span>
          </div>
        </div>
      )}

      <FilterBar />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-slate-50/70 dark:bg-slate-950/70">
          <CurrencyNoticeBanner />
          <Outlet />
        </main>
      </div>

      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
      />
    </div>
  );
};
