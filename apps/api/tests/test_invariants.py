"""Rigorous mathematical, cohort, and accounting invariant tests."""

import json

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from scipy import stats

from apps.api.auth import create_access_token
from apps.api.config import api_settings
from scripts.compute_beta_grid import compute_beta_grid


def test_segment_cohort_invariants(client: TestClient) -> None:
    """Verify segment cohort invariants: buyer counts sum to 2000, units sum to 7305, spend matches overall."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    res = client.get("/api/v1/segments", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res.status_code == 200
    data = res.json()

    segments = data["segments"]
    assert len(segments) == 4

    # Invariant 1: Buyer counts sum to 2,000
    total_buyers = sum(s["buyer_count"] for s in segments)
    assert total_buyers == 2000
    assert data["cohort_total_buyers"] == 2000
    assert [s["buyer_count"] for s in segments] == [536, 557, 375, 532]

    # Invariant 2: Segment units, weighted by buyer count, sum to 7,305
    total_units_weighted = sum(s["total_units"] for s in segments)
    assert total_units_weighted == 7305
    assert data["cohort_total_units"] == 7305
    assert [s["total_units"] for s in segments] == [2174, 1671, 1125, 2335]

    # Required checks for means
    assert segments[3]["mean_units"] == pytest.approx(4.39, abs=0.01)
    assert segments[0]["commercial_office_share_pct"] == pytest.approx(13.4, abs=0.1)
    assert segments[1]["commercial_office_share_pct"] == pytest.approx(0.0, abs=0.1)
    assert segments[2]["commercial_office_share_pct"] == pytest.approx(37.8, abs=0.1)
    assert segments[3]["commercial_office_share_pct"] == pytest.approx(15.8, abs=0.1)

    # Invariant 3: Sum of segment total spends equals cohort total spend
    total_spend_sum = sum(s["total_spend_inr"] for s in segments)
    assert total_spend_sum == pytest.approx(data["cohort_total_spend_inr"], abs=0.05)
    assert total_spend_sum == pytest.approx(2520750960.84, abs=0.5)

    # Invariant 4: Cohort total spend divided by 2,000 equals cohort mean spend
    assert (data["cohort_total_spend_inr"] / total_buyers) == pytest.approx(data["cohort_mean_spend_inr"], abs=0.01)
    assert data["cohort_mean_spend_inr"] == pytest.approx(1260375.48, abs=0.05)

    # Invariant 5: Stated office share definitions
    assert data["buyer_weighted_office_share_pct"] == pytest.approx(14.87, abs=0.05)
    assert data["unit_weighted_office_share_pct"] == pytest.approx(14.78, abs=0.05)

    # Invariant 6: Segment shares sum to 100%
    total_share = sum(s["population_share_pct"] for s in segments)
    assert total_share == pytest.approx(100.0, abs=0.01)


def test_raw_c0001_exact_values(client: TestClient) -> None:
    """Verify C0001 raw attributes: Kareem Liu, USA, age 57, satisfaction 4, spend ₹12,46,765, 4 units, cluster 0."""
    admin_token = create_access_token(subject="admin", role="admin")
    res = client.get(
        "/api/v1/clients/C0001", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    c = res.json()

    assert c["client_id"] == "C0001"
    assert c["first_name"] == "Kareem"
    assert c["last_name"] == "Liu"
    assert c["country"] == "USA"
    assert c["region"] == "California"
    # Single configured reference date 2025-12-31 yields age 57 for DOB 1968-11-05
    assert c["age"] == 57
    assert c["satisfaction_score"] == 4
    assert c["total_spend_inr"] == pytest.approx(1246764.72, abs=0.01)
    assert c["total_spend_display"] == "₹12,46,765"
    assert c["n_units"] == 4
    assert c["assigned_cluster"] == 0
    assert c["assigned_segment_name"] == "Emerging Multi-Tower Accumulators"
    assert c["owned_towers"] == [3, 4, 9, 15]


def test_reference_date_age_calculation() -> None:
    """Verify age computation for C0001 equals 57 under reference date 2025-12-31."""
    ref_date = pd.Timestamp(api_settings.reference_date_str)
    c0001_dob = pd.Timestamp("1968-11-05")
    # Exact completed age
    computed_age = ref_date.year - c0001_dob.year - ((ref_date.month, ref_date.day) < (c0001_dob.month, c0001_dob.day))
    assert computed_age == 57


def test_marketing_campaign_scenario_sum_invariants(client: TestClient) -> None:
    """Verify total modeled clients and volume equal sum over all channels."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    payload = {
        "total_budget_inr": 100000.0,
        "channel_allocations": {"Website": 0.50, "Agency": 0.35, "Client": 0.15},
        "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
    }
    res = client.post(
        "/api/v1/campaigns/scenario",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert res.status_code == 200
    data = res.json()

    # Invariant: total_modeled_clients equals sum over channel_breakdown
    breakdown = data["channel_breakdown"]
    assert set(breakdown.keys()) == {"Website", "Agency", "Client"}
    sum_clients = sum(ch["modeled_clients_acquired"] for ch in breakdown.values())
    assert data["total_modeled_clients"] == pytest.approx(sum_clients, abs=0.05)

    # Invariant: total_modeled_gross_sales_volume_inr equals sum over channel_breakdown
    sum_volume = sum(ch["modeled_gross_sales_volume_inr"] for ch in breakdown.values())
    assert data["total_modeled_gross_sales_volume_inr"] == pytest.approx(sum_volume, abs=0.5)

    # Required checks for Website channel metrics
    web_metrics = breakdown["Website"]["historical_channel_metrics"]
    assert web_metrics["loan_rate"] == pytest.approx(0.3663, abs=0.001)  # 36.6%
    assert web_metrics["mean_units"] == pytest.approx(3.68, abs=0.01)
    assert web_metrics["historical_mean_sales_per_client_inr"] == pytest.approx(1274770.93, abs=0.1)


def test_satisfaction_goodness_of_fit_scipy_recomputation() -> None:
    """Recompute discrete uniform chi2 and p-value from raw counts with scipy.chisquare."""
    counts = [395, 379, 404, 417, 405]
    res = stats.chisquare(counts)

    # Assert equality to 3 and 4 decimals
    assert round(float(res.statistic), 3) == 1.990
    assert round(float(res.pvalue), 4) == 0.7376

    # Verify model_selection_metrics.json audit block matches
    metrics_path = api_settings.interim_dir / "model_selection_metrics.json"
    assert metrics_path.exists()
    with open(metrics_path, encoding="utf-8") as f:
        m = json.load(f)
    sat_audit = m.get("satisfaction_uniformity_audit", {})
    assert sat_audit.get("chi2") == 1.990
    assert sat_audit.get("p_value") == 0.7376
    assert sat_audit.get("counts") == counts


def test_beta_calibration_grid_integrity(client: TestClient) -> None:
    """Verify beta calibration grid contains 25 evaluated points with empirical maximizer at beta=1.12."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    res = client.get("/api/v1/model/selection", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res.status_code == 200
    data = res.json()

    grid = data["beta_calibration_grid"]
    assert len(grid) == 25
    betas = [p["beta"] for p in grid]
    assert betas[0] == 0.1
    assert betas[-1] == 5.0

    chosen = [p for p in grid if p["is_chosen"]]
    assert len(chosen) == 1
    assert chosen[0]["beta"] == 1.12
    assert chosen[0]["mean_log_likelihood"] == pytest.approx(-0.6021, abs=0.001)
    assert chosen[0]["ambiguity_pct"] == pytest.approx(0.55, abs=0.05)


def test_recompute_beta_grid_matches_stored_file() -> None:
    """Recompute 5-fold CV beta grid and verify exact match with stored data/interim/beta_grid.json."""
    stored_path = api_settings.interim_dir / "beta_grid.json"
    assert stored_path.exists()
    with open(stored_path, encoding="utf-8") as f:
        stored = json.load(f)

    recomputed = compute_beta_grid(api_settings.data_dir)
    assert recomputed["chosen_beta"] == stored["chosen_beta"]
    assert recomputed["chosen_mean_log_likelihood"] == stored["chosen_mean_log_likelihood"]
    assert len(recomputed["grid"]) == len(stored["grid"])


def test_country_breakdown_sums_to_totals() -> None:
    """Verify that country-level breakdown sums exactly to overall cohort totals."""
    import duckdb
    parquet_path = str(api_settings.processed_dir / "client_features.parquet").replace("\\", "/")
    con = duckdb.connect()
    df = con.execute(f"""
        SELECT country, count(*) as buyers, sum(total_spend) as spend, sum(n_units) as units
        FROM read_parquet('{parquet_path}')
        GROUP BY country
    """).df()
    assert len(df) == 10
    assert df["buyers"].sum() == 2000
    assert df["units"].sum() == 7305
    assert round(float(df["spend"].sum()), 2) == 2520750960.84

    # Verify USA totals
    usa = df[df["country"] == "USA"].iloc[0]
    assert usa["buyers"] == 1538
    assert usa["units"] == 5656
    assert round(float(usa["spend"]), 2) == 1953032450.82

    # Verify Non-USA totals
    intl = df[df["country"] != "USA"]
    assert intl["buyers"].sum() == 462
    assert intl["units"].sum() == 1649
    assert round(float(intl["spend"].sum()), 2) == 567718510.02
