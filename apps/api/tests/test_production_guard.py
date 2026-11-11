"""Unit tests for Production Startup Guard verifying rejection of weak/default secrets."""

import pytest
from pydantic import ValidationError

from apps.api.config import APISettings


def test_production_guard_rejects_default_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    """Production mode must refuse default development fallback JWT secret."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "dev-fallback-insecure-secret-key-for-local-testing-only-32bytes")

    with pytest.raises((RuntimeError, ValidationError), match="Default development JWT secret detected"):
        APISettings()


def test_production_guard_rejects_short_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    """Production mode must refuse JWT secret shorter than 32 characters."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "too-short-secret-123")

    with pytest.raises((RuntimeError, ValidationError), match="at least 32 characters long"):
        APISettings()


def test_production_guard_rejects_default_admin_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Production mode must refuse default demo admin key."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "a-very-secure-32-byte-long-production-jwt-secret-key!")
    monkeypatch.setenv("DEMO_ADMIN_KEY", "admin-secret-key-change-in-production")
    monkeypatch.setenv("DEMO_AUTH_ENABLED", "false")

    with pytest.raises((RuntimeError, ValidationError), match="Default or insecure demo_admin_key detected"):
        APISettings()


def test_production_guard_rejects_demo_auth_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    """Production mode must strictly forbid DEMO_AUTH_ENABLED=True."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "a-very-secure-32-byte-long-production-jwt-secret-key!")
    monkeypatch.setenv("DEMO_ADMIN_KEY", "a-very-secure-production-admin-key-999")
    monkeypatch.setenv("DEMO_AUTH_ENABLED", "true")

    with pytest.raises((RuntimeError, ValidationError), match="DEMO_AUTH_ENABLED must be False in production"):
        APISettings()


def test_production_guard_permits_valid_production_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valid production configuration must initialize cleanly."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "a-very-secure-32-byte-long-production-jwt-secret-key!")
    monkeypatch.setenv("DEMO_ADMIN_KEY", "a-very-secure-production-admin-key-999")
    monkeypatch.setenv("DEMO_AUTH_ENABLED", "false")

    settings = APISettings()
    assert settings.environment == "production"
    assert settings.demo_auth_enabled is False
