import json

import joblib
import pandas as pd

models = joblib.load("data/models/cluster_models.joblib")
phase3_labels = models["labels"]

with open("data/interim/model_selection_metrics.json") as f:
    ms_metrics = json.load(f)

cf = pd.read_parquet("data/processed/client_features.parquet")
prod_labels = cf["assigned_cluster"] if "assigned_cluster" in cf else cf["cluster"]

ctab = pd.crosstab(phase3_labels, prod_labels, rownames=["Phase 3 (cluster_models.joblib)"], colnames=["Production (clients.parquet)"])
print("=== CROSSTAB: Phase 3 labels vs Production labels ===")
print(ctab)

# Let's inspect model_selection_metrics.json variants
print("\n=== MODEL SELECTION VARIANTS ===")
for model_key in ["Model_A", "Model_B1", "Model_B2", "Model_B3", "Model_B4"]:
    if model_key in ms_metrics:
        m = ms_metrics[model_key]
        print(f"{model_key}: k=4 silhouette={m.get('silhouette_k4', m.get('silhouette'))}, mean_ari={m.get('bootstrap_stability_ari', m.get('stability_ari'))}")
