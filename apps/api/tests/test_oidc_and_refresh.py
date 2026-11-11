"""Unit and integration tests for Generic OIDC Single Sign-On and Refresh Token flows."""

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token, verify_refresh_token
from apps.api.config import api_settings
from apps.api.main import app


def test_demo_token_returns_refresh_token():
    """Demo token endpoint must return both access_token and refresh_token."""
    client = TestClient(app)
    resp = client.post("/api/v1/auth/demo-token", json={"role": "analyst"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "analyst"

    # Verify refresh token is valid
    claims = verify_refresh_token(data["refresh_token"])
    assert claims["role"] == "analyst"


def test_refresh_token_rotation_success():
    """Valid refresh token can be exchanged at /api/v1/auth/refresh for new token pair."""
    client = TestClient(app)
    # Obtain initial tokens
    token_resp = client.post("/api/v1/auth/demo-token", json={"role": "analyst"}).json()
    old_refresh = token_resp["refresh_token"]

    # Exchange refresh token
    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh_resp.status_code == 200
    new_data = refresh_resp.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["role"] == "analyst"

    # Verify new access token works against protected endpoint
    auth_header = {"Authorization": f"Bearer {new_data['access_token']}"}
    overview_resp = client.get("/api/v1/overview", headers=auth_header)
    assert overview_resp.status_code == 200


def test_refresh_token_rejects_access_token():
    """Passing an access token to /refresh must return HTTP 401 (invalid token type)."""
    client = TestClient(app)
    access_tok = create_access_token(subject="user-1", role="analyst")
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": access_tok})
    assert resp.status_code == 401
    assert "expected refresh token" in resp.json()["detail"]


def test_oidc_endpoints_when_enabled(monkeypatch: pytest.MonkeyPatch):
    """When OIDC is enabled, /oidc/login and /oidc/callback provide SSO session exchange."""
    monkeypatch.setattr(api_settings, "oidc_enabled", True)
    monkeypatch.setattr(api_settings, "oidc_issuer", "https://sso.enterprise.corp")
    monkeypatch.setattr(api_settings, "oidc_client_id", "parcl-buyer-prod")

    client = TestClient(app)
    # 1. Login init
    login_resp = client.get("/api/v1/auth/oidc/login")
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["oidc_enabled"] is True
    assert "https://sso.enterprise.corp" in login_data["authorization_url"]

    # 2. Callback exchange
    cb_resp = client.post("/api/v1/auth/oidc/callback", json={"code": "auth-code-with-admin-role"})
    assert cb_resp.status_code == 200
    cb_data = cb_resp.json()
    assert cb_data["role"] == "admin"
    assert "access_token" in cb_data
    assert "refresh_token" in cb_data


def test_oidc_endpoints_when_disabled():
    """When OIDC is disabled, /oidc/login returns HTTP 400 Bad Request."""
    client = TestClient(app)
    resp = client.get("/api/v1/auth/oidc/login")
    assert resp.status_code == 400
    assert "not enabled" in resp.json()["detail"]
