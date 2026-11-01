"""Feature engineering, aggregation, statistical bivariate testing, and profiling metrics."""

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, f_oneway, kruskal

from parcl_core.feature_schema import ClientFeaturesSchema
from parcl_core.schemas import validate_dataframe

logger = logging.getLogger(__name__)


def compute_portfolio_features(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Derive client-level purchase metrics from Sold transaction records."""
    # Group by client_ref
    grouped = transactions_df.groupby("client_ref")

    # Aggregated metrics
    n_units = grouped["listing_id"].count().rename("n_units")
    total_spend = grouped["sale_price"].sum().rename("total_spend")
    avg_price = grouped["sale_price"].mean().rename("avg_price")
    max_price = grouped["sale_price"].max().rename("max_price")
    avg_floor_area = grouped["floor_area_sqft"].mean().rename("avg_floor_area")
    price_per_sqft = grouped["price_per_sqft"].mean().rename("price_per_sqft")
    n_towers = grouped["tower_number"].nunique().rename("n_towers")

    # Category shares
    office_counts = (
        transactions_df[transactions_df["unit_category"] == "Office"]
        .groupby("client_ref")["listing_id"]
        .count()
    )
    office_share = (office_counts / n_units).fillna(0.0).rename("office_share")
    apartment_share = (1.0 - office_share).rename("apartment_share")

    # Portfolio concentration: HHI over towers = sum(s_i^2) where s_i is tower share
    tower_client_counts = (
        transactions_df.groupby(["client_ref", "tower_number"])["listing_id"]
        .count()
        .reset_index(name="tower_count")
    )
    tower_client_counts = tower_client_counts.merge(n_units.reset_index(), on="client_ref")
    tower_client_counts["share_sq"] = (
        tower_client_counts["tower_count"] / tower_client_counts["n_units"]
    ) ** 2
    hhi = (
        tower_client_counts.groupby("client_ref")["share_sq"]
        .sum()
        .round(4)
        .rename("portfolio_towers_hhi")
    )

    # Purchase time window
    min_date = grouped["transaction_date"].min()
    max_date = grouped["transaction_date"].max()
    first_month = min_date.dt.strftime("%Y-%m").rename("first_purchase_month")
    last_month = max_date.dt.strftime("%Y-%m").rename("last_purchase_month")

    # Purchase span in months: (year_diff * 12 + month_diff)
    span_months = (
        (max_date.dt.year - min_date.dt.year) * 12 + (max_date.dt.month - min_date.dt.month)
    ).rename("purchase_span_months")

    portfolio_df = (
        pd.concat(
            [
                n_units,
                total_spend,
                avg_price,
                max_price,
                avg_floor_area,
                price_per_sqft,
                n_towers,
                office_share,
                apartment_share,
                hhi,
                first_month,
                last_month,
                span_months,
            ],
            axis=1,
        )
        .reset_index()
        .rename(columns={"client_ref": "client_id"})
    )

    portfolio_df["is_multi_unit"] = portfolio_df["n_units"] >= 2
    portfolio_df["spend_percentile"] = (portfolio_df["total_spend"].rank(pct=True) * 100.0).round(2)

    return portfolio_df


def engineer_client_features(
    clients_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge clients with derived portfolio traits and validate against Pandera schema."""
    portfolio_df = compute_portfolio_features(transactions_df)
    features_df = clients_df.merge(portfolio_df, on="client_id", how="inner")

    # Derive age band
    bins = [17, 35, 50, 65, 120]
    labels = ["18-35", "36-50", "51-65", "66+"]
    features_df["age_band"] = pd.cut(features_df["age"], bins=bins, labels=labels).astype(str)

    # Missing value handling policy: audit indicators if any imputation needed
    for col in features_df.columns:
        null_count = features_df[col].isnull().sum()
        if null_count > 0:
            logger.warning("Imputing %d missing values in feature: %s", null_count, col)
            features_df[f"{col}_is_imputed"] = features_df[col].isnull()
            if pd.api.types.is_numeric_dtype(features_df[col]):
                features_df[col] = features_df[col].fillna(features_df[col].median())
            else:
                features_df[col] = features_df[col].fillna(features_df[col].mode()[0])

    # Validate against schema
    validated_df = validate_dataframe(features_df, ClientFeaturesSchema)
    logger.info("Successfully engineered %d client feature records", len(validated_df))
    return validated_df


def evaluate_satisfaction_bivariate_dependencies(features_df: pd.DataFrame) -> dict[str, Any]:
    """Evaluate bivariate statistical dependency between satisfaction_score and key business attributes."""
    results: dict[str, Any] = {}

    # Categoricals: Chi-square test of independence
    categoricals = ["acquisition_purpose", "loan_applied", "referral_channel", "country"]
    for cat in categoricals:
        contingency = pd.crosstab(features_df["satisfaction_score"], features_df[cat])
        chi2, p_val, dof, _ = chi2_contingency(contingency)
        n = len(features_df)
        min_dim = min(contingency.shape) - 1
        cramers_v = float(np.sqrt(chi2 / (n * min_dim))) if min_dim > 0 else 0.0

        results[cat] = {
            "test": "Chi-Square Test of Independence",
            "chi2_statistic": float(chi2),
            "p_value": float(p_val),
            "degrees_of_freedom": int(dof),
            "cramers_v": round(cramers_v, 4),
            "is_significant_alpha_0_05": bool(p_val < 0.05),
        }

    # Spend vs Satisfaction: Kruskal-Wallis & ANOVA
    spend_groups = [
        features_df[features_df["satisfaction_score"] == s]["total_spend"].values
        for s in sorted(features_df["satisfaction_score"].unique())
    ]
    kw_stat, kw_p = kruskal(*spend_groups)
    anova_stat, anova_p = f_oneway(*spend_groups)

    results["total_spend"] = {
        "kruskal_wallis": {
            "h_statistic": float(kw_stat),
            "p_value": float(kw_p),
            "is_significant_alpha_0_05": bool(kw_p < 0.05),
        },
        "anova": {
            "f_statistic": float(anova_stat),
            "p_value": float(anova_p),
            "is_significant_alpha_0_05": bool(anova_p < 0.05),
        },
    }

    return results
