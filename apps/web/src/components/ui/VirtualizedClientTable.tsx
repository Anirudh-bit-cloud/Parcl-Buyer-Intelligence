import React, { useMemo, useRef, useState } from 'react';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Download,
  FileSpreadsheet,
  FileText,
  SlidersHorizontal,
} from 'lucide-react';
import { ClientSummary } from '../../types';
import { useAuthStore } from '../../stores/authStore';
import { exportToCSV, exportToExcel, exportToPDF } from '../../utils/exportUtils';
import { Badge, BadgeVariant } from './Badge';

interface VirtualizedClientTableProps {
  data: ClientSummary[];
  onSelectClient?: (clientId: string) => void;
  selectedClientId?: string | null;
}

export const VirtualizedClientTable: React.FC<VirtualizedClientTableProps> = ({
  data,
  onSelectClient,
  selectedClientId,
}) => {
  const { role } = useAuthStore();
  const [sorting, setSorting] = useState<SortingState>([{ id: 'total_spend_inr', desc: true }]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [showColumnMenu, setShowColumnMenu] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);

  const columns = useMemo<ColumnDef<ClientSummary>[]>(
    () => [
      {
        accessorKey: 'client_id',
        header: 'Client ID',
        cell: (info) => (
          <span className="font-mono text-xs font-semibold text-sky-600 dark:text-sky-400">
            {info.getValue<string>()}
          </span>
        ),
        size: 90,
      },
      {
        accessorKey: 'first_name',
        header: 'Buyer Name',
        cell: (info) => {
          const row = info.row.original;
          const isPrivileged = role === 'admin';
          const name = isPrivileged
            ? `${row.first_name} ${row.last_name}`
            : `${row.first_name.slice(0, 2)}*** ${row.last_name.slice(0, 2)}***`;
          return (
            <div className="flex flex-col">
              <span className="text-sm font-medium text-slate-900 dark:text-white">{name}</span>
              <span className="text-xs text-slate-500">{row.client_type}</span>
            </div>
          );
        },
        size: 160,
      },
      {
        accessorKey: 'country',
        header: 'Geography',
        cell: (info) => {
          const row = info.row.original;
          return (
            <span className="text-xs text-slate-700 dark:text-slate-300">
              {row.country} • {row.region}
            </span>
          );
        },
        size: 130,
      },
      {
        accessorKey: 'cluster_name',
        header: 'Assigned Segment',
        cell: (info) => {
          const row = info.row.original;
          const clusterId = row.assigned_cluster >= 0 && row.assigned_cluster <= 3 ? row.assigned_cluster : 0;
          const clusterVariant = `cluster-${clusterId}` as BadgeVariant;
          return (
            <Badge variant={clusterVariant}>
              {info.getValue<string>()}
            </Badge>
          );
        },
        size: 170,
      },
      {
        accessorKey: 'n_units',
        header: 'Units',
        cell: (info) => (
          <span className="font-mono text-sm text-slate-800 dark:text-slate-200">
            {info.getValue<number>()}
          </span>
        ),
        size: 70,
      },
      {
        accessorKey: 'total_spend_inr',
        header: 'Total Spend (₹)',
        cell: (info) => {
          const val = info.getValue<number>();
          return (
            <span className="font-mono text-sm font-medium text-emerald-600 dark:text-emerald-400">
              ₹{val.toLocaleString('en-IN')}
            </span>
          );
        },
        size: 140,
      },
      {
        accessorKey: 'satisfaction_score',
        header: 'Satisfaction',
        cell: (info) => {
          const score = info.getValue<number>();
          return (
            <span
              className={`text-xs font-semibold ${
                score >= 4
                  ? 'text-emerald-600'
                  : score === 3
                  ? 'text-amber-500'
                  : 'text-rose-500'
              }`}
            >
              {score} / 5
            </span>
          );
        },
        size: 90,
      },
      {
        accessorKey: 'referral_channel',
        header: 'Channel',
        cell: (info) => (
          <span className="text-xs text-slate-600 dark:text-slate-400">
            {info.getValue<string>()}
          </span>
        ),
        size: 90,
      },
    ],
    [role]
  );

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnVisibility,
    },
    onSortingChange: setSorting,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  const { rows } = table.getRowModel();
  const tableContainerRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 52,
    overscan: 10,
  });

  const handleExportCSV = () => {
    exportToCSV(data, { filename: 'parcl_clients_export', role });
    setShowExportMenu(false);
  };

  const handleExportExcel = () => {
    exportToExcel(data, { filename: 'parcl_clients_export', role });
    setShowExportMenu(false);
  };

  const handleExportPDF = () => {
    exportToPDF(data, { filename: 'parcl_board_pack_clients', role });
    setShowExportMenu(false);
  };

  return (
    <div className="flex flex-col rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      {/* Table Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-4 py-3 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-800 dark:text-white">
            Client Directory
          </span>
          <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
            {data.length} records
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Column Visibility Menu */}
          <div className="relative">
            <button
              onClick={() => setShowColumnMenu(!showColumnMenu)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
            >
              <SlidersHorizontal className="h-3.5 w-3.5" />
              Columns
            </button>
            {showColumnMenu && (
              <div className="absolute right-0 z-20 mt-1 w-44 rounded-lg border border-slate-200 bg-white p-2 shadow-lg dark:border-slate-700 dark:bg-slate-800">
                <div className="mb-2 text-xs font-semibold text-slate-500">Toggle Columns</div>
                {table.getAllLeafColumns().map((column) => (
                  <label
                    key={column.id}
                    className="flex cursor-pointer items-center gap-2 px-1 py-1 text-xs text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700 rounded"
                  >
                    <input
                      type="checkbox"
                      checked={column.getIsVisible()}
                      onChange={column.getToggleVisibilityHandler()}
                      className="rounded border-slate-300 text-sky-600"
                    />
                    {typeof column.columnDef.header === 'string'
                      ? column.columnDef.header
                      : column.id}
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Export Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowExportMenu(!showExportMenu)}
              className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-sky-500"
            >
              <Download className="h-3.5 w-3.5" />
              Export
            </button>
            {showExportMenu && (
              <div className="absolute right-0 z-20 mt-1 w-44 rounded-lg border border-slate-200 bg-white p-1.5 shadow-lg dark:border-slate-700 dark:bg-slate-800">
                <button
                  onClick={handleExportCSV}
                  className="flex w-full items-center gap-2 rounded px-2.5 py-1.5 text-left text-xs text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                >
                  <FileText className="h-3.5 w-3.5 text-slate-500" />
                  CSV Data (.csv)
                </button>
                <button
                  onClick={handleExportExcel}
                  className="flex w-full items-center gap-2 rounded px-2.5 py-1.5 text-left text-xs text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                >
                  <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600" />
                  Excel Workbook (.xls)
                </button>
                <button
                  onClick={handleExportPDF}
                  className="flex w-full items-center gap-2 rounded px-2.5 py-1.5 text-left text-xs text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                >
                  <Download className="h-3.5 w-3.5 text-rose-500" />
                  Executive PDF Report
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Virtualized Table Container */}
      <div
        ref={tableContainerRef}
        className="relative h-[480px] overflow-auto"
        tabIndex={0}
        aria-label="Virtualized client buyers table"
      >
        <table className="w-full text-left border-collapse">
          {/* Sticky Header */}
          <thead className="sticky top-0 z-10 bg-slate-50 shadow-sm dark:bg-slate-800">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  const canSort = header.column.getCanSort();
                  const isSorted = header.column.getIsSorted();
                  return (
                    <th
                      key={header.id}
                      style={{ width: header.getSize() }}
                      onClick={header.column.getToggleSortingHandler()}
                      className={`px-4 py-3 text-xs font-semibold text-slate-600 dark:text-slate-300 ${
                        canSort ? 'cursor-pointer select-none hover:bg-slate-100 dark:hover:bg-slate-700' : ''
                      }`}
                    >
                      <div className="flex items-center gap-1.5">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {canSort && (
                          <span className="text-slate-400">
                            {isSorted === 'asc' ? (
                              <ArrowUp className="h-3 w-3 text-sky-600" />
                            ) : isSorted === 'desc' ? (
                              <ArrowDown className="h-3 w-3 text-sky-600" />
                            ) : (
                              <ArrowUpDown className="h-3 w-3 opacity-40" />
                            )}
                          </span>
                        )}
                      </div>
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>

          {/* Virtual Body */}
          <tbody>
            {rowVirtualizer.getVirtualItems().length > 0 ? (
              <>
                {rowVirtualizer.getVirtualItems()[0].start > 0 && (
                  <tr>
                    <td
                      colSpan={columns.length}
                      style={{ height: `${rowVirtualizer.getVirtualItems()[0].start}px` }}
                    />
                  </tr>
                )}
                {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                  const row = rows[virtualRow.index];
                  const isSelected = selectedClientId === row.original.client_id;
                  return (
                    <tr
                      key={row.id}
                      onClick={() => onSelectClient?.(row.original.client_id)}
                      className={`border-b border-slate-100 transition-colors dark:border-slate-800/60 ${
                        isSelected
                          ? 'bg-sky-50 dark:bg-sky-950/40'
                          : 'hover:bg-slate-50/80 dark:hover:bg-slate-800/50'
                      } ${onSelectClient ? 'cursor-pointer' : ''}`}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <td key={cell.id} className="px-4 py-3 align-middle">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                  );
                })}
                {rowVirtualizer.getTotalSize() -
                  (rowVirtualizer.getVirtualItems()[rowVirtualizer.getVirtualItems().length - 1]?.end || 0) >
                  0 && (
                  <tr>
                    <td
                      colSpan={columns.length}
                      style={{
                        height: `${
                          rowVirtualizer.getTotalSize() -
                          (rowVirtualizer.getVirtualItems()[rowVirtualizer.getVirtualItems().length - 1]?.end || 0)
                        }px`,
                      }}
                    />
                  </tr>
                )}
              </>
            ) : (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-4 py-12 text-center text-sm text-slate-500"
                >
                  No client records found matching the active cohort filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
