"""Tests for /api/v1/health and root discovery endpoints."""

from fastapi.testclient import TestClient


def test_health_check_returns_ok_and_metadata(client: TestClient) -> None:
    """Verify health endpoint reports online status and exact dataset microdata counts."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "Parcl Buyer Intelligence API"
    assert data["version"] == "1.2.0"
    assert data["currency"] == "INR"
    assert data["currency_symbol"] == "₹"
    assert data["reference_date"] == "2025-12-31"
    assert data["datasets"]["clients_count"] == 2000
    assert data["datasets"]["transactions_count"] == 7305
    assert data["datasets"]["current_available_inventory"] == 313
    assert data["datasets"]["towers_count"] == 20
    assert data["datasets"]["as_of"] == "December 2025"


def test_root_endpoint(client: TestClient) -> None:
    """Verify root GET endpoint responds with discovery links and INR currency."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["as_of"] == "December 2025"
    assert data["currency"] == "INR"
    assert "/docs" in data["docs"]
