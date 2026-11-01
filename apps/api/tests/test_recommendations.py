"""Tests for Opportunity Finder and Next-Best-Offer recommendation endpoints."""

from fastapi.testclient import TestClient

from apps.api.auth import create_access_token


def test_opportunity_finder_strictly_313_inventory(client: TestClient) -> None:
    """Verify Opportunity Finder evaluates strictly against the 313 deduplicated units."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get(
        "/api/v1/recommendations/opportunities?segment_id=2&limit=10",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["target_segment_id"] == 2
    assert data["target_segment_name"] == "Commercial Office Diversifiers"
    assert data["total_inventory_evaluated"] == 313
    assert len(data["recommendations"]) == 10
    assert data["metadata"]["as_of"] == "December 2025"
    assert data["metadata"]["currency"] == "INR"

    # Verify score ordering (descending)
    scores = [r["affinity_score"] for r in data["recommendations"]]
    assert scores == sorted(scores, reverse=True)
    assert all("₹" in r["sale_price_display"] for r in data["recommendations"])


def test_opportunity_finder_category_filter(client: TestClient) -> None:
    """Verify category filtering isolates commercial office units for Segment 2."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get(
        "/api/v1/recommendations/opportunities?segment_id=2&category_filter=Office&limit=5",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["category_filter_applied"] == "Office"
    assert all(r["unit_category"] == "Office" for r in data["recommendations"])
    top_ids = [r["listing_id"] for r in data["recommendations"][:3]]
    assert top_ids == [170425, 170191, 40120]


def test_nbo_recommendations_for_client_c0001(client: TestClient) -> None:
    """Verify personalized NBO recommendations for C0001 with 20-tower accounting."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get(
        "/api/v1/recommendations/nbo/C0001?top_n=5",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["client_id"] == "C0001"
    assert data["client_segment_id"] == 0
    assert data["client_segment_name"] == "Emerging Multi-Tower Accumulators"
    assert data["owned_towers"] == [3, 4, 9, 15]
    assert data["unowned_towers_count"] == 16  # 20 - 4
    assert data["mean_bonus_eligibility_share_pct"] == 81.86
    assert len(data["recommendations"]) == 5

    top_ids = [r["listing_id"] for r in data["recommendations"][:3]]
    assert top_ids == [20365, 200449, 80385]

    for rec in data["recommendations"]:
        assert rec["tower_diversification_bonus"] in [0.0, 0.15]
        assert "untested_assumption_note" in rec
        assert "₹" in rec["sale_price_display"]


def test_nbo_client_not_found(client: TestClient) -> None:
    """Verify 404 for non-existent client NBO query."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    response = client.get(
        "/api/v1/recommendations/nbo/C9999",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 404
