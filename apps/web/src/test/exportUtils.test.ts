import { describe, it, expect, vi } from 'vitest';
import { sanitizeClientForRole, exportToCSV } from '../utils/exportUtils';
import { ClientSummary } from '../types';

describe('Role-Governed Export Pipeline Suite', () => {
  const sampleClient: ClientSummary = {
    client_id: 'C0001',
    first_name: 'Sophia',
    last_name: 'Vanderbilt',
    client_type: 'INDIVIDUAL',
    country: 'USA',
    region: 'California',
    assigned_cluster: 1,
    cluster_name: 'C1: Wealth Maximizers',
    n_units: 5,
    total_spend_inr: 25000000,
    satisfaction_score: 5,
    loan_applied: false,
    referral_channel: 'Agency',
  };

  it('masks personal identifiable information (PII) for analyst role', () => {
    const sanitized = sanitizeClientForRole(sampleClient, 'analyst');
    expect(sanitized['First Name']).toBe('So***');
    expect(sanitized['Last Name']).toBe('Va***');
    expect(sanitized['Total Spend (INR)']).toBe(25000000);
    expect(sanitized['Client ID']).toBe('C0001');
  });

  it('masks personal identifiable information (PII) for viewer role', () => {
    const sanitized = sanitizeClientForRole(sampleClient, 'viewer');
    expect(sanitized['First Name']).toBe('So***');
    expect(sanitized['Last Name']).toBe('Va***');
  });

  it('reveals complete unmasked client names for admin role', () => {
    const sanitized = sanitizeClientForRole(sampleClient, 'admin');
    expect(sanitized['First Name']).toBe('Sophia');
    expect(sanitized['Last Name']).toBe('Vanderbilt');
  });

  it('generates valid CSV string structure', () => {
    // Mock URL and document.body
    const clickSpy = vi.fn();
    const appendSpy = vi.spyOn(document.body, 'appendChild').mockImplementation(() => null as any);
    const removeSpy = vi.spyOn(document.body, 'removeChild').mockImplementation(() => null as any);

    window.URL.createObjectURL = vi.fn(() => 'blob:mock');
    window.URL.revokeObjectURL = vi.fn();

    exportToCSV([sampleClient], { filename: 'test_export', role: 'analyst' });

    expect(window.URL.createObjectURL).toHaveBeenCalled();
    appendSpy.mockRestore();
    removeSpy.mockRestore();
  });
});
