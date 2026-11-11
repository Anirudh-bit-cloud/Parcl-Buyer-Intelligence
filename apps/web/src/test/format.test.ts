import { describe, it, expect } from 'vitest';
import { formatINR, formatNumber, formatPercent } from '../utils/format';

describe('Format Utilities (Zero-Fabrication & Currency Standard)', () => {
  it('formats Indian Rupees with proper Indian digit grouping and paise', () => {
    // Standard thousands, lakhs, crores
    expect(formatINR(1260375.48, true)).toBe('₹12,60,375.48');
    expect(formatINR(2520750960.84, true)).toBe('₹2,52,07,50,960.84');
    expect(formatINR(345072.0, true)).toBe('₹3,45,072.00');
    expect(formatINR(100000.0, true)).toBe('₹1,00,000.00');
  });

  it('formats Indian Rupees without paise when requested', () => {
    expect(formatINR(2520750961, false)).toBe('₹2,52,07,50,961');
    expect(formatINR(1246765, false)).toBe('₹12,46,765');
  });

  it('handles zero, negative and null values cleanly', () => {
    expect(formatINR(0)).toBe('₹0.00');
    expect(formatINR(null)).toBe('₹0.00');
    expect(formatINR(undefined)).toBe('₹0.00');
    expect(formatINR(-50000, false)).toBe('-₹50,000');
  });

  it('formats percentages accurately', () => {
    expect(formatPercent(26.8)).toBe('26.8%');
    expect(formatPercent(27.85, 2)).toBe('27.85%');
    expect(formatPercent(0.55, 2)).toBe('0.55%');
  });

  it('formats standard integers with Indian grouping', () => {
    expect(formatNumber(2000)).toBe('2,000');
    expect(formatNumber(7305)).toBe('7,305');
  });
});


import { formatCurrencyValue, formatIndianGrouping, formatInternationalGrouping } from '../utils/format';
import { useCurrencyStore } from '../stores/currencyStore';
import { TRANSLATIONS } from '../utils/i18n';

describe('Enterprise Currency & FX Utilities (Phase 3)', () => {
  it('formats currency values with distinct symbols and international grouping', () => {
    expect(formatCurrencyValue(1234567.89, 'USD', true, 'international', false)).toBe('$1,234,567.89');
    expect(formatCurrencyValue(1234567.89, 'EUR', true, 'international', false)).toBe('€1,234,567.89');
    expect(formatCurrencyValue(1234567.89, 'INR', true, 'indian', false)).toBe('₹12,34,567.89');
  });

  it('supports mathematical FX conversion', () => {
    // 1000 USD * 83.50 FX = 83500 INR
    expect(formatCurrencyValue(1000, 'INR', false, 'indian', true, 83.50)).toBe('₹83,500');
  });

  it('verifies multilingual i18n dictionaries for en, hi, de, ar', () => {
    expect(TRANSLATIONS.en.overview).toBe('Executive Overview');
    expect(TRANSLATIONS.hi.overview).toContain('अवलोकन');
    expect(TRANSLATIONS.de.overview).toBe('Vorstandsübersicht');
    expect(TRANSLATIONS.ar.overview).toContain('التنفيذية');
  });
});
