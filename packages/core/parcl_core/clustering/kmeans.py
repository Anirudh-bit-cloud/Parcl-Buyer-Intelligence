"""K-Means clustering module with deterministic seeding and kneedle elbow detection."""

import logging
from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score

logger = logging.getLogger(__name__)


def fit_kmeans(
    X: np.ndarray,
    n_clusters: int,
    random_state: int = 42,
    n_init: int = 50,
) -> KMeans:
    """Fit deterministic K-Means model with k-means++ initialization."""
    km = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        n_init=n_init,
        random_state=random_state,
    )
    km.fit(X)
    return km


def evaluate_kmeans_range(
    X: np.ndarray,
    k_range: range = range(2, 11),
    random_state: int = 42,
    n_init: int = 20,
) -> list[dict[str, Any]]:
    """Compute comprehensive evaluation metrics for K-Means across k in k_range."""
    metrics_list = []

    for k in k_range:
        km = fit_kmeans(X, n_clusters=k, random_state=random_state, n_init=n_init)
        labels = km.labels_

        sil = float(silhouette_score(X, labels))
        dbi = float(davies_bouldin_score(X, labels))
        chi = float(calinski_harabasz_score(X, labels))
        inertia = float(km.inertia_)

        # Cluster size balance
        _, counts = np.unique(labels, return_counts=True)
        min_size = int(counts.min())
        max_size = int(counts.max())

        metrics_list.append(
            {
                "k": k,
                "inertia": inertia,
                "silhouette": sil,
                "davies_bouldin": dbi,
                "calinski_harabasz": chi,
                "min_cluster_size": min_size,
                "max_cluster_size": max_size,
            }
        )

    return metrics_list


def detect_kneedle_elbow(k_values: list[int], inertias: list[float]) -> int:
    """Detect elbow point using the maximum perpendicular distance method (Kneedle)."""
    p1 = np.array([float(k_values[0]), float(inertias[0]), 0.0])
    p2 = np.array([float(k_values[-1]), float(inertias[-1]), 0.0])

    # Line vector from p1 to p2
    line_vec = p2 - p1
    line_norm = np.linalg.norm(line_vec)
    if line_norm == 0:
        return k_values[0]

    distances = []
    for k, inert in zip(k_values, inertias, strict=True):
        p = np.array([float(k), float(inert), 0.0])
        # Perpendicular distance to line in 3D
        dist = np.linalg.norm(np.cross(line_vec, p1 - p)) / line_norm
        distances.append(dist)

    best_idx = int(np.argmax(distances))
    return k_values[best_idx]
