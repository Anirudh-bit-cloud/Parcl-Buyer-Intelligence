"""Tests for data quality summary and model card governance reports."""

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token


def test_data_quality_report(client: TestClient) -> None:
    """Verify data quality lineage and empirical sensitivity audit numbers."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get(
        "/api/v1/governance/data-quality", headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["raw_clients_count"] == 2000
    assert data["raw_properties_count"] == 10000
    assert data["clean_sold_transactions"] == 7305
    assert data["clean_current_inventory"] == 313
    assert data["towers_count"] == 20
    assert data["reference_date"] == "2025-12-31"
    assert data["dob_sensitivity_age_switches"] == 0
    assert data["satisfaction_chi2"] == pytest.approx(1.990, abs=0.001)
    assert data["satisfaction_uniform_p"] == pytest.approx(0.7376, abs=0.001)


def test_model_card_and_truth_matrix(client: TestClient) -> None:
    """Verify model card benchmarks, beta grid, and PRD hypothesis matrix."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get(
        "/api/v1/governance/model-card", headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["production_variant"] == "Model_B3_Downweighted_Geo"
    assert data["k_selected"] == 4
    assert data["k2_silhouette"] == pytest.approx(0.5072, abs=0.001)
    assert data["k4_silhouette"] == pytest.approx(0.1211, abs=0.001)
    assert data["cophenetic_correlation"] == pytest.approx(0.9066, abs=0.001)
    assert data["bootstrap_stability_mean_ari"] == pytest.approx(0.7730, abs=0.01)
    assert data["sensitivity_ari_without_all_proxies"] == pytest.approx(0.2013, abs=0.001)
    assert len(data["beta_calibration_grid"]) == 25

    # Truth matrix has all 4 PRD hypotheses using PRD names, marked NOT SUPPORTED
    matrix = data["prd_truth_matrix"]
    assert len(matrix) == 4
    cluster_tags = [(item["prd_cluster"], item["prd_hypothesis_name"]) for item in matrix]
    expected_pairs = [
        ("C1", "Global Investors"),
        ("C2", "First-Time Buyers"),
        ("C3", "Corporate Buyers"),
        ("C4", "Luxury Investors"),
    ]
    assert cluster_tags == expected_pairs
    for item in matrix:
        assert item["empirical_verdict"] == "NOT SUPPORTED"

    # Confirm company share in C3 is 5.15%
    c3 = [m for m in matrix if m["prd_cluster"] == "C3"][0]
    assert "5.15%" in c3["data_reality_finding"]
    assert "~20%" not in c3["data_reality_finding"]

    # Confirm C4 does NOT cite price-only hit-rate
    c4 = [m for m in matrix if m["prd_cluster"] == "C4"][0]
    assert "hit-rate" not in c4["data_reality_finding"].lower()
    assert "price-only" not in c4["data_reality_finding"].lower()
