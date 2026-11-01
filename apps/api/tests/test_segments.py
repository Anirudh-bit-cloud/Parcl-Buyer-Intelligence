"""Tests for segment catalog, detail profiles, silhouette policy, and cohort filtering."""

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token


def test_segments_catalog_and_validation_framing(client: TestClient) -> None:
    """Verify segment catalog exposes all 4 segments with weak-cluster policy metadata."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get("/api/v1/segments", headers={"Authorization": f"Bearer {analyst_token}"})
    assert response.status_code == 200
    data = response.json()

    assert data["k_selected"] == 4
    assert len(data["segments"]) == 4

    # Verify canonical Phase 3 segment names
    expected_names = [
        "Emerging Multi-Tower Accumulators",
        "Concentrated Residential Buyers",
        "Commercial Office Diversifiers",
        "Established Senior Estate Investors",
    ]
    actual_names = [s["segment_name"] for s in data["segments"]]
    assert actual_names == expected_names

    # Verify silhouette context
    sil = data["silhouette_validation"]
    assert sil["k2_strong_macrostructure_silhouette"] == pytest.approx(0.5072, abs=0.001)
    assert sil["k4_weak_substructure_silhouette"] == pytest.approx(0.1211, abs=0.001)
    assert "Weak Cluster Policy Triggered" in sil["soft_behavioral_tendencies_framing"]

    # Verify sum of segment sizes equals 2000
    total_buyers = sum(s["buyer_count"] for s in data["segments"])
    assert total_buyers == 2000
    assert data["cohort_total_buyers"] == 2000
    assert data["cohort_total_units"] == 7305


def test_segment_detail_and_surrogate_rules(client: TestClient) -> None:
    """Verify deep-dive statistical distributions and surrogate splitting rules."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    for s_id in range(4):
        response = client.get(f"/api/v1/segments/{s_id}", headers={"Authorization": f"Bearer {analyst_token}"})
        assert response.status_code == 200
        data = response.json()

        assert data["segment_id"] == s_id
        assert data["buyer_count"] > 100  # Business viability constraint
        assert len(data["surrogate_rules"]) >= 1
        assert "numeric_metrics" in data
        assert "categorical_distributions" in data
        assert "₹" in data["mean_spend_display"]
        assert "₹" in data["total_spend_display"]


def test_segment_detail_not_found(client: TestClient) -> None:
    """Verify 404 for invalid segment ID."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get("/api/v1/segments/99", headers={"Authorization": f"Bearer {analyst_token}"})
    assert response.status_code == 404


def test_segment_statistics_under_country_filter(client: TestClient) -> None:
    """Verify country=USA recomputes segment counts, units, and spend dynamically while invariants hold."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get("/api/v1/segments?country=USA", headers={"Authorization": f"Bearer {analyst_token}"})
    assert response.status_code == 200
    data = response.json()

    assert data["active_filters"]["country"] == "USA"
    assert data["metadata"]["is_unfiltered_model_space"] is False

    usa_buyers = data["cohort_total_buyers"]
    assert usa_buyers < 2000  # Subset of cohort
    assert usa_buyers > 500

    # Invariant 1: Sum of filtered segment buyer counts equals filtered cohort total buyers
    sum_buyers = sum(s["buyer_count"] for s in data["segments"])
    assert sum_buyers == usa_buyers

    # Invariant 2: Sum of filtered segment units equals filtered cohort total units
    sum_units = sum(s["total_units"] for s in data["segments"])
    assert sum_units == data["cohort_total_units"]

    # Invariant 3: Sum of filtered segment total spends equals filtered cohort total spend
    sum_spends = sum(s["total_spend_inr"] for s in data["segments"])
    assert sum_spends == pytest.approx(data["cohort_total_spend_inr"], abs=0.5)

    # Invariant 4: Filtered cohort total spend / total buyers equals filtered mean spend
    assert (data["cohort_total_spend_inr"] / usa_buyers) == pytest.approx(data["cohort_mean_spend_inr"], abs=0.05)


def test_cluster_names_match_defining_conditions(client: TestClient) -> None:
    """Verify each cluster name matches its empirical defining traits."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get("/api/v1/segments", headers={"Authorization": f"Bearer {analyst_token}"})
    assert response.status_code == 200
    segments = {s["segment_id"]: s for s in response.json()["segments"]}

    # Cluster 0: Emerging Multi-Tower Accumulators (units > 3.5, age < 50)
    c0 = segments[0]
    assert c0["segment_name"] == "Emerging Multi-Tower Accumulators"
    assert c0["mean_units"] > 3.5
    assert c0["mean_units"] == pytest.approx(4.06, abs=0.05)
    assert c0["mean_age"] < 50.0
    assert c0["mean_age"] == pytest.approx(42.05, abs=0.1)

    # Cluster 1: Concentrated Residential Buyers (units <= 3.2, office < 0.05)
    c1 = segments[1]
    assert c1["segment_name"] == "Concentrated Residential Buyers"
    assert c1["mean_units"] <= 3.2
    assert c1["mean_units"] == pytest.approx(3.00, abs=0.01)
    assert c1["commercial_office_share_pct"] < 0.05
    assert c1["commercial_office_share_pct"] == pytest.approx(0.0, abs=0.01)

    # Cluster 2: Commercial Office Diversifiers (units <= 3.2, office >= 0.05)
    c2 = segments[2]
    assert c2["segment_name"] == "Commercial Office Diversifiers"
    assert c2["mean_units"] <= 3.2
    assert c2["mean_units"] == pytest.approx(3.00, abs=0.01)
    assert c2["commercial_office_share_pct"] >= 5.0
    assert c2["commercial_office_share_pct"] == pytest.approx(37.78, abs=0.1)

    # Cluster 3: Established Senior Estate Investors (units > 3.5, age >= 50)
    c3 = segments[3]
    assert c3["segment_name"] == "Established Senior Estate Investors"
    assert c3["mean_units"] > 3.5
    assert c3["mean_units"] == pytest.approx(4.39, abs=0.05)
    assert c3["mean_age"] >= 50.0
    assert c3["mean_age"] == pytest.approx(69.21, abs=0.1)
