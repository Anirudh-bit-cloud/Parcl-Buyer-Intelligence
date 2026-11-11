"""Dataset export router with RBAC masking, admin authorization, async job engine, and audit trail."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy import desc

from apps.api.auth import get_current_user_role
from apps.api.config import api_settings
from apps.api.db import AuditLogEntity, ExportJobEntity, SessionLocal, verify_audit_log_chain
from apps.api.middleware import record_audit
from apps.api.schemas.common import ActiveFilters, ResponseMetadata
from apps.api.schemas.export import (
    ExportClientRecord,
    ExportJobCreateRequest,
    ExportJobResponse,
    ExportResponse,
)
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/api/v1/export", tags=["Data Export"])

EXPORTS_DIR = api_settings.data_dir / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


@router.get(
    "",
    summary="Export Filtered Cohort Data with Admin Privilege and INR Currency",
    response_model=None,
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
    export_format: str = Query(
        default="csv", alias="format", description="Output format: 'csv' (default) or 'json'."
    ),
    role: Annotated[str, Depends(get_current_user_role)] = "analyst",
) -> Any:
    """Export buyer records in CSV or JSON. Restricted strictly to admin and auditor roles."""
    if role not in ["admin", "auditor"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Admin privilege required for bulk data export.",
        )

    active_filters = ActiveFilters(
        country=country,
        region=region,
        acquisition_purpose=acquisition_purpose,
        client_type=client_type,
        assigned_cluster=assigned_cluster,
    )
    res = data_service.get_export(active_filters, role=role)

    # Record immutable audit trail
    record_audit(
        user_id=f"user-{role}",
        role=role,
        action="EXPORT_SYNC",
        resource="/api/v1/export",
        details=f"Format: {export_format}, records: {res['exported_records_count']}, filters: {active_filters.model_dump()}",
    )

    if export_format.lower() == "csv":
        output = io.StringIO()
        fieldnames = [
            "client_id",
            "client_type",
            "first_name",
            "last_name",
            "country",
            "region",
            "age",
            "satisfaction_score",
            "loan_applied",
            "referral_channel",
            "total_spend_inr",
            "total_spend_display",
            "n_units",
            "office_share",
            "assigned_cluster",
            "assigned_segment_name",
            "currency",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in res["data"]:
            writer.writerow(row)

        return Response(
            content=output.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=clients_export.csv"},
        )

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice="Export format standardizes on INR currency units.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return ExportResponse(
        exported_records_count=res["exported_records_count"],
        currency="INR",
        data=[ExportClientRecord(**r) for r in res["data"]],
        active_filters=active_filters,
        metadata=metadata,
    )


@router.post(
    "/async",
    summary="Submit Idempotent Asynchronous Export Job",
    response_model=ExportJobResponse,
)
async def create_async_export_job(
    payload: ExportJobCreateRequest,
    role: Annotated[str, Depends(get_current_user_role)] = "analyst",
) -> ExportJobResponse:
    """Submit an asynchronous export request with deterministic job hash for idempotency."""
    if role not in ["admin", "auditor"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Admin or Auditor privilege required for asynchronous export jobs.",
        )

    if payload.format.lower() not in ["csv", "json"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported export format. Supported formats: 'csv', 'json'.",
        )

    filter_dict = payload.model_dump()
    filter_repr = json.dumps(filter_dict, sort_keys=True)
    job_hash = hashlib.sha256(f"{filter_repr}:{role}".encode()).hexdigest()[:16]
    job_id = f"job-{job_hash}"

    file_ext = "csv" if payload.format.lower() == "csv" else "json"
    file_path = EXPORTS_DIR / f"{job_id}.{file_ext}"

    # Generate data
    active_filters = ActiveFilters(
        country=payload.country,
        region=payload.region,
        acquisition_purpose=payload.acquisition_purpose,
        client_type=payload.client_type,
        assigned_cluster=payload.assigned_cluster,
    )
    res = data_service.get_export(active_filters, role=role)

    if file_ext == "csv":
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "client_id",
                "client_type",
                "first_name",
                "last_name",
                "country",
                "region",
                "age",
                "satisfaction_score",
                "loan_applied",
                "referral_channel",
                "total_spend_inr",
                "total_spend_display",
                "n_units",
                "office_share",
                "assigned_cluster",
                "assigned_segment_name",
                "currency",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in res["data"]:
                writer.writerow(r)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)

    now_iso = datetime.now(UTC).isoformat()

    # Save to database
    with SessionLocal() as session:
        existing = session.query(ExportJobEntity).filter_by(job_id=job_id).first()
        if not existing:
            job_record = ExportJobEntity(
                job_id=job_id,
                user_id=f"user-{role}",
                role=role,
                status="completed",
                format=file_ext,
                filter_params=filter_repr,
                record_count=res["exported_records_count"],
                file_path=str(file_path),
            )
            session.add(job_record)
            session.commit()

    record_audit(
        user_id=f"user-{role}",
        role=role,
        action="EXPORT_ASYNC_CREATED",
        resource=f"/api/v1/export/jobs/{job_id}",
        details=f"Job {job_id} generated with {res['exported_records_count']} rows.",
    )

    return ExportJobResponse(
        job_id=job_id,
        status="completed",
        format=file_ext,
        created_at=now_iso,
        record_count=res["exported_records_count"],
        download_url=f"/api/v1/export/jobs/{job_id}/download",
    )


@router.get(
    "/jobs/{job_id}",
    summary="Get Asynchronous Export Job Status",
    response_model=ExportJobResponse,
)
async def get_async_export_job(
    job_id: str,
    role: Annotated[str, Depends(get_current_user_role)] = "analyst",
) -> ExportJobResponse:
    """Retrieve the current processing state and download link for an export job."""
    if role not in ["admin", "auditor"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Admin or Auditor privilege required to inspect export jobs.",
        )

    with SessionLocal() as session:
        job = session.query(ExportJobEntity).filter_by(job_id=job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Export job '{job_id}' not found.")

        return ExportJobResponse(
            job_id=str(job.job_id),
            status=str(job.status),
            format=str(job.format),
            created_at=job.created_at.isoformat() if job.created_at else "",
            record_count=int(job.record_count),
            download_url=f"/api/v1/export/jobs/{job.job_id}/download"
            if job.status == "completed"
            else None,
            error_message=str(job.error_message) if job.error_message else None,
        )


@router.get(
    "/jobs/{job_id}/download",
    summary="Download Completed Export File",
)
async def download_export_job_file(
    job_id: str,
    role: Annotated[str, Depends(get_current_user_role)] = "analyst",
) -> Response:
    """Download the generated export artifact for a completed job."""
    if role not in ["admin", "auditor"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Admin or Auditor privilege required to download export files.",
        )

    with SessionLocal() as session:
        job = session.query(ExportJobEntity).filter_by(job_id=job_id).first()
        if not job or not job.file_path or not Path(job.file_path).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Export artifact for job '{job_id}' is unavailable.",
            )

        record_audit(
            user_id=f"user-{role}",
            role=role,
            action="EXPORT_FILE_DOWNLOADED",
            resource=f"/api/v1/export/jobs/{job_id}/download",
            details=f"Downloaded {job.record_count} rows.",
        )

        media_type = "text/csv; charset=utf-8" if job.format == "csv" else "application/json"
        return FileResponse(
            path=job.file_path,
            filename=f"parcl_export_{job_id}.{job.format}",
            media_type=media_type,
        )


@router.get(
    "/audit-logs",
    summary="Query Immutable Security Audit Trail",
)
async def get_audit_logs(
    limit: int = Query(default=50, ge=1, le=500),
    role: Annotated[str, Depends(get_current_user_role)] = "analyst",
) -> dict[str, Any]:
    """Retrieve immutable security and export audit logs (Admin & Auditor only)."""
    if role not in ["admin", "auditor"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Auditor or Admin role required to inspect audit logs.",
        )

    with SessionLocal() as session:
        logs = session.query(AuditLogEntity).order_by(desc(AuditLogEntity.id)).limit(limit).all()
        chain_verification = verify_audit_log_chain(session)
        return {
            "total_returned": len(logs),
            "chain_verification": chain_verification,
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else "",
                    "user_id": log.user_id,
                    "role": log.role,
                    "action": log.action,
                    "resource": log.resource,
                    "details": log.details,
                    "ip_address": log.ip_address,
                    "prev_hash": log.prev_hash,
                    "entry_hash": log.entry_hash,
                }
                for log in logs
            ],
        }


@router.get(
    "/audit-logs/verify",
    summary="Cryptographically Verify Audit Log Hash Chain (Auditor & Admin)",
)
async def verify_audit_logs(
    role: Annotated[str, Depends(get_current_user_role)] = "analyst",
) -> dict[str, Any]:
    """Verify cryptographic integrity of append-only audit trail."""
    if role not in ["admin", "auditor"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Auditor or Admin role required to verify audit log chain.",
        )

    with SessionLocal() as session:
        return verify_audit_log_chain(session)
