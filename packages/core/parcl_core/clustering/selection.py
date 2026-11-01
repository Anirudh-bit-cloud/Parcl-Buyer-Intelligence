"""Optimal cluster selection, Gap statistic calculation, and model comparison engine."""

import logging
from typing import Any

import numpy as np
from sklearn.cluster import KMeans

from parcl_core.clustering.kmeans import evaluate_kmeans_range
from parcl_core.clustering.stability import evaluate_bootstrap_stability

logger = logging.getLogger(__name__)


def compute_gap_statistic(
    X: np.ndarray,
    k_range: range = range(2, 11),
    n_refs: int = 10,
    random_state: int = 42,
) -> list[dict[str, Any]]:
    """Compute Gap Statistic against uniform reference distributions.

    Caveat: For sparse one-hot binary columns, a continuous uniform bounding box
    tends to overestimate dispersion. Results are interpreted as relative curvature.
    """
    rng = np.random.default_rng(random_state)
    mins = X.min(axis=0)
    maxs = X.max(axis=0)

    gap_results = []

    for k in k_range:
        # Fit actual data
        actual_km = KMeans(n_clusters=k, random_state=random_state, n_init=10).fit(X)
        actual_log_wcss = np.log(actual_km.inertia_)

        # Fit reference null datasets
        ref_log_wcss = []
        for _ in range(n_refs):
            X_ref = rng.uniform(mins, maxs, size=X.shape)
            ref_km = KMeans(n_clusters=k, random_state=int(rng.integers(1, 100000)), n_init=5).fit(
                X_ref
            )
            ref_log_wcss.append(np.log(ref_km.inertia_))

        mean_ref_log_wcss = float(np.mean(ref_log_wcss))
        gap = float(mean_ref_log_wcss - actual_log_wcss)
        s_k = float(np.std(ref_log_wcss) * np.sqrt(1 + 1 / n_refs))

        gap_results.append(
            {
                "k": k,
                "gap": gap,
                "s_k": s_k,
                "actual_log_wcss": float(actual_log_wcss),
                "ref_log_wcss": mean_ref_log_wcss,
            }
        )

    return gap_results


def compare_model_variants_across_metrics(
    variant_matrices: dict[str, np.ndarray],
    k_range: range = range(2, 7),
    random_state: int = 42,
) -> dict[str, Any]:
    """Compare Model A and Models B1-B4 across the same battery of evaluation metrics."""
    comparison_summary: dict[str, Any] = {}

    for var_name, X in variant_matrices.items():
        logger.info("Evaluating variant: %s (Dimensions: %s)", var_name, X.shape)
        km_metrics = evaluate_kmeans_range(X, k_range=k_range, random_state=random_state, n_init=20)

        # Stability at k=4 (benchmark comparison)
        stability_k4 = evaluate_bootstrap_stability(
            X, n_clusters=4, n_iterations=30, random_state=random_state
        )

        # Find peak silhouette
        best_km = max(km_metrics, key=lambda m: m["silhouette"])

        comparison_summary[var_name] = {
            "n_features": X.shape[1],
            "best_k_silhouette": best_km["k"],
            "max_silhouette": best_km["silhouette"],
            "k4_silhouette": next(m["silhouette"] for m in km_metrics if m["k"] == 4),
            "k4_davies_bouldin": next(m["davies_bouldin"] for m in km_metrics if m["k"] == 4),
            "k4_stability_mean_ari": stability_k4["mean_ari"],
            "metrics_by_k": km_metrics,
        }

    return comparison_summary
