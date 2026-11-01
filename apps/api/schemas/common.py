"""Common metadata, pagination, and filter schemas across API responses."""

from pydantic import BaseModel, ConfigDict, Field


class ActiveFilters(BaseModel):
    """PRD active filtering parameters applied to query."""

    model_config = ConfigDict(extra="ignore")

    country: str | None = Field(default=None, description="Country filter (e.g. 'USA').")
    region: str | None = Field(default=None, description="Regional administrative area filter.")
    acquisition_purpose: str | None = Field(
        default=None, description="Purchase intent ('HOME' or 'INVESTMENT')."
    )
    client_type: str | None = Field(
        default=None, description="Entity type ('INDIVIDUAL' or 'COMPANY')."
    )
    assigned_cluster: int | None = Field(
        default=None, description="Assigned segment ID (0, 1, 2, 3)."
    )


class ResponseMetadata(BaseModel):
    """Audited metadata block attached to every API response."""

    model_config = ConfigDict(extra="ignore")

    as_of: str = Field(
        default="December 2025",
        description="Dataset snapshot cutoff date.",
        examples=["December 2025"],
    )
    currency: str = Field(
        default="INR",
        description="Accounting currency standard (Indian Rupees).",
        examples=["INR"],
    )
    currency_symbol: str = Field(
        default="₹",
        description="Currency symbol prefix.",
        examples=["₹"],
    )
    is_unfiltered_model_space: bool = Field(
        default=False,
        description="True for global model benchmarks; False for user-filtered data views.",
    )
    untested_assumptions_notice: str = Field(
        default="None",
        description="Notice regarding heuristic business weights or model proxy assumptions.",
    )
    notices: list[str] = Field(
        default_factory=list,
        description="System, security, RBAC masking, and accounting labeling notices.",
        examples=[
            [
                "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country.",
                "Server-side personal identity masking active under current role.",
            ]
        ],
    )


class PaginationMetadata(BaseModel):
    """Standard pagination details."""

    model_config = ConfigDict(extra="ignore")

    page: int = Field(ge=1, examples=[1])
    page_size: int = Field(ge=1, le=100, examples=[20])
    total_records: int = Field(ge=0, examples=[2000])
    total_pages: int = Field(ge=1, examples=[100])
