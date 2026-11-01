"""Investor Behavior router (PRD Module 2)."""

from fastapi import APIRouter, Query

from apps.api.schemas.behavior import InvestorBehaviorResponse
from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/api/v1/behavior", tags=["Investor Behavior (Module 2)"])


@router.get(
    "",
    response_model=InvestorBehaviorResponse,
    summary="Investor Behavior & Financing Analysis (PRD Module 2)",
)
async def get_behavior(
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
) -> InvestorBehaviorResponse:
    """Analyze acquisition purpose, mortgage financing dependency, and referral channel performance."""
    active_filters = ActiveFilters(
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=assigned_cluster,
    )
    res = data_service.get_behavior(active_filters)

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="Behavioral cross-tabulations computed directly from active microdata cohort.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return InvestorBehaviorResponse(
        total_buyers_evaluated=res["total_buyers_evaluated"],
        acquisition_purpose_breakdown=res["acquisition_purpose_breakdown"],
        loan_application_breakdown=res["loan_application_breakdown"],
        client_type_breakdown=res["client_type_breakdown"],
        referral_channel_breakdown=res["referral_channel_breakdown"],
        commercial_office_vs_residential=res["commercial_office_vs_residential"],
        active_filters=active_filters,
        metadata=metadata,
    )
