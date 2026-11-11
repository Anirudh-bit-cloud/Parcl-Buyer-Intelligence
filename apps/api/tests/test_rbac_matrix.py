"""Comprehensive RBAC Endpoint Matrix Test Suite.

Validates access across all 5 security states:
1. Unauthenticated (no token)
2. Viewer (read-only, PII-masked)
3. Analyst (operational analytics, scenario simulations)
4. Admin (full system & dataset management)
5. Auditor (audit trail inspection & cryptographic chain verification)
"""

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token
from apps.api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module")
def tokens() -> dict[str, str]:
    return {
        "viewer": create_access_token(subject="user-viewer", role="viewer"),
        "analyst": create_access_token(subject="user-analyst", role="analyst"),
        "admin": create_access_token(subject="user-admin", role="admin"),
        "auditor": create_access_token(subject="user-auditor", role="auditor"),
    }


def auth_hdr(tokens: dict[str, str], role: str | None) -> dict[str, str]:
    if role is None:
        return {}
    return {"Authorization": f"Bearer {tokens[role]}"}


# Public endpoints matrix: Accessible to unauthenticated callers (200 OK)
@pytest.mark.parametrize(
    "path",
    [
        "/health/live",
        "/health/ready",
        "/api/v1/meta/filters",
        "/api/v1/datasets",
    ],
)
def test_public_endpoints_unauthenticated(client: TestClient, path: str):
    resp = client.get(path)
    assert resp.status_code == 200, f"Expected 200 for public {path}, got {resp.status_code}"


# Protected analytical endpoints: 401 for unauthenticated; 200 for viewer, analyst, admin, auditor
@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/overview",
        "/api/v1/segments",
        "/api/v1/segments/2",
        "/api/v1/clients?page=1&page_size=5",
        "/api/v1/behavior",
        "/api/v1/geo",
        "/api/v1/towers",
        "/api/v1/recommendations/nbo/C0001",
        "/api/v1/governance/data-quality",
        "/api/v1/governance/drift",
        "/api/v1/governance/fairness",
        "/api/v1/projection",
    ],
)
def test_protected_endpoints_matrix(client: TestClient, tokens: dict[str, str], path: str):
    # 1. Unauthenticated -> 401
    unauth_resp = client.get(path)
    assert unauth_resp.status_code == 401, f"Expected 401 for {path} unauthenticated"

    # 2. All 4 authenticated roles -> 200
    for role in ["viewer", "analyst", "admin", "auditor"]:
        resp = client.get(path, headers=auth_hdr(tokens, role))
        assert resp.status_code == 200, f"Expected 200 for {path} with role {role}, got {resp.status_code}"


# Privileged auditor/admin endpoints: 401 unauthenticated, 403 viewer/analyst, 200 admin/auditor
@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/export/audit-logs",
        "/api/v1/export/audit-logs/verify",
    ],
)
def test_auditor_admin_endpoints_matrix(client: TestClient, tokens: dict[str, str], path: str):
    # 1. Unauthenticated -> 401
    assert client.get(path).status_code == 401

    # 2. Viewer -> 403
    assert client.get(path, headers=auth_hdr(tokens, "viewer")).status_code == 403

    # 3. Analyst -> 403
    assert client.get(path, headers=auth_hdr(tokens, "analyst")).status_code == 403

    # 4. Admin -> 200
    assert client.get(path, headers=auth_hdr(tokens, "admin")).status_code == 200

    # 5. Auditor -> 200
    assert client.get(path, headers=auth_hdr(tokens, "auditor")).status_code == 200


def test_pii_masking_rbac_matrix(client: TestClient, tokens: dict[str, str]):
    """Verify viewer and analyst get masked PII, whereas admin gets unmasked client names."""
    # Analyst request
    analyst_resp = client.get("/api/v1/clients/C0001", headers=auth_hdr(tokens, "analyst"))
    assert analyst_resp.status_code == 200
    analyst_data = analyst_resp.json()
    assert analyst_data["first_name"].endswith("***")
    assert analyst_data["last_name"].endswith("***")

    # Viewer request
    viewer_resp = client.get("/api/v1/clients/C0001", headers=auth_hdr(tokens, "viewer"))
    assert viewer_resp.status_code == 200
    viewer_data = viewer_resp.json()
    assert viewer_data["first_name"].endswith("***")

    # Admin request
    admin_resp = client.get("/api/v1/clients/C0001", headers=auth_hdr(tokens, "admin"))
    assert admin_resp.status_code == 200
    admin_data = admin_resp.json()
    assert not admin_data["first_name"].endswith("***")
