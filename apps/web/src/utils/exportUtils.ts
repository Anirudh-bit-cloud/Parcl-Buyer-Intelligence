/**
 * Enterprise Multi-Format Data & Board Pack Exporters.
 *
 * Implements role-governed CSV, Excel, and PDF export pipelines with:
 * - PII masking enforcement for viewer/analyst roles
 * - RFC 4180 CSV escaping
 * - Clean SpreadsheetML / XML Excel format (0 vulnerabilities, native Excel & Sheets compatibility)
 * - jsPDF executive PDF board packs with KPI summary and data tables
 */

import { jsPDF } from 'jspdf';
import { ClientSummary } from '../types';

export interface ExportOptions {
  filename: string;
  role: string;
  filtersDescription?: string;
}

/**
 * Clean and mask client row based on active RBAC role.
 */
export function sanitizeClientForRole(client: ClientSummary, role: string): Record<string, any> {
  const isPrivileged = role === 'admin';
  return {
    'Client ID': client.client_id,
    'Client Type': client.client_type,
    'First Name': isPrivileged ? client.first_name : `${client.first_name.slice(0, 2)}***`,
    'Last Name': isPrivileged ? client.last_name : `${client.last_name.slice(0, 2)}***`,
    'Country': client.country,
    'Region': client.region,
    'Assigned Cluster': `Cluster ${client.assigned_cluster}`,
    'Cluster Name': client.cluster_name,
    'Units Purchased': client.n_units,
    'Total Spend (INR)': client.total_spend_inr,
    'Satisfaction Score': client.satisfaction_score,
    'Loan Applied': client.loan_applied ? 'Yes' : 'No',
    'Referral Channel': client.referral_channel,
  };
}

/**
 * Export rows to RFC-4180 compliant CSV.
 */
export function exportToCSV(data: ClientSummary[], options: ExportOptions): void {
  if (!data || data.length === 0) return;

  const sanitized = data.map((c) => sanitizeClientForRole(c, options.role));
  const headers = Object.keys(sanitized[0]);

  const csvRows = [
    headers.join(','),
    ...sanitized.map((row) =>
      headers
        .map((header) => {
          const val = row[header] ?? '';
          const escaped = String(val).replace(/"/g, '""');
          return `"${escaped}"`;
        })
        .join(',')
    ),
  ];

  const blob = new Blob([csvRows.join('\r\n')], { type: 'text/csv;charset=utf-8;' });
  triggerBrowserDownload(blob, `${options.filename}.csv`);
}

/**
 * Export rows to XML Spreadsheet (Excel compatible without sheetjs CVE vulnerabilities).
 */
export function exportToExcel(data: ClientSummary[], options: ExportOptions): void {
  if (!data || data.length === 0) return;

  const sanitized = data.map((c) => sanitizeClientForRole(c, options.role));
  const headers = Object.keys(sanitized[0]);

  let xml = '<?xml version="1.0"?>\n';
  xml += '<?mso-application progid="Excel.Sheet"?>\n';
  xml += '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"\n';
  xml += ' xmlns:o="urn:schemas-microsoft-com:office:office"\n';
  xml += ' xmlns:x="urn:schemas-microsoft-com:office:excel"\n';
  xml += ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"\n';
  xml += ' xmlns:html="http://www.w3.org/TR/REC-html40">\n';
  xml += ' <Styles>\n';
  xml += '  <Style ss:ID="Header">\n';
  xml += '   <Font ss:Bold="1" ss:Color="#FFFFFF"/>\n';
  xml += '   <Interior ss:Color="#1E293B" ss:Pattern="Solid"/>\n';
  xml += '  </Style>\n';
  xml += ' </Styles>\n';
  xml += ' <Worksheet ss:Name="Parcl Buyers">\n';
  xml += '  <Table>\n';

  // Headers
  xml += '   <Row ss:StyleID="Header">\n';
  headers.forEach((h) => {
    xml += `    <Cell><Data ss:Type="String">${escapeXml(h)}</Data></Cell>\n`;
  });
  xml += '   </Row>\n';

  // Rows
  sanitized.forEach((row) => {
    xml += '   <Row>\n';
    headers.forEach((h) => {
      const val = row[h];
      const isNum = typeof val === 'number';
      xml += `    <Cell><Data ss:Type="${isNum ? 'Number' : 'String'}">${escapeXml(String(val ?? ''))}</Data></Cell>\n`;
    });
    xml += '   </Row>\n';
  });

  xml += '  </Table>\n';
  xml += ' </Worksheet>\n';
  xml += '</Workbook>\n';

  const blob = new Blob([xml], { type: 'application/vnd.ms-excel;charset=utf-8;' });
  triggerBrowserDownload(blob, `${options.filename}.xls`);
}

/**
 * Generate an executive PDF board pack report using jsPDF.
 */
export function exportToPDF(data: ClientSummary[], options: ExportOptions): void {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'pt', format: 'a4' });

  // Header / Title Banner
  doc.setFillColor(15, 23, 42); // slate-900
  doc.rect(0, 0, 842, 60, 'F');

  doc.setTextColor(255, 255, 255);
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Parcl Buyer Intelligence Platform — Executive Board Pack', 40, 36);

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text(`Generated: ${new Date().toISOString().split('T')[0]} | Role: ${options.role.toUpperCase()}`, 600, 36);

  // Metadata block
  doc.setTextColor(51, 65, 85);
  doc.setFontSize(11);
  doc.text(`Export Scope: ${data.length} client buyers | Filters: ${options.filtersDescription || 'All Cohorts'}`, 40, 85);
  doc.text('CONFIDENTIAL — Intended solely for authorized institutional real estate portfolio managers.', 40, 102);

  // Table summary headers
  let y = 130;
  doc.setFillColor(241, 245, 249);
  doc.rect(40, y - 15, 762, 22, 'F');
  doc.setTextColor(15, 23, 42);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');

  doc.text('Client ID', 50, y);
  doc.text('Name', 120, y);
  doc.text('Type', 210, y);
  doc.text('Country', 280, y);
  doc.text('Segment', 360, y);
  doc.text('Units', 480, y);
  doc.text('Total Spend (₹)', 540, y);
  doc.text('Satisfaction', 660, y);
  doc.text('Channel', 740, y);

  // Rows (limit to first 25 on summary sheet)
  y += 18;
  doc.setFont('helvetica', 'normal');
  const previewRows = data.slice(0, 25);
  previewRows.forEach((client, idx) => {
    if (idx % 2 === 1) {
      doc.setFillColor(248, 250, 252);
      doc.rect(40, y - 12, 762, 16, 'F');
    }

    const isPrivileged = options.role === 'admin';
    const name = isPrivileged
      ? `${client.first_name} ${client.last_name}`
      : `${client.first_name.slice(0, 2)}*** ${client.last_name.slice(0, 2)}***`;

    doc.text(client.client_id, 50, y);
    doc.text(name.slice(0, 16), 120, y);
    doc.text(client.client_type, 210, y);
    doc.text(client.country.slice(0, 12), 280, y);
    doc.text(client.cluster_name.slice(0, 18), 360, y);
    doc.text(String(client.n_units), 480, y);
    doc.text(`₹${client.total_spend_inr.toLocaleString('en-IN')}`, 540, y);
    doc.text(`${client.satisfaction_score}/5`, 660, y);
    doc.text(client.referral_channel, 740, y);

    y += 16;
  });

  if (data.length > 25) {
    doc.setFontSize(9);
    doc.setTextColor(100, 116, 139);
    doc.text(`... and ${data.length - 25} more client buyers (full dataset available in CSV/Excel export).`, 40, y + 10);
  }

  // Footer
  doc.setFontSize(8);
  doc.setTextColor(148, 163, 184);
  doc.text('Parcl Buyer Intelligence Platform v2.0.0 — Grounded in empirical Model B3 K-Means clustering.', 40, 560);

  doc.save(`${options.filename}.pdf`);
}

function escapeXml(unsafe: string): string {
  return unsafe.replace(/[<>&'"]/g, (c) => {
    switch (c) {
      case '<':
        return '&lt;';
      case '>':
        return '&gt;';
      case '&':
        return '&amp;';
      case '\'':
        return '&apos;';
      case '"':
        return '&quot;';
      default:
        return c;
    }
  });
}

function triggerBrowserDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
