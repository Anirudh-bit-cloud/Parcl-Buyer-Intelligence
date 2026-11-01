"""Unit tests for Pandera validation schemas."""

import pandas as pd
import pandera.errors
import pytest
from parcl_core.schemas import (
    RawClientsSchema,
    RawPropertiesSchema,
    validate_dataframe,
)


def test_raw_clients_schema_valid() -> None:
    """Test RawClientsSchema passes with valid data."""
    valid_data = pd.DataFrame(
        {
            "client_id": ["C0001", "C0002"],
            "client_type": ["Individual", "Company"],
            "first_name": ["Alice", "Bob"],
            "last_name": ["Smith", "Jones"],
            "date_of_birth": ["11/26/1962", "05-11-1968"],
            "gender": ["Female", "Male"],
            "country": ["USA", "UK"],
            "region": ["California", "London"],
            "acquisition_purpose": ["Home", "Investment"],
            "satisfaction_score": [4, 5],
            "loan_applied": ["Yes", "No"],
            "referral_channel": ["Website", "Agency"],
        }
    )
    validated = validate_dataframe(valid_data, RawClientsSchema)
    assert len(validated) == 2


def test_raw_clients_schema_invalid_referral() -> None:
    """Test RawClientsSchema rejects ungrounded referral channels."""
    invalid_data = pd.DataFrame(
        {
            "client_id": ["C0001"],
            "client_type": ["Individual"],
            "first_name": ["Alice"],
            "last_name": ["Smith"],
            "date_of_birth": ["11/26/1962"],
            "gender": ["Female"],
            "country": ["USA"],
            "region": ["California"],
            "acquisition_purpose": ["Home"],
            "satisfaction_score": [4],
            "loan_applied": ["Yes"],
            "referral_channel": ["Broker"],  # Invalid! Must be Website, Agency, Client
        }
    )
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_dataframe(invalid_data, RawClientsSchema)


def test_raw_properties_schema_valid() -> None:
    """Test RawPropertiesSchema passes with valid properties data."""
    valid_data = pd.DataFrame(
        {
            "listing_id": [1012, 1015],
            "tower_number": [1, 2],
            "transaction_date": ["01-01-2024", "02-01-2024"],
            "unit_category": ["Apartment", "Office"],
            "unit_number": [101, 202],
            "floor_area_sqft": [850.5, 1200.0],
            "sale_price": ["$300,385.62", "$450,000.00"],
            "listing_status": ["Sold", "Available"],
            "client_ref": ["C0027", None],
        }
    )
    validated = validate_dataframe(valid_data, RawPropertiesSchema)
    assert len(validated) == 2
