"""Pydantic v2 schemas for metadata and active filter choices."""

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ResponseMetadata


class FilterOptionItem(BaseModel):
    """Filter value with matching record count."""

    model_config = ConfigDict(extra="ignore")

    value: str = Field(examples=["USA"])
    display_label: str = Field(examples=["United States"])
    count: int = Field(examples=[1538])


class MetaFiltersResponse(BaseModel):
    """Available PRD filter dimensions and matching counts."""

    model_config = ConfigDict(extra="ignore")

    total_clients: int = Field(examples=[2000])
    countries: list[FilterOptionItem]
    regions: list[FilterOptionItem]
    acquisition_purposes: list[FilterOptionItem]
    client_types: list[FilterOptionItem]
    assigned_clusters: list[FilterOptionItem]
    metadata: ResponseMetadata
