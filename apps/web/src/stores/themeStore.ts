import { create } from 'zustand';
import { PaletteKey } from '../design/tokens';

export type Theme = 'light' | 'dark' | 'high-contrast';

interface ThemeState {
  theme: Theme;
  palette: PaletteKey;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  setPalette: (palette: PaletteKey) => void;
}

const getInitialTheme = (): Theme => {
  try {
    if (typeof window !== 'undefined' && typeof window.localStorage?.getItem === 'function') {
      const saved = window.localStorage.getItem('parcl_theme') as Theme;
      if (saved === 'dark' || saved === 'light' || saved === 'high-contrast') {
        return saved;
      }
    }
  } catch {
    // fallback in testing environments
  }
  return 'light';
};

const getInitialPalette = (): PaletteKey => {
  try {
    if (typeof window !== 'undefined' && typeof window.localStorage?.getItem === 'function') {
      const saved = window.localStorage.getItem('parcl_palette') as PaletteKey;
      if (saved) return saved;
    }
  } catch {
    // fallback
  }
  return 'okabeIto';
};

const applyThemeClasses = (theme: Theme) => {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  const body = document.body;
  root.classList.remove('dark', 'high-contrast');
  if (body) body.classList.remove('dark', 'high-contrast');

  if (theme === 'dark') {
    root.classList.add('dark');
    if (body) body.classList.add('dark');
  } else if (theme === 'high-contrast') {
    root.classList.add('dark', 'high-contrast');
    if (body) body.classList.add('dark', 'high-contrast');
  }
};

const initialTheme = getInitialTheme();
applyThemeClasses(initialTheme);

export const useThemeStore = create<ThemeState>((set) => ({
  theme: initialTheme,
  palette: getInitialPalette(),
  setTheme: (theme) => {
    try {
      if (typeof window !== 'undefined' && typeof window.localStorage?.setItem === 'function') {
        window.localStorage.setItem('parcl_theme', theme);
      }
    } catch {
      // ignore
    }
    applyThemeClasses(theme);
    set({ theme });
  },
  toggleTheme: () => {
    set((state) => {
      const next: Theme = state.theme === 'dark' ? 'light' : 'dark';
      try {
        if (typeof window !== 'undefined' && typeof window.localStorage?.setItem === 'function') {
          window.localStorage.setItem('parcl_theme', next);
        }
      } catch {
        // ignore
      }
      applyThemeClasses(next);
      return { theme: next };
    });
  },
  setPalette: (palette) => {
    try {
      if (typeof window !== 'undefined' && typeof window.localStorage?.setItem === 'function') {
        window.localStorage.setItem('parcl_palette', palette);
      }
    } catch {
      // ignore
    }
    set({ palette });
  },
}));
