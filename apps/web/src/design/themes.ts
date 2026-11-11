/**
 * Theme tokens and CSS variable mappings for Light (Default), Dark, and High-Contrast modes.
 * Clean, calm, professional enterprise surface and text colors meeting WCAG 2.2 AA standards, with dedicated AAA-contrast theme.
 */

export interface ThemeColors {
  // Surfaces
  bgApp: string;
  bgCard: string;
  bgCardHover: string;
  bgSidebar: string;
  bgHeader: string;
  bgSubtle: string;
  bgMuted: string;

  // Borders
  border: string;
  borderSubtle: string;
  borderFocus: string;

  // Text
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  textInverse: string;

  // Accent
  accent: string;
  accentHover: string;
  accentBg: string;
  accentBorder: string;

  // Status
  success: string;
  warning: string;
  error: string;
  info: string;
}

export const lightTheme: ThemeColors = {
  bgApp: '#f8fafc',        // slate-50
  bgCard: '#ffffff',       // pure white
  bgCardHover: '#f1f5f9',  // slate-100
  bgSidebar: '#ffffff',
  bgHeader: '#ffffff',
  bgSubtle: '#f1f5f9',
  bgMuted: '#e2e8f0',      // slate-200

  border: '#e2e8f0',       // slate-200
  borderSubtle: '#f1f5f9',
  borderFocus: '#2563eb',

  textPrimary: '#0f172a',  // slate-900
  textSecondary: '#475569',// slate-600
  textMuted: '#94a3b8',    // slate-400
  textInverse: '#ffffff',

  accent: '#2563eb',
  accentHover: '#1d4ed8',
  accentBg: '#eff6ff',
  accentBorder: '#bfdbfe',

  success: '#16a34a',
  warning: '#d97706',
  error: '#dc2626',
  info: '#2563eb',
};

export const darkTheme: ThemeColors = {
  bgApp: '#090d16',        // deep dark
  bgCard: '#0f172a',       // slate-900
  bgCardHover: '#1e293b',  // slate-800
  bgSidebar: '#0b1120',
  bgHeader: '#0f172a',
  bgSubtle: '#1e293b',
  bgMuted: '#334155',

  border: '#1e293b',       // slate-800
  borderSubtle: '#172033',
  borderFocus: '#3b82f6',

  textPrimary: '#f8fafc',  // slate-50
  textSecondary: '#94a3b8',// slate-400
  textMuted: '#64748b',    // slate-500
  textInverse: '#0f172a',

  accent: '#3b82f6',
  accentHover: '#60a5fa',
  accentBg: 'rgba(59, 130, 246, 0.12)',
  accentBorder: 'rgba(59, 130, 246, 0.3)',

  success: '#22c55e',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#38bdf8',
};

export const highContrastTheme: ThemeColors = {
  bgApp: '#000000',
  bgCard: '#000000',
  bgCardHover: '#111111',
  bgSidebar: '#000000',
  bgHeader: '#000000',
  bgSubtle: '#111111',
  bgMuted: '#222222',

  border: '#ffffff',
  borderSubtle: '#cccccc',
  borderFocus: '#ffff00',

  textPrimary: '#ffffff',
  textSecondary: '#ffffff',
  textMuted: '#dddddd',
  textInverse: '#000000',

  accent: '#ffff00',
  accentHover: '#ffff66',
  accentBg: 'rgba(255, 255, 0, 0.2)',
  accentBorder: '#ffff00',

  success: '#00ff00',
  warning: '#ffff00',
  error: '#ff3333',
  info: '#00ffff',
};
