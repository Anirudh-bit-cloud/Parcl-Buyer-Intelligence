"""Pandera validation schemas for raw, clean, and processed datasets."""

from typing import Any

import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

# ---------------------------------------------------------
# Raw Data Schemas
# ---------------------------------------------------------

RawClientsSchema = DataFrameSchema(
    columns={
        "client_id": Column(pa.String, nullable=False, unique=True),
        "client_type": Column(
            pa.String,
            Check.isin(["Individual", "Company", "INDIVIDUAL", "COMPANY"]),
            nullable=False,
        ),
        "first_name": Column(pa.String, nullable=False),
        "last_name": Column(pa.String, nullable=False),
        "date_of_birth": Column(pa.String, nullable=False),
        "gender": Column(
            pa.String, Check.isin(["Male", "Female", "M", "F", "Other"]), nullable=False
        ),
        "country": Column(pa.String, nullable=False),
        "region": Column(pa.String, nullable=False),
        "acquisition_purpose": Column(
            pa.String,
            Check.isin(["Home", "Investment", "HOME", "INVESTMENT", "Personal use"]),
            nullable=False,
        ),
        "satisfaction_score": Column(pa.Int, Check.in_range(1, 5), nullable=False),
        "loan_applied": Column(
            pa.String, Check.isin(["Yes", "No", "Y", "N", "True", "False"]), nullable=False
        ),
        "referral_channel": Column(
            pa.String, Check.isin(["Website", "Agency", "Client"]), nullable=False
        ),
    },
    strict=False,
    coerce=True,
)


RawPropertiesSchema = DataFrameSchema(
    columns={
        "listing_id": Column(pa.Int, nullable=False, unique=True),
        "tower_number": Column(pa.Int, Check.greater_than_or_equal_to(1), nullable=False),
        "transaction_date": Column(pa.String, nullable=False),
        "unit_category": Column(pa.String, Check.isin(["Apartment", "Office"]), nullable=False),
        "unit_number": Column(pa.Int, nullable=False),
        "floor_area_sqft": Column(pa.Float, Check.greater_than(0.0), nullable=False),
        "sale_price": Column(pa.String, nullable=False),
        "listing_status": Column(pa.String, Check.isin(["Sold", "Available"]), nullable=False),
        "client_ref": Column(pa.String, nullable=True),
    },
    strict=False,
    coerce=True,
)


# ---------------------------------------------------------
# Clean Data Schemas
# ---------------------------------------------------------

CleanClientsSchema = DataFrameSchema(
    columns={
        "client_id": Column(pa.String, nullable=False, unique=True),
        "client_type": Column(pa.String, Check.isin(["INDIVIDUAL", "COMPANY"]), nullable=False),
        "first_name": Column(pa.String, nullable=False),
        "last_name": Column(pa.String, nullable=False),
        "date_of_birth": Column(pa.DateTime, nullable=False),
        "age": Column(pa.Int, Check.in_range(18, 120), nullable=False),
        "gender": Column(pa.String, Check.isin(["Male", "Female"]), nullable=False),
        "country": Column(pa.String, nullable=False),
        "region": Column(pa.String, nullable=False),
        "acquisition_purpose": Column(
            pa.String, Check.isin(["HOME", "INVESTMENT"]), nullable=False
        ),
        "satisfaction_score": Column(pa.Int, Check.in_range(1, 5), nullable=False),
        "loan_applied": Column(pa.Bool, nullable=False),
        "referral_channel": Column(
            pa.String, Check.isin(["Website", "Agency", "Client"]), nullable=False
        ),
    },
    strict=False,
    coerce=True,
)


CleanPropertiesSchema = DataFrameSchema(
    columns={
        "listing_id": Column(pa.Int, nullable=False, unique=True),
        "tower_number": Column(pa.Int, Check.greater_than_or_equal_to(1), nullable=False),
        "transaction_date": Column(pa.DateTime, nullable=False),
        "transaction_month": Column(pa.String, nullable=False),
        "unit_category": Column(pa.String, Check.isin(["Apartment", "Office"]), nullable=False),
        "unit_number": Column(pa.Int, nullable=False),
        "floor_area_sqft": Column(pa.Float, Check.greater_than(0.0), nullable=False),
        "sale_price": Column(pa.Float, Check.greater_than(0.0), nullable=False),
        "price_per_sqft": Column(pa.Float, Check.greater_than(0.0), nullable=False),
        "listing_status": Column(pa.String, Check.isin(["Sold", "Available"]), nullable=False),
        "client_ref": Column(pa.String, nullable=True),
    },
    strict=False,
    coerce=True,
)


def validate_dataframe(df: Any, schema: DataFrameSchema) -> Any:
    """Validate dataframe with Pandera schema and provide detailed errors."""
    return schema.validate(df, lazy=True)
