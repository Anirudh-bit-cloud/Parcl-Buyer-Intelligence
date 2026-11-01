"""Pydantic v2 schemas for 2D latent space projections (PCA / UMAP)."""

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ActiveFilters, ResponseMetadata


class ProjectedPoint(BaseModel):
    """Client projection point in 2D space."""

    model_config = ConfigDict(extra="ignore")

    client_id: str = Field(examples=["C0001"])
    x: float = Field(examples=[1.425])
    y: float = Field(examples=[-0.852])
    assigned_cluster: int = Field(examples=[0])
    assigned_segment_name: str = Field(examples=["Emerging Multi-Tower Buyers"])
    n_units: int = Field(examples=[4])
    total_spend_inr: float = Field(examples=[1246764.72])
    total_spend_display: str = Field(examples=["₹12,46,765"])
    age: int = Field(examples=[57])
    office_share: float = Field(examples=[0.0])


class ProjectionResponse(BaseModel):
    """2D latent space projection response for interactive cluster visualization."""

    model_config = ConfigDict(extra="ignore")

    projection_method: str = Field(default="PCA", examples=["PCA"])
    total_points: int = Field(examples=[2000])
    explained_variance_ratio: list[float] = Field(default=[0.245, 0.182], examples=[[0.245, 0.182]])
    points: list[ProjectedPoint]
    active_filters: ActiveFilters
    metadata: ResponseMetadata
