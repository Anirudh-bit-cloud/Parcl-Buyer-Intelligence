"""Property-based testing with Hypothesis for data cleaning robustness."""

import pandas as pd
from hypothesis import given
from hypothesis import strategies as st
from parcl_core.cleaning import clean_properties


@given(
    price=st.floats(min_value=1000.0, max_value=10000000.0, allow_nan=False, allow_infinity=False),
    area=st.floats(min_value=100.0, max_value=20000.0, allow_nan=False, allow_infinity=False),
    tower=st.integers(min_value=1, max_value=50),
    unit=st.integers(min_value=1, max_value=9999),
)
def test_clean_properties_invariants(price: float, area: float, tower: int, unit: int) -> None:
    """Hypothesis test verifying numerical invariants across arbitrary valid floats/integers."""
    formatted_price = f"${price:,.2f}"
    raw_df = pd.DataFrame(
        {
            "listing_id": [99999],
            "tower_number": [tower],
            "transaction_date": ["05-01-2024"],
            "unit_category": ["Apartment"],
            "unit_number": [unit],
            "floor_area_sqft": [area],
            "sale_price": [formatted_price],
            "listing_status": ["Sold"],
            "client_ref": ["C9999"],
        }
    )

    sold_df, _ = clean_properties(raw_df)

    # Assert price extracted accurately within rounding tolerance
    assert abs(sold_df.iloc[0]["sale_price"] - round(price, 2)) < 0.05
    # Assert price_per_sqft is positive and accurately calculated
    assert sold_df.iloc[0]["price_per_sqft"] > 0
    expected_ppsqft = round(sold_df.iloc[0]["sale_price"] / area, 2)
    assert abs(sold_df.iloc[0]["price_per_sqft"] - expected_ppsqft) < 0.05
