import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { formatINR, formatNumber, formatPercent } from '../utils/format';
import { useAuthStore } from '../stores/authStore';
import { PageHeader } from '../components/ui/PageHeader';
import { KPICard } from '../components/ui/KPICard';
import { KPISkeletonRow } from '../components/ui/Skeleton';
import { InfoTooltip } from '../components/ui/InfoTooltip';
import { DataTable, Column } from '../components/ui/DataTable';
import { VirtualizedClientTable } from '../components/ui/VirtualizedClientTable';
import { Badge } from '../components/ui/Badge';
import { tokens } from '../design/tokens';
import {
  Search,
  User,
  Shield,
  X,
  PlayCircle,
  Building,
  CheckCircle2,
} from 'lucide-react';

export const ClientLookup: React.FC = () => {
  const [clients, setClients] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClient, setSelectedClient] = useState<any | null>(null);
  const [clientDetail, setClientDetail] = useState<any | null>(null);
  const [isPredictModalOpen, setIsPredictModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const { role } = useAuthStore();

  // Predict Form State
  const [predictAge, setPredictAge] = useState<number>(45);
  const [predictCountry, setPredictCountry] = useState<string>('USA');
  const [predictRegion, setPredictRegion] = useState<string>('California');
  const [predictPurpose, setPredictPurpose] = useState<string>('INVESTMENT');
  const [predictChannel, setPredictChannel] = useState<string>('Website');
  const [predictUnits, setPredictUnits] = useState<number>(4);
  const [predictionResult, setPredictionResult] = useState<any | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getClients(1, 50, searchQuery).then((res) => {
      if (isMounted) {
        setClients(res.clients || []);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [searchQuery]);

  useEffect(() => {
    let isMounted = true;
    if (selectedClient) {
      api.getClientDetail(selectedClient.client_id).then((res) => {
        if (isMounted) setClientDetail(res);
      });
    }
    return () => {
      isMounted = false;
    };
  }, [selectedClient]);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsPredicting(true);
    try {
      const res = await api.predictSegment({
        age: predictAge,
        country: predictCountry,
        region: predictRegion,
        acquisition_purpose: predictPurpose,
        referral_channel: predictChannel,
        n_units: predictUnits,
      });
      setPredictionResult(res);
    } finally {
      setIsPredicting(false);
    }
  };

  const columns: Column<any>[] = [
    {
      key: 'client_id',
      header: 'Client ID',
      render: (c) => {
        const clusterInfo = tokens.clusters[c.assigned_cluster as 0 | 1 | 2 | 3] || tokens.clusters[0];
        return (
          <span className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-mono">
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: clusterInfo.color }} />
            {c.client_id}
          </span>
        );
      },
    },
    {
      key: 'name',
      header: 'Name',
      render: (c) => {
        const nameDisplay = role === 'admin'
          ? `${c.first_name || 'Kareem'} ${c.last_name || 'Liu'}`
          : `${c.first_name || 'K***'} ${c.last_name || 'L***'}`;
        return <span className="font-sans text-slate-800 dark:text-slate-200">{nameDisplay}</span>;
      },
    },
    {
      key: 'country',
      header: 'Jurisdiction',
      render: (c) => (
        <span className="text-slate-500 dark:text-slate-400">
          {c.country} ({c.region})
        </span>
      ),
    },
    {
      key: 'age',
      header: 'Age',
      isNumeric: true,
      render: (c) => c.age,
    },
    {
      key: 'n_units',
      header: 'Units',
      isNumeric: true,
      render: (c) => <span className="font-bold text-slate-900 dark:text-slate-100">{c.n_units}</span>,
    },
    {
      key: 'total_spend_inr',
      header: 'Total Spend (₹)',
      isNumeric: true,
      render: (c) => (
        <span className="text-emerald-600 dark:text-emerald-400 font-semibold font-mono">
          {c.total_spend_display || formatINR(c.total_spend_inr, true)}
        </span>
      ),
    },
    {
      key: 'assigned_segment',
      header: 'Assigned Segment',
      render: (c) => {
        const badgeVariant = (`cluster-${c.assigned_cluster}`) as any;
        return (
          <Badge variant={badgeVariant}>
            C{c.assigned_cluster}: {c.assigned_segment_name}
          </Badge>
        );
      },
    },
    {
      key: 'top_soft_probability',
      header: 'Confidence (p_max)',
      isNumeric: true,
      render: (c) => (
        <span className="text-blue-600 dark:text-blue-400 font-medium font-mono">
          {(c.top_soft_probability * 100).toFixed(1)}%
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Action',
      align: 'center',
      render: () => (
        <span className="text-blue-600 dark:text-blue-400 hover:underline font-medium cursor-pointer">
          Inspect &rarr;
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Client Intelligence & Live Scoring"
        description="Search 2,000 buyers, inspect portfolio transactions, boundary margins, and run live inference scoring."
        moduleBadge="Differentiators 10 & 19"
        keyTakeaway="Role-based PII governance automatically masks sensitive personal details for Analysts while preserving full transaction auditing for Admins."
        actions={
          <button
            onClick={() => setIsPredictModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition-colors shadow-2xs cursor-pointer"
          >
            <PlayCircle className="w-3.5 h-3.5" />
            <span>Live Segment Scoring Modal</span>
          </button>
        }
      />

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Cohort Directory"
          value={formatNumber(2000)}
          subtitle="Multi-unit buyers indexed"
          icon={<User className="w-4 h-4" />}
          badge={{ text: '2,000 Cohort', variant: 'accent' }}
        />
        <KPICard
          label="Role-Based PII Masking"
          value={role === 'admin' ? 'Unmasked (Admin)' : 'Masked (Analyst)'}
          subtitle={role === 'admin' ? 'Full names & exports visible' : 'Names & PII anonymized'}
          icon={<Shield className="w-4 h-4" />}
          badge={{
            text: role === 'admin' ? 'Full Access' : 'Protected',
            variant: role === 'admin' ? 'warning' : 'success',
          }}
          tooltip="Analyst role masks names (e.g. K*** L***). Admin role unlocks full client identity."
        />
        <KPICard
          label="Loaded Directory Rows"
          value={`${clients.length} Records`}
          subtitle={searchQuery ? `Filtered by "${searchQuery}"` : 'First 50 displayed'}
          icon={<Search className="w-4 h-4" />}
        />
        <KPICard
          label="Inference Scoring Standard"
          value="Model B3 Softmax"
          subtitle="Temperature beta = 1.12"
          icon={<PlayCircle className="w-4 h-4" />}
          tooltip="Temperature-scaled membership score (beta = 1.12)."
        />
      </div>

      {/* Search & Role Filter Bar */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-2xs">
        <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-xs w-full max-w-sm">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by Client ID (e.g. C0001) or Name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-transparent text-slate-900 dark:text-slate-100 outline-none w-full placeholder-slate-400 font-mono text-xs"
          />
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 font-mono text-xs">
            <span>Access Mode:</span>
            <Badge variant={role === 'admin' ? 'warning' : 'accent'}>
              {role === 'admin' ? 'Admin (Unmasked PII)' : 'Analyst (Masked PII)'}
            </Badge>
          </div>
        </div>
      </div>

      {/* Clients Table */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-xs">
          <h2 className="font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider">
            Client Directory ({clients.length} matching)
          </h2>
          <span className="font-mono text-slate-400 text-xs">Showing First 50 Records</span>
        </div>

        {loading ? (
          <KPISkeletonRow />
        ) : (
          <VirtualizedClientTable
            data={clients}
            onSelectClient={(id) => {
              const found = clients.find((c) => c.client_id === id);
              if (found) setSelectedClient(found);
            }}
            selectedClientId={selectedClient?.client_id}
          />
        )}
      </div>

      {/* Client Detail Modal */}
      {selectedClient && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 dark:bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-in fade-in zoom-in-95 duration-100">
            <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{
                    backgroundColor:
                      tokens.clusters[selectedClient.assigned_cluster as 0 | 1 | 2 | 3]?.color || '#2563eb',
                  }}
                />
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 font-mono flex items-center gap-2">
                    Client {selectedClient.client_id}
                    <span className="text-xs font-sans text-slate-500 dark:text-slate-400">
                      ({role === 'admin' ? `${selectedClient.first_name} ${selectedClient.last_name}` : 'PII Masked'})
                    </span>
                  </h3>
                  <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                    {selectedClient.assigned_segment_name}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedClient(null)}
                className="p-1 text-slate-400 hover:text-slate-700 dark:hover:text-white rounded cursor-pointer"
                aria-label="Close client detail modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-5 space-y-5">
              {/* Profile Summary */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                <div className="bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Age</span>
                  <span className="text-sm font-bold text-slate-900 dark:text-slate-100">{selectedClient.age} yrs</span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Total Units</span>
                  <span className="text-sm font-bold text-slate-900 dark:text-slate-100">{selectedClient.n_units} units</span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Total Spend</span>
                  <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                    {selectedClient.total_spend_display || formatINR(selectedClient.total_spend_inr, true)}
                  </span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Referral Channel</span>
                  <span className="text-sm font-bold text-blue-600 dark:text-blue-400">{selectedClient.referral_channel}</span>
                </div>
              </div>

              {/* Softmax Probabilities & Ambiguity Callout */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                    Softmax Segment Probabilities (beta = 1.12)
                  </span>
                  {clientDetail && (
                    <Badge variant={clientDetail.is_ambiguous_margin ? 'warning' : 'success'}>
                      {clientDetail.is_ambiguous_margin ? 'Ambiguous Margin (<0.10)' : 'Clear Margin'}
                    </Badge>
                  )}
                </div>

                {clientDetail?.soft_membership_probabilities && (
                  <div className="grid grid-cols-4 gap-2 text-xs font-mono text-center">
                    {Object.entries(clientDetail.soft_membership_probabilities).map(([k, v]: [string, any]) => (
                      <div key={k} className="p-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
                        <span className="text-[10px] text-slate-400 block">{k}</span>
                        <span className="text-xs text-slate-900 dark:text-slate-100 font-bold">{(v * 100).toFixed(2)}%</span>
                      </div>
                    ))}
                  </div>
                )}

                <p className="text-[11px] text-slate-500 leading-relaxed font-mono">
                  *C0001 Boundary Note: p_max = 0.5085 &ge; 0.50 (slim technical majority), but top-2 margin |p0 - p3| = 0.0273 &lt; 0.10. Validation samples cross between Cluster 0 and 3 at 46.8% rate.
                </p>
              </div>

              {/* Historical Property Transactions */}
              {clientDetail?.transactions && (
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                    Purchased Units ({clientDetail.transactions.length})
                  </h4>
                  <div className="space-y-2">
                    {clientDetail.transactions.map((tx: any, idx: number) => (
                      <div
                        key={idx}
                        className="bg-slate-50 dark:bg-slate-950 p-3 rounded-lg border border-slate-200 dark:border-slate-800 flex justify-between items-center text-xs font-mono"
                      >
                        <div>
                          <span className="text-slate-900 dark:text-slate-100 font-bold">
                            Tower {tx.tower_number} • Unit {tx.unit_number} ({tx.unit_category})
                          </span>
                          <span className="block text-[10px] text-slate-400 mt-0.5">
                            {tx.transaction_date?.slice(0, 10)} • {tx.floor_area_sqft} SqFt
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-emerald-600 dark:text-emerald-400 font-bold block">
                            {tx.sale_price_display || formatINR(tx.sale_price_inr, true)}
                          </span>
                          <span className="text-[10px] text-slate-400">
                            ₹{tx.price_per_sqft_inr?.toFixed(2)} / SqFt
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Live Scoring Modal */}
      {isPredictModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 dark:bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl w-full max-w-lg p-5 space-y-4 animate-in fade-in zoom-in-95 duration-100">
            <div className="flex justify-between items-center pb-3 border-b border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold text-sm">
                <PlayCircle className="w-5 h-5" />
                <span>Live Client Segment Predictor (/predict/segment)</span>
              </div>
              <button
                onClick={() => setIsPredictModalOpen(false)}
                className="p-1 text-slate-400 hover:text-slate-700 dark:hover:text-white rounded cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handlePredict} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-600 dark:text-slate-400 block mb-1">Age</label>
                  <input
                    type="number"
                    min="18"
                    max="100"
                    value={predictAge}
                    onChange={(e) => setPredictAge(Number(e.target.value))}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded p-2 text-slate-900 dark:text-slate-100 font-mono outline-none"
                  />
                </div>
                <div>
                  <label className="text-slate-600 dark:text-slate-400 block mb-1">Units Planned</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={predictUnits}
                    onChange={(e) => setPredictUnits(Number(e.target.value))}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded p-2 text-slate-900 dark:text-slate-100 font-mono outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-600 dark:text-slate-400 block mb-1">Country</label>
                  <select
                    value={predictCountry}
                    onChange={(e) => setPredictCountry(e.target.value)}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded p-2 text-slate-900 dark:text-slate-100 outline-none cursor-pointer"
                  >
                    <option value="USA">USA</option>
                    <option value="UK">UK</option>
                    <option value="Canada">Canada</option>
                    <option value="Germany">Germany</option>
                    <option value="France">France</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-600 dark:text-slate-400 block mb-1">Region</label>
                  <input
                    type="text"
                    value={predictRegion}
                    onChange={(e) => setPredictRegion(e.target.value)}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded p-2 text-slate-900 dark:text-slate-100 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-600 dark:text-slate-400 block mb-1">Acquisition Purpose</label>
                  <select
                    value={predictPurpose}
                    onChange={(e) => setPredictPurpose(e.target.value)}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded p-2 text-slate-900 dark:text-slate-100 outline-none cursor-pointer"
                  >
                    <option value="HOME">HOME</option>
                    <option value="INVESTMENT">INVESTMENT</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-600 dark:text-slate-400 block mb-1">Referral Channel</label>
                  <select
                    value={predictChannel}
                    onChange={(e) => setPredictChannel(e.target.value)}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded p-2 text-slate-900 dark:text-slate-100 outline-none cursor-pointer"
                  >
                    <option value="Website">Website</option>
                    <option value="Agency">Agency</option>
                    <option value="Client">Client</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={isPredicting}
                className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition-colors text-xs flex justify-center items-center gap-2 shadow-2xs cursor-pointer"
              >
                {isPredicting ? 'Evaluating Centroid Softmax...' : 'Predict Segment Assignment'}
              </button>
            </form>

            {predictionResult && (
              <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-blue-200 dark:border-blue-800 space-y-2 mt-3 font-mono">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500 dark:text-slate-400">Assigned Cluster:</span>
                  <span className="text-slate-900 dark:text-slate-100 font-bold">
                    Cluster {predictionResult.assigned_cluster} ({predictionResult.assigned_cluster_name})
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500 dark:text-slate-400">Confidence (p_max):</span>
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                    {(predictionResult.confidence_probability * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
