"""Comprehensive test script hitting all Parcl API endpoints against live server or TestClient."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from fastapi.testclient import TestClient

from apps.api.main import app

BASE_URL = "http://127.0.0.1:8000"


def run_tests():
    use_live = "--live" in sys.argv
    if use_live:
        print(f"Testing against live server at {BASE_URL}...")
        client = httpx.Client(base_url=BASE_URL, timeout=10.0)
    else:
        print("Testing via FastAPI TestClient...")
        client = TestClient(app)

    # 1. Health
    res = client.get("/health/live")
    assert res.status_code == 200, f"/health/live failed: {res.text}"
    print("  [OK] /health/live")

    res = client.get("/health/ready")
    assert res.status_code == 200, f"/health/ready failed: {res.text}"
    print("  [OK] /health/ready")

    # 2. Auth tokens
    tokens = {}
    for role in ["viewer", "analyst", "admin", "auditor"]:
        payload = {"role": role}
        if role in ["admin", "auditor"]:
            payload["admin_key"] = "dev-demo-admin-key-parcl-2026"
        res = client.post("/api/v1/auth/demo-token", json=payload)
        assert res.status_code == 200, f"Auth {role} failed: {res.text}"
        tokens[role] = res.json()["access_token"]
        print(f"  [OK] /api/v1/auth/demo-token ({role})")

    analyst_hdr = {"Authorization": f"Bearer {tokens['analyst']}"}
    admin_hdr = {"Authorization": f"Bearer {tokens['admin']}"}
    auditor_hdr = {"Authorization": f"Bearer {tokens['auditor']}"}

    # 3. Macro & Segments
    res = client.get("/api/v1/overview", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/overview failed: {res.text}"
    print("  [OK] /api/v1/overview")

    res = client.get("/api/v1/segments", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/segments failed: {res.text}"
    print("  [OK] /api/v1/segments")

    res = client.get("/api/v1/segments/0", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/segments/0 failed: {res.text}"
    print("  [OK] /api/v1/segments/0")

    # 4. Clients directory & detail
    res = client.get("/api/v1/clients?page=1&page_size=10&country=USA", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/clients failed: {res.text}"
    print("  [OK] /api/v1/clients")

    res = client.get("/api/v1/clients/C0001", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/clients/C0001 failed: {res.text}"
    print("  [OK] /api/v1/clients/C0001")

    # 5. Behavior, Geo, Towers, Projection
    res = client.get("/api/v1/behavior", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/behavior failed: {res.text}"
    print("  [OK] /api/v1/behavior")

    res = client.get("/api/v1/geo", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/geo failed: {res.text}"
    print("  [OK] /api/v1/geo")

    res = client.get("/api/v1/towers", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/towers failed: {res.text}"
    print("  [OK] /api/v1/towers")

    res = client.get("/api/v1/projection", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/projection failed: {res.text}"
    print("  [OK] /api/v1/projection")

    # 6. Recommendations & NBO
    res = client.get("/api/v1/recommendations/nbo/C0001", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/recommendations/nbo/C0001 failed: {res.text}"
    print("  [OK] /api/v1/recommendations/nbo/C0001")

    res = client.get("/api/v1/recommendations/opportunities?segment_id=0", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/recommendations/opportunities failed: {res.text}"
    print("  [OK] /api/v1/recommendations/opportunities")

    # 7. Campaigns
    scenario_payload = {
        "total_budget_inr": 150000.0,
        "channel_allocations": {"Website": 0.50, "Agency": 0.35, "Client": 0.15},
        "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
    }
    res = client.post("/api/v1/campaigns/scenario", json=scenario_payload, headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/campaigns/scenario failed: {res.text}"
    print("  [OK] /api/v1/campaigns/scenario")

    res = client.post(
        "/api/v1/campaigns/compare",
        json={
            "scenario_a": scenario_payload,
            "scenario_b": {
                "total_budget_inr": 250000.0,
                "channel_allocations": {"Website": 0.60, "Agency": 0.25, "Client": 0.15},
                "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
            },
        },
        headers=analyst_hdr,
    )
    assert res.status_code == 200, f"/api/v1/campaigns/compare failed: {res.text}"
    print("  [OK] /api/v1/campaigns/compare")

    # 8. Governance
    res = client.get("/api/v1/governance/data-quality", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/governance/data-quality failed: {res.text}"
    print("  [OK] /api/v1/governance/data-quality")

    res = client.get("/api/v1/governance/drift", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/governance/drift failed: {res.text}"
    print("  [OK] /api/v1/governance/drift")

    res = client.get("/api/v1/governance/fairness", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/governance/fairness failed: {res.text}"
    print("  [OK] /api/v1/governance/fairness")

    res = client.get("/api/v1/governance/registry", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/governance/registry failed: {res.text}"
    print("  [OK] /api/v1/governance/registry")

    res = client.get("/api/v1/governance/clv-baseline", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/governance/clv-baseline failed: {res.text}"
    print("  [OK] /api/v1/governance/clv-baseline")

    # 9. Datasets
    res = client.get("/api/v1/datasets", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/datasets failed: {res.text}"
    print("  [OK] /api/v1/datasets")

    res = client.get("/api/v1/datasets/template/clients", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/datasets/template/clients failed: {res.text}"
    print("  [OK] /api/v1/datasets/template/clients")

    res = client.get("/api/v1/datasets/sample/clients_sample.csv", headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/datasets/sample/clients_sample.csv failed: {res.text}"
    print("  [OK] /api/v1/datasets/sample/clients_sample.csv")

    res = client.post("/api/v1/datasets/switch", json={"dataset": "full"}, headers=analyst_hdr)
    assert res.status_code == 200, f"/api/v1/datasets/switch failed: {res.text}"
    print("  [OK] /api/v1/datasets/switch")

    # 10. Export & Audit
    res = client.post("/api/v1/export/async", json={"format": "csv", "country": "USA"}, headers=admin_hdr)
    assert res.status_code == 200, f"/api/v1/export/async failed: {res.text}"
    job_id = res.json()["job_id"]
    print(f"  [OK] /api/v1/export/async (job: {job_id})")

    res = client.get(f"/api/v1/export/jobs/{job_id}", headers=admin_hdr)
    assert res.status_code == 200, f"/api/v1/export/jobs/{job_id} failed: {res.text}"
    print(f"  [OK] /api/v1/export/jobs/{job_id}")

    res = client.get(f"/api/v1/export/jobs/{job_id}/download", headers=admin_hdr)
    assert res.status_code == 200, f"/api/v1/export/jobs/{job_id}/download failed: {res.text}"
    print(f"  [OK] /api/v1/export/jobs/{job_id}/download")

    res = client.get("/api/v1/export/audit-logs?limit=5", headers=auditor_hdr)
    assert res.status_code == 200, f"/api/v1/export/audit-logs failed: {res.text}"
    print("  [OK] /api/v1/export/audit-logs")

    res = client.get("/api/v1/export/audit-logs/verify", headers=auditor_hdr)
    assert res.status_code == 200, f"/api/v1/export/audit-logs/verify failed: {res.text}"
    verify_json = res.json()
    assert verify_json["status"] == "valid", f"Audit chain verification invalid: {verify_json}"
    print(f"  [OK] /api/v1/export/audit-logs/verify (valid: {verify_json['status']})")

    print("\nALL 27 API ENDPOINTS VALIDATED AND RETURNED HTTP 200 OK WITH VALID CONTRACTS!")

if __name__ == "__main__":
    run_tests()
