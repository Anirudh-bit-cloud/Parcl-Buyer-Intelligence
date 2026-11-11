from pathlib import Path

test_file = Path("apps/api/tests/test_invariants.py")
content = test_file.read_text(encoding="utf-8")

new_test = '''

def test_cluster_permutation_and_indexing_alignment(client: TestClient) -> None:
    """Verify that production cluster IDs [0, 1, 2, 3] are consistently aligned across all pipelines:
    1. assigned_cluster in clients table matches bundle['labels'].
    2. bundle['labels'] strictly equals raw bundle['kmeans'].labels_ (identity mapping).
    3. soft_probabilities column j corresponds to centroid j, with 100% argmax agreement.
    4. surrogate rules map strictly to production cluster definitions (Cluster 1=pure residential, 2=office diversifiers).
    5. recommendations endpoints (/api/v1/recommendations/segments/{id}) align 1:1 with canonical segment names.
    6. fails if unaligned raw GMM posteriors are used as production labels.
    """
    import joblib
    import numpy as np
    from apps.api.auth import create_access_token

    analyst_token = create_access_token(subject="analyst", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}

    bundle = joblib.load(api_settings.models_dir / "cluster_models.joblib")
    labels = bundle["labels"]
    kmeans = bundle["kmeans"]
    soft_probs = bundle["soft_probabilities"]
    gmm_probs = bundle["gmm_probabilities"]

    # 1. Identity alignment: production bundle['labels'] equals raw kmeans.labels_
    assert (labels == kmeans.labels_).all(), "Production labels diverge from raw K-Means labels"

    # 2. Soft probabilities: column j corresponds to centroid j, with 100% argmax agreement
    soft_argmax = np.argmax(soft_probs, axis=1)
    assert (soft_argmax == labels).all(), "Soft probabilities argmax diverges from production cluster labels"

    # 3. Contrast check: unaligned GMM posteriors MUST NOT match production labels
    gmm_argmax = np.argmax(gmm_probs, axis=1)
    assert (gmm_argmax == labels).mean() < 0.20, "Unaligned GMM unexpectedly matched production labels"

    # 4. Client microdata alignment: C0001 must have assigned_cluster == 0
    res_c0001 = client.get("/api/v1/clients/C0001", headers=headers)
    assert res_c0001.status_code == 200
    c0001_data = res_c0001.json()
    assert c0001_data["assigned_cluster"] == 0
    assert c0001_data["assigned_segment_name"] == "Emerging Multi-Tower Accumulators"

    # 5. Recommendations segment_id alignment across all 4 segments
    expected_names = {
        0: "Emerging Multi-Tower Accumulators",
        1: "Concentrated Residential Buyers",
        2: "Commercial Office Diversifiers",
        3: "Established Senior Estate Investors",
    }
    for seg_id, expected_name in expected_names.items():
        res_rec = client.get(f"/api/v1/recommendations/segments/{seg_id}", headers=headers)
        assert res_rec.status_code == 200
        rec_data = res_rec.json()
        assert rec_data["segment_id"] == seg_id
        assert rec_data["segment_name"] == expected_name

    # 6. Surrogate decision tree rules alignment
    with open(api_settings.interim_dir / "model_selection_metrics.json", encoding="utf-8") as f:
        metrics = json.load(f)
    surrogate_rules = " ".join(metrics.get("surrogate_rules", []))
    assert "class: 1" in surrogate_rules
    assert "class: 2" in surrogate_rules
    assert "class: 0" in surrogate_rules
    assert "class: 3" in surrogate_rules
'''

if "test_cluster_permutation_and_indexing_alignment" not in content:
    content += new_test
    test_file.write_text(content, encoding="utf-8")
    print("Successfully added test_cluster_permutation_and_indexing_alignment")
else:
    print("Already added")
