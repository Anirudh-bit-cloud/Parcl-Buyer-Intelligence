import duckdb
import joblib
import pandas as pd

con = duckdb.connect()
cf = con.execute("SELECT * FROM read_parquet('data/processed/client_features.parquet')").df()
cf["cluster"] = joblib.load("data/models/cluster_models.joblib")["labels"]

features = ["age", "n_units", "office_share", "portfolio_towers_hhi", "loan_applied"]
cohort_means = {f: cf[f].mean() for f in features}
cohort_sds = {f: cf[f].std() for f in features}

print("=== COHORT OVERALL STATS ===")
for f in features:
    print(f"{f}: mean={cohort_means[f]:.4f}, sd={cohort_sds[f]:.4f}")

clusters = sorted(cf["cluster"].unique())

print("\n=== STANDARDIZED MEAN DIFFERENCES (SMD = (mean_cluster - mean_overall) / sd_overall) ===")
smd_data = []
for cid in clusters:
    sub = cf[cf["cluster"] == cid]
    row = {"cluster_id": cid, "count": len(sub)}
    for f in features:
        c_mean = sub[f].mean()
        smd = (c_mean - cohort_means[f]) / cohort_sds[f]
        row[f"{f}_mean"] = round(c_mean, 4)
        row[f"{f}_smd"] = round(smd, 4)
    smd_data.append(row)

smd_df = pd.DataFrame(smd_data)
for _, r in smd_df.iterrows():
    cid = int(r["cluster_id"])
    print(f"\nCluster {cid} (n={int(r['count'])}):")
    for f in features:
        print(f"  {f:20s}: Mean = {r[f'{f}_mean']:8.4f} | SMD = {r[f'{f}_smd']:+8.4f}")
