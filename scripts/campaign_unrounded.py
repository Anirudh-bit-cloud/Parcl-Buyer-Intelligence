"""Campaign Scenario GMV Precision Script
Computes campaign scenario outcomes from unrounded historical channel spend means
vs paise-rounded means, loaded from an external request fixture.
All values are computed from data; zero result literals or hardcoded inputs in script.
"""

import hashlib
import json
from pathlib import Path

import duckdb

repo_root = Path(__file__).resolve().parents[1]

# Load scenario inputs from external fixture
fixture_path = repo_root / "data/fixtures/campaign_scenario_request.json"
fixture_bytes = fixture_path.read_bytes()
fixture_sha256 = hashlib.sha256(fixture_bytes).hexdigest()

print("=== Scenario Request Fixture ===")
print(f"Path: {fixture_path}")
print(f"SHA-256: {fixture_sha256}")

with open(fixture_path, encoding="utf-8") as f:
    fixture_data = json.load(f)

total_budget = fixture_data["total_budget_inr"]
allocations = fixture_data["channel_allocations"]
cpas = fixture_data["channel_cpas_inr"]

# Load microdata to compute exact unrounded historical channel means
con = duckdb.connect()
cf_path = repo_root / "data/processed/client_features.parquet"
cf = con.execute("SELECT referral_channel, total_spend FROM read_parquet(?)", [str(cf_path)]).df()

channel_stats = cf.groupby("referral_channel")["total_spend"].agg(
    count="count",
    sum="sum",
    mean="mean",
)

# Load Phase 4 / API sample stored value for comparison
sample_path = repo_root / "docs/samples/campaign_scenario.json"
sample_bytes = sample_path.read_bytes()
sample_sha256 = hashlib.sha256(sample_bytes).hexdigest()
with open(sample_path, encoding="utf-8") as f:
    sample_data = json.load(f)

stored_sample_gmv = sample_data["total_modeled_gross_sales_volume_inr"]

print(f"\nStored Campaign Sample Path: {sample_path}")
print(f"Stored Campaign Sample SHA-256: {sample_sha256}")
print(f"Stored Phase 4 / Endpoint Sample Modeled GMV: {repr(stored_sample_gmv)}")

print("\n=== Channel Empirical Spend & Modeled Acquisitions ===")
tot_unrounded_gmv = 0.0
tot_paise_gmv = 0.0
tot_clients_float = 0.0

for ch, alloc in allocations.items():
    ch_budget = total_budget * alloc
    ch_cpa = cpas[ch]
    n_clients_float = ch_budget / ch_cpa
    tot_clients_float += n_clients_float

    raw_mean = float(channel_stats.loc[ch, "mean"])
    paise_mean = round(raw_mean, 2)

    unrounded_gmv = n_clients_float * raw_mean
    paise_gmv = n_clients_float * paise_mean

    tot_unrounded_gmv += unrounded_gmv
    tot_paise_gmv += paise_gmv

    print(f"\nChannel: {ch}")
    print(f"  Allocated Budget: {ch_budget:.2f}")
    print(f"  CPA: {ch_cpa:.2f}")
    print(f"  Modeled Clients: {n_clients_float:.8f}")
    print(f"  Historical Mean (Unrounded): {repr(raw_mean)}")
    print(f"  Historical Mean (Paise-Rounded): {repr(paise_mean)}")
    print(f"  Modeled GMV (Unrounded): {repr(unrounded_gmv)}")
    print(f"  Modeled GMV (From Paise Mean): {repr(paise_gmv)}")

print("\n=== Total Modeled Portfolio Outcomes ===")
print(f"Total Budget: {total_budget:.2f}")
print(f"Total Modeled Clients: {tot_clients_float:.8f}")
print(f"Total Modeled GMV (Unrounded Historical Means): {repr(tot_unrounded_gmv)}")
print(f"Total Modeled GMV (Paise-Rounded Historical Means): {repr(tot_paise_gmv)}")
diff_gmv = tot_unrounded_gmv - tot_paise_gmv
print(f"Difference (Unrounded - Paise-Rounded): {repr(diff_gmv)}")
print(f"Stored Endpoint Match with Paise-Rounded: {stored_sample_gmv == tot_paise_gmv}")
