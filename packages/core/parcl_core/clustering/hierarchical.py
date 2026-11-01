"""Agglomerative Hierarchical clustering with Ward linkage and cophenetic correlation."""

import logging
from typing import Any

import numpy as np
from scipy.cluster.hierarchy import cophenet, linkage
from scipy.spatial.distance import pdist
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score

logger = logging.getLogger(__name__)


def fit_hierarchical_ward(
    X: np.ndarray, n_clusters: int
) -> tuple[AgglomerativeClustering, np.ndarray]:
    """Fit Agglomerative clustering using Ward linkage and return model and linkage matrix."""
    # Compute full linkage matrix for dendrogram
    Z = linkage(X, method="ward")

    # Fit scikit-learn clusterer
    agg = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
    agg.fit_predict(X)

    return agg, Z


def compute_cophenetic_correlation(X: np.ndarray, Z: np.ndarray) -> float:
    """Compute Cophenetic Correlation Coefficient measuring tree preservation of pairwise distances."""
    coph_corr, _ = cophenet(Z, pdist(X))
    return float(coph_corr)


def compare_kmeans_hierarchical(
    kmeans_labels: np.ndarray,
    hierarchical_labels: np.ndarray,
) -> dict[str, Any]:
    """Compute partition agreement between K-Means and Hierarchical clusters via ARI and contingency."""
    ari = float(adjusted_rand_score(kmeans_labels, hierarchical_labels))
    contingency = np.zeros(
        (len(np.unique(kmeans_labels)), len(np.unique(hierarchical_labels))),
        dtype=int,
    )
    for k_lab, h_lab in zip(kmeans_labels, hierarchical_labels, strict=True):
        contingency[k_lab, h_lab] += 1

    return {
        "adjusted_rand_index": ari,
        "contingency_matrix": contingency.tolist(),
    }
