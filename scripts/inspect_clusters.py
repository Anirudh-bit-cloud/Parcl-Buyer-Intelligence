"""Inspect production cluster statistics and Phase 3 naming engine decisions."""

import json
from pathlib import Path
import joblib
import pandas as pd

bundle = joblib.load("data/models/cluster_models.joblib")
labels = bundle["labels"]
cf = pd.read_parquet("data/processed/client_features.parquet")
cf["cluster"] = labels

print("=== PRODUCTION (MODEL B3) CLUSTER STATS ===")
for c in range(4):
    sub = cf[cf["cluster"] == c]
    u = sub["n_units"].mean()
    o = sub["office_share"].mean() * 100
    h = sub["portfolio_towers_hhi"].mean()
    a = sub["age"].mean()
    cnt = len(sub)
    print(
        f"Cluster {c}: count={cnt}, n_units_mean={u:.2f}, "
        f"office_share_mean={o:.2f}%, HHI={h:.4f}, age_mean={a:.2f}"
    )

# Let's inspect model_selection_metrics.json to see how Phase 3 named them
with open("data/interim/model_selection_metrics.json", encoding="utf-8") as f:
    m = json.load(f)

print("\n=== MODEL SELECTION METRICS CLUSTER PROFILES ===")
if "cluster_profiles" in m:
    for k, v in m["cluster_profiles"].items():
        cid = v.get("cluster_id")
        num = v.get("numeric_metrics", {})
        print(f"Profile {k} (cid={cid}): size={v.get('size')}, "
              f"age={num.get('age', {}).get('mean')}, "
              f"units={num.get('n_units', {}).get('mean')}, "
              f"office={num.get('office_share', {}).get('mean')}")

print("\n=== NAMING.PY RULES ===")
with open("packages/core/parcl_core/naming.py", encoding="utf-8") as f:
    print(f.read())
