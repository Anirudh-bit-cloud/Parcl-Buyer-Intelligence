"""Pydantic v2 schemas for geographic buyer intelligence (PRD Module 3)."""

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ActiveFilters, ResponseMetadata


class GeoUnitMetrics(BaseModel):
    """Country or regional cohort breakdown."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(examples=["USA"])
    buyer_count: int = Field(examples=[1538])
    share_pct: float = Field(examples=[76.9])
    mean_spend_inr: float = Field(examples=[1273500.0])
    mean_spend_display: str = Field(examples=["₹12,73,500"])
    mean_units: float = Field(examples=[3.66])
    investment_purpose_share_pct: float = Field(examples=[30.82])


class GeoDomesticVsInternational(BaseModel):
    """Empirical comparison between Domestic (USA) and International buyers."""

    model_config = ConfigDict(extra="ignore")

    domestic_buyers: int = Field(examples=[1538])
    domestic_mean_spend_inr: float = Field(examples=[1273500.0])
    domestic_mean_spend_display: str = Field(examples=["₹12,73,500"])
    domestic_investment_share_pct: float = Field(examples=[30.82])
    international_buyers: int = Field(examples=[462])
    international_mean_spend_inr: float = Field(examples=[1232374.0])
    international_mean_spend_display: str = Field(examples=["₹12,32,374"])
    international_investment_share_pct: float = Field(examples=[31.60])
    spend_difference_pct: float = Field(description="Domestic premium over international.", examples=[3.34])
    two_sample_t_stat: float = Field(examples=[2.2253])
    t_test_p_value: float = Field(examples=[0.0262])
    cohens_d: float = Field(examples=[0.1181])


class GeographicIntelligenceResponse(BaseModel):
    """PRD Module 3 geographic buyer analysis."""

    model_config = ConfigDict(extra="ignore")

    total_buyers_evaluated: int = Field(examples=[2000])
    domestic_vs_international: GeoDomesticVsInternational
    top_countries: list[GeoUnitMetrics]
    top_regions: list[GeoUnitMetrics]
    active_filters: ActiveFilters
    metadata: ResponseMetadata
