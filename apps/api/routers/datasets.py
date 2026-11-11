# NOTE: Global ACTIVE_DATASET with singleton switch is safe because:
# 1. Single-user analytics dashboard (not multi-tenant)
# 2. Uvicorn runs with 1 worker in dev/production single-instance mode
# 3. Switch is instantaneous (clears caches, next request loads new data)
# For distributed multi-tenant deployment, use per-request query param routing (?dataset=sample) instead.
"""Dataset management and switching router for Parcl Buyer Intelligence Platform."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse

from apps.api.auth import get_current_user_role
from apps.api.config import api_settings
from apps.api.schemas.datasets import (
    DatasetInfo,
    DatasetListResponse,
    DatasetSwitchRequest,
    DatasetSwitchResponse,
    ValidationReport,
)
from apps.api.services.data_service import data_service
from packages.core.parcl_core.schemas import RawClientsSchema, RawPropertiesSchema

router = APIRouter(prefix="/api/v1/datasets", tags=["Dataset Management"])

SAMPLE_DIR = api_settings.data_dir / "sample"
RAW_DIR = api_settings.data_dir / "raw"

# In-memory active dataset state
ACTIVE_DATASET: str = "full"


@router.get(
    "",
    summary="List available datasets (Full production vs Synthetic sample)",
    response_model=DatasetListResponse,
)
async def list_datasets() -> DatasetListResponse:
    """Return available datasets and metadata."""
    return DatasetListResponse(
        active_dataset=ACTIVE_DATASET,
        datasets=[
            DatasetInfo(
                name="full",
                label="Full Production Dataset",
                description="Complete multi-unit cohort (2,000 buyers, 7,305 transactions) as of Dec 2025.",
                is_active=(ACTIVE_DATASET == "full"),
                buyer_count=2000,
                property_count=7305,
            ),
            DatasetInfo(
                name="sample",
                label="Synthetic Sample Dataset",
                description="Small anonymized test cohort (200 buyers, 865 properties across 20 towers) with matching schema. Using sample data when active.",
                is_active=(ACTIVE_DATASET == "sample"),
                buyer_count=200,
                property_count=865,
            ),
        ],
    )


@router.post(
    "/switch",
    summary="Switch active dataset context",
    response_model=DatasetSwitchResponse,
)
async def switch_dataset(payload: DatasetSwitchRequest) -> DatasetSwitchResponse:
    """Switch the operational dataset between full and sample."""
    global ACTIVE_DATASET
    target = payload.dataset.strip().lower()
    if target not in {"full", "sample"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid dataset name. Must be 'full' or 'sample'.",
        )
    ACTIVE_DATASET = target
    # Wire the singleton data_service to the correct processed directory
    if target == "sample":
        data_service.switch_to(SAMPLE_DIR / "processed")
    else:
        data_service.switch_to(api_settings.processed_dir)

    return DatasetSwitchResponse(
        active_dataset=ACTIVE_DATASET,
        message=f"Dataset context switched to '{target}'.",
        requires_retraining_note=(
            "Note: Switching dataset view changes preview and inspection context. "
            "Model parameters and statistical benchmarks reflect the production baseline."
        ),
    )


@router.get(
    "/sample/{filename}",
    summary="Download synthetic sample dataset CSV",
)
async def download_sample_file(filename: str) -> FileResponse:
    """Download clients_sample.csv or properties_sample.csv."""
    safe_name = Path(filename).name
    if safe_name not in {"clients_sample.csv", "properties_sample.csv"}:
        raise HTTPException(
            status_code=404,
            detail="Requested sample file not found. Options: clients_sample.csv, properties_sample.csv",
        )

    file_path = SAMPLE_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {safe_name} does not exist on server.")

    return FileResponse(
        path=str(file_path),
        filename=safe_name,
        media_type="text/csv",
    )


@router.get(
    "/template/{dataset_type}",
    summary="Download CSV schema template with header and example row",
)
async def download_csv_template(dataset_type: str) -> Response:
    """Download header + single example row template for clients or properties."""
    dtype = dataset_type.lower().strip()
    if dtype in {"clients", "client"}:
        content = (
            "client_id,client_type,first_name,last_name,date_of_birth,gender,country,region,acquisition_purpose,satisfaction_score,loan_applied,referral_channel\n"
            "C0001,Individual,John,Doe,01-15-1975,M,USA,California,Home,4,Yes,Website\n"
        )
        filename = "clients_template.csv"
    elif dtype in {"properties", "property"}:
        content = (
            "listing_id,tower_number,transaction_date,unit_category,unit_number,floor_area_sqft,sale_price,listing_status,client_ref\n"
            "1001,1,01-01-2024,Apartment,12,850.50,\"$220,000.00\",Sold,C0001\n"
        )
        filename = "properties_template.csv"
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid dataset_type. Choose 'clients' or 'properties'.",
        )

    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post(
    "/validate",
    summary="Validate an uploaded CSV dataset against Pandera schemas (Admin only)",
    response_model=ValidationReport,
)
async def validate_uploaded_dataset(
    file: UploadFile = File(...),
    role: Annotated[str, Depends(get_current_user_role)] = "analyst",
) -> ValidationReport:
    """Validate uploaded CSV file structure and schema constraints."""
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Admin privilege required to upload and validate datasets.",
        )

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        return ValidationReport(
            is_valid=False,
            dataset_type="unknown",
            row_count=0,
            column_count=0,
            columns=[],
            errors=[f"Failed to parse CSV file: {exc}"],
        )

    columns = list(df.columns)
    row_count = len(df)
    column_count = len(columns)

    # Determine type
    if "client_id" in columns:
        dtype = "clients"
        schema = RawClientsSchema
    elif "listing_id" in columns:
        dtype = "properties"
        schema = RawPropertiesSchema
    else:
        return ValidationReport(
            is_valid=False,
            dataset_type="unknown",
            row_count=row_count,
            column_count=column_count,
            columns=columns,
            errors=[
                "Unrecognized dataset schema. Must contain either 'client_id' (clients) or 'listing_id' (properties)."
            ],
        )

    errors: list[str] = []
    warnings: list[str] = []

    try:
        schema.validate(df, lazy=True)
        is_valid = True
    except Exception as schema_err:
        is_valid = False
        # Collect schema failure details
        err_msg = str(schema_err)
        errors.append(f"Pandera schema validation failed: {err_msg[:300]}")

    if row_count < 10:
        warnings.append(f"Small dataset warning: contains only {row_count} rows.")

    return ValidationReport(
        is_valid=is_valid,
        dataset_type=dtype,
        row_count=row_count,
        column_count=column_count,
        columns=columns,
        errors=errors,
        warnings=warnings,
    )
