"""Gaussian Mixture Model Audit Script
Measures empirical GMM component assignment distribution, crosstab against production K-Means labels,
and diagonal alignment rate.
All values are computed directly from the cluster model artifact; zero result literals.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

repo_root = Path(__file__).resolve().parents[1]
models_path = repo_root / "data/models/cluster_models.joblib"
models = joblib.load(models_path)
prod_labels = models["labels"]

gmm_probs = models["gmm_probabilities"]
gmm_preds = np.argmax(gmm_probs, axis=1)

comp_sizes = pd.Series(gmm_preds).value_counts().sort_index()
total_clients = len(gmm_preds)

print(f"Total Clients Evaluated: {total_clients}")
print("\nGMM Component Sizes & Shares:")
for comp_id, cnt in comp_sizes.items():
    pct = (cnt / total_clients) * 100
    print(f"Component {comp_id}: {cnt} clients ({pct:.4f}%)")

crosstab = pd.crosstab(
    gmm_preds,
    prod_labels,
    rownames=["GMM_Component"],
    colnames=["KMeans_Cluster"],
)
print("\nGMM Component vs Production K-Means Cluster Crosstab:")
print(crosstab.to_string())

diag_matches = int(np.sum(gmm_preds == prod_labels))
diag_pct = (diag_matches / total_clients) * 100
print(f"\nUnaligned Diagonal Agreement (gmm_preds == prod_labels): {diag_matches}/{total_clients} ({diag_pct:.4f}%)")
