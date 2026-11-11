import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { formatINR, formatNumber, formatPercent, CLUSTER_NAMES } from '../utils/format';
import { PageHeader } from '../components/ui/PageHeader';
import { KPICard } from '../components/ui/KPICard';
import { KPISkeletonRow } from '../components/ui/Skeleton';
import { InfoTooltip } from '../components/ui/InfoTooltip';
import { DataTable, Column } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import {
  Target,
  Building,
  Search,
  Sparkles,
  Layers,
  CheckCircle2,
  HelpCircle,
} from 'lucide-react';

export const OpportunityFinder: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'SEGMENT' | 'CLIENT'>('SEGMENT');

  // Segment Tab State
  const [selectedSegment, setSelectedSegment] = useState<number>(2); // Default to Cluster 2
  const [selectedCategory, setSelectedCategory] = useState<string>('Office');
  const [segmentOppData, setSegmentOppData] = useState<any>(null);

  // Client NBO Tab State
  const [clientIdInput, setClientIdInput] = useState<string>('C0001');
  const [clientNboData, setClientNboData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getOpportunities(selectedSegment, selectedCategory).then((res) => {
      if (isMounted) {
        setSegmentOppData(res);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [selectedSegment, selectedCategory]);

  useEffect(() => {
    let isMounted = true;
    api.getClientRecommendations(clientIdInput).then((res) => {
      if (isMounted) {
        setClientNboData(res);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [clientIdInput]);

  const oppUnits = segmentOppData?.recommendations || [];
  const nboUnits = clientNboData?.recommendations || [];

  const columns: Column<any>[] = [
    {
      key: 'listing_id',
      header: 'Listing ID',
      render: (row) => (
        <span className="font-mono font-medium text-slate-900 dark:text-slate-100">
          #{row.listing_id}
        </span>
      ),
    },
    {
      key: 'tower_number',
      header: 'Tower',
      render: (row) => `Tower ${row.tower_number}`,
    },
    {
      key: 'unit_number',
      header: 'Unit',
      render: (row) => `Unit ${row.unit_number}`,
    },
    {
      key: 'unit_category',
      header: 'Category',
      render: (row) => (
        <span
          className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
            row.unit_category === 'Office'
              ? 'bg-amber-50 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border-amber-200 dark:border-amber-800'
              : 'bg-blue-50 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-800'
          }`}
        >
          {row.unit_category}
        </span>
      ),
    },
    {
      key: 'floor_area_sqft',
      header: 'Floor Area (SqFt)',
      isNumeric: true,
      render: (row) => row.floor_area_sqft?.toFixed(2),
    },
    {
      key: 'price_per_sqft_inr',
      header: 'Price / SqFt (₹)',
      isNumeric: true,
      render: (row) => `₹${row.price_per_sqft_inr?.toFixed(2)}`,
    },
    {
      key: 'sale_price_inr',
      header: 'Sale Price (₹)',
      isNumeric: true,
      render: (row) => (
        <span className="text-emerald-600 dark:text-emerald-400 font-semibold font-mono">
          {row.sale_price_display || formatINR(row.sale_price_inr, true)}
        </span>
      ),
    },
    {
      key: 'affinity_score',
      header: 'Affinity Score',
      isNumeric: true,
      render: (row) => (
        <span className="text-blue-600 dark:text-blue-400 font-bold font-mono">
          {(row.affinity_score * 100).toFixed(1)}%
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Opportunity Finder & NBO Engine"
        description="Matching 313 available property units (as of Dec 2025) to segment archetypes and personalized client portfolios."
        moduleBadge="Differentiators 7 & 8"
        keyTakeaway="Affinity engine scores unsold properties against segment centroids and portfolio gaps, unlocking targeted Next-Best-Offer recommendations."
        actions={
          <div className="flex bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setActiveTab('SEGMENT')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-colors cursor-pointer ${
                activeTab === 'SEGMENT'
                  ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-2xs font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Target className="w-3.5 h-3.5" />
              <span>Segment Opportunity Finder</span>
            </button>
            <button
              onClick={() => setActiveTab('CLIENT')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-colors cursor-pointer ${
                activeTab === 'CLIENT'
                  ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-2xs font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Personalized NBO (Client)</span>
            </button>
          </div>
        }
      />

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Available Inventory"
          value="313 Units"
          subtitle="49 offices · 264 apartments (Dec 2025)"
          icon={<Building className="w-4 h-4" />}
          badge={{ text: 'Ready Stock', variant: 'accent' }}
        />
        <KPICard
          label="Active Target Segment"
          value={`Cluster ${selectedSegment}`}
          subtitle={CLUSTER_NAMES[selectedSegment]}
          icon={<Target className="w-4 h-4" />}
        />
        <KPICard
          label="Category Filter"
          value={selectedCategory === '' ? 'All (313)' : selectedCategory}
          subtitle="Category inventory constraint"
          icon={<Layers className="w-4 h-4" />}
        />
        <KPICard
          label="Ranked Opportunity Units"
          value={oppUnits.length.toString()}
          subtitle="Units matching affinity threshold"
          icon={<CheckCircle2 className="w-4 h-4" />}
        />
      </div>

      {/* TAB 1: SEGMENT MATCHING */}
      {activeTab === 'SEGMENT' && (
        <div className="space-y-4">
          {/* Controls Bar */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-2xs">
            {/* Segment Selector */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">Target Segment:</span>
              <div className="flex bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-0.5 text-xs">
                {[0, 1, 2, 3].map((cid) => (
                  <button
                    key={cid}
                    onClick={() => setSelectedSegment(cid)}
                    className={`px-3 py-1 rounded font-mono transition-colors cursor-pointer ${
                      selectedSegment === cid
                        ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 font-semibold shadow-2xs'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    Cluster {cid}
                  </button>
                ))}
              </div>
              <span className="text-xs text-blue-600 dark:text-blue-400 font-semibold hidden sm:inline">
                {CLUSTER_NAMES[selectedSegment]}
              </span>
            </div>

            {/* Category Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">Category:</span>
              <div className="flex bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-0.5 text-xs">
                {['', 'Apartment', 'Office'].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-2.5 py-1 rounded transition-colors cursor-pointer ${
                      selectedCategory === cat
                        ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 font-semibold shadow-2xs'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    {cat === '' ? 'All (313)' : cat === 'Office' ? 'Offices (49)' : 'Apartments (264)'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Units Table */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <h2 className="font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                Top Compatible Units for {CLUSTER_NAMES[selectedSegment]}
              </h2>
              <span className="font-mono text-slate-400">{oppUnits.length} Units Ranked</span>
            </div>

            <DataTable
              columns={columns}
              data={oppUnits}
              keyField="listing_id"
              emptyMessage="No matching units found for selected segment and category."
            />
          </div>
        </div>
      )}

      {/* TAB 2: PERSONALIZED NEXT-BEST-OFFER (CLIENT) */}
      {activeTab === 'CLIENT' && (
        <div className="space-y-5">
          {/* Client Lookup Box */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-2xs">
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">Select Client:</span>
              <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-1 text-xs">
                <Search className="w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  value={clientIdInput}
                  onChange={(e) => setClientIdInput(e.target.value.toUpperCase())}
                  placeholder="Client ID (e.g. C0001)"
                  className="bg-transparent text-slate-900 dark:text-slate-100 font-mono outline-none w-28 uppercase"
                />
              </div>
            </div>

            {clientNboData && (
              <div className="flex items-center gap-4 text-xs font-mono">
                <div className="text-slate-500 dark:text-slate-400">
                  Segment: <span className="text-blue-600 dark:text-blue-400 font-bold">{clientNboData.client_segment_name}</span>
                </div>
                <div className="text-slate-500 dark:text-slate-400">
                  Owned Towers: <span className="text-slate-800 dark:text-slate-200">[{clientNboData.owned_towers?.join(', ')}]</span>
                </div>
                <div className="text-slate-500 dark:text-slate-400">
                  Unowned Towers: <span className="text-emerald-600 dark:text-emerald-400 font-bold">{clientNboData.unowned_towers_count} of 20</span>
                </div>
              </div>
            )}
          </div>

          {/* NBO Ranking Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {nboUnits.slice(0, 6).map((unit: any, idx: number) => (
              <div
                key={unit.listing_id || idx}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-2xs"
              >
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-mono font-bold text-slate-900 dark:text-slate-100">
                      Listing #{unit.listing_id}
                    </span>
                    <Badge variant="success">Rank #{idx + 1}</Badge>
                  </div>

                  <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                    Tower {unit.tower_number} • Unit {unit.unit_number} ({unit.unit_category})
                  </h3>

                  <div className="mt-3 space-y-1.5 text-xs font-mono">
                    <div className="flex justify-between text-slate-500 dark:text-slate-400">
                      <span>Sale Price:</span>
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                        {unit.sale_price_display || formatINR(unit.sale_price_inr, true)}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-500 dark:text-slate-400">
                      <span>Floor Area:</span>
                      <span className="text-slate-800 dark:text-slate-200">{unit.floor_area_sqft?.toFixed(2)} SqFt</span>
                    </div>
                    <div className="flex justify-between text-slate-500 dark:text-slate-400">
                      <span>Price / SqFt:</span>
                      <span className="text-slate-800 dark:text-slate-200">₹{unit.price_per_sqft_inr?.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500 dark:text-slate-400">Portfolio Diversification:</span>
                    <span className="text-emerald-600 dark:text-emerald-400 font-mono text-[11px] font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      +0.15 Tower Bonus
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500 dark:text-slate-400">Composite NBO Score:</span>
                    <span className="text-blue-600 dark:text-blue-400 font-mono font-bold">
                      {unit.final_nbo_score?.toFixed(4)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 text-[11px] text-slate-500 dark:text-slate-400 font-mono">
            *NBO heuristic assumption: Unclipped composite score = segment_affinity + 0.15 tower_diversification_bonus + 0.10 category_diversification_bonus.
          </div>
        </div>
      )}
    </div>
  );
};
