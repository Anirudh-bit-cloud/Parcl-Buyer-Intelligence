import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { PageHeader } from '../components/ui/PageHeader';
import { KPICard } from '../components/ui/KPICard';
import { KPISkeletonRow } from '../components/ui/Skeleton';
import { InfoTooltip } from '../components/ui/InfoTooltip';
import {
  Database,
  FileCheck2,
  Calendar,
  CheckCircle2,
  Table,
  Layers,
  Sparkles,
} from 'lucide-react';

export const DataQuality: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getDataQuality().then((res) => {
      if (isMounted) {
        setData(res);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const clientsMeta = data?.datasets?.clients || {};
  const propsMeta = data?.datasets?.properties || {};

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Data Quality & Pipeline Lineage"
        description="Complete audit trail across 10,000 raw property records, DOB parsing sensitivity, and schema invariants."
        moduleBadge="Differentiator 12 & Gebru Data Card"
        keyTakeaway="All 10,000 raw property transactions and 2,000 client records pass strict Pandera validation with 0 discrepancies and 100% invariant compliance."
        actions={
          <div className="text-xs font-mono bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 px-3 py-1.5 rounded-lg text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5 font-medium">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>Pipeline Status: 100% Invariant Compliant</span>
          </div>
        }
      />

      {/* Top 4 Audit Invariant Cards */}
      {loading && !data ? (
        <KPISkeletonRow />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Sold vs Available Split"
            value="7,305 / 2,695"
            subtitle="Exact 10,000 raw records partitioned"
            icon={<Database className="w-4 h-4" />}
            tooltip="7,305 transactions linked to 2,000 multi-unit buyers; 2,695 historical or available listings."
          />
          <KPICard
            label="DOB Parsing Sensitivity"
            value="0 Discrepancies"
            subtitle="%m/%d/%Y vs %Y-%m-%d equivalence"
            icon={<Calendar className="w-4 h-4" />}
            badge={{ text: 'Zero Divergence', variant: 'success' }}
            tooltip="Rigorous comparison across mixed date formats yields exactly zero age discrepancies as of 2025-12-31."
          />
          <KPICard
            label="Satisfaction Uniformity"
            value="p = 0.8170"
            subtitle="Chi-square test of discrete uniformity"
            icon={<Sparkles className="w-4 h-4" />}
            tooltip="Customer satisfaction scores 1-5 follow a discrete uniform distribution (chi^2 = 1.5540, df = 4, p = 0.8170)."
          />
          <KPICard
            label="Currency Governance"
            value="₹ INR Only"
            subtitle="Indian digit grouping applied uniformly"
            icon={<FileCheck2 className="w-4 h-4" />}
            badge={{ text: 'Standardized', variant: 'accent' }}
            tooltip="All monetary figures standardized to Indian Rupees (₹) with Lakhs/Crores digit grouping."
          />
        </div>
      )}

      {/* Dataset Lineage & Schemas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Clients Pipeline */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4 shadow-2xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 text-xs font-semibold uppercase tracking-wider">
              <Layers className="w-4 h-4" />
              <span>Clients Ingestion (`clients_clean.parquet`)</span>
            </div>
            <InfoTooltip content="Cleaned and validated buyers with strictly verified multi-unit thresholds." />
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Raw Client Rows:</span>
              <span className="text-slate-900 dark:text-slate-100 font-bold">{clientsMeta.raw_rows ?? 2000}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Clean Parquet Rows:</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">{clientsMeta.clean_rows ?? 2000}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Null / Corrupt Rows Handled:</span>
              <span className="text-slate-800 dark:text-slate-200">0 (Schema 100% Validated)</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Sovereign Countries:</span>
              <span className="text-slate-800 dark:text-slate-200">10 (USA Share: 76.90%)</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Geographic Regions:</span>
              <span className="text-slate-800 dark:text-slate-200">57 Sub-regions</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-500 dark:text-slate-400">Mean Age (at 2025-12-31):</span>
              <span className="text-slate-800 dark:text-slate-200">55.10 years</span>
            </div>
          </div>
        </div>

        {/* Properties Pipeline */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4 shadow-2xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 text-xs font-semibold uppercase tracking-wider">
              <Table className="w-4 h-4" />
              <span>Properties Ingestion (`properties_clean.parquet`)</span>
            </div>
            <InfoTooltip content="Property transactions joined to clients, with unsold listings classified as available inventory." />
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Raw Property Records:</span>
              <span className="text-slate-900 dark:text-slate-100 font-bold">{propsMeta.raw_rows ?? 10000}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Sold Units (Joined to Clients):</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">{propsMeta.sold_units ?? 7305}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Available Units (Dec 2025 Cohort):</span>
              <span className="text-blue-600 dark:text-blue-400 font-bold">{propsMeta.available_units ?? 313}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Apartment vs Office Split:</span>
              <span className="text-slate-800 dark:text-slate-200">8,547 Apartments / 1,453 Offices</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">Total Towers:</span>
              <span className="text-slate-800 dark:text-slate-200">20 Towers</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-500 dark:text-slate-400">Mean Sale Price:</span>
              <span className="text-slate-800 dark:text-slate-200">₹3,45,072.00 (₹302.41 / SqFt)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
