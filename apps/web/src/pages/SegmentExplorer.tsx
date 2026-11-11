import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { formatINR, formatNumber, formatPercent } from '../utils/format';
import { PageHeader } from '../components/ui/PageHeader';
import { KPICard } from '../components/ui/KPICard';
import { Badge } from '../components/ui/Badge';
import { InfoTooltip } from '../components/ui/InfoTooltip';
import { ChartCard } from '../components/ui/ChartCard';
import { tokens } from '../design/tokens';
import {
  Users,
  Building,
  Layers,
  GitBranch,
  Calendar,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export const SegmentExplorer: React.FC = () => {
  const [catalog, setCatalog] = useState<any>(null);
  const [selectedCluster, setSelectedCluster] = useState<number>(0);
  const [, setDetailData] = useState<any>(null);

  useEffect(() => {
    let isMounted = true;
    api.getSegments().then((res) => {
      if (isMounted) {
        setCatalog(res);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    api.getSegmentDetail(selectedCluster).then((res) => {
      if (isMounted) {
        setDetailData(res);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [selectedCluster]);

  const segments = catalog?.segments || [];
  const currentSegment =
    segments.find((s: any) => s.segment_id === selectedCluster) || segments[0];

  const comparisonData = segments.map((s: any) => ({
    name: `Cluster ${s.segment_id}`,
    units: Number(s.mean_units.toFixed(2)),
    office_pct: Number(s.commercial_office_share_pct.toFixed(1)),
    age: Number(s.mean_age.toFixed(1)),
  }));

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Segment Persona Explorer"
        description="Empirical profiling of 4 buyer archetypes derived from 84 behavioural and geographic features."
        moduleBadge="Model B3 Grounded"
        keyTakeaway="The 4 clusters cleanly separate high-volume accumulators from single-tower residential and office buyers using unit counts, age, and office share."
        actions={
          <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
            <span className="text-xs text-slate-500 dark:text-slate-400 px-2 font-medium">Cluster:</span>
            {[0, 1, 2, 3].map((cid) => (
              <button
                key={cid}
                onClick={() => setSelectedCluster(cid)}
                className={`px-2.5 py-1 rounded text-xs font-mono font-medium transition-colors cursor-pointer ${
                  selectedCluster === cid
                    ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-2xs font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                C{cid}
              </button>
            ))}
          </div>
        }
      />

      {/* 4 Segment Quick Selection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {segments.map((seg: any) => {
          const sid = seg.segment_id as 0 | 1 | 2 | 3;
          const isSelected = selectedCluster === sid;
          const badgeVariant = (`cluster-${sid}`) as any;

          return (
            <button
              key={sid}
              onClick={() => setSelectedCluster(sid)}
              className={`text-left p-4 rounded-xl border transition-all flex flex-col justify-between cursor-pointer ${
                isSelected
                  ? 'bg-blue-50/40 dark:bg-blue-950/20 border-blue-600 dark:border-blue-500 ring-1 ring-blue-500/30 shadow-xs'
                  : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 shadow-2xs'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Badge variant={badgeVariant}>Cluster {sid}</Badge>
                  <span className="text-xs font-mono text-slate-500 dark:text-slate-400 font-medium">
                    {formatPercent(seg.population_share_pct)}
                  </span>
                </div>
                <h3 className="text-xs font-semibold text-slate-900 dark:text-slate-100 leading-snug">
                  {seg.segment_name}
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                  {seg.persona_label}
                </p>
              </div>

              <div className="mt-3.5 pt-2.5 border-t border-slate-100 dark:border-slate-800 grid grid-cols-2 gap-2 text-[11px]">
                <div>
                  <span className="text-slate-400 block">Units</span>
                  <span className="font-mono text-slate-800 dark:text-slate-200 font-medium">
                    {seg.mean_units.toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Office Share</span>
                  <span className="font-mono text-slate-800 dark:text-slate-200 font-medium">
                    {formatPercent(seg.commercial_office_share_pct)}
                  </span>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Segment Details & Comparative Chart */}
      {currentSegment && (
        <div className="space-y-6">
          {/* KPI Row (Max 4 Cards) for Selected Segment */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard
              label="Segment Buyers"
              value={formatNumber(currentSegment.buyer_count)}
              subtitle={`${formatPercent(currentSegment.population_share_pct)} of cohort population`}
              icon={<Users className="w-4 h-4" />}
              badge={{
                text: `Cluster ${selectedCluster}`,
                variant: 'accent',
              }}
            />
            <KPICard
              label="Mean Property Units"
              value={currentSegment.mean_units.toFixed(2)}
              subtitle={`${currentSegment.total_units} total purchased units`}
              icon={<Building className="w-4 h-4" />}
            />
            <KPICard
              label="Office Portfolio Share"
              value={formatPercent(currentSegment.commercial_office_share_pct)}
              subtitle={currentSegment.commercial_office_share_pct > 0.05 ? 'Diversified commercial' : 'Pure residential'}
              icon={<Layers className="w-4 h-4" />}
            />
            <KPICard
              label="Spatial Concentration (HHI)"
              value={currentSegment.towers_hhi.toFixed(4)}
              subtitle="Tower distribution index"
              icon={<Calendar className="w-4 h-4" />}
              tooltip="Herfindahl-Hirschman Index across towers (0 to 1). Values near 1.0 indicate concentration in a single tower; lower values indicate multi-tower spread."
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Deep-Dive Card (2 Cols) */}
            <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-5 shadow-2xs">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-2.5">
                  <div
                    className="w-3.5 h-3.5 rounded-full"
                    style={{
                      backgroundColor:
                        tokens.clusters[selectedCluster as 0 | 1 | 2 | 3]?.color || '#2563eb',
                    }}
                  />
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                      Cluster {selectedCluster}: {currentSegment.segment_name}
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {currentSegment.persona_label}
                    </p>
                  </div>
                </div>

                <div className="text-right font-mono text-xs text-slate-500 dark:text-slate-400">
                  <span>Age: </span>
                  <span className="font-semibold text-slate-900 dark:text-slate-100">
                    {currentSegment.mean_age.toFixed(1)} yrs
                  </span>
                </div>
              </div>

              {/* Observed Spend Snapshot */}
              <div className="bg-slate-50 dark:bg-slate-950/50 p-4 rounded-lg border border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row justify-between gap-4">
                <div>
                  <span className="text-xs text-slate-500 dark:text-slate-400">Total Observed Spend</span>
                  <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400 font-mono mt-0.5">
                    {formatINR(currentSegment.total_spend_inr, true)}
                  </p>
                </div>
                <div>
                  <span className="text-xs text-slate-500 dark:text-slate-400">Mean Buyer Spend</span>
                  <p className="text-lg font-bold text-slate-900 dark:text-slate-100 font-mono mt-0.5">
                    {formatINR(currentSegment.mean_spend_inr, true)}
                  </p>
                </div>
                <div>
                  <span className="text-xs text-slate-500 dark:text-slate-400">Key Towers</span>
                  <p className="text-xs text-slate-700 dark:text-slate-300 font-mono mt-1">
                    {currentSegment.top_towers?.slice(0, 5).join(', ')}...
                  </p>
                </div>
              </div>

              {/* Surrogate Decision Rules */}
              <div className="space-y-2">
                <div className="flex items-center gap-1.5 text-blue-600 dark:text-blue-400 text-xs font-semibold uppercase tracking-wider">
                  <GitBranch className="w-3.5 h-3.5" />
                  <span>Surrogate Decision Tree Rule (Reproducibility & Explainability)</span>
                  <InfoTooltip content="Interpretable surrogate decision tree fitted on production labels to explain cluster assignments." />
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-mono text-slate-700 dark:text-slate-300 leading-relaxed">
                  {selectedCluster === 0 && (
                    <p>
                      IF <span className="font-semibold text-amber-600 dark:text-amber-400">n_units &gt; 3.5</span> AND{' '}
                      <span className="font-semibold text-blue-600 dark:text-blue-400">age &le; 56.5</span> THEN Cluster 0{' '}
                      <span className="text-slate-400">
                        (Emerging Multi-Tower Accumulators, Mean age 42.05, 4.06 units, 13.38% office)
                      </span>
                    </p>
                  )}
                  {selectedCluster === 1 && (
                    <p>
                      IF <span className="font-semibold text-amber-600 dark:text-amber-400">n_units &le; 3.5</span> AND{' '}
                      <span className="font-semibold text-blue-600 dark:text-blue-400">office_share &le; 0.01</span> THEN Cluster 1{' '}
                      <span className="text-slate-400">
                        (Concentrated Residential Buyers, Mean age 54.11, exactly 3.00 units, 0.00% office)
                      </span>
                    </p>
                  )}
                  {selectedCluster === 2 && (
                    <p>
                      IF <span className="font-semibold text-amber-600 dark:text-amber-400">n_units &le; 3.5</span> AND{' '}
                      <span className="font-semibold text-blue-600 dark:text-blue-400">office_share &gt; 0.01</span> THEN Cluster 2{' '}
                      <span className="text-slate-400">
                        (Commercial Office Diversifiers, Mean age 55.19, exactly 3.00 units, 37.78% office)
                      </span>
                    </p>
                  )}
                  {selectedCluster === 3 && (
                    <p>
                      IF <span className="font-semibold text-amber-600 dark:text-amber-400">n_units &gt; 3.5</span> AND{' '}
                      <span className="font-semibold text-blue-600 dark:text-blue-400">age &gt; 56.5</span> THEN Cluster 3{' '}
                      <span className="text-slate-400">
                        (Established Senior Estate Investors, Mean age 69.21, 4.39 units, 14.13% office)
                      </span>
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Right: Comparative Multi-Cluster Chart (1 Col) */}
            <ChartCard
              title="Segment Comparison"
              icon={<Layers className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
              action={<span className="text-xs text-slate-400 font-mono">4 Clusters</span>}
              footer={
                <div className="space-y-1.5 font-mono">
                  <div className="flex justify-between">
                    <span>Model Feature Count:</span>
                    <span className="text-slate-800 dark:text-slate-200 font-semibold">84 Features</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="flex items-center">
                      Cluster Separation:
                      <InfoTooltip content="Macro silhouette coefficient measuring compactness and separation." />
                    </span>
                    <span className="text-slate-800 dark:text-slate-200 font-semibold">0.1211</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="flex items-center">
                      Temperature (&beta;):
                      <InfoTooltip content="Temperature calibration parameter for softmax probability scaling." />
                    </span>
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold">&beta; = 1.12</span>
                  </div>
                </div>
              }
            >
              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.6} />
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} tickLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        borderColor: '#334155',
                        borderRadius: '0.375rem',
                        color: '#f8fafc',
                        fontSize: '11px',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                    <Bar dataKey="units" name="Mean Units" fill="#0284c7" radius={[3, 3, 0, 0]} />
                    <Bar dataKey="office_pct" name="Office %" fill="#d97706" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>
          </div>
        </div>
      )}
    </div>
  );
};
