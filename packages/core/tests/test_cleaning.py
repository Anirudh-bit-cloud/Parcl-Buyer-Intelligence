"""Unit tests for cleaning, normalization, and statistical routines."""

import pandas as pd
from parcl_core.cleaning import (
    clean_clients,
    clean_properties,
    evaluate_satisfaction_uniformity,
    parse_date_of_birth,
)


def test_parse_date_of_birth_mixed() -> None:
    """Test date parsing handles slash and dash formats correctly."""
    dates = pd.Series(["11/26/1962", "05-11-1968"])

    # DD-MM-YYYY assumption
    parsed_dd = parse_date_of_birth(dates, dash_format="DD-MM-YYYY")
    assert parsed_dd.iloc[0] == pd.Timestamp("1962-11-26")
    assert parsed_dd.iloc[1] == pd.Timestamp("1968-11-05")

    # MM-DD-YYYY assumption
    parsed_mm = parse_date_of_birth(dates, dash_format="MM-DD-YYYY")
    assert parsed_mm.iloc[0] == pd.Timestamp("1962-11-26")
    assert parsed_mm.iloc[1] == pd.Timestamp("1968-05-11")


def test_clean_clients_normalization() -> None:
    """Test normalization of client type and acquisition purpose enums."""
    raw_df = pd.DataFrame(
        {
            "client_id": ["C1", "C2", "C3"],
            "client_type": ["Individual ", " Company", "Corporate"],
            "first_name": ["John", "Jane", "Acme"],
            "last_name": ["Doe", "Smith", "Inc"],
            "date_of_birth": ["01/15/1990", "12-05-1985", "03/20/1975"],
            "gender": ["Male", "Female", "Male"],
            "country": ["USA", "UK", "Canada"],
            "region": ["CA", "London", "ON"],
            "acquisition_purpose": [" Home ", "Personal use", "Investment"],
            "satisfaction_score": [5, 4, 3],
            "loan_applied": ["Yes", "No", "Y"],
            "referral_channel": ["Website", "Agency", "Client"],
        }
    )
    clean_df = clean_clients(raw_df)

    # Assert canonical enums
    assert list(clean_df["client_type"]) == ["INDIVIDUAL", "COMPANY", "COMPANY"]
    assert list(clean_df["acquisition_purpose"]) == ["HOME", "HOME", "INVESTMENT"]
    assert list(clean_df["loan_applied"]) == [True, False, True]
    assert all(clean_df["age"] >= 18)


def test_clean_properties_split_and_types() -> None:
    """Test currency cleaning, price_per_sqft calculation, and Sold/Available split."""
    raw_df = pd.DataFrame(
        {
            "listing_id": [1, 2],
            "tower_number": [1, 2],
            "transaction_date": ["01-01-2024", "02-01-2024"],
            "unit_category": ["Apartment", "Office"],
            "unit_number": [101, 202],
            "floor_area_sqft": [1000.0, 500.0],
            "sale_price": ["$250,000.00", "$150,000.50"],
            "listing_status": ["Sold", "Available"],
            "client_ref": ["C1", None],
        }
    )
    sold_df, avail_df = clean_properties(raw_df)

    assert len(sold_df) == 1
    assert len(avail_df) == 1
    assert sold_df.iloc[0]["sale_price"] == 250000.00
    assert sold_df.iloc[0]["price_per_sqft"] == 250.00
    assert avail_df.iloc[0]["sale_price"] == 150000.50
    assert avail_df.iloc[0]["price_per_sqft"] == 300.00
    assert sold_df.iloc[0]["client_ref"] == "C1"
    assert pd.isna(avail_df.iloc[0]["client_ref"])


def test_satisfaction_chi_square_uniformity() -> None:
    """Test Chi-Square test runs correctly and outputs expected structure."""
    df = pd.DataFrame({"satisfaction_score": [1, 2, 3, 4, 5] * 20})
    result = evaluate_satisfaction_uniformity(df)
    assert result["degrees_of_freedom"] == 4
    assert result["chi_square_statistic"] == 0.0
    assert result["p_value"] == 1.0
    assert result["is_uniform_at_alpha_0_05"] is True
