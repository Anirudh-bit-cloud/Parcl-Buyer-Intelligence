"""Client directory and individual buyer profiling router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api.auth import get_current_user_role
from apps.api.schemas.clients import ClientDetailResponse, ClientListResponse
from apps.api.schemas.common import ActiveFilters, PaginationMetadata, ResponseMetadata
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/api/v1/clients", tags=["Clients & Directory"])


@router.get("", response_model=ClientListResponse, summary="Query Client Directory with PRD Filters")
async def list_clients(
    page: int = Query(default=1, ge=1, description="Page number."),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page."),
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
    role: Annotated[str, Depends(get_current_user_role)] = "analyst",
) -> ClientListResponse:
    """Retrieve paginated buyer directory filtered by PRD attributes with role-based name masking."""
    result = data_service.get_clients(
        page=page,
        page_size=page_size,
        role=role,
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=assigned_cluster,
    )

    notices = [
        "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
    ]
    if role != "admin":
        notices.append("Server-side personal identity masking active under current role.")

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="None",
        notices=notices,
    )

    return ClientListResponse(
        clients=result["clients"],
        pagination=PaginationMetadata(**result["pagination"]),
        active_filters=ActiveFilters(**result["active_filters"]),
        metadata=metadata,
    )


@router.get("/{client_id}", response_model=ClientDetailResponse, summary="Get Full Buyer Profile & Portfolio")
async def get_client_detail(
    client_id: str,
    role: Annotated[str, Depends(get_current_user_role)] = "analyst",
) -> ClientDetailResponse:
    """Retrieve full buyer profile, 20-tower holdings, and historical portfolio transactions."""
    client = data_service.get_client_detail(client_id, role=role)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found.")

    notices = [
        "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
    ]
    if role != "admin":
        notices.append("Server-side personal identity masking active under current role.")

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="None",
        notices=notices,
    )

    return ClientDetailResponse(
        client_id=client["client_id"],
        client_type=client["client_type"],
        first_name=client["first_name"],
        last_name=client["last_name"],
        country=client["country"],
        region=client["region"],
        age=client["age"],
        satisfaction_score=client["satisfaction_score"],
        loan_applied=client["loan_applied"],
        referral_channel=client["referral_channel"],
        total_spend_inr=client["total_spend_inr"],
        total_spend_display=client["total_spend_display"],
        n_units=client["n_units"],
        office_share=client["office_share"],
        owned_towers=client["owned_towers"],
        assigned_cluster=client["assigned_cluster"],
        assigned_segment_name=client["assigned_segment_name"],
        soft_membership_probabilities=client["soft_membership_probabilities"],
        is_ambiguous_boundary=client["is_ambiguous_boundary"],
        is_ambiguous_margin=client["is_ambiguous_margin"],
        transactions=client["transactions"],
        metadata=metadata,
    )
