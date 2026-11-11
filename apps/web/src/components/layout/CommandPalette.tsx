import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  LayoutDashboard,
  Users,
  Compass,
  Globe2,
  Building2,
  ScatterChart,
  Target,
  Calculator,
  FlaskConical,
  ShieldCheck,
  Database,
  X,
  ArrowRight,
  Shield,
  UserCheck,
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const { role, setRole, fetchDemoToken } = useAuthStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onClose();
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const commands = [
    { name: 'Executive Overview', path: '/', icon: LayoutDashboard, category: 'Pages' },
    { name: 'Segment Explorer', path: '/segments', icon: Users, category: 'Pages' },
    { name: 'Investor Behavior Lab', path: '/behavior', icon: Compass, category: 'Pages' },
    { name: 'Geo Intelligence', path: '/geo', icon: Globe2, category: 'Pages' },
    { name: 'Tower & Inventory Heatmap', path: '/towers', icon: Building2, category: 'Pages' },
    { name: 'Cluster Map (PCA)', path: '/cluster-map', icon: ScatterChart, category: 'Pages' },
    { name: 'Opportunity Finder & NBO', path: '/opportunities', icon: Target, category: 'Pages' },
    { name: 'Campaign Simulator', path: '/campaigns', icon: Calculator, category: 'Pages' },
    { name: 'Client Lookup & Predict', path: '/clients', icon: Search, category: 'Pages' },
    { name: 'Model Lab & Validation', path: '/model-lab', icon: FlaskConical, category: 'Pages' },
    { name: 'Data Quality & Lineage', path: '/data-quality', icon: ShieldCheck, category: 'Pages' },
    { name: 'Data Source & Sample Datasets', path: '/data', icon: Database, category: 'Pages' },
    {
      name: role === 'analyst' ? 'Switch Role to Admin (Unmasked PII)' : 'Switch Role to Analyst (Masked PII)',
      action: () => {
        const next = role === 'analyst' ? 'admin' : 'analyst';
        setRole(next);
        fetchDemoToken(next);
        onClose();
      },
      icon: role === 'analyst' ? Shield : UserCheck,
      category: 'Security & Access',
    },
  ];

  const filtered = commands.filter(
    (c) =>
      c.name.toLowerCase().includes(query.toLowerCase()) ||
      c.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 dark:bg-slate-950/80 backdrop-blur-xs flex items-start justify-center pt-24 px-4">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-100">
        <div className="p-3 border-b border-slate-200 dark:border-slate-800 flex items-center gap-2">
          <Search className="w-4 h-4 text-slate-400 shrink-0" />
          <input
            type="text"
            autoFocus
            placeholder="Type a command or jump to page..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 outline-none"
          />
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded"
            aria-label="Close command palette"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <p className="text-xs text-slate-400 text-center py-6">No matching actions or pages found.</p>
          ) : (
            filtered.map((item, idx) => {
              const Icon = item.icon;
              return (
                <button
                  key={idx}
                  onClick={() => {
                    if (item.action) {
                      item.action();
                    } else if (item.path) {
                      navigate(item.path);
                      onClose();
                    }
                  }}
                  className="w-full flex items-center justify-between p-2.5 rounded-lg text-xs text-left text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors group cursor-pointer"
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                    <span>{item.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-slate-500 bg-slate-100 dark:bg-slate-950 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-800">
                      {item.category}
                    </span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200 transition-colors" />
                  </div>
                </button>
              );
            })
          )}
        </div>

        <div className="p-2.5 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/50 flex justify-between items-center text-[11px] text-slate-500 px-3">
          <span>Navigate with mouse or keyboard</span>
          <span className="font-mono">ESC to exit</span>
        </div>
      </div>
    </div>
  );
};
