/**
 * Enterprise Currency, Number, and Localization formatting utilities.
 * Conforms to zero-fabrication rules, Indian Rupee (₹), USD ($), EUR (€),
 * Lakh/Crore vs Million/Billion grouping, and Intl formatting.
 */

import { CurrencyCode, GroupingStyle, useCurrencyStore } from '../stores/currencyStore';

export function formatIndianGrouping(intPart: string): string {
  if (intPart.length <= 3) return intPart;
  const lastThree = intPart.substring(intPart.length - 3);
  const otherNumbers = intPart.substring(0, intPart.length - 3);
  return otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree;
}

export function formatInternationalGrouping(intPart: string): string {
  return intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

export function formatINR(val: number | null | undefined, showPaise = true): string {
  if (val === null || val === undefined || isNaN(val)) return '₹0.00';
  
  const isNegative = val < 0;
  const absVal = Math.abs(val);
  const [intPart, decPart] = absVal.toFixed(2).split('.');
  
  const formattedInt = formatIndianGrouping(intPart);
  const result = showPaise ? `₹${formattedInt}.${decPart}` : `₹${formattedInt}`;
  return isNegative ? `-${result}` : result;
}

export function formatCurrencyValue(
  val: number | null | undefined,
  currency: CurrencyCode = 'INR',
  showPaise = true,
  grouping: GroupingStyle = 'indian',
  applyConversion = false,
  fxRate = 83.50,
): string {
  if (val === null || val === undefined || isNaN(val)) {
    const symbol = currency === 'INR' ? '₹' : currency === 'USD' ? '$' : '€';
    return `${symbol}0.00`;
  }

  let finalVal = val;
  if (currency === 'INR' && applyConversion) {
    finalVal = val * fxRate;
  } else if (currency === 'USD' && applyConversion) {
    finalVal = val / fxRate;
  }

  const isNegative = finalVal < 0;
  const absVal = Math.abs(finalVal);
  const [intPart, decPart] = absVal.toFixed(2).split('.');

  const formattedInt = grouping === 'indian'
    ? formatIndianGrouping(intPart)
    : formatInternationalGrouping(intPart);

  const symbol = currency === 'INR' ? '₹' : currency === 'USD' ? '$' : '€';
  const result = showPaise ? `${symbol}${formattedInt}.${decPart}` : `${symbol}${formattedInt}`;
  return isNegative ? `-${result}` : result;
}

export function formatNumber(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return '0';
  return new Intl.NumberFormat('en-IN').format(val);
}

export function formatPercent(val: number | null | undefined, decimals = 1): string {
  if (val === null || val === undefined || isNaN(val)) return '0.0%';
  return `${val.toFixed(decimals)}%`;
}

export const CLUSTER_NAMES: Record<number, string> = {
  0: 'Emerging Multi-Tower Accumulators',
  1: 'Concentrated Residential Buyers',
  2: 'Commercial Office Diversifiers',
  3: 'Established Senior Estate Investors',
};

export const CLUSTER_COLORS: Record<number, string> = {
  0: '#38bdf8', // Sky 400
  1: '#34d399', // Emerald 400
  2: '#fbbf24', // Amber 400
  3: '#a78bfa', // Purple 400
};

export const CLUSTER_BG_COLORS: Record<number, string> = {
  0: 'bg-sky-500/10 border-sky-500/30 text-sky-300',
  1: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
  2: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
  3: 'bg-purple-500/10 border-purple-500/30 text-purple-300',
};
