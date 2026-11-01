"""Contract tests for OpenAPI specification, ETag caching, and sliding rate limiter."""

from fastapi.testclient import TestClient

from apps.api.auth import create_access_token
from apps.api.config import api_settings


def test_openapi_spec_structure_and_routes(client: TestClient) -> None:
    """Verify OpenAPI 3.1.0 schema contains all required endpoints and data schemas."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()

    assert spec["openapi"].startswith("3.")
    assert spec["info"]["title"] == "Parcl Buyer Intelligence API"
    assert spec["info"]["version"] == api_settings.app_version

    expected_routes = [
        "/api/v1/health",
        "/api/v1/auth/demo-token",
        "/api/v1/meta/filters",
        "/api/v1/overview",
        "/api/v1/clients",
        "/api/v1/clients/{client_id}",
        "/api/v1/segments",
        "/api/v1/segments/{segment_id}",
        "/api/v1/behavior",
        "/api/v1/geo",
        "/api/v1/towers",
        "/api/v1/recommendations/opportunities",
        "/api/v1/recommendations/nbo/{client_id}",
        "/api/v1/campaigns/scenario",
        "/api/v1/campaigns/allocate",
        "/api/v1/campaigns/simulate",
        "/api/v1/predict/segment",
        "/api/v1/model/selection",
        "/api/v1/model/compare",
        "/api/v1/governance/data-quality",
        "/api/v1/governance/model-card",
        "/api/v1/projection",
        "/api/v1/export",
        "/",
    ]
    for route in expected_routes:
        assert route in spec["paths"], f"Expected route {route} missing from OpenAPI paths"


def test_etag_caching_and_304_handling(client: TestClient) -> None:
    """Verify ETag calculation on GET endpoints and 304 Not Modified behavior."""
    analyst_token = create_access_token(subject="analyst", role="analyst")
    headers = {"Authorization": f"Bearer {analyst_token}"}

    # First GET returns 200 with ETag header
    res1 = client.get("/api/v1/governance/model-card", headers=headers)
    assert res1.status_code == 200
    etag = res1.headers.get("ETag")
    assert etag is not None
    assert etag.startswith('"') and etag.endswith('"')

    # Second GET with matching If-None-Match returns 304
    headers_304 = {"Authorization": f"Bearer {analyst_token}", "If-None-Match": etag}
    res2 = client.get("/api/v1/governance/model-card", headers=headers_304)
    assert res2.status_code == 304
    assert res2.headers.get("ETag") == etag


def test_performance_timing_header(client: TestClient) -> None:
    """Verify X-Process-Time-Ms header is injected into all responses."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Process-Time-Ms" in response.headers
    assert float(response.headers["X-Process-Time-Ms"]) >= 0.0


def test_rate_limiting_enforcement(client: TestClient) -> None:
    """Verify in-memory sliding window rate limiter returns 429 when max threshold is exceeded."""
    limit = api_settings.rate_limit_per_minute

    # Exhaust allowance on a public endpoint subject to rate limiting
    hit_429 = False
    for _ in range(limit + 5):
        res = client.get("/api/v1/meta/filters")
        if res.status_code == 429:
            hit_429 = True
            assert "Rate limit exceeded" in res.json()["detail"]
            assert res.headers.get("Retry-After") == "60"
            break

    assert hit_429, f"Failed to trigger 429 after {limit + 5} requests"
