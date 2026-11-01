"""Geographic Buyer Intelligence router (PRD Module 3)."""

from fastapi import APIRouter, Query

from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.schemas.geo import GeographicIntelligenceResponse
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/api/v1/geo", tags=["Geographic Analysis (Module 3)"])


@router.get(
    "",
    response_model=GeographicIntelligenceResponse,
    summary="Geographic Buyer Analysis & Domestic vs International (PRD Module 3)",
)
async def get_geo(
    country: str | None = Query(default=None, description="Filter by buyer country."),
    region: str | None = Query(default=None, description="Filter by administrative region."),
    acquisition_purpose: str | None = Query(
        default=None, description="Filter by purchase intent (HOME or INVESTMENT)."
    ),
    client_type: str | None = Query(
        default=None, description="Filter by client type (INDIVIDUAL or COMPANY)."
    ),
    assigned_cluster: int | None = Query(
        default=None, ge=0, le=3, description="Filter by assigned segment ID (0, 1, 2, 3)."
    ),
) -> GeographicIntelligenceResponse:
    """Analyze geographic concentration, domestic vs international spend disparity, and regional clusters."""
    active_filters = ActiveFilters(
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=assigned_cluster,
    )
    res = data_service.get_geo(active_filters)

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="Geographic significance evaluated via Welch's two-sample t-test and Cohen's d effect size.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return GeographicIntelligenceResponse(
        total_buyers_evaluated=res["total_buyers_evaluated"],
        domestic_vs_international=res["domestic_vs_international"],
        top_countries=res["top_countries"],
        top_regions=res["top_regions"],
        active_filters=active_filters,
        metadata=metadata,
    )
