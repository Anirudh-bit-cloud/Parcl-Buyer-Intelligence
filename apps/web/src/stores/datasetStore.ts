import { create } from 'zustand';

export type DatasetMode = 'full' | 'sample';

interface DatasetState {
  activeDataset: DatasetMode;
  isOffline: boolean;
  setActiveDataset: (mode: DatasetMode) => void;
  setIsOffline: (offline: boolean) => void;
  switchDataset: (mode: DatasetMode) => Promise<boolean>;
}

const getInitialDataset = (): DatasetMode => {
  try {
    if (typeof window !== 'undefined' && typeof window.localStorage?.getItem === 'function') {
      const saved = window.localStorage.getItem('parcl_dataset_mode');
      if (saved === 'sample' || saved === 'full') {
        return saved;
      }
    }
  } catch {
    // fallback
  }
  return 'full';
};

export const useDatasetStore = create<DatasetState>((set, get) => ({
  activeDataset: getInitialDataset(),
  isOffline: false,
  setActiveDataset: (mode) => {
    try {
      if (typeof window !== 'undefined' && typeof window.localStorage?.setItem === 'function') {
        window.localStorage.setItem('parcl_dataset_mode', mode);
      }
    } catch {
      // ignore
    }
    set({ activeDataset: mode });
  },
  setIsOffline: (offline) => set({ isOffline: offline }),
  switchDataset: async (mode: DatasetMode) => {
    try {
      const res = await fetch('/api/v1/datasets/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dataset: mode }),
      });
      if (res.ok) {
        get().setActiveDataset(mode);
        return true;
      }
    } catch {
      // Backend unreachable, set locally
      get().setActiveDataset(mode);
      get().setIsOffline(true);
      return true;
    }
    get().setActiveDataset(mode);
    return true;
  },
}));
