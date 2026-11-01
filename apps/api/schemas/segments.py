"""Pydantic v2 schemas for segment profiles, personas, and silhouette validation framing."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ActiveFilters, ResponseMetadata


class SilhouetteContext(BaseModel):
    """Audited dual-structure silhouette and Weak Cluster Policy metadata."""

    model_config = ConfigDict(extra="ignore")

    k2_strong_macrostructure_silhouette: float = Field(
        default=0.5072,
        description="Strong mathematical macrostructure partitioning 3-unit vs 4+ buyers.",
        examples=[0.5072],
    )
    k2_davies_bouldin: float = Field(default=0.8066, examples=[0.8066])
    k4_weak_substructure_silhouette: float = Field(
        default=0.1211,
        description="Sub-0.25 weak cluster silhouette requiring soft behavioral framing.",
        examples=[0.1211],
    )
    k4_davies_bouldin: float = Field(default=2.6079, examples=[2.6079])
    soft_behavioral_tendencies_framing: str = Field(
        default=(
            "Weak Cluster Policy Triggered: Best k=4 silhouette is 0.1211 (< 0.25). Segments represent "
            "overlapping soft behavioral tendencies rather than isolated discrete partitions. "
            "Downstream systems must respect continuous soft probabilities."
        )
    )


class SegmentSummaryItem(BaseModel):
    """Segment catalog summary item computed dynamically from cohort data."""

    model_config = ConfigDict(extra="ignore")

    segment_id: int = Field(examples=[0])
    segment_name: str = Field(examples=["Emerging Multi-Tower Accumulators"])
    persona_label: str = Field(examples=["Emerging Multi-Tower Portfolio Accumulators"])
    buyer_count: int = Field(examples=[536])
    population_share_pct: float = Field(examples=[26.8])
    mean_age: float = Field(examples=[42.1])
    mean_units: float = Field(examples=[4.06])
    total_units: int = Field(examples=[2174])
    mean_spend_inr: float = Field(description="Mean observed spend in INR.", examples=[1376040.58])
    mean_spend_display: str = Field(examples=["₹13,76,041"])
    total_spend_inr: float = Field(description="Total observed spend across segment in INR.", examples=[737557751.16])
    total_spend_display: str = Field(examples=["₹73,75,57,751"])
    commercial_office_share_pct: float = Field(examples=[13.4])
    towers_hhi: float = Field(examples=[0.2504])
    top_towers: list[int] = Field(examples=[[1, 2, 7, 8, 13, 14, 19, 20]])


class SegmentListResponse(BaseModel):
    """Catalog of all 4 production segments with validation framing and active cohort filtering."""

    model_config = ConfigDict(extra="ignore")

    production_variant: str = Field(examples=["Model_B3_Downweighted_Geo"])
    k_selected: int = Field(examples=[4])
    cohort_total_buyers: int = Field(examples=[2000])
    cohort_total_units: int = Field(examples=[7305])
    cohort_mean_spend_inr: float = Field(examples=[1260375.48])
    cohort_mean_spend_display: str = Field(examples=["₹12,60,375"])
    cohort_total_spend_inr: float = Field(examples=[2520750960.84])
    cohort_total_spend_display: str = Field(examples=["₹2,52,07,50,961"])
    buyer_weighted_office_share_pct: float = Field(
        default=14.87,
        description="Buyer-weighted office share: mean of client office shares across cohort.",
        examples=[14.87],
    )
    unit_weighted_office_share_pct: float = Field(
        default=14.78,
        description="Unit-weighted office share: commercial office transactions / total transactions (1,080 / 7,305).",
        examples=[14.78],
    )
    segments: list[SegmentSummaryItem]
    silhouette_validation: SilhouetteContext
    active_filters: ActiveFilters
    metadata: ResponseMetadata


class SegmentDetailResponse(BaseModel):
    """Deep-dive profiling distributions and surrogate splitting rules for a segment."""

    model_config = ConfigDict(extra="ignore")

    segment_id: int = Field(examples=[2])
    segment_name: str = Field(examples=["Commercial Office Diversifiers"])
    persona_description: str = Field(examples=["Specialized buyers allocating significant capital to commercial office suites."])
    buyer_count: int = Field(examples=[375])
    population_share_pct: float = Field(examples=[18.75])
    mean_spend_inr: float = Field(examples=[1100608.39])
    mean_spend_display: str = Field(examples=["₹11,00,608"])
    total_spend_inr: float = Field(examples=[412728147.48])
    total_spend_display: str = Field(examples=["₹41,27,28,147"])
    mean_units: float = Field(examples=[3.00])
    commercial_office_share_pct: float = Field(examples=[37.8])
    numeric_metrics: dict[str, dict[str, float]]
    categorical_distributions: dict[str, Any]
    surrogate_rules: list[str] = Field(examples=[["quantile_units__n_units <= -2.33 (units == 3)", "std_num__office_share > 0.10 (office > 0%)"]])
    silhouette_validation: SilhouetteContext
    active_filters: ActiveFilters
    metadata: ResponseMetadata
