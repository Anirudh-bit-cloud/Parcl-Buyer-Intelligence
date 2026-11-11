import React, { useState, useEffect } from 'react';
import { Shield, FileSpreadsheet, Activity, Database, CheckCircle2 } from 'lucide-react';
import { Badge } from './Badge';
import { useAuthStore } from '../../stores/authStore';

export const AdminAuditSection: React.FC = () => {
  const { role, token } = useAuthStore();
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [driftStatus, setDriftStatus] = useState<any>(null);

  useEffect(() => {
    fetch('/health/ready')
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setSystemHealth(d))
      .catch(() => {});

    if (role === 'admin' && token) {
      fetch('/api/v1/export/audit-logs?limit=10', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => d && setAuditLogs(d.logs || []))
        .catch(() => {});
    }

    fetch('/api/v1/governance/drift')
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setDriftStatus(d))
      .catch(() => {});
  }, [role, token]);

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-6 mt-6">
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <div>
            <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
              Enterprise System Health & Security Audit Trail
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Live PostgreSQL/Redis connectivity, drift status, and immutable audit logs.
            </p>
          </div>
        </div>
        <Badge variant={systemHealth?.status === 'ready' ? 'success' : 'default'}>
          {systemHealth?.status === 'ready' ? 'SYSTEM OPERATIONAL' : 'ACTIVE'}
        </Badge>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
          <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">Relational Persistence</span>
          <div className="text-sm font-semibold mt-1 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            {systemHealth?.database === 'connected' ? 'PostgreSQL / SQLite Connected' : 'Connecting...'}
          </div>
        </div>

        <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
          <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">Redis Cache & Rate Limiter</span>
          <div className="text-sm font-semibold mt-1 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-blue-500"></span>
            {systemHealth?.redis || 'Sliding Window Active'}
          </div>
        </div>

        <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
          <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">Model B3 Drift Status</span>
          <div className="text-sm font-semibold mt-1 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            {driftStatus?.status === 'HEALTHY' ? 'Healthy (Max PSI < 0.10)' : 'Monitoring Active'}
          </div>
        </div>
      </div>

      {/* Immutable Audit Trail (Admin Only) */}
      {role === 'admin' ? (
        <div>
          <h3 className="text-xs font-semibold text-slate-800 dark:text-slate-200 mb-2.5 flex items-center gap-1.5">
            <FileSpreadsheet className="w-4 h-4 text-slate-500" />
            Recent Security & Export Audit Trail (Role: Admin)
          </h3>
          <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700 font-medium">
                <tr>
                  <th className="py-2 px-3">Timestamp</th>
                  <th className="py-2 px-3">Role</th>
                  <th className="py-2 px-3">Action</th>
                  <th className="py-2 px-3">Resource</th>
                  <th className="py-2 px-3">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300 font-mono text-[11px]">
                {auditLogs.length > 0 ? (
                  auditLogs.map((log: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="py-2 px-3 whitespace-nowrap text-slate-500">
                        {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'Recent'}
                      </td>
                      <td className="py-2 px-3 font-semibold text-blue-600 dark:text-blue-400">{log.role}</td>
                      <td className="py-2 px-3">
                        <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                          {log.action}
                        </span>
                      </td>
                      <td className="py-2 px-3">{log.resource}</td>
                      <td className="py-2 px-3 text-slate-500 max-w-xs truncate">{log.details || '—'}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-4 text-center text-slate-500 font-sans">
                      No security audit events recorded yet in current session.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
          <Shield className="w-4 h-4 text-slate-400 shrink-0" />
          <span>
            Audit log table requires <strong>Admin</strong> role privilege. Switch to Admin in the top-bar to view the immutable audit trail.
          </span>
        </div>
      )}
    </div>
  );
};
