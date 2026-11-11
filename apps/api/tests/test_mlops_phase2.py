"""Tests for Phase 2 ML/MLOps: Drift, Registry, Fairness, Surrogate Tree Metrics, and Campaign Compare."""

import numpy as np
from fastapi.testclient import TestClient
from parcl_core.drift import calculate_psi

from apps.api.auth import create_access_token


def test_psi_calculation_stable_distribution() -> None:
    """Verify that identical distributions yield PSI close to 0 (< 0.10)."""
    np.random.seed(42)
    ref = np.random.normal(100, 15, 1000)
    curr = np.random.normal(100, 15, 1000)
    psi, buckets = calculate_psi(ref, curr, num_buckets=8)
    assert psi < 0.10
    assert len(buckets) > 0


def test_psi_calculation_drifted_distribution() -> None:
    """Verify that substantially shifted distributions trigger high PSI (> 0.25)."""
    np.random.seed(42)
    ref = np.random.normal(100, 15, 1000)
    curr = np.random.normal(150, 25, 1000)
    psi, _ = calculate_psi(ref, curr, num_buckets=8)
    assert psi > 0.25


def test_drift_and_fairness_endpoints(client: TestClient) -> None:
    """Verify API endpoints for drift monitoring, algorithmic fairness, and model registry."""
    analyst_token = create_access_token(subject="analyst_user", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}

    # 1. Drift Monitoring
    res_drift = client.get("/api/v1/governance/drift", headers=headers)
    assert res_drift.status_code == 200
    d_data = res_drift.json()
    assert d_data["status"] in ["HEALTHY", "WARNING", "CRITICAL"]
    assert "feature_drift" in d_data
    assert len(d_data["feature_drift"]) >= 3

    # 2. Algorithmic Fairness Audit
    res_fair = client.get("/api/v1/governance/fairness", headers=headers)
    assert res_fair.status_code == 200
    f_data = res_fair.json()
    assert f_data["status"] in ["DESCRIPTIVE_DISPARITY_REPORT", "PASS_AUDITED"]
    assert "country_demographic_parity" in f_data

    # 3. Model Registry & Metadata
    res_reg = client.get("/api/v1/governance/registry", headers=headers)
    assert res_reg.status_code == 200
    r_data = res_reg.json()
    assert r_data["model_id"] == "parcl-buyer-segmentation-b3"
    assert "git_commit" in r_data
    assert "dataset_hash" in r_data
    if "surrogate_tree_report" in r_data:
        assert r_data["surrogate_tree_report"]["fidelity_accuracy"] >= 0.90
        assert len(r_data["surrogate_tree_report"]["confusion_matrix"]) == 4

    # 4. Experimental CLV Baseline
    res_clv = client.get("/api/v1/governance/clv-baseline", headers=headers)
    assert res_clv.status_code == 200
    clv_data = res_clv.json()
    assert clv_data["status"] == "EXPERIMENTAL_BASELINE"
    assert len(clv_data["segments"]) == 4


def test_campaign_scenario_compare(client: TestClient) -> None:
    """Verify side-by-side scenario comparison endpoint with delta ROI."""
    analyst_token = create_access_token(subject="analyst_user", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}

    payload = {
        "scenario_a": {
            "total_budget_inr": 100000.0,
            "channel_allocations": {"Website": 0.50, "Agency": 0.35, "Client": 0.15},
            "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
        },
        "scenario_b": {
            "total_budget_inr": 200000.0,
            "channel_allocations": {"Website": 0.60, "Agency": 0.20, "Client": 0.20},
            "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
        },
    }

    res = client.post("/api/v1/campaigns/compare", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["budget_delta_inr"] == 100000.0
    assert data["clients_delta"] > 0
    assert data["sales_delta_inr"] > 0
