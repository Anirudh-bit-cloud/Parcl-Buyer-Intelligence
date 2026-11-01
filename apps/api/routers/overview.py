"""Executive Overview router (PRD Module 1)."""

from fastapi import APIRouter, Query

from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.schemas.overview import ExecutiveOverviewResponse
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/api/v1/overview", tags=["Executive Overview (Module 1)"])


@router.get(
    "",
    response_model=ExecutiveOverviewResponse,
    summary="Executive Overview KPIs & Segment Distribution (PRD Module 1)",
)
async def get_overview(
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
) -> ExecutiveOverviewResponse:
    """Compute high-level executive KPIs, segment breakdown, and key takeaways for filtered cohort."""
    active_filters = ActiveFilters(
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=assigned_cluster,
    )
    res = data_service.get_overview(active_filters)

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="All monetary values displayed in Indian Rupees (₹) with Indian lakh/crore digit grouping.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return ExecutiveOverviewResponse(
        total_buyers=res["total_buyers"],
        total_transactions=res["total_transactions"],
        total_sales_volume_inr=res["total_sales_volume_inr"],
        total_sales_volume_display=res["total_sales_volume_display"],
        mean_sales_price_inr=res["mean_sales_price_inr"],
        mean_sales_price_display=res["mean_sales_price_display"],
        mean_units_per_buyer=res["mean_units_per_buyer"],
        mean_buyer_spend_inr=res["mean_buyer_spend_inr"],
        mean_buyer_spend_display=res["mean_buyer_spend_display"],
        available_units_count=res["available_units_count"],
        towers_count=res["towers_count"],
        segments=res["segments"],
        key_takeaways=res["key_takeaways"],
        active_filters=active_filters,
        metadata=metadata,
    )
