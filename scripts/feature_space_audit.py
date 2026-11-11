"""Feature Space Audit Script
Generates the raw feature list from the Model B3 preprocessor, counts the blocks,
audits total_spend inclusion, and computes empirical cohort imputation medians.
All values are derived directly from data and model artifacts; no literal results or inputs.
"""

from pathlib import Path

import joblib
import pandas as pd

repo_root = Path(__file__).resolve().parents[1]
models_path = repo_root / "data/models/cluster_models.joblib"
models = joblib.load(models_path)
preprocessor = models["preprocessor"]
feat_names = list(preprocessor.get_feature_names_out())

# Block prefixes and counts
prefixes = [
    "std_num__",
    "quantile_units__",
    "bool_pass__",
    "core_cat__",
    "geo_cat__country_",
    "geo_cat__region_",
]
counts = dict.fromkeys(prefixes, 0)
for f in feat_names:
    for p in prefixes:
        if f.startswith(p):
            counts[p] += 1
            break

print(f"Feature List (total {len(feat_names)} features):")
for i, fn in enumerate(feat_names):
    print(f"[{i:02d}] {fn}")

print("\nBlock Counts:")
for p, c in counts.items():
    print(f"{p}: {c}")

city_features = [f for f in feat_names if f.startswith("geo_cat__city_")]
print(f"City Features Count: {len(city_features)}")

# Total spend audit
total_spend_in_out = any("total_spend" in f for f in feat_names)
total_spend_in_in = hasattr(preprocessor, "feature_names_in_") and "total_spend" in preprocessor.feature_names_in_
print(f"\ntotal_spend in get_feature_names_out: {total_spend_in_out}")
print(f"total_spend in feature_names_in: {total_spend_in_in}")

# Imputation table from client_features.parquet
cf_path = repo_root / "data/processed/client_features.parquet"
cf = pd.read_parquet(cf_path)

imputation_medians = {
    "price_per_sqft": float(cf["price_per_sqft"].median()),
    "avg_floor_area": float(cf["avg_floor_area"].median()),
    "portfolio_towers_hhi": float(cf["portfolio_towers_hhi"].median()),
    "purchase_span_months": float(cf["purchase_span_months"].median()),
    "n_towers": float(cf["n_towers"].median()),
    "satisfaction_score": float(cf["satisfaction_score"].median()),
}

print("\nEmpirical Cohort Imputation Medians:")
for k, v in imputation_medians.items():
    print(f"{k}: {v:.6f}")

mode_referral = cf["referral_channel"].mode()[0]
print(f"referral_channel mode: {mode_referral}")
