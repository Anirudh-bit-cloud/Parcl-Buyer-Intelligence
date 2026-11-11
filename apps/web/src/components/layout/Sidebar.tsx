import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Compass,
  Globe2,
  Building2,
  ScatterChart,
  Target,
  Calculator,
  Search,
  FlaskConical,
  ShieldCheck,
  Database,
  ChevronRight,
} from 'lucide-react';
import { useDatasetStore } from '../../stores/datasetStore';

interface NavGroup {
  group: string;
  items: {
    name: string;
    path: string;
    icon: React.ComponentType<{ className?: string }>;
    exact?: boolean;
  }[];
}

const navGroups: NavGroup[] = [
  {
    group: 'Overview',
    items: [
      { name: 'Executive Overview', path: '/', icon: LayoutDashboard, exact: true },
    ],
  },
  {
    group: 'Buyers',
    items: [
      { name: 'Segment Explorer', path: '/segments', icon: Users },
      { name: 'Behavior Lab', path: '/behavior', icon: Compass },
      { name: 'Geo Intelligence', path: '/geo', icon: Globe2 },
    ],
  },
  {
    group: 'Inventory',
    items: [
      { name: 'Tower Heatmap', path: '/towers', icon: Building2 },
      { name: 'Opportunities & NBO', path: '/opportunities', icon: Target },
    ],
  },
  {
    group: 'Tools',
    items: [
      { name: 'Campaign Simulator', path: '/campaigns', icon: Calculator },
      { name: 'Client Lookup & Predict', path: '/clients', icon: Search },
      { name: 'Cluster Map (PCA)', path: '/cluster-map', icon: ScatterChart },
    ],
  },
  {
    group: 'Model & Data',
    items: [
      { name: 'Model Lab & Validation', path: '/model-lab', icon: FlaskConical },
      { name: 'Data Quality & Lineage', path: '/data-quality', icon: ShieldCheck },
      { name: 'Data Source', path: '/data', icon: Database },
    ],
  },
];

export const Sidebar: React.FC = () => {
  const { activeDataset } = useDatasetStore();

  return (
    <aside
      className="w-60 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col shrink-0 min-h-[calc(100vh-3.5rem)] transition-colors"
      aria-label="Sidebar navigation"
    >
      <nav className="p-3 space-y-4 flex-1 overflow-y-auto">
        {navGroups.map((group) => (
          <div key={group.group} className="space-y-1">
            <h2 className="px-2.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              {group.group}
            </h2>
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.exact}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 font-semibold'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800/60'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <div className="flex items-center gap-2.5">
                          <Icon
                            className={`w-4 h-4 transition-colors ${
                              isActive
                                ? 'text-blue-600 dark:text-blue-400'
                                : 'text-slate-400 dark:text-slate-500'
                            }`}
                          />
                          <span>{item.name}</span>
                        </div>
                        {isActive && (
                          <ChevronRight className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                        )}
                      </>
                    )}
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Dataset & Baseline Cohort Summary */}
      <div className="p-3.5 border-t border-slate-200 dark:border-slate-800 text-[11px] text-slate-500 dark:text-slate-400 space-y-1 bg-slate-50/50 dark:bg-slate-950/40">
        <div className="flex justify-between items-center">
          <span>Active Dataset</span>
          <span className="font-mono font-medium text-slate-800 dark:text-slate-200">
            {activeDataset === 'sample' ? 'Sample (200)' : 'Prod (2,000)'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span>Transactions</span>
          <span className="font-mono text-slate-700 dark:text-slate-300">
            {activeDataset === 'sample' ? '865' : '7,305'}
          </span>
        </div>
        <div className="flex justify-between items-center pt-1 border-t border-slate-200/80 dark:border-slate-800/80">
          <span>Base Ledger</span>
          <span className="font-mono text-emerald-600 dark:text-emerald-400 font-medium">
            ₹ INR Standard
          </span>
        </div>
      </div>
    </aside>
  );
};
