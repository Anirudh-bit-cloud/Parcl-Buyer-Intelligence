"""Health check, readiness, liveness, and Prometheus metrics router."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import text

from apps.api.config import api_settings
from apps.api.db import engine
from apps.api.services.data_service import data_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["System Health & Observability"])

# Prometheus Metrics Definitions
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)


@router.get("/health/live", summary="Kubernetes Liveness Probe")
@router.get("/api/v1/health/live", include_in_schema=False)
async def health_live() -> dict[str, str]:
    """Lightweight probe verifying the HTTP server process is running."""
    return {"status": "alive"}


@router.get("/health/ready", summary="Kubernetes Readiness Probe")
@router.get("/api/v1/health/ready", include_in_schema=False)
async def health_ready() -> dict[str, Any]:
    """Readiness probe verifying operational dependencies (PostgreSQL / SQLite, Redis, Datasets)."""
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Readiness probe database connection error: %s", exc)
        db_status = f"unhealthy: {exc}"

    redis_status = "disabled"
    if api_settings.redis_enabled:
        try:
            import redis

            r = redis.from_url(api_settings.redis_url, socket_timeout=1.0)
            r.ping()
            redis_status = "connected"
        except Exception as exc:
            logger.warning("Readiness probe Redis check warning: %s", exc)
            redis_status = f"unreachable: {exc}"

    is_ready = db_status == "connected" and not redis_status.startswith("unreachable")
    return {
        "status": "ready" if is_ready else "degraded",
        "database": db_status,
        "redis": redis_status,
        "records_loaded": len(data_service.client_features),
    }


@router.get("/metrics", summary="Prometheus Metrics Scrape Endpoint")
async def prometheus_metrics() -> Response:
    """Exposes Prometheus application and runtime metrics in OpenMetrics/text format."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/api/v1/health", summary="Health Check & Microdata Metrics")
@router.get("/api/health", include_in_schema=False)
async def health_check() -> dict[str, Any]:
    """Return system online status, dataset record counts, and accounting currency."""
    return {
        "status": "healthy",
        "service": api_settings.app_name,
        "version": api_settings.app_version,
        "environment": api_settings.environment,
        "currency": api_settings.currency,
        "currency_symbol": api_settings.currency_symbol,
        "reference_date": api_settings.reference_date_str,
        "datasets": {
            "clients_count": len(data_service.client_features),
            "transactions_count": len(data_service.transactions),
            "current_available_inventory": len(data_service.available_properties),
            "towers_count": 20,
            "as_of": "December 2025",
        },
    }
