"""Pydantic v2 schemas for client directory, profiling, and portfolio views."""

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ActiveFilters, PaginationMetadata, ResponseMetadata


class ClientTransactionItem(BaseModel):
    """Historical transaction record within buyer portfolio."""

    model_config = ConfigDict(extra="ignore")

    listing_id: int = Field(examples=[10042])
    tower_number: int = Field(examples=[3])
    unit_number: int = Field(examples=[14])
    transaction_date: str = Field(examples=["2024-10"])
    unit_category: str = Field(examples=["Apartment"])
    floor_area_sqft: float = Field(examples=[980.5])
    sale_price_inr: float = Field(description="Transaction amount in INR.", examples=[311691.18])
    sale_price_display: str = Field(examples=["₹3,11,691"])
    price_per_sqft_inr: float = Field(examples=[317.89])


class ClientDirectoryItem(BaseModel):
    """Client record summary in paginated directory."""

    model_config = ConfigDict(extra="ignore")

    client_id: str = Field(examples=["C0001"])
    client_type: str = Field(examples=["INDIVIDUAL"])
    first_name: str = Field(description="Role-masked personal name.", examples=["K***"])
    last_name: str = Field(description="Role-masked surname.", examples=["L***"])
    country: str = Field(examples=["USA"])
    region: str = Field(examples=["California"])
    age: int = Field(examples=[57])
    satisfaction_score: int = Field(examples=[4])
    loan_applied: bool = Field(examples=[True])
    referral_channel: str = Field(examples=["Website"])
    total_spend_inr: float = Field(description="Observed spend in INR.", examples=[1246764.72])
    total_spend_display: str = Field(examples=["₹12,46,765"])
    n_units: int = Field(examples=[4])
    assigned_cluster: int = Field(examples=[0])
    assigned_segment_name: str = Field(examples=["Emerging Multi-Tower Buyers"])
    top_soft_probability: float = Field(examples=[0.4532])


class ClientListResponse(BaseModel):
    """Paginated client list response."""

    model_config = ConfigDict(extra="ignore")

    clients: list[ClientDirectoryItem]
    pagination: PaginationMetadata
    active_filters: ActiveFilters
    metadata: ResponseMetadata


class ClientDetailResponse(BaseModel):
    """Deep-dive buyer portfolio and behavioral profile."""

    model_config = ConfigDict(extra="ignore")

    client_id: str = Field(examples=["C0001"])
    client_type: str = Field(examples=["INDIVIDUAL"])
    first_name: str = Field(description="Unmasked if admin; masked otherwise.", examples=["Kareem"])
    last_name: str = Field(description="Unmasked if admin; masked otherwise.", examples=["Liu"])
    country: str = Field(examples=["USA"])
    region: str = Field(examples=["California"])
    age: int = Field(description="Completed age at 2025-12-31.", examples=[57])
    satisfaction_score: int = Field(examples=[4])
    loan_applied: bool = Field(examples=[True])
    referral_channel: str = Field(examples=["Website"])
    total_spend_inr: float = Field(examples=[1246764.72])
    total_spend_display: str = Field(examples=["₹12,46,765"])
    n_units: int = Field(examples=[4])
    office_share: float = Field(examples=[0.0])
    owned_towers: list[int] = Field(examples=[[3, 4, 9, 15]])
    assigned_cluster: int = Field(examples=[0])
    assigned_segment_name: str = Field(examples=["Emerging Multi-Tower Buyers"])
    soft_membership_probabilities: dict[str, float] = Field(
        examples=[{"Cluster_0": 0.4532, "Cluster_1": 0.2104, "Cluster_2": 0.1842, "Cluster_3": 0.1522}]
    )
    is_ambiguous_boundary: bool = Field(
        description="True if max soft probability < 0.50 (absence of strict majority).",
        examples=[True],
    )
    is_ambiguous_margin: bool = Field(
        default=False,
        description="True if top-2 softmax probability margin (p_1 - p_2) < 0.10.",
        examples=[True],
    )
    transactions: list[ClientTransactionItem]
    metadata: ResponseMetadata
