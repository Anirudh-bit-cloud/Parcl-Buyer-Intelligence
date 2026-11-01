"""Unit and regression tests for Phase 3: Clustering, selection, stability, and auto-naming."""

import numpy as np
import pytest
from parcl_core.clustering.gmm import fit_gmm
from parcl_core.clustering.hierarchical import compute_cophenetic_correlation, fit_hierarchical_ward
from parcl_core.clustering.kmeans import detect_kneedle_elbow, evaluate_kmeans_range
from parcl_core.clustering.selection import compute_gap_statistic
from parcl_core.clustering.stability import align_cluster_labels, evaluate_bootstrap_stability
from parcl_core.explain import generate_prd_hypothesis_truth_matrix
from parcl_core.pipeline import run_phase_3


@pytest.fixture
def synthetic_features() -> np.ndarray:
    """Generate 200 synthetic rows with 4 distinct Gaussian centroids."""
    rng = np.random.default_rng(42)
    c1 = rng.normal(loc=[-3, -3], scale=0.5, size=(50, 2))
    c2 = rng.normal(loc=[3, 3], scale=0.5, size=(50, 2))
    c3 = rng.normal(loc=[-3, 3], scale=0.5, size=(50, 2))
    c4 = rng.normal(loc=[3, -3], scale=0.5, size=(50, 2))
    return np.vstack([c1, c2, c3, c4])


def test_kmeans_fitting_and_elbow(synthetic_features: np.ndarray) -> None:
    """Test deterministic K-Means and Kneedle detection."""
    metrics = evaluate_kmeans_range(synthetic_features, k_range=range(2, 6), random_state=42)
    assert len(metrics) == 4
    inertias = [m["inertia"] for m in metrics]
    k_vals = [m["k"] for m in metrics]
    elbow_k = detect_kneedle_elbow(k_vals, inertias)
    assert 2 <= elbow_k <= 5


def test_hierarchical_ward(synthetic_features: np.ndarray) -> None:
    """Test Ward linkage hierarchical clustering and cophenetic correlation."""
    agg, Z = fit_hierarchical_ward(synthetic_features, n_clusters=4)
    coph = compute_cophenetic_correlation(synthetic_features, Z)
    assert 0.70 <= coph <= 1.0


def test_gmm_diagonal_posterior(synthetic_features: np.ndarray) -> None:
    """Test GMM with diagonal covariance computes normalized probabilities."""
    gmm, hard_labels, probs = fit_gmm(synthetic_features, n_components=4, covariance_type="diag")
    assert probs.shape == (200, 4)
    assert np.allclose(probs.sum(axis=1), 1.0)


def test_bootstrap_stability_and_alignment(synthetic_features: np.ndarray) -> None:
    """Test bootstrap stability with Hungarian label alignment."""
    # Test label alignment directly
    ref = np.array([0, 0, 1, 1])
    cand = np.array([1, 1, 0, 0])
    aligned = align_cluster_labels(ref, cand)
    assert (aligned == ref).all()

    # Test stability on synthetic data
    res = evaluate_bootstrap_stability(synthetic_features, n_clusters=4, n_iterations=20)
    assert res["mean_ari"] >= 0.80
    assert res["is_stable"] is True


def test_gap_statistic(synthetic_features: np.ndarray) -> None:
    """Test Gap statistic returns expected structure."""
    gaps = compute_gap_statistic(synthetic_features, k_range=range(2, 5), n_refs=5)
    assert len(gaps) == 3
    assert "gap" in gaps[0]
    assert "s_k" in gaps[0]


def test_prd_truth_matrix() -> None:
    """Test PRD hypothesis truth table output contains C1-C4."""
    dummy_profiles = {"cluster_profiles": {}}
    matrix = generate_prd_hypothesis_truth_matrix(dummy_profiles)
    assert len(matrix) == 4
    cluster_ids = [m["prd_cluster"] for m in matrix]
    assert cluster_ids == ["C1", "C2", "C3", "C4"]


def test_run_phase_3_execution() -> None:
    """Test end-to-end Phase 3 execution produces models and metrics."""
    res = run_phase_3()
    assert "models_bundle" in res
    assert "metrics_json" in res
