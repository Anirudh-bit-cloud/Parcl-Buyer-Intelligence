"""Pydantic v2 schemas for high-level executive overview (PRD Module 1)."""

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ActiveFilters, ResponseMetadata


class SegmentShareBreakdown(BaseModel):
    """Segment share metrics in cohort."""

    model_config = ConfigDict(extra="ignore")

    segment_id: int = Field(examples=[0])
    segment_name: str = Field(examples=["Emerging Multi-Tower Buyers"])
    buyer_count: int = Field(examples=[536])
    share_pct: float = Field(examples=[26.8])
    mean_spend_inr: float = Field(examples=[1376041.01])
    mean_spend_display: str = Field(examples=["₹13,76,041"])
    total_units: int = Field(examples=[2174])


class ExecutiveOverviewResponse(BaseModel):
    """PRD Module 1 executive overview KPIs and narrative takeaways."""

    model_config = ConfigDict(extra="ignore")

    total_buyers: int = Field(examples=[2000])
    total_transactions: int = Field(examples=[7305])
    total_sales_volume_inr: float = Field(examples=[2520750960.84])
    total_sales_volume_display: str = Field(examples=["₹2,52,07,50,961"])
    mean_sales_price_inr: float = Field(examples=[345072.0])
    mean_sales_price_display: str = Field(examples=["₹3,45,072"])
    mean_units_per_buyer: float = Field(examples=[3.65])
    mean_buyer_spend_inr: float = Field(examples=[1260375.48])
    mean_buyer_spend_display: str = Field(examples=["₹12,60,375"])
    available_units_count: int = Field(examples=[313])
    towers_count: int = Field(examples=[20])
    segments: list[SegmentShareBreakdown]
    key_takeaways: list[str]
    active_filters: ActiveFilters
    metadata: ResponseMetadata
