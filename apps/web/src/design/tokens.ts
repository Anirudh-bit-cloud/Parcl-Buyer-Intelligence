/**
 * Design Tokens for Parcl Buyer Intelligence Platform
 * Calm, professional, data-first enterprise design tokens.
 * Single source of truth for color scales, 8 data-viz palettes, typography, spacing, and elevation.
 */

export const PALETTES = {
  okabeIto: {
    name: 'Okabe-Ito (Colorblind-Safe Default)',
    colors: ['#0284c7', '#059669', '#d97706', '#7c3aed', '#ea580c', '#0d9488', '#e11d48', '#4b5563'],
    darkColors: ['#38bdf8', '#34d399', '#fbbf24', '#a78bfa', '#fb923c', '#2dd4bf', '#f43f5e', '#9ca3af'],
  },
  tableau10: {
    name: 'Tableau 10 (Enterprise Classic)',
    colors: ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#b07aa1', '#ff9da7'],
    darkColors: ['#6ba2d6', '#f5a452', '#ea787a', '#94c9c5', '#78b96e', '#f1d56f', '#c497b7', '#ffb5bd'],
  },
  viridis: {
    name: 'Viridis (Perceptually Uniform)',
    colors: ['#440154', '#414487', '#2a788e', '#22a884', '#7ad151', '#fde725', '#35b779', '#31688e'],
    darkColors: ['#6d1f85', '#575ba8', '#388fa8', '#2ec49b', '#92dc6d', '#feeb4d', '#42c888', '#407ba3'],
  },
  plasma: {
    name: 'Plasma (High Contrast Vibrance)',
    colors: ['#0d0887', '#4b03a1', '#7d03a8', '#a82296', '#cc4778', '#e66c5c', '#f89540', '#f0f921'],
    darkColors: ['#2822a8', '#6318be', '#971bc4', '#be3bb0', '#dd5f8f', '#f28273', '#faa85f', '#f5fc51'],
  },
  coolwarm: {
    name: 'Coolwarm (Diverging Analytical)',
    colors: ['#3b4cc0', '#6788ee', '#9abbff', '#c9d7f0', '#edd1c2', '#f7a889', '#e26952', '#b40426'],
    darkColors: ['#596be2', '#839ff5', '#b3cbff', '#dbe5f7', '#f4ded3', '#f9baa2', '#ea8470', '#cf2746'],
  },
  monochrome: {
    name: 'Monochrome (Slate Density)',
    colors: ['#0f172a', '#334155', '#475569', '#64748b', '#94a3b8', '#cbd5e1', '#e2e8f0', '#f1f5f9'],
    darkColors: ['#f8fafc', '#e2e8f0', '#cbd5e1', '#94a3b8', '#64748b', '#475569', '#334155', '#1e293b'],
  },
  emeraldTech: {
    name: 'Emerald Tech (Fintech Precision)',
    colors: ['#064e3b', '#047857', '#059669', '#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5'],
    darkColors: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#047857', '#065f46', '#064e3b', '#022c22'],
  },
  oceanic: {
    name: 'Oceanic (Cobalt & Cyan Marine)',
    colors: ['#0c4a6e', '#0369a1', '#0284c7', '#0ea5e9', '#38bdf8', '#7dd3fc', '#bae6fd', '#e0f2fe'],
    darkColors: ['#38bdf8', '#7dd3fc', '#bae6fd', '#0284c7', '#0369a1', '#075985', '#0c4a6e', '#082f49'],
  },
} as const;

export type PaletteKey = keyof typeof PALETTES;

export const tokens = {
  // Brand & Single Accent Color
  accent: {
    DEFAULT: '#2563eb', // Blue 600
    hover: '#1d4ed8',   // Blue 700
    light: '#dbeafe',   // Blue 100
    subtle: '#eff6ff',  // Blue 50
    darkSubtle: 'rgba(37, 99, 235, 0.15)',
    border: '#93c5fd',  // Blue 300
  },

  // Colorblind-Safe Cluster Colors (Okabe-Ito inspired palette)
  clusters: {
    0: {
      name: 'Emerging Multi-Tower Accumulators',
      color: '#0284c7', // Sky 600 (Light) / Sky 400 (Dark)
      darkColor: '#38bdf8',
      bgLight: '#e0f2fe',
      bgDark: 'rgba(56, 189, 248, 0.12)',
      borderLight: '#bae6fd',
      borderDark: 'rgba(56, 189, 248, 0.3)',
      textLight: '#0369a1',
      textDark: '#7dd3fc',
    },
    1: {
      name: 'Concentrated Residential Buyers',
      color: '#059669', // Emerald 600 (Light) / Emerald 400 (Dark)
      darkColor: '#34d399',
      bgLight: '#d1fae5',
      bgDark: 'rgba(52, 211, 153, 0.12)',
      borderLight: '#a7f3d0',
      borderDark: 'rgba(52, 211, 153, 0.3)',
      textLight: '#047857',
      textDark: '#6ee7b7',
    },
    2: {
      name: 'Commercial Office Diversifiers',
      color: '#d97706', // Amber 600 (Light) / Amber 400 (Dark)
      darkColor: '#fbbf24',
      bgLight: '#fef3c7',
      bgDark: 'rgba(251, 191, 36, 0.12)',
      borderLight: '#fde68a',
      borderDark: 'rgba(251, 191, 36, 0.3)',
      textLight: '#b45309',
      textDark: '#fcd34d',
    },
    3: {
      name: 'Established Senior Estate Investors',
      color: '#7c3aed', // Violet 600 (Light) / Violet 400 (Dark)
      darkColor: '#a78bfa',
      bgLight: '#ede9fe',
      bgDark: 'rgba(167, 139, 250, 0.12)',
      borderLight: '#ddd6fe',
      borderDark: 'rgba(167, 139, 250, 0.3)',
      textLight: '#6d28d9',
      textDark: '#c4b5fd',
    },
  },

  // 8 Data Visualization Palettes
  palettes: PALETTES,

  // Typography Scale (Max 3 text sizes per page + Page Title)
  typography: {
    pageTitle: 'text-xl font-semibold tracking-tight',
    sectionHeader: 'text-sm font-semibold tracking-normal',
    body: 'text-sm font-normal leading-normal',
    caption: 'text-xs font-normal leading-relaxed',
    kpiValue: 'text-2xl font-semibold tracking-tight tabular-nums',
    code: 'font-mono text-xs',
  },

  // Border Radius
  radius: {
    sm: 'rounded',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-xl',
    full: 'rounded-full',
  },

  // Shadows & Elevation
  shadow: {
    card: 'shadow-sm',
    dropdown: 'shadow-md',
    modal: 'shadow-xl',
  },

  // White-Label Configuration Defaults
  whiteLabel: {
    organizationName: 'Parcl Real Estate Capital',
    brandTagline: 'Institutional Buyer Intelligence & Allocation Engine',
    primaryColor: '#2563eb',
  },
} as const;
