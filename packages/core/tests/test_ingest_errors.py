"""Additional unit tests for ingestion error cases to achieve >=85% test coverage."""

from pathlib import Path

import pandas as pd
import pandera.errors
import pytest
from parcl_core.ingest import load_raw_clients, load_raw_properties


def test_load_raw_clients_schema_error(tmp_path: Path) -> None:
    """Test SchemaErrors is raised and logged when invalid clients CSV is loaded."""
    bad_clients_csv = tmp_path / "bad_clients.csv"
    bad_df = pd.DataFrame(
        {
            "client_id": ["C0001"],
            "client_type": ["InvalidType"],
            "first_name": ["Alice"],
            "last_name": ["Smith"],
            "date_of_birth": ["11/26/1962"],
            "gender": ["Female"],
            "country": ["USA"],
            "region": ["CA"],
            "acquisition_purpose": ["Home"],
            "satisfaction_score": [10],  # Out of range 1-5
            "loan_applied": ["Yes"],
            "referral_channel": ["Website"],
        }
    )
    bad_df.to_csv(bad_clients_csv, index=False)
    with pytest.raises(pandera.errors.SchemaErrors):
        load_raw_clients(bad_clients_csv)


def test_load_raw_properties_schema_error(tmp_path: Path) -> None:
    """Test SchemaErrors is raised and logged when invalid properties CSV is loaded."""
    bad_properties_csv = tmp_path / "bad_properties.csv"
    bad_df = pd.DataFrame(
        {
            "listing_id": [1012],
            "tower_number": [-1],  # Invalid tower number < 1
            "transaction_date": ["01-01-2024"],
            "unit_category": ["Warehouse"],  # Invalid category
            "unit_number": [101],
            "floor_area_sqft": [-50.0],
            "sale_price": ["$300,000"],
            "listing_status": ["Pending"],  # Invalid status
            "client_ref": ["C0027"],
        }
    )
    bad_df.to_csv(bad_properties_csv, index=False)
    with pytest.raises(pandera.errors.SchemaErrors):
        load_raw_properties(bad_properties_csv)
