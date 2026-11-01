"""Feature encoding, transformations, and geographic ablation pipelines."""

from typing import Literal

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, QuantileTransformer, StandardScaler

# Model A (Exact PRD Step 2 Baseline)
MODEL_A_NUMERICS = ["age", "satisfaction_score"]
MODEL_A_CATEGORICALS = [
    "client_type",
    "acquisition_purpose",
    "referral_channel",
    "country",
    "region",
]

# Model B Behavioral & Portfolio Pool (Excluding all spend metrics: total_spend, avg_price, max_price)
MODEL_B_BASE_NUMERICS = [
    "age",
    "avg_floor_area",
    "price_per_sqft",
    "n_towers",
    "portfolio_towers_hhi",
    "purchase_span_months",
    "office_share",
]
MODEL_B_CATEGORICALS = ["client_type", "acquisition_purpose", "referral_channel"]
MODEL_B_BOOLEANS = ["loan_applied", "is_multi_unit"]


def build_model_a_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    """Build exact Scikit-learn ColumnTransformer for PRD Model A baseline."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), MODEL_A_NUMERICS),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                MODEL_A_CATEGORICALS,
            ),
        ],
        remainder="drop",
    )
    preprocessor.fit(df)
    return preprocessor


def build_model_b_preprocessor(
    df: pd.DataFrame,
    include_satisfaction: bool = True,
    geo_mode: Literal["full", "downweighted", "removed"] = "full",
    quantile_n_units: bool = True,
) -> tuple[ColumnTransformer, list[str]]:
    """Build enriched ColumnTransformer for Model B with ablation variants."""
    transformers = []
    feature_names = []

    # 1. Continuous numerics
    num_cols = list(MODEL_B_BASE_NUMERICS)
    if include_satisfaction:
        num_cols.append("satisfaction_score")
    transformers.append(("std_num", StandardScaler(), num_cols))
    feature_names.extend(num_cols)

    # 2. Portfolio volume n_units (Quantile transformed or log1p)
    if quantile_n_units:
        transformers.append(
            (
                "quantile_units",
                QuantileTransformer(
                    n_quantiles=min(100, len(df)), output_distribution="normal", random_state=42
                ),
                ["n_units"],
            )
        )
    else:
        transformers.append(("std_units", StandardScaler(), ["n_units"]))
    feature_names.append("n_units_transformed")

    # 3. Booleans (loan_applied, is_multi_unit) -> pass as float 0.0/1.0
    transformers.append(("bool_pass", "passthrough", MODEL_B_BOOLEANS))
    feature_names.extend(MODEL_B_BOOLEANS)

    # 4. Core categoricals
    transformers.append(
        (
            "core_cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            MODEL_B_CATEGORICALS,
        )
    )

    # 5. Geography handling (Ablation: full / downweighted / removed)
    if geo_mode in ["full", "downweighted"]:
        geo_cols = ["country", "region"]
        transformers.append(
            (
                "geo_cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                geo_cols,
            )
        )

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    preprocessor.fit(df)
    return preprocessor, feature_names


def transform_and_ablate_model_b(
    df: pd.DataFrame,
    include_satisfaction: bool = True,
    geo_mode: Literal["full", "downweighted", "removed"] = "full",
) -> np.ndarray:
    """Transform features and apply geographic weighting factor if downweighted."""
    preprocessor, _ = build_model_b_preprocessor(
        df,
        include_satisfaction=include_satisfaction,
        geo_mode=geo_mode,
        quantile_n_units=True,
    )
    X = preprocessor.transform(df)

    if geo_mode == "downweighted":
        # Identify geo column indices and downweight by 0.5
        # Everything after core categoricals is geo
        # For simplicity and exact weighting:
        cat_encoder = preprocessor.named_transformers_["core_cat"]
        n_core_cat = cat_encoder.transform(df[MODEL_B_CATEGORICALS]).shape[1]
        n_prev = (
            len(MODEL_B_BASE_NUMERICS)
            + (1 if include_satisfaction else 0)
            + 1
            + len(MODEL_B_BOOLEANS)
            + n_core_cat
        )
        X[:, n_prev:] = X[:, n_prev:] * 0.5

    return X
