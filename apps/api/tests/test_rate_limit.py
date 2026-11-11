"""Unit tests for sliding-window rate limiting with dual Redis and in-memory fallback."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from apps.api.config import api_settings
from apps.api.main import app
from apps.api.middleware import InMemoryRateLimitMiddleware


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    InMemoryRateLimitMiddleware.reset()
    yield
    InMemoryRateLimitMiddleware.reset()


def test_in_memory_rate_limit_exceeded():
    """Verify HTTP 429 when client exceeds max requests in window."""
    client = TestClient(app)

    # Set rate records for "testclient" (TestClient's host) within current active window
    import time
    now = time.time()
    InMemoryRateLimitMiddleware.client_records["testclient"] = [now] * 125

    # Health check is exempt
    resp_health = client.get("/health/ready")
    assert resp_health.status_code == 200

    # Business endpoint throttled
    resp = client.get("/api/v1/meta/filters")
    assert resp.status_code == 429
    assert "Rate limit exceeded" in resp.json()["detail"]
    assert resp.headers.get("Retry-After") == "60"


def test_rate_limiter_redis_fallback_on_error(monkeypatch: pytest.MonkeyPatch):
    """Verify rate limiter transparently falls back to in-memory if Redis ping fails."""
    monkeypatch.setattr(api_settings, "redis_enabled", True)
    monkeypatch.setattr(InMemoryRateLimitMiddleware, "_redis_failed", False)
    monkeypatch.setattr(InMemoryRateLimitMiddleware, "_redis_client", None)

    # Force redis import to raise or fail
    mock_redis = MagicMock()
    mock_redis.from_url.side_effect = ConnectionError("Could not connect to Redis")
    monkeypatch.setattr("redis.from_url", mock_redis.from_url, raising=False)

    client = TestClient(app)
    # Should not crash; should fall back to in-memory and succeed
    resp = client.get("/api/v1/meta/filters")
    assert resp.status_code == 200
    assert InMemoryRateLimitMiddleware._redis_failed is True
