"""Dataset export router with RBAC masking and PRD filtering."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from apps.api.auth import get_current_user_role
from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.schemas.export import ExportClientRecord, ExportResponse
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/api/v1/export", tags=["Data Export"])


@router.get(
    "",
    response_model=ExportResponse,
    summary="Export Filtered Cohort Data with RBAC Masking (INR)",
)
async def export_cohort_data(
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
) -> ExportResponse:
    """Export buyer records respecting active PRD filters, RBAC identity masking, and INR currency."""
    active_filters = ActiveFilters(
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=assigned_cluster,
    )
    res = data_service.get_export(active_filters, role=role)

    notices = [
        "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
    ]
    if role != "admin":
        notices.append("Server-side personal identity masking active under current role.")

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="Export format standardizes on INR currency units.",
        notices=notices,
    )

    return ExportResponse(
        exported_records_count=res["exported_records_count"],
        currency="INR",
        data=[ExportClientRecord(**r) for r in res["data"]],
        active_filters=active_filters,
        metadata=metadata,
    )
