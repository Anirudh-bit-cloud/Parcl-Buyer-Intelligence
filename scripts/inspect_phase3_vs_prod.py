import datetime
import json
import os

import duckdb
import joblib
import pandas as pd
from parcl_core.encoding import build_model_b_preprocessor
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score


def fit_kmeans(X, n_clusters=4, random_state=42):
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    km.fit(X)
    return km

with open("data/interim/model_selection_metrics.json", encoding="utf-8") as f:
    ms = json.load(f)

print("=== Model Variants in model_selection_metrics.json ===")
for k in ["Model_B1_Full_Features", "Model_B2_No_Satisfaction", "Model_B3_Downweighted_Geo", "Model_B4_Removed_Geo"]:
    v = ms["variants_comparison"].get(k, {})
    print(f"{k}:")
    print(f"  k=4 silhouette: {v.get('silhouette')}")
    print(f"  stability ARI: {v.get('stability_ari')}")

mtime = os.path.getmtime("data/models/cluster_models.joblib")
print(f"\ncluster_models.joblib mtime: {datetime.datetime.fromtimestamp(mtime).isoformat()}")

con = duckdb.connect()
cf = con.execute("SELECT * FROM read_parquet('data/processed/client_features.parquet')").df()

# Fit Model B2 (No Satisfaction, Unweighted Geo)
prep_b2, _ = build_model_b_preprocessor(cf, include_satisfaction=False, geo_mode="full")
X_b2 = prep_b2.fit_transform(cf)
km_b2 = fit_kmeans(X_b2, n_clusters=4, random_state=42)
labels_b2 = km_b2.labels_

# Fit Model B3 (No Satisfaction, Downweighted Geo)
prep_b3, _ = build_model_b_preprocessor(cf, include_satisfaction=False, geo_mode="downweighted")
X_b3 = prep_b3.fit_transform(cf)
km_b3 = fit_kmeans(X_b3, n_clusters=4, random_state=42)
labels_b3 = km_b3.labels_

bundle = joblib.load("data/models/cluster_models.joblib")
prod_labels = bundle["labels"]

print("\n=== B2 vs B3 Labels ===")
print(f"ARI(labels_b2, labels_b3): {adjusted_rand_score(labels_b2, labels_b3):.4f}")
print(f"ARI(prod_labels, labels_b3): {adjusted_rand_score(prod_labels, labels_b3):.4f}")
print("Crosstab B2 (rows) vs B3 (cols):")
print(pd.crosstab(labels_b2, labels_b3, rownames=["Model B2"], colnames=["Model B3"]))

print("\n=== Per-cluster means for Model B2 ===")
cf["cluster_b2"] = labels_b2
for c, sub in cf.groupby("cluster_b2"):
    print(f"B2 Cluster {c}: n={len(sub)}, age={sub['age'].mean():.2f}, units={sub['n_units'].mean():.2f}, office={sub['office_share'].mean()*100:.2f}%")

print("\n=== Per-cluster means for Model B3 ===")
cf["cluster_b3"] = labels_b3
for c, sub in cf.groupby("cluster_b3"):
    print(f"B3 Cluster {c}: n={len(sub)}, age={sub['age'].mean():.2f}, units={sub['n_units'].mean():.2f}, office={sub['office_share'].mean()*100:.2f}%")
