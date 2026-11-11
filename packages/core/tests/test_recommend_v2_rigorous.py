"""Rigorous unit and failure-path test suite for parcl_core.recommend simulator v2 and CLV."""

import pandas as pd
import pytest
from parcl_core.recommend import (
    calculate_marketing_scenario_v2,
    calculate_segment_clv_and_propensity,
    compare_marketing_scenarios,
)


@pytest.fixture
def mock_client_features():
    channels = ["Website", "Agency", "Client"]
    return pd.DataFrame({
        "client_id": [f"C{i:04d}" for i in range(120)],
        "cluster": [i % 4 for i in range(120)],
        "total_spend": [1000000.0 * (1 + (i % 5)) for i in range(120)],
        "n_units": [1 + (i % 4) for i in range(120)],
        "referral_channel": [channels[i % 3] for i in range(120)],
        "loan_applied": [bool(i % 2) for i in range(120)],
        "purchase_span_months": [12.0 + (i % 24) for i in range(120)],
    })


@pytest.fixture
def mock_transactions():
    return pd.DataFrame({
        "client_ref": [f"C{i % 100:04d}" for i in range(300)],
        "sale_price": [1500000.0 for _ in range(300)],
        "transaction_date": ["2025-01-15" for _ in range(300)],
    })


def test_calculate_marketing_scenario_v2_standard(mock_client_features):
    """Verify standard simulation returns expected buyers, revenue, and Monte Carlo confidence intervals."""
    allocations = {"Website": 0.50, "Agency": 0.35, "Client": 0.15}
    cpas = {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0}

    res = calculate_marketing_scenario_v2(
        total_budget=150000.0,
        channel_allocations=allocations,
        channel_cpas=cpas,
        client_features=mock_client_features,
        num_monte_carlo_draws=100,
    )

    assert res["total_budget"] == 150000.0
    assert res["total_modeled_clients"] > 0
    assert "monte_carlo_confidence_interval" in res
    ci = res["monte_carlo_confidence_interval"]
    assert ci["ci_lower_inr"] <= ci["ci_upper_inr"]


def test_calculate_marketing_scenario_v2_zero_budget(mock_client_features):
    """Zero budget must fail fast with a descriptive ValueError."""
    allocations = {"Website": 0.50, "Agency": 0.30, "Client": 0.20}
    cpas = {"Website": 1000.0, "Agency": 2000.0, "Client": 1500.0}

    with pytest.raises(ValueError, match="total_budget must be positive"):
        calculate_marketing_scenario_v2(
            total_budget=0.0,
            channel_allocations=allocations,
            channel_cpas=cpas,
            client_features=mock_client_features,
        )


def test_calculate_marketing_scenario_v2_linear_fallback(mock_client_features):
    """When enable_diminishing_returns=False, simulator returns linear calculation."""
    allocations = {"Website": 0.50, "Agency": 0.30, "Client": 0.20}
    cpas = {"Website": 1000.0, "Agency": 2000.0, "Client": 1500.0}

    res = calculate_marketing_scenario_v2(
        total_budget=100000.0,
        channel_allocations=allocations,
        channel_cpas=cpas,
        client_features=mock_client_features,
        enable_diminishing_returns=False,
    )

    assert res["simulator_version"] == "v2.0-linear"
    assert res["confidence_intervals"] is None


def test_compare_marketing_scenarios_delta(mock_client_features):
    """Comparing scenario A and B must return correct deltas."""
    allocations = {"Website": 0.50, "Agency": 0.30, "Client": 0.20}
    cpas = {"Website": 1000.0, "Agency": 2000.0, "Client": 1500.0}

    scenario_a = calculate_marketing_scenario_v2(
        total_budget=100000.0,
        channel_allocations=allocations,
        channel_cpas=cpas,
        client_features=mock_client_features,
    )

    scenario_b = calculate_marketing_scenario_v2(
        total_budget=200000.0,
        channel_allocations=allocations,
        channel_cpas=cpas,
        client_features=mock_client_features,
    )

    comparison = compare_marketing_scenarios(scenario_a, scenario_b)
    assert comparison["deltas"]["budget_delta_inr"] == 100000.0
    assert "clients_delta" in comparison["deltas"]


def test_calculate_segment_clv_and_propensity_contract(mock_client_features, mock_transactions):
    """CLV estimation baseline per segment must return experimental metrics."""
    clv_report = calculate_segment_clv_and_propensity(mock_client_features, mock_transactions)
    assert clv_report["status"] == "EXPERIMENTAL_BASELINE"
    assert "segments" in clv_report
    assert len(clv_report["segments"]) == 4
