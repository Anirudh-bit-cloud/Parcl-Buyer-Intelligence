import json

with open("data/interim/model_selection_metrics.json", encoding="utf-8") as f:
    ms = json.load(f)

for k in ["Model_B1_Full_With_Sat", "Model_B2_Purged_Sat", "Model_B3_Downweighted_Geo", "Model_B4_Pure_Behavior"]:
    v = ms["variants_comparison"][k]
    print(k)
    print("  n_features:", v.get("n_features"))
    print("  k=4 silhouette:", v.get("k4_silhouette"))
    print("  k=4 stability mean ARI:", v.get("k4_stability_mean_ari"))
    print("  k=4 Davies-Bouldin:", v.get("k4_davies_bouldin"))
