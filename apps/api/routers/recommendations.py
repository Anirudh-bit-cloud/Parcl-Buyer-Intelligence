"""Opportunity Finder and Next-Best-Offer recommendations router."""

from fastapi import APIRouter, HTTPException, Query

from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.schemas.recommendations import (
    NBORecommendationItem,
    NBOResponse,
    OpportunityFinderResponse,
    ScoredPropertyListingItem,
)
from apps.api.services.model_service import model_service

router = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendation Engines"])


@router.get(
    "/opportunities",
    response_model=OpportunityFinderResponse,
    summary="Opportunity Finder: Rank Available Inventory by Segment Affinity",
)
async def get_opportunities(
    segment_id: int = Query(ge=0, le=3, description="Target segment ID (0, 1, 2, 3)."),
    category_filter: str | None = Query(
        default=None,
        description="Optional filter by unit category ('Apartment' or 'Office').",
    ),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of listings to return."),
) -> OpportunityFinderResponse:
    """Rank currently available physical inventory (313 units as of Dec 2025) for a target buyer segment."""
    try:
        res = model_service.get_opportunities(
            segment_id=segment_id, category_filter=category_filter, limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    active_filters = ActiveFilters(assigned_cluster=segment_id)

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice=(
            "Heuristic scoring weights: category=0.35, price=0.30, floor_area=0.20, tower=0.15; "
            "evaluated strictly against 313 deduplicated currently available physical units as of Dec 2025."
        ),
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return OpportunityFinderResponse(
        target_segment_id=res["target_segment_id"],
        target_segment_name=res["target_segment_name"],
        category_filter_applied=res["category_filter_applied"],
        total_inventory_evaluated=res["total_inventory_evaluated"],
        recommendations=[ScoredPropertyListingItem(**r) for r in res["recommendations"]],
        active_filters=active_filters,
        metadata=metadata,
    )


@router.get(
    "/nbo/{client_id}",
    response_model=NBOResponse,
    summary="Personalized Next-Best-Offer Recommendations for a Buyer",
)
async def get_client_nbo(
    client_id: str,
    category_filter: str | None = Query(
        default=None,
        description="Optional category filter ('Apartment' or 'Office').",
    ),
    top_n: int = Query(default=5, ge=1, le=20, description="Number of recommendations."),
) -> NBOResponse:
    """Generate unclipped additive Next-Best-Offer recommendations with 20-tower diversification bonus."""
    try:
        res = model_service.get_nbo_recommendations(
            client_id=client_id, category_filter=category_filter, top_n=top_n
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if not res:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found.")

    active_filters = ActiveFilters(assigned_cluster=res["client_segment_id"])

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice=(
            "Untested assumptions: Tower diversification bonus (+0.15) and category bonus (+0.10) "
            "are additive heuristic adjustments. Portfolio spans 20 towers; ~81.86% of available units earn tower bonus."
        ),
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return NBOResponse(
        client_id=res["client_id"],
        client_segment_id=res["client_segment_id"],
        client_segment_name=res["client_segment_name"],
        owned_towers=res["owned_towers"],
        unowned_towers_count=res["unowned_towers_count"],
        mean_bonus_eligibility_share_pct=res["mean_bonus_eligibility_share_pct"],
        recommendations=[NBORecommendationItem(**r) for r in res["recommendations"]],
        active_filters=active_filters,
        metadata=metadata,
    )
