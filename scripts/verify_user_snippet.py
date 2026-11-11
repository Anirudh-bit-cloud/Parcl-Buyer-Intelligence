"""Verification snippet checking MANIFEST hashes, contingency table, and unit counts."""

import hashlib
import json
from pathlib import Path

import pandas as pd

manifest_file = Path("docs/samples/MANIFEST.json")
with manifest_file.open("r", encoding="utf-8") as f:
    m = json.load(f)

for r, s in m["samples"].items():
    p = Path(s["file_path"])
    with p.open("rb") as sf:
        h = hashlib.sha256(sf.read()).hexdigest()
    print(r, h == s["sha256"])

c = pd.read_parquet("data/processed/clients_clean.parquet")
print("\n--- Contingency Table (USA vs Acquisition Purpose) ---")
print(pd.crosstab(c["country"] == "USA", c["acquisition_purpose"]))

f_df = pd.read_parquet("data/processed/client_features.parquet")
print("\n--- Unit Counts Value Counts & Sum ---")
print(f_df["n_units"].value_counts().sort_index(), f_df["n_units"].sum())
