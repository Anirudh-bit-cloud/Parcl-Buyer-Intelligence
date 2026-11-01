"""Metadata and query filter enumeration router."""

from fastapi import APIRouter

from apps.api.schemas.common import ResponseMetadata
from apps.api.schemas.meta import MetaFiltersResponse
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/api/v1/meta", tags=["Metadata & Filters"])


@router.get(
    "/filters",
    response_model=MetaFiltersResponse,
    summary="Get PRD Dimension Filter Choices & Counts",
)
async def get_filters() -> MetaFiltersResponse:
    """Retrieve distinct choices and client counts for country, region, purpose, client_type, and cluster."""
    meta = data_service.get_meta_filters()
    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="Counts reflect discrete totals across the complete 2,000-buyer baseline cohort.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )
    return MetaFiltersResponse(
        total_clients=meta["total_clients"],
        countries=meta["countries"],
        regions=meta["regions"],
        acquisition_purposes=meta["acquisition_purposes"],
        client_types=meta["client_types"],
        assigned_clusters=meta["assigned_clusters"],
        metadata=metadata,
    )
