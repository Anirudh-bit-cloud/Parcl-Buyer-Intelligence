import joblib
import pandas as pd

bundle = joblib.load("data/models/cluster_models.joblib")
labels = bundle["labels"]
kmeans = bundle["kmeans"]
df = pd.read_parquet("data/processed/client_features.parquet")
df["cluster"] = labels

print("=== RAW KMEANS VS PRODUCTION ===")
print("kmeans.labels_ == bundle['labels']:", (kmeans.labels_ == labels).all())
print("crosstab:")
print(pd.crosstab(kmeans.labels_, labels, rownames=['Raw KMeans'], colnames=['Production ID']))

print("\n=== CLUSTER EXACT STATS ===")
for c, sub in df.groupby("cluster"):
    print(f"Cluster {c}:")
    print(f"  Count: {len(sub)}")
    print(f"  Mean Age: {sub['age'].mean():.6f} (2dp: {sub['age'].mean():.2f})")
    print(f"  Mean Units: {sub['n_units'].mean():.6f} (2dp: {sub['n_units'].mean():.2f})")
    print(f"  Office Share: {sub['office_share'].mean()*100:.6f}% (2dp: {sub['office_share'].mean()*100:.2f}%)")
    print(f"  Total Units: {sub['n_units'].sum()}")
    print(f"  Total Spend: {sub['total_spend'].sum():.2f}")
    print(f"  Mean Spend: {sub['total_spend'].mean():.2f}")
