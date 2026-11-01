"""2D Latent space projection router for cluster visualization."""

from fastapi import APIRouter, Query

from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.schemas.projections import ProjectedPoint, ProjectionResponse
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/api/v1/projection", tags=["Cluster Projections"])


@router.get(
    "",
    response_model=ProjectionResponse,
    summary="Get 2D Latent Space Coordinates for Visualization",
)
async def get_projections(
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
) -> ProjectionResponse:
    """Retrieve 2D PCA projection coordinates for interactive cluster exploration."""
    active_filters = ActiveFilters(
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=assigned_cluster,
    )
    res = data_service.get_projections(active_filters)

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="2D projection fitted on standardized continuous behavioral features via PCA.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return ProjectionResponse(
        projection_method=res["projection_method"],
        total_points=res["total_points"],
        explained_variance_ratio=res["explained_variance_ratio"],
        points=[ProjectedPoint(**p) for p in res["points"]],
        active_filters=active_filters,
        metadata=metadata,
    )
