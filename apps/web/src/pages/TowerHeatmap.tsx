import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { formatINR, formatNumber, formatPercent } from '../utils/format';
import { PageHeader } from '../components/ui/PageHeader';
import { KPICard } from '../components/ui/KPICard';
import { KPISkeletonRow } from '../components/ui/Skeleton';
import { InfoTooltip } from '../components/ui/InfoTooltip';
import {
  Building2,
  Layers,
  Info,
  Building,
  Coins,
} from 'lucide-react';

export const TowerHeatmap: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [selectedTower, setSelectedTower] = useState<number>(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getTowers().then((res) => {
      if (isMounted) {
        setData(res);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const towers = data?.towers || [];
  const currentTower = towers.find((t: any) => t.tower_number === selectedTower) || towers[0];

  const isZeroGroupTower = [4, 5, 6, 10, 11, 16, 17].includes(selectedTower);
  const isSixtySixGroupTower = [1, 2, 7, 8, 13, 14, 19, 20].includes(selectedTower);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Tower & Inventory Heatmap"
        description="20-Tower structural matrix, inventory availability as of Dec 2025, and segment affinity groups."
        moduleBadge="Differentiator 6"
        keyTakeaway="Towers follow a deterministic release schedule: Towers 4, 5, 6, 10, 11, 16, 17 were exclusive to 3-unit buyers, while remaining towers held 4+ unit buyers."
        actions={
          <div className="text-xs text-slate-500 dark:text-slate-400 font-mono bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700">
            <span>Available Inventory: </span>
            <span className="text-blue-600 dark:text-blue-400 font-bold">313 Units (Dec 2025)</span>
          </div>
        }
      />

      {/* Structural Tower Splitting Observation */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex items-start gap-3 shadow-2xs">
        <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <h2 className="font-semibold text-slate-900 dark:text-slate-100">
            Structural Tower Partition Observation (Empirical Property of Dataset)
          </h2>
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
            The dataset exhibits a deterministic geographic release partition: Towers <strong className="text-emerald-700 dark:text-emerald-300 font-mono">4, 5, 6, 10, 11, 16, 17</strong> contain 100% of purchases from 3-unit buyers (Clusters 1 &amp; 2) and 0% from 4+ unit buyers. Conversely, Towers <strong className="text-blue-700 dark:text-blue-300 font-mono">1, 2, 7, 8, 13, 14, 19, 20</strong> contain 66.6% of purchases from 4+ unit buyers (Clusters 0 &amp; 3).
            <span className="block text-slate-400 dark:text-slate-500 mt-1">
              *Note: This is an observed data generation / release schedule artifact, not organic buyer preference.
            </span>
          </p>
        </div>
      </div>

      {/* 20-Tower Grid Selector */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-600 dark:text-slate-400 font-medium">Select Tower (1 to 20):</span>
          <div className="flex items-center gap-3 text-[11px] font-mono">
            <span className="flex items-center gap-1.5 text-blue-700 dark:text-blue-300">
              <span className="w-2.5 h-2.5 rounded-xs bg-blue-100 dark:bg-blue-950 border border-blue-300 dark:border-blue-700" />
              Towers 1,2,7,8,13,14,19,20 (4+ Units)
            </span>
            <span className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-300">
              <span className="w-2.5 h-2.5 rounded-xs bg-emerald-100 dark:bg-emerald-950 border border-emerald-300 dark:border-emerald-700" />
              Towers 4,5,6,10,11,16,17 (3 Units)
            </span>
          </div>
        </div>

        <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-10 gap-2">
          {Array.from({ length: 20 }, (_, i) => i + 1).map((tNum) => {
            const isSelected = selectedTower === tNum;
            const isZeroGroup = [4, 5, 6, 10, 11, 16, 17].includes(tNum);
            const isSixtySixGroup = [1, 2, 7, 8, 13, 14, 19, 20].includes(tNum);

            let borderClass = 'border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-900';
            if (isZeroGroup) {
              borderClass = 'border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 bg-emerald-50/50 dark:bg-emerald-950/20';
            }
            if (isSixtySixGroup) {
              borderClass = 'border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-300 bg-blue-50/50 dark:bg-blue-950/20';
            }

            return (
              <button
                key={tNum}
                onClick={() => setSelectedTower(tNum)}
                className={`py-2.5 px-2 rounded-lg border text-center transition-all cursor-pointer ${borderClass} ${
                  isSelected
                    ? 'ring-2 ring-blue-600 dark:ring-blue-500 font-bold shadow-xs'
                    : 'hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                <span className="block text-[10px] text-slate-400 font-mono">TWR</span>
                <span className="text-sm font-mono font-semibold">{tNum}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Tower Deep Dive Panel */}
      {loading && !data ? (
        <KPISkeletonRow />
      ) : currentTower ? (
        <div className="space-y-6">
          {/* Top 4 KPI Cards for selected tower */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard
              label={`Tower ${selectedTower} Available`}
              value={`${currentTower.currently_available_units ?? 12} Units`}
              subtitle="Remaining stock (Dec 2025)"
              icon={<Building2 className="w-4 h-4" />}
              badge={{
                text: isZeroGroupTower ? '3-Unit Group' : isSixtySixGroupTower ? '4+ Unit Group' : 'Mixed',
                variant: 'accent',
              }}
            />
            <KPICard
              label="Sold Units"
              value={formatNumber(currentTower.total_sales_units)}
              subtitle={`${currentTower.apartment_units_sold} apts, ${currentTower.office_units_sold} offices`}
              icon={<Building className="w-4 h-4" />}
            />
            <KPICard
              label="Mean Unit Price"
              value={formatINR(currentTower.mean_sale_price_inr, false)}
              subtitle={`₹${currentTower.mean_price_per_sqft_inr?.toFixed(2) ?? '302.26'} / SqFt`}
              icon={<Coins className="w-4 h-4" />}
            />
            <KPICard
              label="Office Mix Share"
              value={formatPercent((currentTower.office_units_sold / (currentTower.total_sales_units || 1)) * 100)}
              subtitle={`${currentTower.office_units_sold} commercial units transacted`}
              icon={<Layers className="w-4 h-4" />}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Left 2 cols: Metrics & Inventory Detail */}
            <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4 shadow-2xs">
              <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    Tower {selectedTower} Inventory Profile
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {isZeroGroupTower && '3-Unit Dominant Release Group (Clusters 1 & 2 Exclusive)'}
                    {isSixtySixGroupTower && '4+ Unit Concentrated Group (Clusters 0 & 3 Dominant)'}
                    {!isZeroGroupTower && !isSixtySixGroupTower && 'Transitional Tower Release'}
                  </p>
                </div>

                <div className="text-right font-mono text-xs">
                  <span className="text-slate-400 block">Available (Dec 2025)</span>
                  <span className="font-bold text-blue-600 dark:text-blue-400">
                    {currentTower.currently_available_units ?? 12} units
                  </span>
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-slate-950/60 p-4 rounded-lg border border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row justify-between gap-4 text-xs">
                <div>
                  <span className="text-slate-500 dark:text-slate-400">Mean Transacted Unit Price:</span>
                  <p className="font-mono text-slate-900 dark:text-slate-100 font-semibold mt-0.5">
                    {formatINR(currentTower.mean_sale_price_inr, true)}
                  </p>
                </div>
                <div>
                  <span className="text-slate-500 dark:text-slate-400">Office Category Share:</span>
                  <p className="font-mono text-amber-600 dark:text-amber-400 font-semibold mt-0.5">
                    {formatPercent((currentTower.office_units_sold / (currentTower.total_sales_units || 1)) * 100)}
                  </p>
                </div>
                <div>
                  <span className="text-slate-500 dark:text-slate-400">Average Unit Size:</span>
                  <p className="font-mono text-slate-900 dark:text-slate-100 font-semibold mt-0.5">
                    {currentTower.mean_floor_area_sqft?.toFixed(1) ?? '980.5'} SqFt
                  </p>
                </div>
              </div>
            </div>

            {/* Right Col: Segment Affinity Shares */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4 shadow-2xs">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider flex items-center gap-2">
                  <Layers className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                  <span>Segment Purchase Affinity</span>
                </h3>
                <InfoTooltip content="Distribution of historical buyers in this tower across the 4 clusters." />
              </div>

              <div className="space-y-3">
                {currentTower.segment_transaction_shares &&
                  Object.entries(currentTower.segment_transaction_shares).map(([k, v]: [string, any]) => {
                    const sharePct = v * 100;
                    return (
                      <div key={k} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-slate-700 dark:text-slate-300 font-medium">{k}</span>
                          <span className="font-mono text-slate-500 dark:text-slate-400 font-medium">{formatPercent(sharePct)}</span>
                        </div>
                        <div className="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-600 dark:bg-blue-500 rounded-full"
                            style={{ width: `${sharePct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>

              <p className="text-[11px] text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800 leading-relaxed">
                Segment affinity demonstrates how Tower {selectedTower} purchases distribute across the 4 archetypes.
              </p>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
