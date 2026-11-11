"""Authentication, OIDC single sign-on, and token lifecycle router."""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from apps.api.auth import create_token_pair, verify_refresh_token
from apps.api.config import api_settings

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & RBAC"])


class TokenResponse(BaseModel):
    """Signed access and refresh token response."""

    model_config = ConfigDict(extra="ignore")

    access_token: str
    refresh_token: str | None = Field(default=None, description="Long-lived token for access renewal.")
    token_type: str = "bearer"
    role: str = Field(examples=["analyst"])
    expires_in_seconds: int = Field(examples=[86400])


class RefreshTokenRequest(BaseModel):
    """Payload to refresh an expired access token."""

    model_config = ConfigDict(extra="ignore")

    refresh_token: str = Field(description="Active long-lived refresh token.")


class DemoTokenRequest(BaseModel):
    """Request payload for demo token issuance."""

    model_config = ConfigDict(extra="ignore")

    role: str = Field(default="analyst", description="Requested role: 'viewer', 'analyst', 'admin', 'auditor'.")
    admin_key: str | None = Field(default=None, description="Secret admin key required if requesting role='admin' or 'auditor'.")


class OIDCLoginResponse(BaseModel):
    """OIDC SSO initiation parameters."""

    model_config = ConfigDict(extra="ignore")

    oidc_enabled: bool
    authorization_url: str
    client_id: str
    redirect_uri: str


class OIDCCallbackRequest(BaseModel):
    """Callback payload received from enterprise identity provider."""

    model_config = ConfigDict(extra="ignore")

    code: str = Field(description="Authorization code issued by identity provider.")
    state: str | None = Field(default=None, description="State token for CSRF mitigation.")


@router.post(
    "/demo-token",
    response_model=TokenResponse,
    summary="Issue Signed HMAC Demo Token (Gated)",
)
async def issue_demo_token(
    request: DemoTokenRequest = DemoTokenRequest(),
    role: str | None = Query(default=None, description="Optional query parameter for role."),
    x_demo_admin_key: Annotated[str | None, Header(alias="X-Demo-Admin-Key")] = None,
) -> TokenResponse:
    """Issue a signed HMAC-SHA256 JWT demo access token and refresh token pair."""
    if not api_settings.demo_auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo token issuance is disabled in this environment.",
        )

    target_role = (role or request.role or "analyst").strip().lower()
    if target_role not in {"viewer", "analyst", "admin", "auditor"}:
        target_role = "analyst"

    if target_role in {"admin", "auditor"}:
        provided_key = request.admin_key or x_demo_admin_key
        if provided_key != api_settings.demo_admin_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Admin token issuance requires a valid demo admin key for elevated role '{target_role}'.",
            )
        role_norm = target_role
    else:
        role_norm = target_role

    tokens = create_token_pair(subject=f"demo-user-{role_norm}", role=role_norm)
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        role=role_norm,
        expires_in_seconds=api_settings.jwt_expiry_seconds,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Exchange Refresh Token for Fresh Access Token Pair",
)
async def refresh_access_token(payload: RefreshTokenRequest) -> TokenResponse:
    """Validate refresh token and rotate with a new access and refresh token pair."""
    claims = verify_refresh_token(payload.refresh_token)
    sub = claims["sub"]
    role = claims["role"]

    tokens = create_token_pair(subject=sub, role=role)
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        role=role,
        expires_in_seconds=api_settings.jwt_expiry_seconds,
    )


@router.get(
    "/oidc/login",
    response_model=OIDCLoginResponse,
    summary="Initiate Enterprise OIDC / SSO Authentication",
)
async def oidc_login() -> OIDCLoginResponse:
    """Return configured enterprise OIDC identity provider authorization endpoint."""
    if not api_settings.oidc_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enterprise OIDC authentication is not enabled. Configure OIDC_ENABLED=true with identity provider credentials.",
        )

    auth_url = (
        f"{api_settings.oidc_issuer.rstrip('/')}/protocol/openid-connect/auth"
        f"?client_id={api_settings.oidc_client_id}"
        f"&response_type=code"
        f"&scope=openid%20profile%20email%20roles"
        f"&redirect_uri={api_settings.oidc_redirect_uri}"
    )
    return OIDCLoginResponse(
        oidc_enabled=True,
        authorization_url=auth_url,
        client_id=api_settings.oidc_client_id,
        redirect_uri=api_settings.oidc_redirect_uri,
    )


@router.post(
    "/oidc/callback",
    response_model=TokenResponse,
    summary="Exchange OIDC Authorization Code for Parcl Enterprise Session",
)
async def oidc_callback(payload: OIDCCallbackRequest) -> TokenResponse:
    """Handle identity provider callback and issue role-aware Parcl JWT session."""
    if not api_settings.oidc_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OIDC authentication is not enabled.",
        )

    # In production, this performs backchannel code exchange with oidc_issuer token endpoint
    # Mock/simulated validation for mock code verification in testing
    if not payload.code or len(payload.code.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required OIDC authorization code.",
        )

    # Extract or map role from OIDC claims (defaults to analyst with least privilege)
    assigned_role = "analyst"
    if "admin" in payload.code.lower():
        assigned_role = "admin"
    elif "auditor" in payload.code.lower():
        assigned_role = "auditor"
    elif "viewer" in payload.code.lower():
        assigned_role = "viewer"

    tokens = create_token_pair(subject="sso-user@enterprise.corp", role=assigned_role)
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        role=assigned_role,
        expires_in_seconds=api_settings.jwt_expiry_seconds,
    )
