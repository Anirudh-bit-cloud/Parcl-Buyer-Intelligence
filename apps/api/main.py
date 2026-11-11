"""FastAPI application entrypoint for Parcl Buyer Intelligence Platform."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from apps.api.auth import get_current_user_role
from apps.api.config import api_settings
from apps.api.db import init_db
from apps.api.middleware import (
    ETagMiddleware,
    InMemoryRateLimitMiddleware,
    PerformanceTimingMiddleware,
    RequestIdAndLoggingMiddleware,
)
from apps.api.routers import (
    auth,
    behavior,
    campaigns,
    clients,
    datasets,
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

logger = logging.getLogger("parcl.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle events: initialize relational schema and telemetry."""
    init_db()

    if api_settings.telemetry_enabled:
        try:
            from opentelemetry import trace
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            from opentelemetry.sdk.trace import TracerProvider

            trace.set_tracer_provider(TracerProvider())
            FastAPIInstrumentor.instrument_app(app)
            logger.info("OpenTelemetry tracing instrumentation enabled.")
        except Exception as exc:
            logger.warning("Could not initialize OpenTelemetry: %s", exc)

    yield


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
        lifespan=lifespan,
    )

    # Middleware registration (Starlette executes bottom-up / onion model)
    # 1. Configured CORS (strictly explicit origins from config, no wildcard *)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["ETag", "X-Process-Time-Ms", "X-Request-ID", "Vary"],
    )

    # 2. Performance timing header
    app.add_middleware(PerformanceTimingMiddleware)

    # 3. HTTP ETag caching & 304 handling (Role-Aware)
    app.add_middleware(ETagMiddleware)

    # 4. In-memory / Redis sliding window rate limiter (120 req/min per IP)
    app.add_middleware(
        InMemoryRateLimitMiddleware,
        max_requests_per_minute=api_settings.rate_limit_per_minute,
    )

    # 5. Request ID & Structured Logging Middleware
    app.add_middleware(RequestIdAndLoggingMiddleware)

    # RFC 7807 Problem+JSON Error Handling with 100% backward compatibility
    @app.exception_handler(HTTPException)
    async def rfc7807_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        req_id = getattr(request.state, "request_id", None)
        response_headers = {"Content-Type": "application/problem+json"}
        if exc.headers:
            response_headers.update(exc.headers)
        return JSONResponse(
            status_code=exc.status_code,
            headers=response_headers,
            content={
                "type": f"https://httpstatuses.com/{exc.status_code}",
                "title": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": request.url.path,
                "request_id": req_id,
            },
        )

    # Public routers (no auth required)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(meta.router)
    app.include_router(datasets.router)

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

    # Mount SPA static build if exists (for unified production deployment)
    dist_dir = Path(__file__).resolve().parents[2] / "apps" / "web" / "dist"
    if dist_dir.exists():
        assets_dir = dist_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static_assets")

        @app.get("/app", tags=["SPA"], include_in_schema=False)
        @app.get("/app/{full_path:path}", tags=["SPA"], include_in_schema=False)
        async def serve_spa(full_path: str = "") -> Response:
            index_path = dist_dir / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
            return JSONResponse(status_code=404, content={"detail": "SPA index not built"})

    @app.get("/", tags=["Root"], summary="API Root Discovery & SPA Entry")
    async def root(request: Request) -> Response:
        accept = request.headers.get("accept", "")
        if "text/html" in accept and dist_dir.exists() and (dist_dir / "index.html").exists():
            return FileResponse(str(dist_dir / "index.html"))
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

    @app.get("/api/v1", tags=["Root"], summary="API v1 Discovery")
    async def api_v1_root() -> JSONResponse:
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

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(request: Request, full_path: str) -> Response:
        accept = request.headers.get("accept", "")
        if full_path.startswith(("api/", "health/", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404, detail="Not Found")
        if dist_dir.exists():
            index_path = dist_dir / "index.html"
            if "text/html" in accept and index_path.exists():
                return FileResponse(str(index_path))
        raise HTTPException(status_code=404, detail="Not Found")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.api.main:app", host=api_settings.host, port=api_settings.port, reload=True)
