"""Compute out-of-fold agreement log-likelihood temperature beta grid for K-Means centroid distance softmax.

Methodology & Leakage Disclosure:
- Production cluster labels (y_i) were fit on the full cohort of N=2,000 clients.
- 5-Fold Cross-Validation splits the cohort into 5 folds (N_val=400 each).
- Training folds fit K-Means (k=4, random_state=42, n_init=10) on 84-dimensional Model B3 features.
- Training fold centroids are aligned to production centroids via Hungarian assignment (scipy.optimize.linear_sum_assignment).
- Validation fold clients are scored against aligned fold centroids at temperature beta in [0.10, 5.00] (25 grid points).
- Criterion: 'out-of-fold agreement log-likelihood' evaluating how well fold-trained centroids reproduce the full-sample partition:
    LL(beta) = (1/N) sum_i ln p_{y_i}(x_i; beta)
- Out-of-fold agreement rate: proportion of validation clients whose nearest fold centroid matches their production label.
- Quantiles (5th, 25th, 50th, 75th, 95th) of p_max are computed at the optimal agreement beta.
"""

import json
from pathlib import Path
import sys
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.model_selection import KFold

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def compute_beta_grid(
    data_dir: Path,
    n_splits: int = 5,
    random_state: int = 42,
    n_init: int = 10,
) -> dict[str, Any]:
    """Run 5-fold cross-validation and compute out-of-fold agreement log-likelihood across beta grid."""
    model_path = data_dir / "models" / "cluster_models.joblib"
    feat_path = data_dir / "processed" / "client_features.parquet"

    bundle = joblib.load(model_path)
    preprocessor = bundle["preprocessor"]
    cf = pd.read_parquet(feat_path)

    # Feature transformation with geographic downweighting (0.5x per Model B3 specification)
    X = preprocessor.transform(cf)
    from parcl_core.encoding import (
        MODEL_B_BASE_NUMERICS,
        MODEL_B_BOOLEANS,
        MODEL_B_CATEGORICALS,
    )

    cat_encoder = preprocessor.named_transformers_["core_cat"]
    n_core_cat = cat_encoder.transform(cf[MODEL_B_CATEGORICALS]).shape[1]
    n_prev = len(MODEL_B_BASE_NUMERICS) + 1 + len(MODEL_B_BOOLEANS) + n_core_cat
    X[:, n_prev:] = X[:, n_prev:] * 0.5

    full_labels = bundle["labels"]
    full_centroids = bundle["kmeans"].cluster_centers_

    # 5-fold Cross-Validation
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    fold_data = []
    agreement_matches = []

    for train_idx, val_idx in kf.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_val = full_labels[val_idx]

        km = KMeans(n_clusters=4, random_state=random_state, n_init=n_init)
        km.fit(X_train)

        # Hungarian alignment between training fold centroids and production centroids
        cost = np.linalg.norm(
            km.cluster_centers_[:, None, :] - full_centroids[None, :, :], axis=2
        )
        r_ind, c_ind = linear_sum_assignment(cost)
        aligned_centers = np.zeros_like(km.cluster_centers_)
        for r, c in zip(r_ind, c_ind, strict=True):
            aligned_centers[c] = km.cluster_centers_[r]

        # Validation distances to aligned centroids
        dists = np.linalg.norm(X_val[:, None, :] - aligned_centers[None, :, :], axis=2)
        fold_data.append((y_val, dists))

        # Nearest fold-centroid agreement with production labels
        fold_argmin = np.argmin(dists, axis=1)
        agreement_matches.extend(fold_argmin == y_val)

    overall_agreement_rate = float(np.mean(agreement_matches) * 100.0)

    # Evaluate 25 grid points from beta=0.10 to beta=5.00
    betas = np.round(np.linspace(0.1, 5.0, 25), 2)
    grid_points = []
    pmax_per_beta = {}

    for beta in betas:
        lls = []
        ambs = []
        all_pmax = []
        for y_val, dists in fold_data:
            # Numerically stable softmax
            scaled_dists = -float(beta) * dists
            max_val = np.max(scaled_dists, axis=1, keepdims=True)
            exp_d = np.exp(scaled_dists - max_val)
            probs = exp_d / np.sum(exp_d, axis=1, keepdims=True)

            p_max = np.max(probs, axis=1)
            all_pmax.extend(p_max)

            assigned_p = probs[np.arange(len(y_val)), y_val]
            lls.append(np.mean(np.log(np.clip(assigned_p, 1e-12, 1.0))))
            ambs.append(np.mean(p_max < 0.50) * 100.0)

        mean_ll = float(np.mean(lls))
        mean_amb = float(np.mean(ambs))
        pmax_per_beta[float(beta)] = all_pmax

        grid_points.append(
            {
                "beta": float(beta),
                "mean_agreement_log_likelihood": round(mean_ll, 4),
                "mean_log_likelihood": round(mean_ll, 4),
                "ambiguity_pct": round(mean_amb, 2),
                "is_chosen": False,
            }
        )

    # Find the agreement log-likelihood maximizer
    best_point = max(grid_points, key=lambda x: x["mean_agreement_log_likelihood"])
    for pt in grid_points:
        if pt["beta"] == best_point["beta"]:
            pt["is_chosen"] = True

    chosen_pmax = pmax_per_beta[best_point["beta"]]
    pmax_quantiles = {
        "p05": round(float(np.percentile(chosen_pmax, 5)), 4),
        "p25": round(float(np.percentile(chosen_pmax, 25)), 4),
        "p50": round(float(np.percentile(chosen_pmax, 50)), 4),
        "p75": round(float(np.percentile(chosen_pmax, 75)), 4),
        "p95": round(float(np.percentile(chosen_pmax, 95)), 4),
    }

    output_payload = {
        "evaluation_protocol": "5-Fold Cross-Validation on N=2,000 cohort clients (84 Model B3 features)",
        "criterion_name": "out-of-fold agreement log-likelihood",
        "held_out_definition": (
            "Held-out clients in validation fold scored against training-fold centroids "
            "aligned to production centroids via Hungarian assignment (linear_sum_assignment). "
            "Evaluates agreement with full-cohort production labels."
        ),
        "leakage_disclosure": (
            "Target cluster labels (y_i) were fit on the full 2,000-client cohort. Scoring held-out validation "
            "points measures out-of-fold agreement with the production partition rather than external ground truth."
        ),
        "selection_rule": (
            "Empirical maximizer of out-of-fold agreement log-likelihood across the evaluated beta grid. "
            "Balances probability concentration against overconfident boundary mismatch penalties."
        ),
        "chosen_beta": best_point["beta"],
        "chosen_mean_agreement_log_likelihood": best_point["mean_agreement_log_likelihood"],
        "chosen_mean_log_likelihood": best_point["mean_agreement_log_likelihood"],
        "chosen_ambiguity_pct": best_point["ambiguity_pct"],
        "out_of_fold_agreement_rate_pct": round(overall_agreement_rate, 2),
        "chosen_p_max_quantiles": pmax_quantiles,
        "grid": grid_points,
    }

    out_file = data_dir / "interim" / "beta_grid.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Beta grid saved to {out_file}")
    print(f"Chosen Beta: {best_point['beta']} (LL: {best_point['mean_agreement_log_likelihood']}, Ambiguity: {best_point['ambiguity_pct']}%)")
    print(f"Out-of-Fold Agreement Rate: {overall_agreement_rate:.2f}%")
    print(f"p_max Quantiles at beta={best_point['beta']}: {pmax_quantiles}")
    return output_payload


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    compute_beta_grid(project_root / "data")
