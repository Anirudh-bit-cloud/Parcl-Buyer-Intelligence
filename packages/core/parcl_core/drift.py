"""Data and Concept Drift Monitoring Engine (PSI, Kolmogorov-Smirnov, Cluster Mix).

Production-grade drift monitoring calculating:
1. Population Stability Index (PSI) for continuous features.
2. Kolmogorov-Smirnov two-sample tests for distribution divergence.
3. Chi-square test on cluster assignment shift between reference and current windows.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


def calculate_psi(
    reference: np.ndarray,
    current: np.ndarray,
    num_buckets: int = 10,
    epsilon: float = 1e-4,
) -> tuple[float, list[dict[str, Any]]]:
    """Calculate Population Stability Index (PSI) between reference and current distributions.

    Standard Industry Thresholds:
    - PSI < 0.10: No significant drift (Stable).
    - 0.10 <= PSI < 0.25: Moderate drift (Monitor).
    - PSI >= 0.25: Significant drift (Action required / Retrain).
    """
    ref = np.asarray(reference, dtype=float)
    curr = np.asarray(current, dtype=float)

    ref = ref[~np.isnan(ref)]
    curr = curr[~np.isnan(curr)]

    if len(ref) == 0 or len(curr) == 0:
        return 0.0, []

    # Quantile bins based on reference sample
    percentiles = np.linspace(0, 100, num_buckets + 1)
    bin_edges = np.percentile(ref, percentiles)
    bin_edges = np.unique(bin_edges)

    if len(bin_edges) < 2:
        return 0.0, []

    # Extend outer edges so shifted values outside reference range are captured
    bin_edges = bin_edges.astype(float)
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    # Bin counts
    ref_counts, _ = np.histogram(ref, bins=bin_edges)
    curr_counts, _ = np.histogram(curr, bins=bin_edges)

    ref_pct = (ref_counts / len(ref)) + epsilon
    curr_pct = (curr_counts / len(curr)) + epsilon

    # Normalize back to 1
    ref_pct = ref_pct / np.sum(ref_pct)
    curr_pct = curr_pct / np.sum(curr_pct)

    psi_values = (curr_pct - ref_pct) * np.log(curr_pct / ref_pct)
    total_psi = float(np.sum(psi_values))

    buckets_data = []
    for i in range(len(ref_counts)):
        low = float(bin_edges[i])
        high = float(bin_edges[i + 1])
        low_str = "-inf" if np.isneginf(low) else f"{low:.2f}"
        high_str = "+inf" if np.isposinf(high) else f"{high:.2f}"
        buckets_data.append(
            {
                "bucket": f"[{low_str}, {high_str}]",
                "reference_pct": float(round(ref_pct[i] * 100, 2)),
                "current_pct": float(round(curr_pct[i] * 100, 2)),
                "bucket_psi": float(round(psi_values[i], 4)),
            }
        )

    return float(round(total_psi, 4)), buckets_data


def run_full_drift_audit(client_features: pd.DataFrame) -> dict[str, Any]:
    """Execute complete drift audit comparing early vs late purchase cohorts.

    Splits clients into:
    - Reference Cohort: First purchase month <= 2024-06 (or first half)
    - Current Cohort: First purchase month > 2024-06 (or second half)
    """
    df = client_features.copy()
    split_col = "first_purchase_month" if "first_purchase_month" in df.columns else None

    if split_col and df[split_col].nunique() > 1:
        median_month = df[split_col].sort_values().iloc[len(df) // 2]
        ref_mask = df[split_col] <= median_month
        curr_mask = ~ref_mask
    else:
        # Fallback to random balanced 50/50 partition
        ref_mask = df.index < len(df) // 2
        curr_mask = ~ref_mask

    df_ref = df[ref_mask]
    df_curr = df[curr_mask]

    numeric_features = ["total_spend", "age", "n_units", "price_per_sqft", "office_share"]
    feature_metrics = []
    max_psi = 0.0

    for feat in numeric_features:
        if feat not in df.columns:
            continue
        vals_ref = df_ref[feat].dropna().values
        vals_curr = df_curr[feat].dropna().values

        psi_val, buckets = calculate_psi(vals_ref, vals_curr, num_buckets=8)
        max_psi = max(max_psi, psi_val)

        # Kolmogorov-Smirnov 2-sample test
        ks_stat, ks_pval = stats.ks_2samp(vals_ref, vals_curr)

        status = "STABLE" if psi_val < 0.10 else ("MODERATE_DRIFT" if psi_val < 0.25 else "HIGH_DRIFT")

        feature_metrics.append(
            {
                "feature": feat,
                "psi": psi_val,
                "ks_statistic": float(round(ks_stat, 4)),
                "ks_pvalue": float(round(ks_pval, 4)),
                "status": status,
                "ref_mean": float(round(np.mean(vals_ref), 2)),
                "curr_mean": float(round(np.mean(vals_curr), 2)),
                "buckets": buckets,
            }
        )

    # Cluster mix drift
    cluster_drift = {}
    if "cluster" in df.columns:
        ref_clusters = df_ref["cluster"].value_counts().sort_index()
        curr_clusters = df_curr["cluster"].value_counts().sort_index()
        all_clusters = sorted(set(ref_clusters.index).union(curr_clusters.index))

        ref_counts = [ref_clusters.get(c, 0) for c in all_clusters]
        curr_counts = [curr_clusters.get(c, 0) for c in all_clusters]

        # Contingency chi2
        contingency = np.array([ref_counts, curr_counts])
        chi2, p_val, dof, _ = stats.chi2_contingency(contingency)

        cluster_shares = []
        for c in all_clusters:
            ref_sh = (ref_clusters.get(c, 0) / len(df_ref)) * 100
            curr_sh = (curr_clusters.get(c, 0) / len(df_curr)) * 100
            cluster_shares.append(
                {
                    "cluster_id": int(c),
                    "reference_share_pct": float(round(ref_sh, 2)),
                    "current_share_pct": float(round(curr_sh, 2)),
                    "shift_pct_pts": float(round(curr_sh - ref_sh, 2)),
                }
            )

        cluster_drift = {
            "chi2_statistic": float(round(chi2, 4)),
            "p_value": float(round(p_val, 4)),
            "is_significant": bool(p_val < 0.05),
            "cluster_breakdown": cluster_shares,
        }

    overall_status = "HEALTHY" if max_psi < 0.10 else ("WARNING" if max_psi < 0.25 else "CRITICAL")

    return {
        "status": overall_status,
        "overall_drift_verdict": overall_status,
        "max_psi": float(round(max_psi, 4)),
        "reference_sample_size": len(df_ref),
        "current_sample_size": len(df_curr),
        "features": feature_metrics,
        "feature_drift": feature_metrics,
        "cluster_mix_drift": cluster_drift,
        "audit_timestamp": pd.Timestamp.now().isoformat(),
    }
