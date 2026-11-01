"""Unit tests for Phase 4: Opportunity Finder, NBO Engine, Scenario Calculator, and Microdata Invariants."""

import json
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from parcl_core.recommend import (
    OpportunityScoringWeights,
    backtest_opportunity_finder,
    calculate_marketing_scenario,
    compute_segment_inventory_rank_correlations,
    recommend_next_best_offers_for_client,
    score_inventory_for_segment,
)


@pytest.fixture
def phase4_data() -> dict[str, Any]:
    """Load processed datasets and metrics bundle for Phase 4 testing."""
    root = Path("e:/parcl-buyer-intelligence")
    available_df = pd.read_parquet(root / "data/processed/available_properties.parquet")
    client_features = pd.read_parquet(root / "data/processed/client_features.parquet")
    transactions = pd.read_parquet(root / "data/processed/transactions_clean.parquet")
    with open(root / "data/interim/model_selection_metrics.json", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(root / "data/interim/phase_4_metrics.json", encoding="utf-8") as f:
        phase4_metrics = json.load(f)

    return {
        "available_properties": available_df,
        "client_features": client_features,
        "transactions_clean": transactions,
        "cluster_profiles": metrics["cluster_profiles"],
        "phase_4_metrics": phase4_metrics,
        "model_selection_metrics": metrics,
    }


def test_weights_validation() -> None:
    """Test heuristic weights sum validation."""
    valid_weights = OpportunityScoringWeights(0.35, 0.30, 0.20, 0.15)
    valid_weights.validate()

    invalid_weights = OpportunityScoringWeights(0.5, 0.5, 0.5, 0.5)
    with pytest.raises(ValueError, match="Weights must sum to 1.0"):
        invalid_weights.validate()


def test_score_inventory_for_segment(phase4_data: dict[str, Any]) -> None:
    """Test inventory scoring runs over deduplicated available properties (313 units)."""
    available_df = phase4_data["available_properties"]
    assert len(available_df) == 313

    # Score for Segment 1 (Pure Residential Multi-Tower Buyers)
    scored = score_inventory_for_segment(
        available_properties=available_df,
        segment_id=1,
        cluster_profiles=phase4_data["cluster_profiles"],
        transactions_clean=phase4_data["transactions_clean"],
        client_features=phase4_data["client_features"],
    )

    assert len(scored) == 313
    assert "affinity_score" in scored.columns
    assert "heuristic_assumption" in scored.columns
    assert (scored["affinity_score"] >= 0.0).all()
    assert (scored["affinity_score"] <= 1.0).all()

    # Segment 1 top recommended units should be Apartments
    top_3 = scored.head(3)
    assert (top_3["unit_category"] == "Apartment").all()


def test_score_inventory_invalid_segment(phase4_data: dict[str, Any]) -> None:
    """Test error handling for non-existent segment ID."""
    with pytest.raises(ValueError, match="Segment Cluster_99 not found"):
        score_inventory_for_segment(
            available_properties=phase4_data["available_properties"],
            segment_id=99,
            cluster_profiles=phase4_data["cluster_profiles"],
            transactions_clean=phase4_data["transactions_clean"],
            client_features=phase4_data["client_features"],
        )


def test_opportunity_finder_client_backtest(phase4_data: dict[str, Any]) -> None:
    """Test Opportunity Finder backtest split strictly by client with baseline comparisons."""
    transactions = phase4_data["transactions_clean"]
    client_features = phase4_data["client_features"]
    profiles = phase4_data["cluster_profiles"]

    backtest = backtest_opportunity_finder(
        transactions_clean=transactions,
        client_features=client_features,
        cluster_profiles=profiles,
        n_splits=5,
    )

    # Full model performance
    full = backtest["full_model"]
    assert full["hit_rate_pct"] > 45.0
    assert full["mrr"] > 0.68

    # Lift over uniform random guessing (25%)
    lifts = backtest["lift_metrics"]
    assert lifts["lift_over_random_multiple"] >= 1.80

    # Category leakage addressal: no-category model (price + area + tower) still achieves high hit rate
    no_cat = backtest["baselines_and_ablations"]["no_category_ablation"]
    assert no_cat["hit_rate_pct"] > 44.0

    # Client-level tower test shows massive statistical significance
    tower_test = backtest["client_level_tower_test"]
    assert tower_test["chi2_statistic"] > 4000.0
    assert tower_test["p_value"] < 0.0001


def test_segment_inventory_rank_correlations(phase4_data: dict[str, Any]) -> None:
    """Test rank correlation of scores between segments confirms indistinguishable macro-cohorts."""
    corrs = compute_segment_inventory_rank_correlations(
        available_properties=phase4_data["available_properties"],
        cluster_profiles=phase4_data["cluster_profiles"],
        transactions_clean=phase4_data["transactions_clean"],
        client_features=phase4_data["client_features"],
    )

    pairwise = corrs["pairwise_unique"]
    # S0 vs S3 are virtually identical in property ranking
    assert pairwise["Cluster_0_vs_Cluster_3"] > 0.99
    # S1 vs S2 are also highly correlated in property ranking
    assert pairwise["Cluster_1_vs_Cluster_2"] > 0.94


def test_recommend_next_best_offers_for_client(phase4_data: dict[str, Any]) -> None:
    """Test NBO recommendations generation for client C0001 (Cluster 0) on deduplicated inventory."""
    client_features = phase4_data["client_features"]
    transactions = phase4_data["transactions_clean"]
    available_df = phase4_data["available_properties"]

    c1_trans = transactions[transactions["client_ref"] == "C0001"]
    owned_towers = sorted(c1_trans["tower_number"].unique())
    # C0001 owns towers 3, 4, 9, 15 out of 20
    assert owned_towers == [3, 4, 9, 15]

    nbos = recommend_next_best_offers_for_client(
        client_id="C0001",
        client_features=client_features,
        transactions_clean=transactions,
        available_properties=available_df,
        cluster_profiles=phase4_data["cluster_profiles"],
        top_n=5,
    )

    assert len(nbos) == 5
    for item in nbos:
        assert item["client_segment_id"] == 0
        assert item["final_nbo_score"] >= 0.0
        assert item["listing_id"] in set(available_df["listing_id"])
        assert 1 <= item["unit_number"] <= 70
        assert 1 <= item["tower_number"] <= 20
        assert "untested_assumption_note" in item


def test_marketing_scenario_calculator_success(phase4_data: dict[str, Any]) -> None:
    """Test scenario calculation with valid channel set and illustrative user CPAs."""
    client_features = phase4_data["client_features"]

    valid_allocations = {"Website": 0.50, "Agency": 0.35, "Client": 0.15}
    user_cpas = {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0}

    scenario = calculate_marketing_scenario(
        total_budget=100_000.0,
        channel_allocations=valid_allocations,
        channel_cpas=user_cpas,
        client_features=client_features,
    )

    assert scenario["total_budget"] == 100_000.0
    assert scenario["total_modeled_clients"] > 0
    assert scenario["total_modeled_gross_sales_volume"] > 0
    assert "revenue_label_notice" in scenario
    assert "channel_targeting_empirical_finding" in scenario
    finding = scenario["channel_targeting_empirical_finding"]
    assert "DOES NOT SUPPORT" in finding["conclusion"]
    assert finding["segment_mix_chi2"] == pytest.approx(0.75, abs=0.05)


def test_allocator_constraints(phase4_data: dict[str, Any]) -> None:
    """Test marketing allocator input validation constraints."""
    client_features = phase4_data["client_features"]
    valid_allocations = {"Website": 0.50, "Agency": 0.35, "Client": 0.15}
    valid_cpas = {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0}

    # Negative budget
    with pytest.raises(ValueError, match="total_budget must be positive"):
        calculate_marketing_scenario(
            total_budget=-5000.0,
            channel_allocations=valid_allocations,
            channel_cpas=valid_cpas,
            client_features=client_features,
        )

    # Invalid channels (e.g. Broker)
    invalid_channels = {"Website": 0.50, "Broker": 0.50}
    with pytest.raises(ValueError, match="Channels must match exact empirical set"):
        calculate_marketing_scenario(
            total_budget=50_000.0,
            channel_allocations=invalid_channels,
            channel_cpas=valid_cpas,
            client_features=client_features,
        )

    # Non-summing allocations
    bad_sum = {"Website": 0.50, "Agency": 0.30, "Client": 0.10}
    with pytest.raises(ValueError, match="Channel allocations must sum to 1.0"):
        calculate_marketing_scenario(
            total_budget=50_000.0,
            channel_allocations=bad_sum,
            channel_cpas=valid_cpas,
            client_features=client_features,
        )

    # Negative allocation
    neg_alloc = {"Website": 1.20, "Agency": -0.20, "Client": 0.0}
    with pytest.raises(ValueError, match="Channel allocation for Agency cannot be negative"):
        calculate_marketing_scenario(
            total_budget=50_000.0,
            channel_allocations=neg_alloc,
            channel_cpas=valid_cpas,
            client_features=client_features,
        )

    # Non-positive CPA
    bad_cpa = {"Website": 1200.0, "Agency": -100.0, "Client": 1800.0}
    with pytest.raises(ValueError, match="CPA for Agency must be positive"):
        calculate_marketing_scenario(
            total_budget=50_000.0,
            channel_allocations=valid_allocations,
            channel_cpas=bad_cpa,
            client_features=client_features,
        )


def test_parquet_recomputation_channel_medians(phase4_data: dict[str, Any]) -> None:
    """Test directly recomputing referral channel medians from client_features.parquet.

    Directly verifies microdata values:
    - Website: $1,238,162.97 (~$1,238,163)
    - Agency: $1,210,176.20 (~$1,210,176)
    - Client: $1,223,339.08 (~$1,223,339)
    """
    cf = phase4_data["client_features"]
    medians = cf.groupby("referral_channel")["total_spend"].median().to_dict()

    assert medians["Website"] == pytest.approx(1238162.97, abs=1.0)
    assert medians["Agency"] == pytest.approx(1210176.20, abs=1.0)
    assert medians["Client"] == pytest.approx(1223339.08, abs=1.0)


def test_real_sample_rows_exist(phase4_data: dict[str, Any]) -> None:
    """Test that all documentation sample entities actually exist in deduplicated parquet data."""
    meta = phase4_data["phase_4_metrics"]["verified_sample_metadata"]
    client_features = phase4_data["client_features"]
    available_df = phase4_data["available_properties"]

    assert len(available_df) == 313
    assert meta["current_inventory_size"] == 313

    # Sample client exists
    assert meta["sample_client_id"] in set(client_features["client_id"])
    assert client_features["client_id"].min() == meta["client_id_range"][0]
    assert client_features["client_id"].max() == meta["client_id_range"][1]

    # Sample listings exist in deduplicated available properties
    available_listing_ids = set(available_df["listing_id"])
    for lid in meta["sample_listing_ids"]:
        assert lid in available_listing_ids

    # Unit numbers strictly in range 1-70
    assert available_df["unit_number"].min() >= 1
    assert available_df["unit_number"].max() <= 70


def test_docs_vs_json_consistency(phase4_data: dict[str, Any]) -> None:
    """Test that key metrics in docs match the authoritative JSON metrics files."""
    m = phase4_data["model_selection_metrics"]
    p4 = phase4_data["phase_4_metrics"]

    # Model selection metrics
    assert m["k2_strong_structure"]["silhouette"] == pytest.approx(0.5072, abs=0.001)
    assert m["k2_strong_structure"]["davies_bouldin"] == pytest.approx(0.8066, abs=0.001)
    assert m["k4_weak_substructure"]["silhouette"] == pytest.approx(0.1211, abs=0.001)
    assert m["k4_weak_substructure"]["davies_bouldin"] == pytest.approx(2.6079, abs=0.001)
    assert m["cophenetic_correlation"] == pytest.approx(0.9066, abs=0.001)

    # Client-split Opportunity Finder backtest
    bt = p4["opportunity_finder_client_backtest"]["full_model"]
    assert bt["hit_rate_pct"] == pytest.approx(47.33, abs=0.2)
    assert bt["mrr"] == pytest.approx(0.7105, abs=0.01)

    # Marketing channel independence
    ct = p4["marketing_scenario_calculator"]["channel_targeting_empirical_finding"]
    assert ct["spend_anova_f"] == pytest.approx(2.1176, abs=0.01)
    assert ct["spend_anova_p"] == pytest.approx(0.1206, abs=0.01)
    assert ct["segment_mix_chi2"] == pytest.approx(0.75, abs=0.01)
    assert ct["segment_mix_p"] == pytest.approx(0.9933, abs=0.005)
