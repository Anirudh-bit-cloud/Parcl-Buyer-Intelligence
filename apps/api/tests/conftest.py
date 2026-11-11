"""Pytest configuration and test client fixture for FastAPI app."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.middleware import InMemoryRateLimitMiddleware


@pytest.fixture(autouse=True)
def reset_rate_limits() -> None:
    """Reset sliding window rate limiter before each test."""
    InMemoryRateLimitMiddleware.reset()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Session-scoped test client for FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client
