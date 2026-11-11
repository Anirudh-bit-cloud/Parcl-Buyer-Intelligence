import joblib
import numpy as np
import pandas as pd
from parcl_core.encoding import (
    MODEL_B_BASE_NUMERICS,
    MODEL_B_BOOLEANS,
    MODEL_B_CATEGORICALS,
)
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold

# 1. Load data & models
cf = pd.read_parquet("data/processed/client_features.parquet")
models = joblib.load("data/models/cluster_models.joblib")
kmeans = models["kmeans"]
preprocessor = models["preprocessor"]
X = preprocessor.transform(cf)

cat_encoder = preprocessor.named_transformers_["core_cat"]
n_core_cat = cat_encoder.transform(cf[MODEL_B_CATEGORICALS]).shape[1]
n_prev = len(MODEL_B_BASE_NUMERICS) + 1 + len(MODEL_B_BOOLEANS) + n_core_cat
X[:, n_prev:] = X[:, n_prev:] * 0.5

prod_labels = models["labels"]
feature_names = preprocessor.get_feature_names_out().tolist()
print(f"Feature count: {len(feature_names)}")
print(f"Evaluation space shape: {X.shape}, equals production space? {X.shape == (2000, 84)}")

# 2. Compute d2 / d1 across all 2,000 clients
centroids = kmeans.cluster_centers_

# Compute distance from each client to all 4 centroids
dists = np.linalg.norm(X[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
sorted_dists = np.sort(dists, axis=1)
d1 = sorted_dists[:, 0]
d2 = sorted_dists[:, 1]
ratio = d2 / d1

print("\n--- d2/d1 Ratio Statistics across 2,000 clients in Production Space ---")
quantiles = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
q_vals = np.quantile(ratio, quantiles)
for q, v in zip(quantiles, q_vals, strict=False):
    print(f"p{int(q*100):02d}: {v:.4f}")
share_above_1_5 = np.mean(ratio > 1.5)
print(f"Share with d2/d1 > 1.5: {share_above_1_5 * 100:.2f}% ({np.sum(ratio > 1.5)} / 2000)")

# 3. Unit-count histogram
print("\n--- Unit-Count Histogram (n_units distribution) ---")
unit_counts = cf["n_units"].value_counts().sort_index()
for u, c in unit_counts.items():
    print(f"{u} units: {c} clients ({c / len(cf) * 100:.2f}%)")

# 4. Out-of-fold confusion matrix matching compute_beta_grid.py (KFold(n_splits=5, shuffle=True, random_state=42))
kf = KFold(n_splits=5, shuffle=True, random_state=42)
oof_preds = np.zeros(len(cf), dtype=int)

for train_idx, val_idx in kf.split(X):
    X_train, X_val = X[train_idx], X[val_idx]
    y_val = prod_labels[val_idx]

    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    km.fit(X_train)

    # Hungarian alignment between training fold centroids and production centroids
    cost = np.linalg.norm(km.cluster_centers_[:, None, :] - centroids[None, :, :], axis=2)
    r_ind, c_ind = linear_sum_assignment(cost)
    aligned_centers = np.zeros_like(km.cluster_centers_)
    for r, c in zip(r_ind, c_ind, strict=False):
        aligned_centers[c] = km.cluster_centers_[r]

    val_dists = np.linalg.norm(X_val[:, None, :] - aligned_centers[None, :, :], axis=2)
    fold_argmin = np.argmin(val_dists, axis=1)
    oof_preds[val_idx] = fold_argmin

cm = confusion_matrix(prod_labels, oof_preds)
print("\n--- Out-of-Fold Confusion Matrix (Rows: Production Label, Cols: Fold OOF Prediction) ---")
print("Prod \\ OOF | Pred 0 | Pred 1 | Pred 2 | Pred 3 | Total")
print("-----------|--------|--------|--------|--------|------")
for i, row in enumerate(cm):
    print(f"Cluster {i:2d} | {row[0]:6d} | {row[1]:6d} | {row[2]:6d} | {row[3]:6d} | {np.sum(row):5d}")
print("-----------|--------|--------|--------|--------|------")
print(f"Total      | {np.sum(cm[:, 0]):6d} | {np.sum(cm[:, 1]):6d} | {np.sum(cm[:, 2]):6d} | {np.sum(cm[:, 3]):6d} | {len(cf):5d}")
oof_acc = np.mean(oof_preds == prod_labels)
print(f"\nOverall Out-of-Fold Agreement Accuracy: {oof_acc * 100:.2f}%")
