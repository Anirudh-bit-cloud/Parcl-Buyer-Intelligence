"""Pydantic v2 schemas for filtered dataset export and asynchronous export jobs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apps.api.schemas.common import ActiveFilters, ResponseMetadata


class ExportClientRecord(BaseModel):
    """Full exported client record with RBAC masking and INR currency."""

    model_config = ConfigDict(extra="ignore")

    client_id: str
    client_type: str
    first_name: str
    last_name: str
    country: str
    region: str
    age: int
    satisfaction_score: int
    loan_applied: bool
    referral_channel: str
    total_spend_inr: float
    total_spend_display: str
    n_units: int
    office_share: float
    assigned_cluster: int
    assigned_segment_name: str
    currency: str = "INR"


class ExportResponse(BaseModel):
    """Export payload containing filtered records and governance metadata."""

    model_config = ConfigDict(extra="ignore")

    exported_records_count: int = Field(examples=[2000])
    currency: str = Field(default="INR", examples=["INR"])
    data: list[ExportClientRecord]
    active_filters: ActiveFilters
    metadata: ResponseMetadata


class ExportJobCreateRequest(BaseModel):
    """Payload for submitting an asynchronous export job."""

    model_config = ConfigDict(extra="ignore")

    format: str = Field(default="csv", description="Export file format: 'csv' or 'json'.")
    country: str | None = None
    region: str | None = None
    acquisition_purpose: str | None = None
    client_type: str | None = None
    assigned_cluster: int | None = Field(default=None, ge=0, le=3)

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if v.lower() not in ["csv", "json"]:
            raise ValueError(f"Unsupported export format '{v}'. Supported formats: 'csv', 'json'.")
        return v.lower()


class ExportJobResponse(BaseModel):
    """Status and metadata for an asynchronous export job."""

    model_config = ConfigDict(extra="ignore")

    job_id: str
    status: str
    format: str
    created_at: str
    record_count: int
    download_url: str | None = None
    error_message: str | None = None
