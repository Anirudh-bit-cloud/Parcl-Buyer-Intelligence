"""Bootstrap stability testing with label alignment and nearest-centroid out-of-bag scoring."""

import logging
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

logger = logging.getLogger(__name__)


def align_cluster_labels(reference_labels: np.ndarray, candidate_labels: np.ndarray) -> np.ndarray:
    """Align candidate cluster labels to reference labels using the Hungarian algorithm."""
    n_clusters = max(reference_labels.max(), candidate_labels.max()) + 1
    cost_matrix = np.zeros((n_clusters, n_clusters), dtype=int)

    for r_lab, c_lab in zip(reference_labels, candidate_labels, strict=True):
        cost_matrix[r_lab, c_lab] += 1

    # Maximize agreement by minimizing negative cost
    row_ind, col_ind = linear_sum_assignment(-cost_matrix)
    mapping = dict(zip(col_ind, row_ind, strict=True))

    aligned_labels = np.array([mapping.get(c, c) for c in candidate_labels])
    return aligned_labels


def evaluate_bootstrap_stability(
    X: np.ndarray,
    n_clusters: int,
    n_iterations: int = 100,
    random_state: int = 42,
) -> dict[str, Any]:
    """Evaluate cluster persistence via bootstrap resampling with nearest-centroid out-of-bag scoring.

    Algorithm:
    1. Fit reference model on full dataset X to obtain base_labels and base_centroids.
    2. In each iteration:
       - Sample with replacement (in-bag index B).
       - Determine out-of-bag index OOB = complement(B).
       - Fit new KMeans model on X[B].
       - Assign OOB points to nearest cluster centroid of new model.
       - Assign OOB points to nearest cluster centroid of reference model.
       - Align labels and compute Adjusted Rand Index on OOB points.
    3. Return mean ARI, std ARI, 5th percentile, and 95th percentile.
    """
    n_samples = X.shape[0]
    rng = np.random.default_rng(random_state)

    # 1. Base reference fit
    ref_km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=20).fit(X)
    ref_labels = ref_km.labels_

    ari_scores: list[float] = []

    for _ in range(n_iterations):
        # In-bag sample
        b_idx = rng.choice(n_samples, size=n_samples, replace=True)
        oob_mask = np.ones(n_samples, dtype=bool)
        oob_mask[b_idx] = False
        oob_idx = np.where(oob_mask)[0]

        if len(oob_idx) < n_clusters * 2:
            continue

        X_b = X[b_idx]
        X_oob = X[oob_idx]

        # Fit model on bootstrap sample
        boot_km = KMeans(
            n_clusters=n_clusters, random_state=int(rng.integers(1, 100000)), n_init=10
        ).fit(X_b)

        # Predict OOB points using nearest centroids
        pred_oob_boot = boot_km.predict(X_oob)
        pred_oob_ref = ref_labels[oob_idx]

        # Align labels via Hungarian algorithm
        aligned_boot = align_cluster_labels(pred_oob_ref, pred_oob_boot)

        ari = float(adjusted_rand_score(pred_oob_ref, aligned_boot))
        ari_scores.append(ari)

    ari_arr = np.array(ari_scores)

    return {
        "n_clusters": n_clusters,
        "n_iterations": len(ari_scores),
        "mean_ari": float(ari_arr.mean()),
        "std_ari": float(ari_arr.std()),
        "p5_ari": float(np.percentile(ari_arr, 5)),
        "p95_ari": float(np.percentile(ari_arr, 95)),
        "is_stable": bool(ari_arr.mean() >= 0.70),
    }
