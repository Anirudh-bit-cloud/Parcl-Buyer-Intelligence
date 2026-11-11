"""Out-of-Fold Confusion Matrix & Concordance Measurement Script
Computes the 5-fold cross-validation confusion matrix, overall out-of-fold agreement,
and per-cluster concordance rates against production Model B3 labels.
All values are computed from live model artifacts and data; zero result literals.
"""

from pathlib import Path

import duckdb
import joblib
import numpy as np
import pandas as pd
from parcl_core.encoding import MODEL_B_BASE_NUMERICS, MODEL_B_BOOLEANS, MODEL_B_CATEGORICALS
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold

repo_root = Path(__file__).resolve().parents[1]

con = duckdb.connect()
cf_path = repo_root / "data/processed/client_features.parquet"
cf = con.execute("SELECT * FROM read_parquet(?)", [str(cf_path)]).df()

models = joblib.load(repo_root / "data/models/cluster_models.joblib")
preprocessor = models["preprocessor"]
X = preprocessor.transform(cf)

cat_encoder = preprocessor.named_transformers_["core_cat"]
n_core_cat = cat_encoder.transform(cf[MODEL_B_CATEGORICALS]).shape[1]
geo_offset = len(MODEL_B_BASE_NUMERICS) + 1 + len(MODEL_B_BOOLEANS) + n_core_cat
X[:, geo_offset:] = X[:, geo_offset:] * 0.5

prod_labels = models["labels"]
centroids = models["kmeans"].cluster_centers_

kf = KFold(n_splits=5, shuffle=True, random_state=42)
oof_preds = np.zeros(len(cf), dtype=int)

for train_idx, val_idx in kf.split(X):
    X_train, X_val = X[train_idx], X[val_idx]
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    km.fit(X_train)

    cost = np.linalg.norm(km.cluster_centers_[:, None, :] - centroids[None, :, :], axis=2)
    r_ind, c_ind = linear_sum_assignment(cost)
    aligned = np.zeros_like(km.cluster_centers_)
    for r, c in zip(r_ind, c_ind, strict=False):
        aligned[c] = km.cluster_centers_[r]

    val_dists = np.linalg.norm(X_val[:, None, :] - aligned[None, :, :], axis=2)
    oof_preds[val_idx] = np.argmin(val_dists, axis=1)

oof_cm = confusion_matrix(prod_labels, oof_preds)
agreement = np.mean(oof_preds == prod_labels) * 100

row_totals = oof_cm.sum(axis=1)
col_totals = oof_cm.sum(axis=0)

print("Out-of-Fold Confusion Matrix (Rows: Production Label, Columns: Fold Prediction):")
cm_df = pd.DataFrame(
    oof_cm,
    index=[f"Prod_Cluster_{i}" for i in range(4)],
    columns=[f"Fold_Pred_{i}" for i in range(4)],
)
cm_df["Row_Total"] = row_totals
print(cm_df.to_string())

col_summary = pd.DataFrame(
    [col_totals],
    index=["Col_Total"],
    columns=[f"Fold_Pred_{i}" for i in range(4)],
)
col_summary["Row_Total"] = int(np.sum(oof_cm))
print(col_summary.to_string())

print(f"\nOverall Out-of-Fold Agreement: {agreement:.4f}%")

print("\nPer-Cluster Concordance & Precision:")
for i in range(4):
    concordant = int(oof_cm[i, i])
    row_tot = int(row_totals[i])
    col_tot = int(col_totals[i])
    concordance_rate = (concordant / row_tot) * 100 if row_tot > 0 else 0.0
    precision_rate = (concordant / col_tot) * 100 if col_tot > 0 else 0.0
    print(f"Cluster {i}: Concordant={concordant}/{row_tot} ({concordance_rate:.4f}%), Precision={concordant}/{col_tot} ({precision_rate:.4f}%)")
