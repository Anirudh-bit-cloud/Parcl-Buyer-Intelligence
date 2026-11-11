"""Pydantic schemas for dataset management and validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DatasetInfo(BaseModel):
    name: str = Field(..., description="Dataset machine identifier ('full' or 'sample')")
    label: str = Field(..., description="Human-readable dataset display label")
    description: str = Field(..., description="Description of the dataset cohort")
    is_active: bool = Field(..., description="Whether this dataset is currently active")
    buyer_count: int = Field(..., description="Number of buyers in dataset")
    property_count: int = Field(..., description="Number of properties in dataset")


class DatasetListResponse(BaseModel):
    active_dataset: str = Field(..., description="Currently active dataset name")
    datasets: list[DatasetInfo] = Field(..., description="Available datasets")


class DatasetSwitchRequest(BaseModel):
    dataset: str = Field(..., description="Target dataset to activate ('full' or 'sample')")


class DatasetSwitchResponse(BaseModel):
    active_dataset: str = Field(..., description="New active dataset identifier")
    message: str = Field(..., description="Status message")
    requires_retraining_note: str = Field(
        ...,
        description="Notice regarding model retraining and serving isolation",
    )


class ValidationReport(BaseModel):
    is_valid: bool = Field(..., description="Whether dataset conforms to raw schemas")
    dataset_type: str = Field(..., description="Inferred or specified type ('clients' or 'properties')")
    row_count: int = Field(..., description="Number of rows parsed")
    column_count: int = Field(..., description="Number of columns parsed")
    columns: list[str] = Field(..., description="Parsed column headers")
    errors: list[str] = Field(default_factory=list, description="Schema or integrity violations")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings or advisories")
