import React, { useEffect, useState } from 'react';
import { Filter, RotateCcw, Globe, User, Home, MapPin } from 'lucide-react';
import { useFilterStore } from '../../stores/filterStore';
import { api } from '../../api/client';

export const FilterBar: React.FC = () => {
  const {
    country,
    region,
    acquisition_purpose,
    client_type,
    setCountry,
    setRegion,
    setAcquisitionPurpose,
    setClientType,
    resetFilters,
  } = useFilterStore();

  const [countriesList, setCountriesList] = useState<string[]>([]);
  const [regionMap, setRegionMap] = useState<Record<string, string[]>>({});

  useEffect(() => {
    let isMounted = true;
    api.getMetaFilters().then((meta: any) => {
      if (isMounted && meta) {
        const rawCountries = meta.countries || [];
        const cList: string[] = rawCountries.map((c: any) =>
          typeof c === 'string' ? c : c.value || c.display_label
        );
        setCountriesList(
          cList.length
            ? cList
            : ['USA', 'UK', 'Canada', 'Germany', 'France', 'Belgium', 'Mexico', 'Australia', 'Russia', 'Denmark']
        );

        if (meta.regions_by_country) {
          setRegionMap(meta.regions_by_country);
        } else if (meta.regions) {
          const rList = meta.regions.map((r: any) => (typeof r === 'string' ? r : r.value));
          setRegionMap({ USA: rList });
        }
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const availableRegions = country && regionMap[country] ? regionMap[country] : [];
  const activeCount = [country, region, acquisition_purpose, client_type].filter(Boolean).length;

  return (
    <div className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 md:px-6 py-2 flex flex-wrap items-center justify-between gap-2.5 text-xs sticky top-14 z-30 transition-colors">
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400 font-medium mr-1">
          <Filter className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
          <span>Filters:</span>
          {activeCount > 0 && (
            <span className="bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-mono text-[10px] px-1.5 py-0.2 rounded-full border border-blue-200 dark:border-blue-800">
              {activeCount} active
            </span>
          )}
        </div>

        {/* Country Selector */}
        <div className="flex items-center gap-1 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded px-2 py-1 shadow-2xs">
          <Globe className="w-3 h-3 text-slate-400" />
          <select
            value={country || ''}
            onChange={(e) => setCountry(e.target.value)}
            className="bg-transparent text-slate-800 dark:text-slate-200 outline-none cursor-pointer pr-1"
            aria-label="Filter by Country"
          >
            <option value="" className="bg-white dark:bg-slate-900 text-slate-500">All Countries (10)</option>
            {countriesList.map((c) => (
              <option key={c} value={c} className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200">
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* Region Selector (Cascade) */}
        <div className="flex items-center gap-1 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded px-2 py-1 shadow-2xs">
          <MapPin className="w-3 h-3 text-slate-400" />
          <select
            value={region || ''}
            onChange={(e) => setRegion(e.target.value)}
            disabled={!country || availableRegions.length === 0}
            className="bg-transparent text-slate-800 dark:text-slate-200 outline-none cursor-pointer disabled:text-slate-400 dark:disabled:text-slate-600 disabled:cursor-not-allowed pr-1"
            aria-label="Filter by Region"
          >
            <option value="" className="bg-white dark:bg-slate-900 text-slate-500">
              {!country ? 'Select Country First' : 'All Regions'}
            </option>
            {availableRegions.map((r) => (
              <option key={r} value={r} className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200">
                {r}
              </option>
            ))}
          </select>
        </div>

        {/* Acquisition Purpose */}
        <div className="flex items-center gap-1 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded px-2 py-1 shadow-2xs">
          <Home className="w-3 h-3 text-slate-400" />
          <select
            value={acquisition_purpose || ''}
            onChange={(e) => setAcquisitionPurpose(e.target.value as 'HOME' | 'INVESTMENT' | '')}
            className="bg-transparent text-slate-800 dark:text-slate-200 outline-none cursor-pointer pr-1"
            aria-label="Filter by Acquisition Purpose"
          >
            <option value="" className="bg-white dark:bg-slate-900 text-slate-500">All Purposes</option>
            <option value="HOME" className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200">Home (69.25%)</option>
            <option value="INVESTMENT" className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200">Investment (30.75%)</option>
          </select>
        </div>

        {/* Client Type */}
        <div className="flex items-center gap-1 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded px-2 py-1 shadow-2xs">
          <User className="w-3 h-3 text-slate-400" />
          <select
            value={client_type || ''}
            onChange={(e) => setClientType(e.target.value as 'INDIVIDUAL' | 'COMPANY' | '')}
            className="bg-transparent text-slate-800 dark:text-slate-200 outline-none cursor-pointer pr-1"
            aria-label="Filter by Client Type"
          >
            <option value="" className="bg-white dark:bg-slate-900 text-slate-500">All Types</option>
            <option value="INDIVIDUAL" className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200">Individual (94.85%)</option>
            <option value="COMPANY" className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200">Company (5.15%)</option>
          </select>
        </div>

        {/* Reset Button */}
        {activeCount > 0 && (
          <button
            onClick={resetFilters}
            className="flex items-center gap-1 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white px-2 py-1 rounded bg-slate-200/80 dark:bg-slate-800 hover:bg-slate-300 transition-colors"
            title="Reset all filters"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset</span>
          </button>
        )}
      </div>

      <div className="text-[11px] font-mono text-slate-500 dark:text-slate-400 flex items-center gap-2">
        <span>As of Dec 2025</span>
        <span>•</span>
        <span className="text-emerald-600 dark:text-emerald-400 font-semibold">₹ INR Only</span>
      </div>
    </div>
  );
};
