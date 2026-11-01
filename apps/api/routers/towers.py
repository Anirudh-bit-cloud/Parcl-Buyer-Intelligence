"""Tower sales, pricing, and segment heatmap router."""

from fastapi import APIRouter, Query

from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.schemas.towers import TowerHeatmapResponse
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/api/v1/towers", tags=["Tower Intelligence & Heatmaps"])


@router.get(
    "",
    response_model=TowerHeatmapResponse,
    summary="Tower Sales, Pricing, and Segment Concentration Heatmap",
)
async def get_towers(
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
) -> TowerHeatmapResponse:
    """Evaluate property transaction volume, available inventory, and segment affinity across all 20 towers."""
    active_filters = ActiveFilters(
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=assigned_cluster,
    )
    res = data_service.get_towers(active_filters)

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="Physical development spans exactly 20 towers. Current inventory evaluates 313 deduplicated units.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return TowerHeatmapResponse(
        total_towers=res["total_towers"],
        total_sold_units=res["total_sold_units"],
        total_available_units=res["total_available_units"],
        towers=res["towers"],
        active_filters=active_filters,
        metadata=metadata,
    )
