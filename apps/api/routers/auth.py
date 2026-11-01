"""Authentication and demo token issuer router."""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from apps.api.auth import create_access_token
from apps.api.config import api_settings

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & RBAC"])


class TokenResponse(BaseModel):
    """Signed demo access token response."""

    model_config = ConfigDict(extra="ignore")

    access_token: str
    token_type: str = "bearer"
    role: str = Field(examples=["analyst"])
    expires_in_seconds: int = Field(examples=[86400])


class DemoTokenRequest(BaseModel):
    """Request payload for demo token issuance."""

    model_config = ConfigDict(extra="ignore")

    role: str = Field(default="analyst", description="Requested role: 'analyst' (default) or 'admin'.")
    admin_key: str | None = Field(default=None, description="Secret admin key required if requesting role='admin'.")


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
    """Issue a signed HMAC-SHA256 JWT demo access token.

    SECURITY GATING:
    - Gated behind DEMO_AUTH_ENABLED config flag. If False, returns HTTP 403 Forbidden.
    - Default role is 'analyst' (least privilege, masked).
    - Requesting 'admin' requires supplying the configured demo_admin_key (via request body or X-Demo-Admin-Key header).
      Without a valid key, returns HTTP 403 Forbidden.
    """
    if not api_settings.demo_auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo token issuance is disabled in this environment.",
        )

    target_role = (role or request.role or "analyst").strip().lower()
    if target_role == "admin":
        provided_key = request.admin_key or x_demo_admin_key
        if provided_key != api_settings.demo_admin_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin token issuance requires a valid demo admin key.",
            )
        role_norm = "admin"
    else:
        role_norm = "analyst"

    token = create_access_token(subject=f"demo-user-{role_norm}", role=role_norm)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=role_norm,
        expires_in_seconds=api_settings.jwt_expiry_seconds,
    )
