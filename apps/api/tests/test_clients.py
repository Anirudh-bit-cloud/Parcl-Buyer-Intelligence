"""Tests for client directory, PRD filtering, and role-based name masking."""

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token


def test_clients_pagination_defaults(client: TestClient) -> None:
    """Verify default pagination parameters on client directory."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get("/api/v1/clients", headers={"Authorization": f"Bearer {analyst_token}"})
    assert response.status_code == 200
    data = response.json()

    assert len(data["clients"]) == 20
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 20
    assert data["pagination"]["total_records"] == 2000
    assert data["pagination"]["total_pages"] == 100
    assert data["metadata"]["as_of"] == "December 2025"
    assert data["metadata"]["currency"] == "INR"
    assert data["metadata"]["currency_symbol"] == "₹"
    assert data["metadata"]["is_unfiltered_model_space"] is False


def test_clients_role_based_name_masking(client: TestClient) -> None:
    """Verify names are masked server-side unless user role is explicitly 'admin'."""
    analyst_token = create_access_token(subject="user", role="analyst")
    admin_token = create_access_token(subject="user", role="admin")

    # Default / analyst role (masked)
    res_analyst = client.get(
        "/api/v1/clients?page_size=5", headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res_analyst.status_code == 200
    c_analyst = res_analyst.json()["clients"][0]
    assert c_analyst["first_name"].endswith("***")
    assert c_analyst["last_name"].endswith("***")

    # Admin role (unmasked plain text)
    res_admin = client.get(
        "/api/v1/clients?page_size=5", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_admin.status_code == 200
    c_admin = res_admin.json()["clients"][0]
    assert not c_admin["first_name"].endswith("***")
    assert not c_admin["last_name"].endswith("***")
    assert c_admin["client_id"] == c_analyst["client_id"]


def test_clients_prd_filters(client: TestClient) -> None:
    """Verify PRD filters (country, region, acquisition_purpose, client_type)."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}

    # Country filter
    res_country = client.get("/api/v1/clients?country=USA&page_size=50", headers=headers)
    assert res_country.status_code == 200
    d_country = res_country.json()
    assert d_country["pagination"]["total_records"] == 1538  # 76.9% of 2000
    assert all(c["country"] == "USA" for c in d_country["clients"])

    # Acquisition purpose and client type filter
    res_filtered = client.get(
        "/api/v1/clients?country=USA&acquisition_purpose=INVESTMENT&client_type=COMPANY",
        headers=headers,
    )
    assert res_filtered.status_code == 200
    d_filtered = res_filtered.json()
    assert all(c["client_type"] == "COMPANY" for c in d_filtered["clients"])


def test_client_detail_profile_and_transactions(client: TestClient) -> None:
    """Verify deep-dive individual buyer profile returns all real portfolio purchases."""
    admin_token = create_access_token(subject="admin", role="admin")
    response = client.get("/api/v1/clients/C0001", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()

    assert data["client_id"] == "C0001"
    assert data["first_name"] == "Kareem"
    assert data["last_name"] == "Liu"
    assert data["country"] == "USA"
    assert data["region"] == "California"
    assert data["age"] == 57
    assert data["satisfaction_score"] == 4
    assert data["total_spend_inr"] == pytest.approx(1246764.72, abs=0.01)
    assert data["total_spend_display"] == "₹12,46,765"
    assert data["n_units"] == 4
    assert len(data["transactions"]) == 4
    assert data["owned_towers"] == [3, 4, 9, 15]
    assert data["assigned_cluster"] == 0
    assert data["assigned_segment_name"] == "Emerging Multi-Tower Accumulators"
    assert "soft_membership_probabilities" in data
    assert sum(data["soft_membership_probabilities"].values()) == pytest.approx(1.0, abs=0.01)


def test_client_detail_not_found(client: TestClient) -> None:
    """Verify 404 for non-existent client ID."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get("/api/v1/clients/C9999", headers={"Authorization": f"Bearer {analyst_token}"})
    assert response.status_code == 404
