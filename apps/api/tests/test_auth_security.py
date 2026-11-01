"""Tests for JWT authentication, role extraction, CORS, and role-aware ETag caching."""

from datetime import timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token
from apps.api.config import APISettings, api_settings


def test_missing_auth_token_returns_401(client: TestClient) -> None:
    """Verify requests without Authorization header receive HTTP 401 Unauthorized on protected endpoints."""
    res = client.get("/api/v1/clients?page=1&page_size=2")
    assert res.status_code == 401
    assert "missing authorization header" in res.json()["detail"].lower()
    assert "bearer" in res.headers.get("WWW-Authenticate", "").lower()

    # Public endpoint (/health) works without token
    h_res = client.get("/api/v1/health")
    assert h_res.status_code == 200


def test_demo_token_analyst_default(client: TestClient) -> None:
    """Verify demo token endpoint defaults to 'analyst' (least privilege, masked)."""
    res = client.post("/api/v1/auth/demo-token")
    assert res.status_code == 200
    data = res.json()
    assert data["token_type"] == "bearer"
    assert data["role"] == "analyst"

    payload = jwt.decode(
        data["access_token"],
        api_settings.jwt_secret,
        algorithms=[api_settings.jwt_algorithm],
        issuer="parcl-api",
        options={"require": ["exp", "iat", "sub", "role"]},
    )
    assert payload["role"] == "analyst"


def test_demo_token_admin_without_key_returns_403(client: TestClient) -> None:
    """Verify requesting admin role without demo admin key returns HTTP 403 Forbidden."""
    res = client.post("/api/v1/auth/demo-token?role=admin")
    assert res.status_code == 403
    assert "requires a valid demo admin key" in res.json()["detail"].lower()


def test_demo_token_admin_with_key_succeeds(client: TestClient) -> None:
    """Verify requesting admin role with valid demo admin key succeeds."""
    headers = {"X-Demo-Admin-Key": api_settings.demo_admin_key}
    res = client.post("/api/v1/auth/demo-token?role=admin", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "admin"


def test_demo_token_disabled_returns_403(client: TestClient) -> None:
    """Verify demo token endpoint returns HTTP 403 Forbidden when disabled in config."""
    original_state = api_settings.demo_auth_enabled
    try:
        api_settings.demo_auth_enabled = False
        res = client.post("/api/v1/auth/demo-token")
        assert res.status_code == 403
        assert "disabled in this environment" in res.json()["detail"].lower()
    finally:
        api_settings.demo_auth_enabled = original_state


def test_jwt_secret_required_outside_dev() -> None:
    """Verify APISettings raises RuntimeError if jwt_secret is empty outside development environment."""
    import os

    old_env_jwt = os.environ.pop("JWT_SECRET_KEY", None)
    old_parcl_jwt = os.environ.pop("PARCL_API_JWT_SECRET", None)
    try:
        with pytest.raises(RuntimeError, match="JWT secret key must be set"):
            APISettings(environment="production", jwt_secret="")
    finally:
        if old_env_jwt:
            os.environ["JWT_SECRET_KEY"] = old_env_jwt
        if old_parcl_jwt:
            os.environ["PARCL_API_JWT_SECRET"] = old_parcl_jwt


def test_tampered_token_returns_401(client: TestClient) -> None:
    """Verify tampered JWT signature is rejected with HTTP 401 Unauthorized."""
    token = create_access_token(subject="user", role="admin")
    tampered = token[:-4] + "xyz1"
    res = client.get("/api/v1/clients", headers={"Authorization": f"Bearer {tampered}"})
    assert res.status_code == 401
    assert "signature verification failed" in res.json()["detail"].lower()


def test_expired_token_returns_401(client: TestClient) -> None:
    """Verify expired JWT is rejected with HTTP 401 Unauthorized."""
    expired_token = create_access_token(
        subject="user", role="admin", expires_delta=timedelta(seconds=-10)
    )
    res = client.get("/api/v1/clients", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert "token has expired" in res.json()["detail"].lower()


def test_role_aware_etag_separation(client: TestClient) -> None:
    """Verify admin and analyst requests produce distinct ETags and cannot cross-serve 304."""
    admin_token = create_access_token(subject="admin-user", role="admin")
    analyst_token = create_access_token(subject="analyst-user", role="analyst")

    # 1. Fetch unmasked admin response
    admin_res = client.get(
        "/api/v1/clients?page=1&page_size=5", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_res.status_code == 200
    admin_etag = admin_res.headers.get("ETag")

    # 2. Fetch masked analyst response
    analyst_res = client.get(
        "/api/v1/clients?page=1&page_size=5", headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert analyst_res.status_code == 200
    analyst_etag = analyst_res.headers.get("ETag")

    # ETags must be different
    assert admin_etag != analyst_etag

    # 3. Requesting admin resource with analyst ETag must NOT return 304
    cross_res = client.get(
        "/api/v1/clients?page=1&page_size=5",
        headers={"Authorization": f"Bearer {admin_token}", "If-None-Match": analyst_etag},
    )
    assert cross_res.status_code == 200  # Full response, not 304!

    # 4. Requesting with matching admin ETag returns 304
    match_res = client.get(
        "/api/v1/clients?page=1&page_size=5",
        headers={"Authorization": f"Bearer {admin_token}", "If-None-Match": admin_etag},
    )
    assert match_res.status_code == 304
    assert match_res.headers.get("Vary") == "Authorization"
    assert "private" in match_res.headers.get("Cache-Control", "")


def test_cors_configuration(client: TestClient) -> None:
    """Verify CORS allowlist contains configured origins and excludes wildcard '*'."""
    for origin in api_settings.cors_origins[:2]:
        res = client.options(
            "/api/v1/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res.headers.get("Access-Control-Allow-Origin") == origin
        assert res.headers.get("Access-Control-Allow-Origin") != "*"

    # Disallowed origin receives NO Access-Control-Allow-Origin header
    disallowed_res = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://malicious-attacker-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert disallowed_res.headers.get("Access-Control-Allow-Origin") is None
