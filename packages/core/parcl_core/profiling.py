"""Segment profiling, feature lift tables, and statistical significance testing."""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_segment_profiles(
    features_df: pd.DataFrame,
    cluster_labels: np.ndarray,
) -> dict[str, Any]:
    """Compute comprehensive descriptive profile, lifts, and statistical tests per cluster."""
    df = features_df.copy()
    df["cluster"] = cluster_labels
    n_cohort = len(df)
    n_clusters = len(np.unique(cluster_labels))

    profiles: dict[str, Any] = {}

    numeric_cols = [
        "age",
        "n_units",
        "avg_floor_area",
        "price_per_sqft",
        "n_towers",
        "portfolio_towers_hhi",
        "purchase_span_months",
        "office_share",
        "apartment_share",
        "total_spend",
        "avg_price",
    ]
    categorical_cols = [
        "acquisition_purpose",
        "client_type",
        "referral_channel",
        "loan_applied",
        "country",
        "is_multi_unit",
    ]

    # 1. Overall cohort baseline
    overall_num_means = {col: float(df[col].mean()) for col in numeric_cols}
    overall_num_stds = {col: float(df[col].std()) for col in numeric_cols}
    overall_cat_freqs = {
        col: df[col].value_counts(normalize=True).to_dict() for col in categorical_cols
    }

    for c_id in sorted(df["cluster"].unique()):
        c_df = df[df["cluster"] == c_id]
        c_size = len(c_df)
        c_share = float(c_size / n_cohort)

        # Numeric stats and Standardized Mean Differences (SMD = (mean_c - mean_all) / std_all)
        num_stats = {}
        for col in numeric_cols:
            mean_c = float(c_df[col].mean())
            std_all = overall_num_stds[col]
            smd = float((mean_c - overall_num_means[col]) / std_all) if std_all > 0 else 0.0
            num_stats[col] = {
                "mean": round(mean_c, 2),
                "median": round(float(c_df[col].median()), 2),
                "smd": round(smd, 3),
            }

        # Categorical distributions and Lift = (freq_c / freq_all) * 100
        cat_stats = {}
        for col in categorical_cols:
            c_freqs = c_df[col].value_counts(normalize=True).to_dict()
            lifts = {}
            for val, base_freq in overall_cat_freqs[col].items():
                cluster_freq = c_freqs.get(val, 0.0)
                lift = round((cluster_freq / base_freq) * 100.0, 1) if base_freq > 0 else 100.0
                lifts[str(val)] = {
                    "share": round(float(cluster_freq), 4),
                    "lift": lift,
                }
            cat_stats[col] = lifts

        profiles[f"Cluster_{c_id}"] = {
            "cluster_id": int(c_id),
            "size": c_size,
            "share": c_share,
            "numeric_metrics": num_stats,
            "categorical_metrics": cat_stats,
        }

    return {
        "n_clusters": n_clusters,
        "n_cohort": n_cohort,
        "cluster_profiles": profiles,
    }
