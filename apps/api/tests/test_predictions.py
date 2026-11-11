"""Tests for segment prediction endpoint and portfolio feature requirement."""

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token


def test_predict_segment_commercial_office_buyer(client: TestClient) -> None:
    """Verify inference for a 3-unit commercial buyer assigning to Segment 2 (Commercial Office Diversifiers)."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}
    payload = {
        "age": 45,
        "n_units": 3,
        "office_share": 0.33,
        "avg_floor_area": 1129.18,
        "portfolio_towers_hhi": 0.3333,
        "purchase_span_months": 6,
        "loan_applied": True,
        "client_type": "INDIVIDUAL",
        "acquisition_purpose": "INVESTMENT",
        "referral_channel": "Website",
        "country": "USA",
        "region": "California",
    }
    response = client.post("/api/v1/predict/segment", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["predicted_segment_id"] == 2
    assert data["predicted_segment_name"] == "Commercial Office Diversifiers"
    assert data["temperature_beta"] == 1.12
    assert "Cluster_2" in data["calibrated_soft_probabilities"]
    assert sum(data["calibrated_soft_probabilities"].values()) == pytest.approx(1.0, abs=0.01)
    assert data["calibrated_soft_probabilities"]["Cluster_2"] > 0.50
    # Neutral portfolio rationale enforced; demographic explanatory power claim omitted
    assert "trained on these behavioral and portfolio architecture features" in data["portfolio_requirement_rationale"]
    assert "less than 3%" not in data["portfolio_requirement_rationale"]
    assert data["metadata"]["is_unfiltered_model_space"] is True


def test_predict_segment_requires_portfolio_attributes(client: TestClient) -> None:
    """Verify endpoint rejects payloads lacking required portfolio attributes."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}
    demographic_only = {
        "age": 45,
        "client_type": "INDIVIDUAL",
        "acquisition_purpose": "INVESTMENT",
        "referral_channel": "Website",
        "country": "USA",
        "region": "California",
    }
    response = client.post("/api/v1/predict/segment", json=demographic_only, headers=headers)
    assert response.status_code == 422  # Missing required portfolio fields
