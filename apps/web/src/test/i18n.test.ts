import { describe, it, expect } from 'vitest';
import { TRANSLATIONS } from '../utils/i18n';
import { SupportedLocale } from '../stores/currencyStore';

describe('Enterprise Internationalization & RTL Localization Suite', () => {
  const locales: SupportedLocale[] = ['en', 'hi', 'de', 'ar'];
  const requiredKeys = [
    'overview',
    'segments',
    'clients',
    'inventory',
    'campaigns',
    'behavior',
    'geo',
    'towers',
    'modelLab',
    'dataQuality',
    'admin',
    'exportBoardPack',
    'relabeledNotice',
    'totalSpend',
    'totalClients',
    'availableUnits',
    'totalTowers',
  ];

  it.each(locales)('locale "%s" contains all required core UI keys', (loc) => {
    const dict = TRANSLATIONS[loc];
    expect(dict).toBeDefined();
    for (const key of requiredKeys) {
      expect(dict[key], `Missing key "${key}" in locale "${loc}"`).toBeDefined();
      expect(dict[key].trim().length).toBeGreaterThan(0);
    }
  });

  it('Arabic dictionary contains right-to-left localized text strings', () => {
    const ar = TRANSLATIONS.ar;
    expect(ar.overview).toContain('نظرة');
    expect(ar.admin).toContain('الإدارية');
  });

  it('Hindi dictionary contains Devanagari script strings', () => {
    const hi = TRANSLATIONS.hi;
    expect(hi.overview).toContain('कार्यकारी');
    expect(hi.totalSpend).toContain('पोर्टफोलियो');
  });

  it('German dictionary contains valid German translations', () => {
    const de = TRANSLATIONS.de;
    expect(de.overview).toBe('Vorstandsübersicht');
    expect(de.admin).toBe('Admin-Konsole');
  });
});
