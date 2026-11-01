"""Tests for Marketing Scenario Calculator, aliases, and referral channel independence."""

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token


def test_marketing_scenario_calculator_valid(client: TestClient) -> None:
    """Verify marketing calculator outputs modeled gross sales volume and empirical test stats."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}
    payload = {
        "total_budget_inr": 100000.0,
        "channel_allocations": {"Website": 0.50, "Agency": 0.35, "Client": 0.15},
        "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
    }
    response = client.post("/api/v1/campaigns/scenario", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total_budget_inr"] == 100000.0
    assert data["total_modeled_clients"] == 60.0
    assert data["total_modeled_gross_sales_volume_inr"] == pytest.approx(75881028.0, abs=1.0)
    assert "₹7,58,81,028" in data["total_modeled_gross_sales_display"]
    assert "gross sales volume (GMV)" in data["revenue_label_notice"]

    # Verify channel breakdown
    assert len(data["channel_breakdown"]) == 3
    web = data["channel_breakdown"]["Website"]
    assert web["allocated_budget_inr"] == 50000.0
    assert web["modeled_clients_acquired"] == pytest.approx(41.67, abs=0.1)

    # Verify empirical independence finding
    finding = data["channel_targeting_empirical_finding"]
    assert finding["spend_difference_pct"] == 2.83
    assert finding["spend_anova_f"] == pytest.approx(2.1176, abs=0.01)
    assert finding["segment_mix_chi2"] == pytest.approx(0.7500, abs=0.01)
    assert finding["segment_mix_p"] == pytest.approx(0.9933, abs=0.01)


def test_marketing_scenario_aliases(client: TestClient) -> None:
    """Verify /api/v1/campaigns/allocate and /api/v1/campaigns/simulate aliases work identically to /scenario."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}
    payload = {
        "total_budget_inr": 100000.0,
        "channel_allocations": {"Website": 0.50, "Agency": 0.35, "Client": 0.15},
        "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
    }
    res_alloc = client.post("/api/v1/campaigns/allocate", json=payload, headers=headers)
    assert res_alloc.status_code == 200
    assert res_alloc.json()["total_modeled_clients"] == 60.0

    res_sim = client.post("/api/v1/campaigns/simulate", json=payload, headers=headers)
    assert res_sim.status_code == 200
    assert res_sim.json()["total_modeled_clients"] == 60.0


def test_marketing_scenario_invalid_allocation_sum(client: TestClient) -> None:
    """Verify rejection when allocations do not sum to 1.0."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}
    payload = {
        "total_budget_inr": 100000.0,
        "channel_allocations": {"Website": 0.40, "Agency": 0.30, "Client": 0.10},  # sum 0.80
        "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
    }
    response = client.post("/api/v1/campaigns/scenario", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Channel allocations must sum to 1.0" in response.json()["detail"]


def test_marketing_scenario_negative_budget(client: TestClient) -> None:
    """Verify rejection of negative or zero total budget."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}
    payload = {
        "total_budget_inr": -5000.0,
        "channel_allocations": {"Website": 0.50, "Agency": 0.35, "Client": 0.15},
        "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
    }
    response = client.post("/api/v1/campaigns/scenario", json=payload, headers=headers)
    assert response.status_code == 422  # Pydantic gt=0 validation error
