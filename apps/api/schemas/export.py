"""Pydantic v2 schemas for filtered dataset export."""

from pydantic import BaseModel, ConfigDict, Field

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
