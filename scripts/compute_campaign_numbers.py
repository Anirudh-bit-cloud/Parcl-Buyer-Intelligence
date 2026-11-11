import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fractions import Fraction

import duckdb

con = duckdb.connect()
df = con.execute("""
    SELECT referral_channel,
           avg(total_spend) as mean_spend,
           count(*) as count,
           sum(total_spend) as sum_spend
    FROM read_parquet('data/processed/client_features.parquet')
    GROUP BY referral_channel
    ORDER BY referral_channel
""").df()

print("=== EXACT HISTORICAL CHANNEL MEANS (REPR) ===")
means = {}
for _, r in df.iterrows():
    ch = r["referral_channel"]
    means[ch] = r["mean_spend"]
    print(f"{ch}: count={r['count']}, mean_spend={repr(r['mean_spend'])}, sum_spend={repr(r['sum_spend'])}")

budget = 100000.0
channels = [
    ("Website", 0.50, 1200.0, Fraction(125, 3)),
    ("Agency", 0.35, 3500.0, Fraction(10, 1)),
    ("Client", 0.15, 1800.0, Fraction(25, 3)),
]

print("\n=== EVALUATED SCENARIO UNROUNDED VALUES ===")
total_gmv = 0.0
for ch, alloc, cpa, frac in channels:
    alloc_budget = budget * alloc
    clients_float = alloc_budget / cpa
    clients_frac = frac
    mean_val = means[ch]
    row_gmv = clients_float * mean_val
    total_gmv += row_gmv
    print(f"Channel: {ch}")
    print(f"  Allocated Budget: ₹{alloc_budget:.2f}")
    print(f"  User CPA: ₹{cpa:.2f}")
    print(f"  Clients (Fraction): {clients_frac} ({float(clients_frac)})")
    print(f"  Clients float repr: {repr(clients_float)}")
    print(f"  Historical Mean repr: {repr(mean_val)}")
    print(f"  Row GMV repr: {repr(row_gmv)} (Formatted: ₹{row_gmv:,.2f})")

print(f"\nTotal Modeled Clients: {sum(float(f) for _, _, _, f in channels)}")
print(f"Total Modeled GMV repr: {repr(total_gmv)}")
print(f"Total Modeled GMV formatted: ₹{total_gmv:,.2f}")
