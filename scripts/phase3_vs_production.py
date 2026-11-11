"""Phase 3 vs Production Comparison Audit Script
Evaluates Model B ablation variants (B1-B4) silhouette scores, ARI concordances,
B2 vs B3 crosstab, production per-cluster feature means, and joblib artifact provenance.
All metrics are computed live from data and model artifacts; zero result literals.
"""

import hashlib
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from parcl_core.encoding import transform_and_ablate_model_b
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

repo_root = Path(__file__).resolve().parents[1]
cf_path = repo_root / "data/processed/client_features.parquet"
cf = pd.read_parquet(cf_path)

models_path = repo_root / "data/models/cluster_models.joblib"
models = joblib.load(models_path)
prod_labels = models["labels"]
cf["cluster"] = prod_labels

# Model variants B1-B4
variant_configs = [
    ("B1", True, "full"),
    ("B2", False, "full"),
    ("B3", False, "downweighted"),
    ("B4", False, "removed"),
]

b_variants = {}
for name, sat, geo in variant_configs:
    X_var = transform_and_ablate_model_b(cf, include_satisfaction=sat, geo_mode=geo)
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    lbls = km.fit_predict(X_var)
    sil = silhouette_score(X_var, lbls)
    b_variants[name] = {
        "feature_count": X_var.shape[1],
        "silhouette": sil,
        "labels": lbls,
    }

print("=== Model B Ablation Battery (B1-B4) ===")
print("Variant | Features | Silhouette (k=4) | ARI vs Production B3")
print("-" * 58)
for name in ["B1", "B2", "B3", "B4"]:
    v = b_variants[name]
    ari = adjusted_rand_score(v["labels"], prod_labels)
    print(f"Model {name} | {v['feature_count']:8d} | {v['silhouette']:.6f}         | {ari:.6f}")

ari_b2_b3 = adjusted_rand_score(b_variants["B2"]["labels"], b_variants["B3"]["labels"])
print(f"\nAdjusted Rand Index between Model B2 and Model B3: {ari_b2_b3:.6f}")

print("\n=== Crosstab: Model B2 Clusters vs Model B3 Clusters ===")
ct_b2_b3 = pd.crosstab(
    b_variants["B2"]["labels"],
    b_variants["B3"]["labels"],
    rownames=["Model_B2_Cluster"],
    colnames=["Model_B3_Cluster"],
)
print(ct_b2_b3.to_string())

print("\n=== Production Cluster Means (Model B3) ===")
summary_cols = ["age", "n_units", "office_share", "portfolio_towers_hhi", "loan_applied"]
cluster_means = cf.groupby("cluster")[summary_cols].mean()
print(cluster_means.to_string())

# Artifact provenance
stat = models_path.stat()
mtime_iso = datetime.fromtimestamp(stat.st_mtime).isoformat()
sha256_hex = hashlib.sha256(models_path.read_bytes()).hexdigest()

print("\n=== Production Model Artifact Provenance ===")
print(f"Path: {models_path}")
print(f"File Size: {stat.st_size} bytes")
print(f"Modification Time (mtime): {mtime_iso}")
print(f"SHA-256: {sha256_hex}")
