import { test, expect } from '@playwright/test';

/**
 * Enterprise Golden Path E2E Test Suite
 *
 * User Journey:
 * 1. Login with demo / analyst credentials
 * 2. Apply global filters (URL-synced state verification)
 * 3. Inspect Segment Explorer (C0 - C3)
 * 4. Inspect Next-Best-Offer (NBO) for representative buyer C0001
 * 5. Run Marketing Campaign Simulator
 * 6. Trigger data export
 * 7. Switch to Auditor role and verify audit trail entry + cryptographic chain validity
 */

test.describe('Enterprise Golden Path E2E Journey', () => {
  const API_BASE = process.env.API_BASE_URL || 'http://127.0.0.1:8000';

  test('Step 1 -> 7: Complete Golden Path Flow with Auditor Verification', async ({ request }) => {
    // 1. Login: issue analyst session token
    const authRes = await request.post(`${API_BASE}/api/v1/auth/demo-token`, {
      data: { role: 'analyst' },
    });
    expect(authRes.status()).toBe(200);
    const authData = await authRes.json();
    expect(authData.role).toBe('analyst');
    expect(authData.access_token).toBeDefined();
    const analystToken = authData.access_token;
    const analystHeaders = { Authorization: `Bearer ${analystToken}` };

    // 2. Filter: query with global filters applied
    const filterRes = await request.get(`${API_BASE}/api/v1/clients?page=1&page_size=10&country=USA&acquisition_purpose=INVESTMENT`, {
      headers: analystHeaders,
    });
    expect(filterRes.status()).toBe(200);
    const filterData = await filterRes.json();
    expect(filterData.pagination.total_records).toBeGreaterThan(0);
    expect(filterData.clients[0].country).toBe('USA');

    // 3. Segment Explorer: inspect segment catalog
    const segmentRes = await request.get(`${API_BASE}/api/v1/segments`, {
      headers: analystHeaders,
    });
    expect(segmentRes.status()).toBe(200);
    const segmentData = await segmentRes.json();
    expect(segmentData.k_selected).toBe(4);
    expect(segmentData.segments.length).toBe(4);

    // 4. Next-Best-Offer (NBO): recommendations for C0001
    const nboRes = await request.get(`${API_BASE}/api/v1/recommendations/nbo/C0001`, {
      headers: analystHeaders,
    });
    expect(nboRes.status()).toBe(200);
    const nboData = await nboRes.json();
    expect(nboData.client_id).toBe('C0001');
    expect(nboData.recommendations.length).toBeGreaterThan(0);

    // 5. Campaign Simulator: run scenario
    const simRes = await request.post(`${API_BASE}/api/v1/campaigns/scenario`, {
      headers: analystHeaders,
      data: {
        total_budget_inr: 200000,
        channel_allocations: { Website: 0.5, Agency: 0.35, Client: 0.15 },
        channel_cpas_inr: { Website: 1200, Agency: 3500, Client: 1800 },
      },
    });
    expect(simRes.status()).toBe(200);
    const simData = await simRes.json();
    expect(simData.total_modeled_clients).toBeGreaterThan(0);

    // 6. Export: initiate asynchronous/downloadable export job (as auditor/admin)
    const auditorAuthRes = await request.post(`${API_BASE}/api/v1/auth/demo-token`, {
      data: { role: 'auditor', admin_key: 'dev-demo-admin-key-parcl-2026' },
    });
    expect(auditorAuthRes.status()).toBe(200);
    const auditorToken = (await auditorAuthRes.json()).access_token;
    const auditorHeaders = { Authorization: `Bearer ${auditorToken}` };

    const exportRes = await request.post(`${API_BASE}/api/v1/export/async`, {
      headers: auditorHeaders,
      data: {
        format: 'csv',
        country: 'USA',
      },
    });
    expect(exportRes.status()).toBe(200);
    const exportData = await exportRes.json();
    expect(exportData.job_id).toBeDefined();

    // 7. Auditor verification: verify audit entry + cryptographic hash chain
    // Inspect audit logs
    const auditRes = await request.get(`${API_BASE}/api/v1/export/audit-logs?limit=10`, {
      headers: auditorHeaders,
    });
    expect(auditRes.status()).toBe(200);
    const auditBody = await auditRes.json();
    expect(auditBody.logs.length).toBeGreaterThan(0);
    expect(auditBody.chain_verification.status).toBe('valid');
    expect(auditBody.chain_verification.tampered).toBe(false);

    // Explicit chain verification endpoint
    const verifyRes = await request.get(`${API_BASE}/api/v1/export/audit-logs/verify`, {
      headers: auditorHeaders,
    });
    expect(verifyRes.status()).toBe(200);
    const verifyBody = await verifyRes.json();
    expect(verifyBody.status).toBe('valid');
    expect(verifyBody.tampered).toBe(false);
  });
});
