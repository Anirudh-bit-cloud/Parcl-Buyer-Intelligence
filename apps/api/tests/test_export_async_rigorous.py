"""Rigorous unit and failure-path test suite for asynchronous export jobs."""

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token
from apps.api.main import app


@pytest.fixture
def admin_client():
    token = create_access_token(subject="user-admin", role="admin")
    client = TestClient(app)
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


def test_async_export_job_lifecycle(admin_client: TestClient):
    """Test full asynchronous export job creation, status polling, and download."""
    # 1. Create job
    create_resp = admin_client.post(
        "/api/v1/export/async",
        json={"format": "csv", "filter_params": '{"country": "USA"}'},
    )
    assert create_resp.status_code == 200
    job_data = create_resp.json()
    job_id = job_data["job_id"]
    assert job_data["status"] in ["pending", "completed"]

    # 2. Poll status
    poll_resp = admin_client.get(f"/api/v1/export/jobs/{job_id}")
    assert poll_resp.status_code == 200
    poll_data = poll_resp.json()
    assert poll_data["job_id"] == job_id
    assert poll_data["format"] == "csv"

    # 3. Download generated file if completed
    if poll_data["status"] == "completed":
        dl_resp = admin_client.get(f"/api/v1/export/jobs/{job_id}/download")
        assert dl_resp.status_code == 200
        assert "text/csv" in dl_resp.headers.get("content-type", "")


def test_async_export_job_not_found(admin_client: TestClient):
    """Polling a non-existent job ID must return HTTP 404."""
    resp = admin_client.get("/api/v1/export/jobs/non-existent-uuid-999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_async_export_unsupported_format(admin_client: TestClient):
    """Requesting unsupported export format must return HTTP 422 or 400 validation error."""
    resp = admin_client.post(
        "/api/v1/export/async",
        json={"format": "unsupported_xyz_format"},
    )
    assert resp.status_code in [400, 422]
