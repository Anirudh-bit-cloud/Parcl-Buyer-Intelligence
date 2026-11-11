"""Tests for /api/v1/export endpoint verifying RBAC 403, CSV export, filters, and INR currency."""

import csv
import io

from fastapi.testclient import TestClient

from apps.api.auth import create_access_token


def test_export_analyst_receives_403(client: TestClient) -> None:
    """Verify that callers with analyst role receive HTTP 403 Forbidden on data export."""
    analyst_token = create_access_token(subject="analyst_user", role="analyst")
    res = client.get("/api/v1/export", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res.status_code == 403
    assert "Admin privilege required" in res.json()["detail"]


def test_export_admin_receives_csv_by_default(client: TestClient) -> None:
    """Verify that admin callers receive a valid CSV response by default."""
    admin_token = create_access_token(subject="admin_user", role="admin")
    res = client.get("/api/v1/export", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=clients_export.csv" in res.headers.get("content-disposition", "")

    # Parse CSV content
    reader = csv.DictReader(io.StringIO(res.text))
    rows = list(reader)
    assert len(rows) == 2000  # All 2,000 cohort clients when unfiltered


def test_export_filters_respected(client: TestClient) -> None:
    """Verify that PRD filters (country, assigned_cluster) are strictly respected in export."""
    admin_token = create_access_token(subject="admin_user", role="admin")
    res = client.get(
        "/api/v1/export?country=USA&assigned_cluster=0",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    reader = csv.DictReader(io.StringIO(res.text))
    rows = list(reader)

    # In Model B3, USA clients in Cluster 0
    assert len(rows) > 0
    for r in rows:
        assert r["country"] == "USA"
        assert int(r["assigned_cluster"]) == 0
        assert r["assigned_segment_name"] == "Emerging Multi-Tower Accumulators"


def test_export_columns_in_inr_currency(client: TestClient) -> None:
    """Verify that export columns standardize on Indian Rupees (*_inr, display with ₹, currency=INR)."""
    admin_token = create_access_token(subject="admin_user", role="admin")
    res = client.get(
        "/api/v1/export?page_size=5",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    reader = csv.DictReader(io.StringIO(res.text))
    rows = list(reader)

    fieldnames = reader.fieldnames or []
    assert "total_spend_inr" in fieldnames
    assert "total_spend_display" in fieldnames
    assert "currency" in fieldnames

    for r in rows[:10]:
        assert r["currency"] == "INR"
        assert "₹" in r["total_spend_display"]
        assert float(r["total_spend_inr"]) > 0.0


def test_async_export_lifecycle(client: TestClient) -> None:
    """Verify asynchronous export creation, status check, download, and audit trail."""
    admin_token = create_access_token(subject="admin_user", role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Analyst cannot submit async job
    analyst_token = create_access_token(subject="analyst_user", role="analyst")
    res_forbidden = client.post(
        "/api/v1/export/async",
        json={"format": "csv", "country": "USA"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert res_forbidden.status_code == 403

    # 2. Admin submits async export job
    res_submit = client.post(
        "/api/v1/export/async",
        json={"format": "csv", "country": "USA"},
        headers=headers,
    )
    assert res_submit.status_code == 200
    data = res_submit.json()
    job_id = data["job_id"]
    assert job_id.startswith("job-")
    assert data["status"] == "completed"
    assert data["record_count"] > 0

    # 3. Check job status
    res_status = client.get(f"/api/v1/export/jobs/{job_id}", headers=headers)
    assert res_status.status_code == 200
    assert res_status.json()["job_id"] == job_id
    assert res_status.json()["status"] == "completed"

    # 4. Download generated export artifact
    res_download = client.get(f"/api/v1/export/jobs/{job_id}/download", headers=headers)
    assert res_download.status_code == 200
    assert res_download.headers["content-type"].startswith("text/csv")
    reader = csv.DictReader(io.StringIO(res_download.text))
    rows = list(reader)
    assert len(rows) == data["record_count"]

    # 5. Query security audit logs
    res_audit = client.get("/api/v1/export/audit-logs", headers=headers)
    assert res_audit.status_code == 200
    logs = res_audit.json()["logs"]
    assert len(logs) > 0
    actions = [entry["action"] for entry in logs]
    assert "EXPORT_ASYNC_CREATED" in actions
