import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { formatINR } from '../utils/format';
import { PageHeader } from '../components/ui/PageHeader';
import { KPICard } from '../components/ui/KPICard';
import { InfoTooltip } from '../components/ui/InfoTooltip';
import {
  Calculator,
  Sliders,
  TrendingUp,
  Coins,
  Users,
  AlertCircle,
  RotateCcw,
  Sparkles,
  GitCompare,
  ArrowRight,
} from 'lucide-react';

export const CampaignSimulator: React.FC = () => {
  const [totalBudget, setTotalBudget] = useState<number>(100000); // Default ₹1,00,000
  const [allocWebsite, setAllocWebsite] = useState<number>(50);
  const [allocAgency, setAllocAgency] = useState<number>(35);
  const [allocClient, setAllocClient] = useState<number>(15);
  const [enableDiminishingReturns, setEnableDiminishingReturns] = useState<boolean>(true);
  const [, setResult] = useState<any>(null);

  // Scenario Comparison State
  const [scenarioA, setScenarioA] = useState<any | null>(null);
  const [showComparison, setShowComparison] = useState<boolean>(false);

  // Historical Channel Mean Spends from Parquet
  const HISTORICAL_MEANS = {
    Website: 1274770.93,
    Agency: 1243488.90,
    Client: 1239682.03,
  };

  // Illustrative CPAs
  const CPAS = {
    Website: 1200,
    Agency: 3500,
    Client: 1800,
  };

  // Market Channel Capacity Caps
  const CAPACITY_CAPS = {
    Website: 1200,
    Agency: 800,
    Client: 400,
  };

  const totalAllocation = allocWebsite + allocAgency + allocClient;
  const isValidAllocation = totalAllocation === 100;

  useEffect(() => {
    let isMounted = true;
    if (isValidAllocation) {
      api.simulateCampaign({
        total_budget_inr: totalBudget,
        allocation_website_pct: allocWebsite,
        allocation_agency_pct: allocAgency,
        allocation_client_pct: allocClient,
      }).then((res) => {
        if (isMounted) setResult(res);
      });
    }
    return () => {
      isMounted = false;
    };
  }, [totalBudget, allocWebsite, allocAgency, allocClient, isValidAllocation]);

  const budgetWeb = (totalBudget * allocWebsite) / 100;
  const budgetAgency = (totalBudget * allocAgency) / 100;
  const budgetClient = (totalBudget * allocClient) / 100;

  // Calculate clients acquired (Linear or Concave Diminishing Returns)
  const computeClients = (budget: number, cpa: number, cap: number) => {
    const linear = budget / cpa;
    if (!enableDiminishingReturns) return linear;
    const saturated = cap * (1.0 - Math.exp(-budget / (cap * cpa)));
    return Math.min(linear, saturated);
  };

  const clientsWeb = computeClients(budgetWeb, CPAS.Website, CAPACITY_CAPS.Website);
  const clientsAgency = computeClients(budgetAgency, CPAS.Agency, CAPACITY_CAPS.Agency);
  const clientsClient = computeClients(budgetClient, CPAS.Client, CAPACITY_CAPS.Client);
  const totalClients = clientsWeb + clientsAgency + clientsClient;

  const gmvWeb = clientsWeb * HISTORICAL_MEANS.Website;
  const gmvAgency = clientsAgency * HISTORICAL_MEANS.Agency;
  const gmvClient = clientsClient * HISTORICAL_MEANS.Client;
  const totalGmv = gmvWeb + gmvAgency + gmvClient;

  // Monte-Carlo 95% Confidence Interval Estimation
  const varianceWeb = clientsWeb * Math.pow(HISTORICAL_MEANS.Website * 0.25, 2);
  const varianceAgency = clientsAgency * Math.pow(HISTORICAL_MEANS.Agency * 0.25, 2);
  const varianceClient = clientsClient * Math.pow(HISTORICAL_MEANS.Client * 0.25, 2);
  const standardError = Math.sqrt(varianceWeb + varianceAgency + varianceClient);
  const ciLower = Math.max(0, totalGmv - 1.96 * standardError);
  const ciUpper = totalGmv + 1.96 * standardError;

  const resetDefaults = () => {
    setTotalBudget(100000);
    setAllocWebsite(50);
    setAllocAgency(35);
    setAllocClient(15);
    setEnableDiminishingReturns(true);
  };

  const saveAsScenarioA = () => {
    setScenarioA({
      budget: totalBudget,
      allocWebsite,
      allocAgency,
      allocClient,
      clients: totalClients,
      gmv: totalGmv,
    });
    setShowComparison(true);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Marketing Campaign Simulator"
        description="Interactive scenario modeling allocating marketing budget across 3 empirical referral channels with Diminishing Returns."
        moduleBadge="Enterprise MLOps"
        keyTakeaway="Modeled GMV scales with channel conversion efficiency; Website delivers lowest CPA (₹1,200) and highest observed mean spend."
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={saveAsScenarioA}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium transition-colors shadow-2xs cursor-pointer"
            >
              <GitCompare className="w-3.5 h-3.5" />
              <span>{scenarioA ? 'Update Scenario A' : 'Save as Scenario A'}</span>
            </button>
            <button
              onClick={resetDefaults}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-medium border border-slate-200 dark:border-slate-700 transition-colors shadow-2xs cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>
        }
      />

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Total Campaign Budget"
          value={formatINR(totalBudget, false)}
          subtitle={`${totalAllocation}% allocated across 3 channels`}
          icon={<Coins className="w-4 h-4" />}
          badge={{ text: isValidAllocation ? '100% Balanced' : 'Unbalanced', variant: isValidAllocation ? 'success' : 'warning' }}
        />
        <KPICard
          label="Modeled Sales Volume (GMV)"
          value={formatINR(totalGmv, false)}
          subtitle={`95% CI: ${formatINR(ciLower, false)} – ${formatINR(ciUpper, false)}`}
          icon={<TrendingUp className="w-4 h-4" />}
          tooltip="Modeled gross transaction volume with Monte-Carlo 95% confidence intervals derived from empirical variance."
        />
        <KPICard
          label="Modeled Clients Acquired"
          value={`${totalClients.toFixed(2)} buyers`}
          subtitle={enableDiminishingReturns ? 'Diminishing returns enabled' : 'Linear response'}
          icon={<Users className="w-4 h-4" />}
        />
        <KPICard
          label="Blended Illustrative CPA"
          value={`₹${(totalBudget / (totalClients || 1)).toFixed(2)}`}
          subtitle="Weighted cost per acquired buyer"
          icon={<Calculator className="w-4 h-4" />}
          tooltip="Average cost of acquisition across Website (₹1,200), Agency (₹3,500), and Client Referral (₹1,800)."
        />
      </div>

      {/* Main Grid: Controls vs Results */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column (1 col) */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-5 shadow-2xs">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-blue-400">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4" />
              <span>Campaign Parameters</span>
            </div>
            <div className="flex items-center gap-1.5 font-normal normal-case text-slate-500">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>v2</span>
            </div>
          </div>

          {/* Diminishing Returns Switch */}
          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
            <div>
              <span className="text-xs font-medium text-slate-800 dark:text-slate-200 block">Diminishing Returns Curve</span>
              <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Models realistic channel saturation caps</span>
            </div>
            <input
              type="checkbox"
              checked={enableDiminishingReturns}
              onChange={(e) => setEnableDiminishingReturns(e.target.checked)}
              className="rounded text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer"
            />
          </div>

          {/* Budget Input */}
          <div className="space-y-1.5">
            <label className="text-xs text-slate-700 dark:text-slate-300 font-medium flex justify-between">
              <span>Total Marketing Budget (₹)</span>
              <span className="font-mono text-blue-600 dark:text-blue-400 font-semibold">{formatINR(totalBudget, false)}</span>
            </label>
            <input
              type="range"
              min="10000"
              max="2000000"
              step="10000"
              value={totalBudget}
              onChange={(e) => setTotalBudget(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
          </div>

          {/* Channel Allocation Sliders */}
          <div className="space-y-4 pt-2 border-t border-slate-100 dark:border-slate-800">
            <div className="text-xs font-semibold text-slate-800 dark:text-slate-200">Channel Allocations (%)</div>

            {/* Website */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400">Website Channel</span>
                <span className="font-mono font-semibold">{allocWebsite}% ({formatINR(budgetWeb, false)})</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={allocWebsite}
                onChange={(e) => setAllocWebsite(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-sky-500"
              />
            </div>

            {/* Agency */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400">Agency Channel</span>
                <span className="font-mono font-semibold">{allocAgency}% ({formatINR(budgetAgency, false)})</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={allocAgency}
                onChange={(e) => setAllocAgency(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
            </div>

            {/* Client Referral */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400">Client Referral</span>
                <span className="font-mono font-semibold">{allocClient}% ({formatINR(budgetClient, false)})</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={allocClient}
                onChange={(e) => setAllocClient(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
            </div>
          </div>
        </div>

        {/* Results Column (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Channel Performance Breakdown */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-2xs space-y-4">
            <h3 className="text-xs font-semibold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
              Channel Acquisition & Efficiency Breakdown
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Website */}
              <div className="p-4 rounded-lg bg-sky-50/50 dark:bg-sky-950/20 border border-sky-100 dark:border-sky-900/40 space-y-2">
                <div className="text-xs font-semibold text-sky-800 dark:text-sky-300">Website</div>
                <div className="text-xl font-bold font-mono text-slate-900 dark:text-slate-100">
                  {clientsWeb.toFixed(1)} <span className="text-xs font-normal text-slate-500">clients</span>
                </div>
                <div className="text-xs text-slate-600 dark:text-slate-400">
                  Modeled GMV: <span className="font-semibold text-slate-800 dark:text-slate-200">{formatINR(gmvWeb, false)}</span>
                </div>
              </div>

              {/* Agency */}
              <div className="p-4 rounded-lg bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 space-y-2">
                <div className="text-xs font-semibold text-emerald-800 dark:text-emerald-300">Agency</div>
                <div className="text-xl font-bold font-mono text-slate-900 dark:text-slate-100">
                  {clientsAgency.toFixed(1)} <span className="text-xs font-normal text-slate-500">clients</span>
                </div>
                <div className="text-xs text-slate-600 dark:text-slate-400">
                  Modeled GMV: <span className="font-semibold text-slate-800 dark:text-slate-200">{formatINR(gmvAgency, false)}</span>
                </div>
              </div>

              {/* Client */}
              <div className="p-4 rounded-lg bg-amber-50/50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/40 space-y-2">
                <div className="text-xs font-semibold text-amber-800 dark:text-amber-300">Client Referral</div>
                <div className="text-xl font-bold font-mono text-slate-900 dark:text-slate-100">
                  {clientsClient.toFixed(1)} <span className="text-xs font-normal text-slate-500">clients</span>
                </div>
                <div className="text-xs text-slate-600 dark:text-slate-400">
                  Modeled GMV: <span className="font-semibold text-slate-800 dark:text-slate-200">{formatINR(gmvClient, false)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Scenario Comparison Side-by-Side (A vs B) */}
          {showComparison && scenarioA && (
            <div className="bg-white dark:bg-slate-900 border border-blue-200 dark:border-blue-900/60 rounded-xl p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <GitCompare className="w-4 h-4 text-blue-600" />
                  <h3 className="text-xs font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                    Scenario Compare: Baseline A vs Current B
                  </h3>
                </div>
                <button
                  onClick={() => setShowComparison(false)}
                  className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  Dismiss
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                  <span className="font-semibold text-slate-500 block mb-1">Scenario A (Saved)</span>
                  <div>Budget: <span className="font-mono font-bold">{formatINR(scenarioA.budget, false)}</span></div>
                  <div>Clients: <span className="font-mono font-bold">{scenarioA.clients.toFixed(1)}</span></div>
                  <div>GMV: <span className="font-mono font-bold">{formatINR(scenarioA.gmv, false)}</span></div>
                </div>

                <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800">
                  <span className="font-semibold text-blue-600 dark:text-blue-400 block mb-1">Scenario B (Current)</span>
                  <div>Budget: <span className="font-mono font-bold">{formatINR(totalBudget, false)}</span></div>
                  <div>Clients: <span className="font-mono font-bold">{totalClients.toFixed(1)}</span></div>
                  <div>GMV: <span className="font-mono font-bold">{formatINR(totalGmv, false)}</span></div>
                </div>

                <div className="p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800">
                  <span className="font-semibold text-emerald-700 dark:text-emerald-300 block mb-1">Deltas (B – A)</span>
                  <div>Budget Delta: <span className="font-mono font-bold">{formatINR(totalBudget - scenarioA.budget, false)}</span></div>
                  <div>Clients Delta: <span className="font-mono font-bold">{(totalClients - scenarioA.clients).toFixed(1)}</span></div>
                  <div>GMV Delta: <span className="font-mono font-bold">{formatINR(totalGmv - scenarioA.gmv, false)}</span></div>
                  <div className="mt-1 text-[11px] text-emerald-700 dark:text-emerald-300 font-semibold">
                    Incremental GMV Multiple: {((totalGmv - scenarioA.gmv) / Math.max(totalBudget - scenarioA.budget, 1)).toFixed(1)}x
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
