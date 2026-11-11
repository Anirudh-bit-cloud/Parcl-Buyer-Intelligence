"""Rigorous unit and failure-path test suite for parcl_core.drift."""

import numpy as np
import pandas as pd
from parcl_core.drift import calculate_psi, run_full_drift_audit


def test_calculate_psi_identical_distributions():
    """Identical distributions must yield PSI approximately 0.0."""
    np.random.seed(42)
    series_a = pd.Series(np.random.normal(loc=50, scale=10, size=1000))
    series_b = series_a.copy()

    psi, buckets = calculate_psi(series_a, series_b, num_buckets=10)
    assert 0.0 <= psi < 0.01, f"Expected PSI near 0 for identical series, got {psi}"
    assert len(buckets) <= 10


def test_calculate_psi_divergent_distributions():
    """Significantly shifted distributions must yield high PSI (> 0.25)."""
    np.random.seed(42)
    baseline = pd.Series(np.random.normal(loc=30, scale=5, size=1000))
    shifted = pd.Series(np.random.normal(loc=70, scale=5, size=1000))

    psi, _ = calculate_psi(baseline, shifted, num_buckets=10)
    assert psi > 0.25, f"Expected severe drift (PSI > 0.25), got {psi}"


def test_calculate_psi_empty_series_failure_path():
    """Empty series must fail safely without crashing (returns 0.0)."""
    empty_a = pd.Series(dtype=float)
    empty_b = pd.Series(dtype=float)

    psi, buckets = calculate_psi(empty_a, empty_b)
    assert psi == 0.0
    assert buckets == []


def test_calculate_psi_constant_single_value_series():
    """Series with identical constant values must not divide by zero."""
    const_a = pd.Series([100.0] * 50)
    const_b = pd.Series([100.0] * 50)

    psi, buckets = calculate_psi(const_a, const_b)
    assert psi == 0.0
    assert buckets == []


def test_run_full_drift_audit_normal():
    """Full drift audit on synthetic data frames with continuous and categorical features."""
    np.random.seed(42)
    n = 200
    current = pd.DataFrame({
        "total_spend": np.random.uniform(100000, 1000000, size=n),
        "age": np.random.randint(25, 75, size=n),
        "cluster": np.random.choice([0, 1, 2, 3], size=n),
        "acquisition_purpose": np.random.choice(["HOME", "INVESTMENT"], size=n),
    })

    report = run_full_drift_audit(current)
    assert "status" in report
    assert "overall_drift_verdict" in report
    assert "features" in report
    assert report["overall_drift_verdict"] in ["HEALTHY", "WARNING", "CRITICAL", "NO_DRIFT", "MODERATE_DRIFT", "SIGNIFICANT_DRIFT"]


def test_run_full_drift_audit_missing_features_failure_path():
    """DataFrame with missing expected columns must skip gracefully without unhandled exceptions."""
    df_empty_cols = pd.DataFrame({"random_col": [1, 2, 3]})
    report = run_full_drift_audit(df_empty_cols)
    assert "overall_drift_verdict" in report
