import { create } from 'zustand';
import { GlobalFilters } from '../types';

export interface SavedView {
  id: string;
  name: string;
  createdAt: string;
  filters: GlobalFilters;
}

interface SavedViewsState {
  savedViews: SavedView[];
  activeViewId: string | null;
  saveCurrentView: (name: string, filters: GlobalFilters) => SavedView;
  loadView: (id: string) => GlobalFilters | null;
  deleteView: (id: string) => void;
}

const STORAGE_KEY = 'parcl_saved_views_v2';

function safeGetItem(key: string): string | null {
  try {
    if (typeof window !== 'undefined' && window.localStorage && typeof window.localStorage.getItem === 'function') {
      return window.localStorage.getItem(key);
    }
  } catch (e) {
    // Ignore error in non-browser env
  }
  return null;
}

function safeSetItem(key: string, val: string): void {
  try {
    if (typeof window !== 'undefined' && window.localStorage && typeof window.localStorage.setItem === 'function') {
      window.localStorage.setItem(key, val);
    }
  } catch (e) {
    // Ignore error in non-browser env
  }
}

function loadPersistedViews(): SavedView[] {
  const raw = safeGetItem(STORAGE_KEY);
  if (raw) {
    try {
      return JSON.parse(raw);
    } catch (e) {
      // fallback
    }
  }
  return [
    {
      id: 'default-all',
      name: 'All Buyers (Unfiltered)',
      createdAt: '2026-01-01T00:00:00.000Z',
      filters: { country: '', region: '', acquisition_purpose: '', client_type: '' },
    },
    {
      id: 'us-investors',
      name: 'USA Investment Buyers',
      createdAt: '2026-01-01T00:00:00.000Z',
      filters: { country: 'USA', region: '', acquisition_purpose: 'INVESTMENT', client_type: '' },
    },
    {
      id: 'corporate-entities',
      name: 'Corporate Portfolios',
      createdAt: '2026-01-01T00:00:00.000Z',
      filters: { country: '', region: '', acquisition_purpose: '', client_type: 'COMPANY' },
    },
  ];
}

function persistViews(views: SavedView[]): void {
  safeSetItem(STORAGE_KEY, JSON.stringify(views));
}

export const useSavedViewsStore = create<SavedViewsState>((set, get) => ({
  savedViews: loadPersistedViews(),
  activeViewId: null,

  saveCurrentView: (name: string, filters: GlobalFilters) => {
    const newView: SavedView = {
      id: `view-${Date.now()}`,
      name,
      createdAt: new Date().toISOString(),
      filters: { ...filters },
    };
    const updated = [...get().savedViews, newView];
    persistViews(updated);
    set({ savedViews: updated, activeViewId: newView.id });
    return newView;
  },

  loadView: (id: string) => {
    const view = get().savedViews.find((v) => v.id === id);
    if (view) {
      set({ activeViewId: id });
      return view.filters;
    }
    return null;
  },

  deleteView: (id: string) => {
    const updated = get().savedViews.filter((v) => v.id !== id);
    persistViews(updated);
    set({
      savedViews: updated,
      activeViewId: get().activeViewId === id ? null : get().activeViewId,
    });
  },
}));
