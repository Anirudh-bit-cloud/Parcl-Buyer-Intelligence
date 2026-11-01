"""Unit tests for Phase 2: Feature engineering, schema validation, and bivariate tests."""

import pandas as pd
import pytest
from parcl_core.cleaning import clean_clients, clean_properties
from parcl_core.encoding import (
    build_model_a_preprocessor,
    transform_and_ablate_model_b,
)
from parcl_core.features import (
    compute_portfolio_features,
    engineer_client_features,
    evaluate_satisfaction_bivariate_dependencies,
)
from parcl_core.ingest import load_raw_clients, load_raw_properties


@pytest.fixture
def clean_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Provide clean clients and transactions DataFrames."""
    raw_clients = load_raw_clients()
    raw_properties = load_raw_properties()
    clients_clean = clean_clients(raw_clients)
    sold_clean, _ = clean_properties(raw_properties)
    return clients_clean, sold_clean


def test_compute_portfolio_features(clean_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test portfolio aggregation logic computes correct invariants."""
    _, sold_clean = clean_data
    portfolio_df = compute_portfolio_features(sold_clean)
    assert len(portfolio_df) == 2000
    assert (portfolio_df["n_units"] >= 1).all()
    assert (portfolio_df["portfolio_towers_hhi"] >= 0.05).all()
    assert (portfolio_df["portfolio_towers_hhi"] <= 1.0).all()
    assert (portfolio_df["office_share"] + portfolio_df["apartment_share"]).round(2).eq(1.0).all()
    assert portfolio_df["total_spend"].gt(0).all()


def test_engineer_client_features(clean_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test client feature engineering and schema validation."""
    clients_clean, sold_clean = clean_data
    features_df = engineer_client_features(clients_clean, sold_clean)
    assert len(features_df) == 2000
    assert "spend_percentile" in features_df.columns
    assert "age_band" in features_df.columns
    # Check all spend variables exist for profiling
    assert {"total_spend", "avg_price", "max_price"}.issubset(features_df.columns)


def test_satisfaction_bivariate_tests(clean_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test satisfaction bivariate dependency tests run and output metrics."""
    clients_clean, sold_clean = clean_data
    features_df = engineer_client_features(clients_clean, sold_clean)
    res = evaluate_satisfaction_bivariate_dependencies(features_df)
    assert "acquisition_purpose" in res
    assert "referral_channel" in res
    assert "total_spend" in res
    assert "p_value" in res["acquisition_purpose"]
    assert "kruskal_wallis" in res["total_spend"]


def test_model_a_encoding(clean_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test Model A preprocessor matches exact PRD step 2 features."""
    clients_clean, sold_clean = clean_data
    features_df = engineer_client_features(clients_clean, sold_clean)
    preprocessor = build_model_a_preprocessor(features_df)
    X = preprocessor.transform(features_df)
    assert X.shape[0] == 2000
    assert X.shape[1] > 10


def test_model_b_ablation_variants(clean_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test Model B preprocessor supports all satisfaction and geographic ablation modes."""
    clients_clean, sold_clean = clean_data
    features_df = engineer_client_features(clients_clean, sold_clean)

    # 1. Full with satisfaction
    X_full = transform_and_ablate_model_b(features_df, include_satisfaction=True, geo_mode="full")
    # 2. Without satisfaction
    X_no_sat = transform_and_ablate_model_b(
        features_df, include_satisfaction=False, geo_mode="full"
    )
    # 3. Geo removed
    X_no_geo = transform_and_ablate_model_b(
        features_df, include_satisfaction=True, geo_mode="removed"
    )
    # 4. Geo downweighted
    X_down = transform_and_ablate_model_b(
        features_df, include_satisfaction=True, geo_mode="downweighted"
    )

    assert X_full.shape[0] == 2000
    assert X_no_sat.shape[1] == X_full.shape[1] - 1
    assert X_no_geo.shape[1] < X_full.shape[1]
    assert X_down.shape == X_full.shape
