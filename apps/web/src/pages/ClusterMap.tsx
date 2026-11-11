import React, { useEffect, useState, useMemo } from 'react';
import { api } from '../api/client';
import { formatINR, formatPercent } from '../utils/format';
import { PageHeader } from '../components/ui/PageHeader';
import { KPICard } from '../components/ui/KPICard';
import { KPISkeletonRow } from '../components/ui/Skeleton';
import { InfoTooltip } from '../components/ui/InfoTooltip';
import { tokens } from '../design/tokens';
import { ChartCard } from '../components/ui/ChartCard';
import {
  ScatterChart as ScatterIcon,
  Search,
  Info,
  Maximize2,
  Activity,
  Layers,
} from 'lucide-react';

export const ClusterMap: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [selectedClusterFilter, setSelectedClusterFilter] = useState<number | 'ALL'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [hoveredPoint, setHoveredPoint] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getProjection().then((res) => {
      if (isMounted) {
        setData(res);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const points = data?.points || [];

  const bounds = useMemo(() => {
    if (!points.length) return { minX: -5, maxX: 5, minY: -5, maxY: 5 };
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    points.forEach((p: any) => {
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    });
    const dx = (maxX - minX) * 0.05;
    const dy = (maxY - minY) * 0.05;
    return { minX: minX - dx, maxX: maxX + dx, minY: minY - dy, maxY: maxY + dy };
  }, [points]);

  const filteredPoints = useMemo(() => {
    return points.filter((p: any) => {
      const matchCluster = selectedClusterFilter === 'ALL' || p.assigned_cluster === selectedClusterFilter;
      const matchSearch = !searchQuery || p.client_id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCluster && matchSearch;
    });
  }, [points, selectedClusterFilter, searchQuery]);

  const svgWidth = 800;
  const svgHeight = 440;

  const scaleX = (x: number) => {
    return ((x - bounds.minX) / (bounds.maxX - bounds.minX)) * (svgWidth - 60) + 30;
  };

  const scaleY = (y: number) => {
    return svgHeight - (((y - bounds.minY) / (bounds.maxY - bounds.minY)) * (svgHeight - 60) + 30);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="2D Cluster Manifold Projection"
        description="Visual projection of 2,000 buyers in reduced continuous feature space with cluster centroid separation."
        moduleBadge="PCA Projection"
        keyTakeaway="Principal Component 1 and 2 capture 55.70% of feature variance, validating the geometric separation of all 4 buyer archetypes."
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-1 text-xs shadow-2xs">
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search Client ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-slate-800 dark:text-slate-200 outline-none w-32 placeholder-slate-400 font-mono text-xs"
              />
            </div>

            <div className="flex bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-0.5 text-xs">
              <button
                onClick={() => setSelectedClusterFilter('ALL')}
                className={`px-2 py-1 rounded font-medium transition-colors cursor-pointer ${
                  selectedClusterFilter === 'ALL'
                    ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-2xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                All (2,000)
              </button>
              {[0, 1, 2, 3].map((cid) => (
                <button
                  key={cid}
                  onClick={() => setSelectedClusterFilter(cid)}
                  className={`px-2 py-1 rounded font-mono transition-colors cursor-pointer ${
                    selectedClusterFilter === cid
                      ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-2xs font-semibold'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  C{cid}
                </button>
              ))}
            </div>
          </div>
        }
      />

      {/* Top 4 KPI Cards */}
      {loading && !data ? (
        <KPISkeletonRow />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Separation Score"
            value="0.1211"
            subtitle="Silhouette score across 4 clusters"
            icon={<Activity className="w-4 h-4" />}
            tooltip="Silhouette coefficient measuring compactness within clusters versus distance to nearest neighboring cluster."
            badge={{ text: 'Model B3', variant: 'accent' }}
          />
          <KPICard
            label="Explained Variance (PC1+2)"
            value="55.70%"
            subtitle="PC1: 36.19% · PC2: 19.51%"
            icon={<Maximize2 className="w-4 h-4" />}
            tooltip="Percentage of total feature variance retained by the first two principal components."
          />
          <KPICard
            label="Reduced Feature Space"
            value="84 → 2 Dims"
            subtitle="StandardScaler + SVD projection"
            icon={<Layers className="w-4 h-4" />}
          />
          <KPICard
            label="Projected Points"
            value={filteredPoints.length.toLocaleString()}
            subtitle={`Showing ${filteredPoints.length} of ${points.length} points`}
            icon={<ScatterIcon className="w-4 h-4" />}
          />
        </div>
      )}

      {/* Main Scatter View & Tooltip Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        {/* Scatter View */}
        <div className="lg:col-span-3">
          <ChartCard
            title="2D Cluster Manifold Projection (StandardScaler + PCA)"
            subtitle="84 Features Projected onto 2 Principal Components"
            tooltip="2-dimensional orthogonal projection preserving 55.70% of cumulative cohort feature variance."
            action={
              <span className="font-mono text-xs text-slate-400">
                {filteredPoints.length} of {points.length} points
              </span>
            }
            footer={
              <div className="w-full flex flex-wrap justify-between items-center text-xs text-slate-500 dark:text-slate-400 font-mono gap-2">
                <div className="flex items-center gap-4 text-[11px]">
                  {[0, 1, 2, 3].map((cid) => (
                    <div key={cid} className="flex items-center gap-1.5">
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{
                          backgroundColor:
                            tokens.clusters[cid as 0 | 1 | 2 | 3]?.color || '#2563eb',
                        }}
                      />
                      <span>Cluster {cid}</span>
                    </div>
                  ))}
                </div>
                <span>PC1 (36.19%) · PC2 (19.51%)</span>
              </div>
            }
          >
            <div className="w-full overflow-x-auto flex justify-center py-2">
              <svg
                viewBox={`0 0 ${svgWidth} ${svgHeight}`}
                className="w-full max-w-[800px] h-[440px] bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 cursor-crosshair"
              >
                <line x1="30" y1={svgHeight / 2} x2={svgWidth - 30} y2={svgHeight / 2} stroke="#cbd5e1" strokeDasharray="3" opacity="0.6" />
                <line x1={svgWidth / 2} y1="30" x2={svgWidth / 2} y2={svgHeight - 30} stroke="#cbd5e1" strokeDasharray="3" opacity="0.6" />

                {filteredPoints.map((p: any) => {
                  const cx = scaleX(p.x);
                  const cy = scaleY(p.y);
                  const clusterInfo = tokens.clusters[p.assigned_cluster as 0 | 1 | 2 | 3] || tokens.clusters[0];
                  const color = clusterInfo.color;
                  const isHovered = hoveredPoint?.client_id === p.client_id;
                  const isSearched = searchQuery && p.client_id.toLowerCase().includes(searchQuery.toLowerCase());

                  return (
                    <circle
                      key={p.client_id}
                      cx={cx}
                      cy={cy}
                      r={isSearched ? 6 : isHovered ? 5 : 2.5}
                      fill={color}
                      opacity={isHovered || isSearched ? 1 : 0.8}
                      stroke={isHovered || isSearched ? '#0f172a' : 'none'}
                      strokeWidth={isHovered || isSearched ? 1.5 : 0}
                      onMouseEnter={() => setHoveredPoint(p)}
                      className="transition-all cursor-pointer"
                    />
                  );
                })}
              </svg>
            </div>
          </ChartCard>
        </div>

        {/* Hover / Selected Client Inspector Panel */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4 flex flex-col justify-between shadow-2xs">
          <div>
            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
              <Info className="w-4 h-4" />
              <span>Client Inspector</span>
            </div>

            {hoveredPoint ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center pb-2 border-b border-slate-200 dark:border-slate-800">
                  <span className="text-base font-bold text-slate-900 dark:text-slate-100 font-mono">
                    {hoveredPoint.client_id}
                  </span>
                  <span
                    className="text-[10px] font-mono px-2 py-0.5 rounded border font-semibold"
                    style={{
                      borderColor: tokens.clusters[hoveredPoint.assigned_cluster as 0 | 1 | 2 | 3]?.color,
                      color: tokens.clusters[hoveredPoint.assigned_cluster as 0 | 1 | 2 | 3]?.color,
                    }}
                  >
                    Cluster {hoveredPoint.assigned_cluster}
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Archetype</span>
                    <p className="text-slate-800 dark:text-slate-200 font-medium">
                      {hoveredPoint.assigned_segment_name}
                    </p>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                    <span className="text-slate-500 dark:text-slate-400">Total Spend</span>
                    <span className="font-mono text-emerald-600 dark:text-emerald-400 font-semibold">
                      {hoveredPoint.total_spend_display || formatINR(hoveredPoint.total_spend_inr, true)}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                    <span className="text-slate-500 dark:text-slate-400">Units Held</span>
                    <span className="font-mono text-slate-800 dark:text-slate-200 font-semibold">
                      {hoveredPoint.n_units} units
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                    <span className="text-slate-500 dark:text-slate-400">Buyer Age</span>
                    <span className="font-mono text-slate-800 dark:text-slate-200 font-semibold">
                      {hoveredPoint.age} yrs
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                    <span className="text-slate-500 dark:text-slate-400">Office Category Share</span>
                    <span className="font-mono text-slate-800 dark:text-slate-200 font-semibold">
                      {formatPercent((hoveredPoint.office_share || 0) * 100)}
                    </span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500 dark:text-slate-400">Coordinates</span>
                    <span className="font-mono text-slate-400 text-[10px]">
                      ({hoveredPoint.x.toFixed(2)}, {hoveredPoint.y.toFixed(2)})
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-10 text-slate-400 text-xs">
                <ScatterIcon className="w-8 h-8 text-slate-300 dark:text-slate-600 mx-auto mb-2 opacity-50" />
                <p>Hover over any coordinate point in the manifold to inspect buyer attributes.</p>
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400 leading-relaxed">
            StandardScaler + SVD projection on Model B3 feature matrix (84 dimensions).
          </div>
        </div>
      </div>
    </div>
  );
};
