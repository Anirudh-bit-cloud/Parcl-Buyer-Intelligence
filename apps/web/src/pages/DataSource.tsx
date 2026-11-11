import React, { useState, useEffect } from 'react';
import { PageHeader } from '../components/ui/PageHeader';
import { KPICard } from '../components/ui/KPICard';
import { Badge } from '../components/ui/Badge';
import { AdminAuditSection } from '../components/ui/AdminAuditSection';
import { useDatasetStore, DatasetMode } from '../stores/datasetStore';
import { useAuthStore } from '../stores/authStore';
import {
  Database,
  Download,
  Upload,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  Info,
  Check,
  Shield,
  Layers,
} from 'lucide-react';

interface DatasetMeta {
  name: string;
  label: string;
  description: string;
  is_active: boolean;
  buyer_count: number;
  property_count: number;
}

interface ValidationReport {
  is_valid: boolean;
  dataset_type: string;
  row_count: number;
  column_count: number;
  columns: string[];
  errors: string[];
  warnings: string[];
}

export const DataSource: React.FC = () => {
  const { activeDataset, switchDataset } = useDatasetStore();
  const { role, token } = useAuthStore();

  const [datasets, setDatasets] = useState<DatasetMeta[]>([
    {
      name: 'full',
      label: 'Full Production Dataset',
      description: 'Complete multi-unit cohort (2,000 buyers, 7,305 transactions) as of Dec 2025.',
      is_active: activeDataset === 'full',
      buyer_count: 2000,
      property_count: 7305,
    },
    {
      name: 'sample',
      label: 'Synthetic Sample Dataset',
      description: 'Small anonymized test cohort (200 buyers, 500 properties) with matching Pandera schema.',
      is_active: activeDataset === 'sample',
      buyer_count: 200,
      property_count: 500,
    },
  ]);

  const [isSwitching, setIsSwitching] = useState(false);
  const [switchMessage, setSwitchMessage] = useState<string | null>(null);

  // File upload & validation state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationReport, setValidationReport] = useState<ValidationReport | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/v1/datasets')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.datasets) {
          setDatasets(data.datasets);
        }
      })
      .catch(() => {});
  }, [activeDataset]);

  const handleDatasetToggle = async (mode: DatasetMode) => {
    if (mode === activeDataset) return;
    setIsSwitching(true);
    setSwitchMessage(null);
    await switchDataset(mode);
    setIsSwitching(false);
    setSwitchMessage(`Successfully switched active dataset context to: ${mode === 'sample' ? 'Synthetic Sample' : 'Full Production'}`);
    setTimeout(() => setSwitchMessage(null), 4000);
  };

  const handleDownloadSample = (filename: string) => {
    window.open(`/api/v1/datasets/sample/${filename}`, '_blank');
  };

  const handleDownloadTemplate = (type: 'clients' | 'properties') => {
    window.open(`/api/v1/datasets/template/${type}`, '_blank');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setValidationReport(null);
      setUploadError(null);
    }
  };

  const handleValidateUpload = async () => {
    if (!selectedFile) return;
    setIsValidating(true);
    setUploadError(null);
    setValidationReport(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const res = await fetch('/api/v1/datasets/validate', {
        method: 'POST',
        headers,
        body: formData,
      });

      if (res.status === 403) {
        setUploadError('Access Denied: Only Admin role can upload and validate custom datasets. Switch role to Admin in the top bar.');
        setIsValidating(false);
        return;
      }

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        setUploadError(errData.detail || `Upload failed with status code ${res.status}`);
        setIsValidating(false);
        return;
      }

      const report: ValidationReport = await res.json();
      setValidationReport(report);
    } catch (err: any) {
      setUploadError(`Network error validating dataset: ${err.message}`);
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Dataset Management & Data Source"
        description="Switch between full production and synthetic sample cohorts, download Pandera schemas, or validate custom CSV files."
        moduleBadge="Model & Data"
        keyTakeaway="The platform supports isolated testing on synthetic cohorts (200 buyers, 500 properties) with zero risk to production cluster baselines."
      />

      {/* Confirmation Toast */}
      {switchMessage && (
        <div className="p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2">
          <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <span>{switchMessage}</span>
        </div>
      )}

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Active Cohort"
          value={activeDataset === 'sample' ? 'Sample (200)' : 'Production (2,000)'}
          subtitle="Currently active analysis cohort"
          icon={<Database className="w-4 h-4" />}
          badge={{
            text: activeDataset === 'sample' ? 'Sample Active' : 'Production Active',
            variant: activeDataset === 'sample' ? 'warning' : 'accent',
          }}
        />
        <KPICard
          label="Cohort Multi-Unit Buyers"
          value={activeDataset === 'sample' ? '200' : '2,000'}
          subtitle="Minimum 2 units per client"
          icon={<FileSpreadsheet className="w-4 h-4" />}
        />
        <KPICard
          label="Property Inventory"
          value={activeDataset === 'sample' ? '500' : '7,305'}
          subtitle="Sold and available inventory"
          icon={<Layers className="w-4 h-4" />}
        />
        <KPICard
          label="Validation Standard"
          value="Pandera Raw"
          subtitle="Zero-fabrication schema enforcement"
          icon={<CheckCircle2 className="w-4 h-4" />}
          badge={{ text: 'Strict Typing', variant: 'success' }}
        />
      </div>

      {/* SECTION 1: Dataset Context Switcher */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
        <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
              Active Dataset Selector
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Select which dataset is active for platform views and calculations.
            </p>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {isSwitching ? 'Updating...' : `Active: ${activeDataset}`}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {datasets.map((d) => {
            const isSelected = activeDataset === d.name;
            return (
              <div
                key={d.name}
                onClick={() => handleDatasetToggle(d.name as DatasetMode)}
                className={`p-4 rounded-xl border-2 transition-all cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/40 dark:bg-blue-950/20'
                    : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40 hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm text-slate-900 dark:text-slate-100">
                        {d.label}
                      </span>
                      {isSelected && (
                        <Badge variant="accent">Active Context</Badge>
                      )}
                    </div>
                    <div
                      className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        isSelected
                          ? 'border-blue-600 bg-blue-600 text-white'
                          : 'border-slate-300 dark:border-slate-700'
                      }`}
                    >
                      {isSelected && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                    </div>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                    {d.description}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800 flex justify-between text-xs text-slate-500 dark:text-slate-400 font-mono">
                  <span>Buyers: {d.buyer_count.toLocaleString()}</span>
                  <span>Properties: {d.property_count.toLocaleString()}</span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-4 p-3 rounded-lg bg-slate-100 dark:bg-slate-800/60 text-xs text-slate-600 dark:text-slate-300 flex items-start gap-2">
          <Info className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
          <p>
            <strong>Statistical Isolation Guarantee:</strong> Switching between datasets adjusts UI exploration, client lookups, and simulated allocation without rewriting trained model weights or benchmark tables.
          </p>
        </div>
      </div>

      {/* SECTION 2: Sample Datasets & Templates Download */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
        <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
          Download Sample Datasets & CSV Templates
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Download verified synthetic datasets or blank CSV templates with correct column headers and typing.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
          {/* Download clients sample */}
          <div className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/40 flex flex-col justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                clients_sample.csv
              </span>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                200 synthetic buyers with age, country, and channel.
              </p>
            </div>
            <button
              onClick={() => handleDownloadSample('clients_sample.csv')}
              className="mt-3 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition-colors shadow-2xs cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download CSV</span>
            </button>
          </div>

          {/* Download properties sample */}
          <div className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/40 flex flex-col justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                properties_sample.csv
              </span>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                500 synthetic properties across 10 towers.
              </p>
            </div>
            <button
              onClick={() => handleDownloadSample('properties_sample.csv')}
              className="mt-3 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition-colors shadow-2xs cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download CSV</span>
            </button>
          </div>

          {/* Download clients template */}
          <div className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/40 flex flex-col justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                Clients Template
              </span>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                Empty header + 1 example row (RawClientsSchema).
              </p>
            </div>
            <button
              onClick={() => handleDownloadTemplate('clients')}
              className="mt-3 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-medium transition-colors cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Template CSV</span>
            </button>
          </div>

          {/* Download properties template */}
          <div className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/40 flex flex-col justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                Properties Template
              </span>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                Empty header + 1 example row (RawPropertiesSchema).
              </p>
            </div>
            <button
              onClick={() => handleDownloadTemplate('properties')}
              className="mt-3 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-medium transition-colors cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Template CSV</span>
            </button>
          </div>
        </div>
      </div>

      {/* SECTION 3: Upload & Validate Custom Dataset (Admin Only) */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
        <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                Upload & Validate Dataset Against Pandera Schema
              </h2>
              {role === 'admin' ? (
                <Badge variant="warning">Admin Enabled</Badge>
              ) : (
                <Badge variant="default">Admin Required</Badge>
              )}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Upload a clients or properties CSV to test structure, typing, and constraint conformity.
            </p>
          </div>
          <Shield className="w-5 h-5 text-slate-400" />
        </div>

        <div className="mt-4 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <input
            type="file"
            accept=".csv"
            aria-label="Upload CSV dataset for Pandera schema validation"
            onChange={handleFileChange}
            disabled={role !== 'admin'}
            className="text-xs text-slate-600 dark:text-slate-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-medium file:bg-blue-50 file:text-blue-700 dark:file:bg-blue-950/60 dark:file:text-blue-300 hover:file:bg-blue-100 cursor-pointer disabled:opacity-50"
          />

          <button
            onClick={handleValidateUpload}
            disabled={!selectedFile || isValidating || role !== 'admin'}
            className="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-2xs shrink-0 cursor-pointer"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>{isValidating ? 'Validating Schema...' : 'Validate Dataset'}</span>
          </button>
        </div>

        {uploadError && (
          <div className="mt-3 p-3 rounded-lg bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 text-xs text-rose-700 dark:text-rose-300 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}

        {validationReport && (
          <div className="mt-4 p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/40 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {validationReport.is_valid ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                )}
                <div>
                  <h3 className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                    {validationReport.is_valid
                      ? `Schema Validation Passed (${validationReport.dataset_type.toUpperCase()})`
                      : `Schema Validation Failed (${validationReport.dataset_type.toUpperCase()})`}
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Analyzed {validationReport.row_count} rows across {validationReport.column_count} columns.
                  </p>
                </div>
              </div>
              <Badge variant={validationReport.is_valid ? 'success' : 'danger'}>
                {validationReport.is_valid ? 'PASSED' : 'FAILED'}
              </Badge>
            </div>

            {/* Columns parsed */}
            <div>
              <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                Parsed Headers:
              </span>
              <div className="flex flex-wrap gap-1">
                {validationReport.columns.map((col) => (
                  <span
                    key={col}
                    className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300"
                  >
                    {col}
                  </span>
                ))}
              </div>
            </div>

            {validationReport.errors.length > 0 && (
              <div className="p-2.5 rounded bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-xs text-rose-700 dark:text-rose-300 space-y-1">
                <span className="font-semibold block">Schema Violations:</span>
                {validationReport.errors.map((err, i) => (
                  <p key={i} className="font-mono text-[11px]">{err}</p>
                ))}
              </div>
            )}

            {validationReport.warnings.length > 0 && (
              <div className="p-2.5 rounded bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900 text-xs text-amber-700 dark:text-amber-300 space-y-1">
                <span className="font-semibold block">Advisories:</span>
                {validationReport.warnings.map((w, i) => (
                  <p key={i}>{w}</p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Enterprise Admin & Security Audit Trail */}
      <AdminAuditSection />
    </div>
  );
};
