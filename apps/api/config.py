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

    # Database Configuration (PostgreSQL primary with SQLite local fallback)
    database_url: str = Field(
        default="sqlite:///e:/parcl-buyer-intelligence/data/parcl.db",
        description="Database connection URI (e.g. postgresql+psycopg2://... or sqlite:///...)",
    )
    database_echo: bool = False

    # Redis Caching & Distributed Rate Limiting
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for distributed caching and rate limiting.",
    )
    redis_enabled: bool = Field(
        default=False,
        description="Whether to use external Redis; falls back to in-memory sliding window when False or unreachable.",
    )

    # Currency, Foreign Exchange & Accounting Standards
    currency: str = "INR"
    currency_symbol: str = "₹"
    fx_rate_usd_to_inr: float = Field(
        default=83.50,
        description="Configurable foreign exchange conversion rate from USD to INR.",
    )
    apply_fx_conversion: bool = Field(
        default=False,
        description="If True, multiplies raw USD figures by fx_rate_usd_to_inr. If False, figures are unscaled relabeled.",
    )

    # OpenTelemetry & Prometheus Observability
    telemetry_enabled: bool = Field(
        default=False,
        description="Enable OpenTelemetry tracing instrumentation.",
    )

    # Generic OIDC / SSO Configuration
    oidc_enabled: bool = Field(
        default=False,
        description="Enable enterprise generic OIDC single sign-on authentication.",
    )
    oidc_issuer: str = Field(
        default="",
        description="OIDC Provider discovery issuer URL.",
    )
    oidc_client_id: str = Field(
        default="",
        description="OIDC Client ID.",
    )
    oidc_client_secret: str = Field(
        default="",
        description="OIDC Client Secret.",
    )
    oidc_jwks_uri: str = Field(
        default="",
        description="OIDC JSON Web Key Set URI (auto-discovered if omitted).",
    )
    oidc_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/oidc/callback",
        description="OIDC Redirect URI callback.",
    )

    # Refresh Token Lifespan
    jwt_refresh_expiry_seconds: int = Field(
        default=604800,  # 7 days
        description="Lifespan of refresh tokens in seconds.",
    )

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
        """Enforce strict production startup guards and secret requirements."""
        env_from_os = os.environ.get("PARCL_API_ENVIRONMENT") or os.environ.get("ENVIRONMENT")
        if env_from_os:
            self.environment = env_from_os

        admin_key_os = os.environ.get("PARCL_API_DEMO_ADMIN_KEY") or os.environ.get("DEMO_ADMIN_KEY")
        if admin_key_os:
            self.demo_admin_key = admin_key_os

        demo_auth_os = os.environ.get("PARCL_API_DEMO_AUTH_ENABLED") or os.environ.get("DEMO_AUTH_ENABLED")
        if demo_auth_os is not None:
            self.demo_auth_enabled = demo_auth_os.strip().lower() in ("true", "1", "yes")

        env_secret = os.environ.get("JWT_SECRET_KEY") or os.environ.get("PARCL_API_JWT_SECRET")
        if env_secret:
            self.jwt_secret = env_secret

        env_lower = self.environment.lower()
        if env_lower != "development":
            if not self.jwt_secret or len(self.jwt_secret.strip()) == 0:
                raise RuntimeError(
                    "JWT secret key must be set via environment variable 'JWT_SECRET_KEY' "
                    "or 'PARCL_API_JWT_SECRET' outside development mode."
                )
            if self.jwt_secret == "dev-fallback-insecure-secret-key-for-local-testing-only-32bytes":
                raise RuntimeError(
                    "Default development JWT secret detected! You must provide a secure, unique "
                    "JWT secret key outside development mode."
                )
            if len(self.jwt_secret) < 32:
                raise RuntimeError("JWT secret key must be at least 32 characters long in production/staging.")

            if env_lower == "production":
                if self.demo_admin_key in ["dev-demo-admin-key-parcl-2026", "admin-secret-key-change-in-production", "admin", "admin123", "secret"]:
                    raise RuntimeError(
                        "Default or insecure demo_admin_key detected in production environment! "
                        "You must set a secure DEMO_ADMIN_KEY via environment variable."
                    )
                if self.demo_auth_enabled:
                    raise RuntimeError(
                        "Production Startup Guard: DEMO_AUTH_ENABLED must be False in production mode. "
                        "Use OIDC/SSO authentication in enterprise deployment."
                    )
        else:
            if not self.jwt_secret:
                self.jwt_secret = "dev-fallback-insecure-secret-key-for-local-testing-only-32bytes"
        return self


api_settings = APISettings()
