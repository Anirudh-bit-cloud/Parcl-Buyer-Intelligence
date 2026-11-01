"""Pydantic v2 schemas for investor behavioral intelligence (PRD Module 2)."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ActiveFilters, ResponseMetadata


class BehavioralCohortMetrics(BaseModel):
    """Behavioral breakdown metrics for a sub-group."""

    model_config = ConfigDict(extra="ignore")

    cohort_label: str = Field(examples=["HOME"])
    buyer_count: int = Field(examples=[1380])
    share_pct: float = Field(examples=[69.0])
    mean_spend_inr: float = Field(examples=[1258412.50])
    mean_spend_display: str = Field(examples=["₹12,58,413"])
    mean_units: float = Field(examples=[3.65])
    loan_rate: float = Field(examples=[0.368])


class InvestorBehaviorResponse(BaseModel):
    """PRD Module 2 investor behavior breakdowns."""

    model_config = ConfigDict(extra="ignore")

    total_buyers_evaluated: int = Field(examples=[2000])
    acquisition_purpose_breakdown: list[BehavioralCohortMetrics]
    loan_application_breakdown: list[BehavioralCohortMetrics]
    client_type_breakdown: list[BehavioralCohortMetrics]
    referral_channel_breakdown: list[BehavioralCohortMetrics]
    commercial_office_vs_residential: dict[str, Any]
    active_filters: ActiveFilters
    metadata: ResponseMetadata
