"""Authentication and RBAC token services for Parcl Buyer Intelligence API."""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from fastapi import Header, HTTPException, status

from apps.api.config import api_settings

VALID_ROLES = {"viewer", "analyst", "admin", "auditor"}


def create_access_token(
    subject: str,
    role: str = "analyst",
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed HMAC-SHA256 JWT access token."""
    now = datetime.now(UTC)
    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(seconds=api_settings.jwt_expiry_seconds)

    norm_role = role.lower() if role.lower() in VALID_ROLES else "analyst"

    payload = {
        "sub": subject,
        "role": norm_role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "parcl-api",
    }
    return jwt.encode(payload, api_settings.jwt_secret, algorithm=api_settings.jwt_algorithm)


def create_refresh_token(
    subject: str,
    role: str = "analyst",
    expires_delta: timedelta | None = None,
) -> str:
    """Create a long-lived signed HMAC-SHA256 JWT refresh token."""
    now = datetime.now(UTC)
    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(seconds=api_settings.jwt_refresh_expiry_seconds)

    norm_role = role.lower() if role.lower() in VALID_ROLES else "analyst"

    payload = {
        "sub": subject,
        "role": norm_role,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "parcl-api",
    }
    return jwt.encode(payload, api_settings.jwt_secret, algorithm=api_settings.jwt_algorithm)


def verify_refresh_token(token: str) -> dict[str, str]:
    """Verify and decode a refresh token, ensuring type='refresh'."""
    try:
        payload = jwt.decode(
            token,
            api_settings.jwt_secret,
            algorithms=[api_settings.jwt_algorithm],
            issuer="parcl-api",
            options={"require": ["exp", "iat", "sub", "role"]},
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type: expected refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"sub": str(payload.get("sub")), "role": str(payload.get("role", "analyst"))}
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please log in again.",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="refresh token expired"'},
        ) from e
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token: signature invalid.",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="invalid token"'},
        ) from e


def create_token_pair(subject: str, role: str) -> dict[str, Any]:
    """Create a coordinated Access Token + Refresh Token pair."""
    norm_role = role.lower() if role.lower() in VALID_ROLES else "analyst"
    access_token = create_access_token(subject=subject, role=norm_role)
    refresh_token = create_refresh_token(subject=subject, role=norm_role)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": norm_role,
        "expires_in_seconds": api_settings.jwt_expiry_seconds,
    }


def get_current_user_role(
    authorization: Annotated[str | None, Header(description="Bearer <JWT>")] = None,
) -> str:
    """Extract and verify user RBAC role from Authorization header.

    STRICT AUTHENTICATION POLICY:
    Every protected endpoint requires a valid 'Authorization: Bearer <token>' header.
    Missing, malformed, expired, or tampered tokens return HTTP 401 Unauthorized.
    Public endpoints (/health, /meta/filters, /auth/demo-token) do not require authentication.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Please provide 'Authorization: Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    try:
        payload = jwt.decode(
            token,
            api_settings.jwt_secret,
            algorithms=[api_settings.jwt_algorithm],
            issuer="parcl-api",
            options={"require": ["exp", "iat", "sub", "role"]},
        )
        role = payload.get("role", "analyst")
        return str(role).lower()
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please request a new token.",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="token expired"'},
        ) from e
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: signature verification failed.",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="tampered or invalid token"'},
        ) from e
