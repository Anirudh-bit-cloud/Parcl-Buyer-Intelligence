"""Configuration settings for the FastAPI backend service."""

import os
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """Application configuration for Parcl Buyer Intelligence API."""

    model_config = SettingsConfigDict(env_prefix="PARCL_API_", extra="ignore")

    app_name: str = "Parcl Buyer Intelligence API"
    app_version: str = "1.2.0"
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = False

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Security & Authentication
    jwt_secret: str = Field(
        default="",
        description="HMAC SHA-256 secret key from environment (required outside development).",
    )
    jwt_algorithm: str = "HS256"
    jwt_expiry_seconds: int = 86400  # 24 hours

    # Demo Authentication Gating
    demo_auth_enabled: bool = Field(
        default=True,
        description="Whether /api/v1/auth/demo-token is enabled (default True in dev, False in production).",
    )
    demo_admin_key: str = Field(
        default="dev-demo-admin-key-parcl-2026",
        description="Shared secret key required to issue admin tokens from /demo-token.",
    )

    # CORS configuration (strictly explicit origins, no wildcard *)
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8501",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8501",
        ],
        description="Allowed CORS origins list.",
    )

    # Rate limiting (requests per minute per client IP)
    rate_limit_per_minute: int = 120

    # Currency and Accounting Standards
    currency: str = "INR"
    currency_symbol: str = "₹"

    # Reference Audit Date (Single configured constant used for all age computations)
    reference_date_str: str = "2025-12-31"

    # Paths (anchored on project root)
    project_root: Path = Path("e:/parcl-buyer-intelligence")
    data_dir: Path = Path("e:/parcl-buyer-intelligence/data")
    models_dir: Path = Path("e:/parcl-buyer-intelligence/data/models")
    interim_dir: Path = Path("e:/parcl-buyer-intelligence/data/interim")
    processed_dir: Path = Path("e:/parcl-buyer-intelligence/data/processed")

    @model_validator(mode="after")
    def validate_jwt_secret_and_env(self) -> "APISettings":
        """Enforce strict secret requirements outside development mode."""
        env_secret = os.environ.get("JWT_SECRET_KEY") or os.environ.get("PARCL_API_JWT_SECRET")
        if env_secret:
            self.jwt_secret = env_secret

        if self.environment.lower() != "development":
            if not self.jwt_secret or len(self.jwt_secret.strip()) == 0:
                raise RuntimeError(
                    "JWT secret key must be set via environment variable 'JWT_SECRET_KEY' "
                    "or 'PARCL_API_JWT_SECRET' outside development mode."
                )
        else:
            if not self.jwt_secret:
                self.jwt_secret = "dev-fallback-insecure-secret-key-for-local-testing-only-32bytes"
        return self


api_settings = APISettings()
