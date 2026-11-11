"""Tests for dataset management, download, and switching endpoints."""

import io

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token
from apps.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_list_datasets(client: TestClient) -> None:
    res = client.get("/api/v1/datasets")
    assert res.status_code == 200
    data = res.json()
    assert "active_dataset" in data
    assert len(data["datasets"]) == 2
    names = [d["name"] for d in data["datasets"]]
    assert "full" in names
    assert "sample" in names


def test_switch_dataset(client: TestClient) -> None:
    # Switch to sample
    res = client.post("/api/v1/datasets/switch", json={"dataset": "sample"})
    assert res.status_code == 200
    assert res.json()["active_dataset"] == "sample"

    # Switch back to full
    res2 = client.post("/api/v1/datasets/switch", json={"dataset": "full"})
    assert res2.status_code == 200
    assert res2.json()["active_dataset"] == "full"

    # Invalid dataset
    res_err = client.post("/api/v1/datasets/switch", json={"dataset": "invalid"})
    assert res_err.status_code == 400


def test_download_sample_files(client: TestClient) -> None:
    res = client.get("/api/v1/datasets/sample/clients_sample.csv")
    assert res.status_code == 200
    assert "client_id" in res.text

    res_props = client.get("/api/v1/datasets/sample/properties_sample.csv")
    assert res_props.status_code == 200
    assert "listing_id" in res_props.text

    # Unknown file
    res_404 = client.get("/api/v1/datasets/sample/unknown.csv")
    assert res_404.status_code == 404


def test_download_templates(client: TestClient) -> None:
    res = client.get("/api/v1/datasets/template/clients")
    assert res.status_code == 200
    assert "client_id" in res.text

    res_p = client.get("/api/v1/datasets/template/properties")
    assert res_p.status_code == 200
    assert "listing_id" in res_p.text


def test_validate_dataset_auth(client: TestClient) -> None:
    csv_bytes = b"client_id,client_type\nC001,Individual\n"

    # Without token -> 401
    res_no_auth = client.post(
        "/api/v1/datasets/validate",
        files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert res_no_auth.status_code == 401

    # With analyst token -> 403
    analyst_token = create_access_token(subject="test_analyst", role="analyst")
    res_analyst = client.post(
        "/api/v1/datasets/validate",
        headers={"Authorization": f"Bearer {analyst_token}"},
        files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert res_analyst.status_code == 403

    # With admin token -> 200 (validation report)
    admin_token = create_access_token(subject="test_admin", role="admin")
    res_admin = client.post(
        "/api/v1/datasets/validate",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert res_admin.status_code == 200
    report = res_admin.json()
    assert "is_valid" in report
    assert report["dataset_type"] == "clients"
