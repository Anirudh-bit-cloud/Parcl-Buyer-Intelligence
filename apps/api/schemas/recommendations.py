"""Pydantic v2 schemas for Opportunity Finder and Next-Best-Offer recommendations."""

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ActiveFilters, ResponseMetadata


class ScoredPropertyListingItem(BaseModel):
    """Available property listing scored for a target buyer segment."""

    model_config = ConfigDict(extra="ignore")

    listing_id: int = Field(examples=[170425])
    tower_number: int = Field(examples=[17])
    unit_number: int = Field(examples=[53])
    unit_category: str = Field(examples=["Office"])
    sale_price_inr: float = Field(description="Listing price in INR.", examples=[384500.0])
    sale_price_display: str = Field(examples=["₹3,84,500"])
    floor_area_sqft: float = Field(examples=[1200.0])
    price_per_sqft_inr: float = Field(examples=[320.42])
    affinity_score: float = Field(description="Normalized heuristic affinity [0..1].", examples=[0.8842])
    heuristic_assumption: str = Field(
        examples=["Category fit (0.35), Price fit (0.30), Area fit (0.20), Tower fit (0.15)"]
    )


class OpportunityFinderResponse(BaseModel):
    """Opportunity Finder recommendations matching available inventory to segment profile."""

    model_config = ConfigDict(extra="ignore")

    target_segment_id: int = Field(examples=[2])
    target_segment_name: str = Field(examples=["Commercial Office Allocators"])
    category_filter_applied: str | None = Field(default=None, examples=["Office"])
    total_inventory_evaluated: int = Field(
        default=313,
        description="Current deduplicated available physical inventory as of December 2025.",
        examples=[313],
    )
    recommendations: list[ScoredPropertyListingItem]
    active_filters: ActiveFilters
    metadata: ResponseMetadata


class NBORecommendationItem(BaseModel):
    """Personalized Next-Best-Offer listing recommendation."""

    model_config = ConfigDict(extra="ignore")

    listing_id: int = Field(examples=[20365])
    tower_number: int = Field(examples=[2])
    unit_number: int = Field(examples=[36])
    unit_category: str = Field(examples=["Apartment"])
    sale_price_inr: float = Field(examples=[328000.0])
    sale_price_display: str = Field(examples=["₹3,28,000"])
    floor_area_sqft: float = Field(examples=[1020.0])
    price_per_sqft_inr: float = Field(examples=[321.57])
    segment_affinity_score: float = Field(examples=[0.7645])
    tower_diversification_bonus: float = Field(
        default=0.15,
        description="Additive bonus (+0.15) if listing tower is not yet owned by client.",
        examples=[0.15],
    )
    category_diversification_bonus: float = Field(
        default=0.0,
        description="Additive bonus (+0.10) if unit introduces commercial office to residential portfolio.",
        examples=[0.0],
    )
    final_nbo_score: float = Field(
        description="Unclipped sum: segment_affinity + tower_bonus + category_bonus.",
        examples=[0.9145],
    )
    diversifies_towers: bool = Field(examples=[True])
    untested_assumption_note: str = Field(
        examples=[
            "Untested assumption: Tower diversification bonus (+0.15) is an additive heuristic assumption."
        ]
    )


class NBOResponse(BaseModel):
    """Personalized Next-Best-Offer output for an individual buyer."""

    model_config = ConfigDict(extra="ignore")

    client_id: str = Field(examples=["C0001"])
    client_segment_id: int = Field(examples=[0])
    client_segment_name: str = Field(examples=["Emerging Multi-Tower Buyers"])
    owned_towers: list[int] = Field(examples=[[3, 4, 9, 15]])
    unowned_towers_count: int = Field(
        default=16,
        description="Remaining unowned towers out of 20 total towers in development.",
        examples=[16],
    )
    mean_bonus_eligibility_share_pct: float = Field(
        default=81.86,
        description="Average percentage of available inventory eligible for tower diversification bonus (~82%).",
        examples=[81.86],
    )
    recommendations: list[NBORecommendationItem]
    active_filters: ActiveFilters
    metadata: ResponseMetadata
