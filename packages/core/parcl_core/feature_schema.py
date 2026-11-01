"""Pandera validation schema for engineered client features."""

import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

ClientFeaturesSchema = DataFrameSchema(
    columns={
        "client_id": Column(pa.String, nullable=False, unique=True),
        # Demographics
        "age": Column(pa.Int, Check.in_range(18, 120), nullable=False),
        "age_band": Column(
            pa.String, Check.isin(["18-35", "36-50", "51-65", "66+"]), nullable=False
        ),
        "gender": Column(pa.String, Check.isin(["Male", "Female"]), nullable=False),
        "country": Column(pa.String, nullable=False),
        "region": Column(pa.String, nullable=False),
        # Behavioral & Financial indicators
        "client_type": Column(pa.String, Check.isin(["INDIVIDUAL", "COMPANY"]), nullable=False),
        "acquisition_purpose": Column(
            pa.String, Check.isin(["HOME", "INVESTMENT"]), nullable=False
        ),
        "loan_applied": Column(pa.Bool, nullable=False),
        "referral_channel": Column(
            pa.String, Check.isin(["Website", "Agency", "Client"]), nullable=False
        ),
        "satisfaction_score": Column(pa.Int, Check.in_range(1, 5), nullable=False),
        # Portfolio structure & intent proxies (Clustering Candidates)
        "n_units": Column(pa.Int, Check.greater_than_or_equal_to(1), nullable=False),
        "is_multi_unit": Column(pa.Bool, nullable=False),
        "n_towers": Column(pa.Int, Check.greater_than_or_equal_to(1), nullable=False),
        "portfolio_towers_hhi": Column(pa.Float, Check.in_range(0.0, 1.0), nullable=False),
        "avg_floor_area": Column(pa.Float, Check.greater_than(0.0), nullable=False),
        "office_share": Column(pa.Float, Check.in_range(0.0, 1.0), nullable=False),
        "apartment_share": Column(pa.Float, Check.in_range(0.0, 1.0), nullable=False),
        "price_per_sqft": Column(pa.Float, Check.greater_than(0.0), nullable=False),
        "purchase_span_months": Column(pa.Int, Check.greater_than_or_equal_to(0), nullable=False),
        # Orthogonal Profiling metrics (EXCLUDED FROM CLUSTERING)
        "total_spend": Column(pa.Float, Check.greater_than(0.0), nullable=False),
        "avg_price": Column(pa.Float, Check.greater_than(0.0), nullable=False),
        "max_price": Column(pa.Float, Check.greater_than(0.0), nullable=False),
        "spend_percentile": Column(pa.Float, Check.in_range(0.0, 100.0), nullable=False),
    },
    strict=False,
    coerce=True,
)
