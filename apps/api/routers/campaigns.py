"""Marketing Scenario Calculator router grounded in empirical channel data."""

from fastapi import APIRouter, HTTPException

from apps.api.schemas.campaigns import ScenarioRequest, ScenarioResponse
from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.services.model_service import model_service

router = APIRouter(prefix="/api/v1/campaigns", tags=["Campaigns & Marketing Simulator"])


@router.post(
    "/scenario",
    response_model=ScenarioResponse,
    summary="Marketing Scenario Calculator (Illustrative GMV & Independence Findings)",
)
@router.post(
    "/allocate",
    response_model=ScenarioResponse,
    summary="Marketing Budget Allocation Calculator (Alias to /scenario)",
    include_in_schema=True,
)
@router.post(
    "/simulate",
    response_model=ScenarioResponse,
    summary="Marketing Simulation Calculator (Alias to /scenario)",
    include_in_schema=True,
)
async def run_scenario(request: ScenarioRequest) -> ScenarioResponse:
    """Calculate modeled marketing acquisition scenario grounded in empirical referral channel data.

    ASSUMPTION & REVENUE NOTICES:
    - Figures reflect modeled gross sales volume (GMV) in INR (₹), NOT net profit.
    - Illustrative user-provided CPAs are inputs, not modeled constants.
    - Empirical finding: channel mix is statistically independent of buyer segments (chi2=0.7500, p=0.9933).
    - Assumes every acquired client buys at historical average sales without funnel attribution.
    """
    try:
        res = model_service.run_marketing_scenario(
            total_budget_inr=request.total_budget_inr,
            channel_allocations=request.channel_allocations,
            channel_cpas_inr=request.channel_cpas_inr,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice=(
            "Gross sales volume (GMV) output in INR (₹); assumes every client buys at historical average; "
            "CPAs are user inputs; segment-channel targeting is empirically unsupported."
        ),
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return ScenarioResponse(
        calculator_type=res["calculator_type"],
        total_budget_inr=res["total_budget_inr"],
        total_budget_display=res["total_budget_display"],
        total_modeled_clients=res["total_modeled_clients"],
        total_modeled_gross_sales_volume_inr=res["total_modeled_gross_sales_volume_inr"],
        total_modeled_gross_sales_display=res["total_modeled_gross_sales_display"],
        revenue_label_notice=res["revenue_label_notice"],
        channel_targeting_empirical_finding=res["channel_targeting_empirical_finding"],
        channel_breakdown=res["channel_breakdown"],
        active_filters=ActiveFilters(),
        metadata=metadata,
    )
