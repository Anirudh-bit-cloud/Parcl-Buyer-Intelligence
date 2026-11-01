"""Gaussian Mixture Model module with diagonal covariance and PCA dimensionality reduction."""

import logging
from typing import Any

import numpy as np
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture

logger = logging.getLogger(__name__)


def fit_gmm(
    X: np.ndarray,
    n_components: int,
    covariance_type: str = "diag",
    random_state: int = 42,
    use_pca: bool = False,
    pca_components: int = 10,
) -> tuple[GaussianMixture, np.ndarray, np.ndarray]:
    """Fit Gaussian Mixture Model on feature matrix or PCA representation.

    Returns:
        (fitted_gmm, hard_cluster_assignments, soft_posterior_probabilities)
    """
    X_train = X
    if use_pca and X.shape[1] > pca_components:
        pca = PCA(n_components=pca_components, random_state=random_state)
        X_train = pca.fit_transform(X)

    gmm = GaussianMixture(
        n_components=n_components,
        covariance_type=covariance_type,
        random_state=random_state,
        n_init=10,
        max_iter=200,
    )
    gmm.fit(X_train)

    probabilities = gmm.predict_proba(X_train)
    hard_labels = gmm.predict(X_train)

    return gmm, hard_labels, probabilities


def evaluate_gmm_range(
    X: np.ndarray,
    k_range: range = range(2, 11),
    covariance_type: str = "diag",
    random_state: int = 42,
) -> list[dict[str, Any]]:
    """Compute BIC and AIC curves across candidate component counts."""
    metrics_list = []
    for k in k_range:
        gmm, labels, probs = fit_gmm(
            X,
            n_components=k,
            covariance_type=covariance_type,
            random_state=random_state,
        )
        bic = float(gmm.bic(X))
        aic = float(gmm.aic(X))

        # Mean entropy of assignment probabilities (higher entropy = softer/more ambiguous boundaries)
        eps = 1e-12
        entropy = -np.sum(probs * np.log(probs + eps), axis=1).mean()

        metrics_list.append(
            {
                "k": k,
                "bic": bic,
                "aic": aic,
                "mean_assignment_entropy": float(entropy),
            }
        )
    return metrics_list
