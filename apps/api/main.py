"""FastAPI application entrypoint for Parcl Buyer Intelligence Platform."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.auth import get_current_user_role
from apps.api.config import api_settings
from apps.api.middleware import (
    ETagMiddleware,
    InMemoryRateLimitMiddleware,
    PerformanceTimingMiddleware,
)
from apps.api.routers import (
    auth,
    behavior,
    campaigns,
    clients,
    export,
    geo,
    health,
    meta,
    model_governance,
    overview,
    predictions,
    projections,
    recommendations,
    segments,
    towers,
)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(
        title=api_settings.app_name,
        version=api_settings.app_version,
        description=(
            "Production-grade buyer segmentation and investment-profiling API for Parcl Co. Limited "
            "(Unified Mentor program sponsor). Zero fabricated numbers; all endpoints grounded on "
            "empirical data and audited Model B3 cluster inference. All monetary figures in INR (₹)."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Middleware registration (Starlette executes bottom-up / onion model)
    # 1. Configured CORS (strictly explicit origins from config, no wildcard *)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["ETag", "X-Process-Time-Ms", "Vary"],
    )

    # 2. Performance timing header
    app.add_middleware(PerformanceTimingMiddleware)

    # 3. HTTP ETag caching & 304 handling (Role-Aware)
    app.add_middleware(ETagMiddleware)

    # 4. In-memory sliding window rate limiter (120 req/min per IP)
    app.add_middleware(
        InMemoryRateLimitMiddleware,
        max_requests_per_minute=api_settings.rate_limit_per_minute,
    )

    # Public routers (no auth required)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(meta.router)

    # Protected routers (strict Bearer token required, 401 if missing)
    auth_dep = [Depends(get_current_user_role)]
    app.include_router(overview.router, dependencies=auth_dep)
    app.include_router(clients.router, dependencies=auth_dep)
    app.include_router(segments.router, dependencies=auth_dep)
    app.include_router(behavior.router, dependencies=auth_dep)
    app.include_router(geo.router, dependencies=auth_dep)
    app.include_router(towers.router, dependencies=auth_dep)
    app.include_router(recommendations.router, dependencies=auth_dep)
    app.include_router(campaigns.router, dependencies=auth_dep)
    app.include_router(predictions.router, dependencies=auth_dep)
    app.include_router(model_governance.router, dependencies=auth_dep)
    app.include_router(projections.router, dependencies=auth_dep)
    app.include_router(export.router, dependencies=auth_dep)

    @app.get("/", tags=["Root"], summary="API Root Discovery")
    @app.get("/api/v1", tags=["Root"], summary="API v1 Discovery")
    async def root() -> JSONResponse:
        return JSONResponse(
            content={
                "name": api_settings.app_name,
                "version": api_settings.app_version,
                "status": "online",
                "as_of": "December 2025",
                "currency": api_settings.currency,
                "currency_symbol": api_settings.currency_symbol,
                "docs": "/docs",
                "openapi": "/openapi.json",
                "api_v1_prefix": "/api/v1",
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.api.main:app", host=api_settings.host, port=api_settings.port, reload=True)
