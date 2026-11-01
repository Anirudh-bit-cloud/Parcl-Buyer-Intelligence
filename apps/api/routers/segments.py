"""Segment catalog and deep-dive profiling router."""

from fastapi import APIRouter, HTTPException, Query

from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.schemas.segments import (
    SegmentDetailResponse,
    SegmentListResponse,
    SegmentSummaryItem,
    SilhouetteContext,
)
from apps.api.services.model_service import model_service

router = APIRouter(prefix="/api/v1/segments", tags=["Buyer Segments"])


@router.get("", response_model=SegmentListResponse, summary="Query Segment Catalog with PRD Cohort Filters")
async def list_segments(
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
) -> SegmentListResponse:
    """Retrieve catalog of all 4 segments recomputed dynamically on the filtered cohort."""
    active_filters = ActiveFilters(
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=assigned_cluster,
    )
    catalog = model_service.get_segment_catalog(active_filters)

    has_filter = any(
        [country, region, acquisition_purpose, client_type, assigned_cluster is not None]
    )

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=not has_filter,
        untested_assumptions_notice="Segment partitions derived from Model B3 (k=4). Metrics recomputed dynamically on active cohort.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return SegmentListResponse(
        production_variant=catalog["production_variant"],
        k_selected=catalog["k_selected"],
        cohort_total_buyers=catalog["cohort_total_buyers"],
        cohort_total_units=catalog["cohort_total_units"],
        cohort_mean_spend_inr=catalog["cohort_mean_spend_inr"],
        cohort_mean_spend_display=catalog["cohort_mean_spend_display"],
        cohort_total_spend_inr=catalog["cohort_total_spend_inr"],
        cohort_total_spend_display=catalog["cohort_total_spend_display"],
        buyer_weighted_office_share_pct=catalog["buyer_weighted_office_share_pct"],
        unit_weighted_office_share_pct=catalog["unit_weighted_office_share_pct"],
        segments=[SegmentSummaryItem(**s) for s in catalog["segments"]],
        silhouette_validation=SilhouetteContext(**catalog["silhouette_validation"]),
        active_filters=active_filters,
        metadata=metadata,
    )


@router.get("/{segment_id}", response_model=SegmentDetailResponse, summary="Get Deep-Dive Segment Statistical Profile")
async def get_segment_detail(
    segment_id: int,
    country: str | None = Query(default=None, description="Filter by buyer country."),
    region: str | None = Query(default=None, description="Filter by administrative region."),
    acquisition_purpose: str | None = Query(
        default=None, description="Filter by purchase intent (HOME or INVESTMENT)."
    ),
    client_type: str | None = Query(
        default=None, description="Filter by client type (INDIVIDUAL or COMPANY)."
    ),
) -> SegmentDetailResponse:
    """Retrieve deep-dive statistical distributions and surrogate splitting rules for a segment."""
    active_filters = ActiveFilters(
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=segment_id,
    )
    detail = model_service.get_segment_detail(segment_id, active_filters)
    if not detail:
        raise HTTPException(
            status_code=404, detail=f"Segment ID {segment_id} not found in evaluated cohort."
        )

    has_filter = any([country, region, acquisition_purpose, client_type])

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=not has_filter,
        untested_assumptions_notice="Surrogate rules represent shallow decision tree paths with 96.35% empirical fidelity.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return SegmentDetailResponse(
        segment_id=detail["segment_id"],
        segment_name=detail["segment_name"],
        persona_description=detail["persona_description"],
        buyer_count=detail["buyer_count"],
        population_share_pct=detail["population_share_pct"],
        mean_spend_inr=detail["mean_spend_inr"],
        mean_spend_display=detail["mean_spend_display"],
        total_spend_inr=detail["total_spend_inr"],
        total_spend_display=detail["total_spend_display"],
        mean_units=detail["mean_units"],
        commercial_office_share_pct=detail["commercial_office_share_pct"],
        numeric_metrics=detail["numeric_metrics"],
        categorical_distributions=detail["categorical_distributions"],
        surrogate_rules=detail["surrogate_rules"],
        silhouette_validation=SilhouetteContext(**detail["silhouette_validation"]),
        active_filters=active_filters,
        metadata=metadata,
    )
