"""Pydantic v2 schemas for tower sales, pricing, and segment affinity heatmaps."""

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ActiveFilters, ResponseMetadata


class TowerDetailMetrics(BaseModel):
    """Aggregated sales, pricing, and category composition for a physical tower."""

    model_config = ConfigDict(extra="ignore")

    tower_number: int = Field(examples=[1])
    total_sales_units: int = Field(examples=[365])
    currently_available_units: int = Field(examples=[15])
    mean_sale_price_inr: float = Field(examples=[344210.50])
    mean_sale_price_display: str = Field(examples=["₹3,44,211"])
    mean_price_per_sqft_inr: float = Field(examples=[301.85])
    apartment_units_sold: int = Field(examples=[320])
    office_units_sold: int = Field(examples=[45])
    segment_transaction_shares: dict[str, float] = Field(
        examples=[{"Cluster_0": 0.45, "Cluster_1": 0.0, "Cluster_2": 0.0, "Cluster_3": 0.55}]
    )


class TowerHeatmapResponse(BaseModel):
    """Tower sales, pricing, and segment concentration heatmap."""

    model_config = ConfigDict(extra="ignore")

    total_towers: int = Field(default=20, examples=[20])
    total_sold_units: int = Field(examples=[7305])
    total_available_units: int = Field(examples=[313])
    towers: list[TowerDetailMetrics]
    active_filters: ActiveFilters
    metadata: ResponseMetadata
