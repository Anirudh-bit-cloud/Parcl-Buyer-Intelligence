"""Health check and service status router."""

from typing import Any

from fastapi import APIRouter

from apps.api.config import api_settings
from apps.api.services.data_service import data_service

router = APIRouter(tags=["System Health"])


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
