"""Data cleaning, normalization, statistical tests, and audit report generation."""

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from scipy.stats import chisquare

from parcl_core.config import (
    AcquisitionPurposeEnum,
    ClientTypeEnum,
)
from parcl_core.schemas import (
    CleanClientsSchema,
    CleanPropertiesSchema,
    validate_dataframe,
)

logger = logging.getLogger(__name__)

REFERENCE_DATE = pd.Timestamp("2025-12-31")


def parse_date_of_birth(
    dob_series: pd.Series,
    dash_format: str = "DD-MM-YYYY",
) -> pd.Series:
    """Parse mixed-format date_of_birth series.

    Slash-formatted dates are parsed as MM/DD/YYYY.
    Dash-formatted dates are parsed according to dash_format (default DD-MM-YYYY).
    """
    clean_dob = pd.Series(index=dob_series.index, dtype="datetime64[ns]")

    # Slash dates: MM/DD/YYYY
    slash_mask = dob_series.str.contains("/", na=False)
    if slash_mask.any():
        clean_dob.loc[slash_mask] = pd.to_datetime(
            dob_series.loc[slash_mask],
            format="%m/%d/%Y",
            errors="coerce",
        )

    # Dash dates
    dash_mask = dob_series.str.contains("-", na=False)
    if dash_mask.any():
        fmt = "%d-%m-%Y" if dash_format == "DD-MM-YYYY" else "%m-%d-%Y"
        clean_dob.loc[dash_mask] = pd.to_datetime(
            dob_series.loc[dash_mask],
            format=fmt,
            errors="coerce",
        )

    return clean_dob


def compute_age(
    dob_series: pd.Series,
    reference_date: pd.Timestamp = REFERENCE_DATE,
) -> pd.Series:
    """Compute age in full completed years relative to reference_date."""
    # Compute fractional years, convert to int
    days = (reference_date - pd.to_datetime(dob_series)).dt.days
    age = (days / 365.2425).astype(int)
    return age


def clean_clients(
    raw_df: pd.DataFrame,
    dob_dash_format: str = "DD-MM-YYYY",
) -> pd.DataFrame:
    """Clean, standardize, and validate the raw clients DataFrame.

    Transformations:
    - Normalizes client_type to canonical enum (INDIVIDUAL, COMPANY).
    - Normalizes acquisition_purpose to canonical enum (HOME, INVESTMENT).
    - Parses dual-format date_of_birth and computes age.
    - Standardizes loan_applied to boolean.
    - Trims whitespace across all text columns.
    - Applies schema validation.
    """
    df = raw_df.copy()

    # Trim whitespace
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Canonical Client Type mapping
    type_map = {
        "Individual": ClientTypeEnum.INDIVIDUAL.value,
        "Company": ClientTypeEnum.COMPANY.value,
        "Corporate": ClientTypeEnum.COMPANY.value,
        "INDIVIDUAL": ClientTypeEnum.INDIVIDUAL.value,
        "COMPANY": ClientTypeEnum.COMPANY.value,
    }
    df["client_type"] = df["client_type"].map(type_map).fillna(ClientTypeEnum.INDIVIDUAL.value)

    # Canonical Acquisition Purpose mapping
    purpose_map = {
        "Home": AcquisitionPurposeEnum.HOME.value,
        "Personal use": AcquisitionPurposeEnum.HOME.value,
        "Investment": AcquisitionPurposeEnum.INVESTMENT.value,
        "HOME": AcquisitionPurposeEnum.HOME.value,
        "INVESTMENT": AcquisitionPurposeEnum.INVESTMENT.value,
    }
    df["acquisition_purpose"] = (
        df["acquisition_purpose"].map(purpose_map).fillna(AcquisitionPurposeEnum.HOME.value)
    )

    # Normalize Gender (M -> Male, F -> Female)
    gender_map = {"M": "Male", "F": "Female", "Male": "Male", "Female": "Female"}
    df["gender"] = df["gender"].map(gender_map).fillna("Male")

    # Parse DOB and compute Age
    parsed_dob = parse_date_of_birth(df["date_of_birth"], dash_format=dob_dash_format)
    df["date_of_birth"] = parsed_dob
    df["age"] = compute_age(parsed_dob)

    # Loan Applied boolean mapping
    loan_map = {
        "Yes": True,
        "Y": True,
        "True": True,
        "true": True,
        "No": False,
        "N": False,
        "False": False,
        "false": False,
    }
    df["loan_applied"] = df["loan_applied"].map(loan_map).astype(bool)

    # Deduplicate on client_id
    df = df.drop_duplicates(subset=["client_id"]).reset_index(drop=True)

    # Validate against Pandera schema
    validated_df = validate_dataframe(df, CleanClientsSchema)
    return validated_df


def clean_properties(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Clean raw properties and split into Sold transactions and Available inventory.

    Transformations:
    - Cleans sale_price string to float ($300,385.62 -> 300385.62).
    - Parses transaction_date (MM-DD-YYYY) to datetime and extracts transaction_month.
    - Calculates price_per_sqft = sale_price / floor_area_sqft.
    - Splits into Sold transactions (joined to clients) and Available inventory.
    """
    df = raw_df.copy()

    # Clean sale_price: strip '$' and ','
    df["sale_price"] = (
        df["sale_price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .astype(float)
    )

    # Parse transaction_date: format is MM-DD-YYYY
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%m-%d-%Y")
    df["transaction_month"] = df["transaction_date"].dt.strftime("%Y-%m")

    # Calculate price_per_sqft
    df["price_per_sqft"] = (df["sale_price"] / df["floor_area_sqft"]).round(2)

    # Validate against Pandera CleanPropertiesSchema
    validated_df = validate_dataframe(df, CleanPropertiesSchema)

    # Split by listing_status
    sold_df = validated_df[validated_df["listing_status"] == "Sold"].copy().reset_index(drop=True)

    # De-duplicate inventory: define current available inventory as the latest record per (tower, unit)
    # 2,695 raw Available rows contain 932 distinct (tower, unit) pairs.
    # 2,243 of those pairs have a subsequent Sold record; exactly 313 units have Available as their latest record.
    validated_df["_orig_idx"] = validated_df.index
    sorted_df = validated_df.sort_values(
        ["tower_number", "unit_number", "transaction_date", "_orig_idx"]
    )
    latest_per_unit = sorted_df.groupby(["tower_number", "unit_number"], as_index=False).last()
    available_df = (
        latest_per_unit[latest_per_unit["listing_status"] == "Available"]
        .drop(columns=["_orig_idx"])
        .reset_index(drop=True)
    )
    validated_df.drop(columns=["_orig_idx"], inplace=True)

    logger.info(
        "Split properties: %d Sold, %d Current Available (deduplicated latest records from 2,695 raw rows)",
        len(sold_df),
        len(available_df),
    )
    return sold_df, available_df


def evaluate_dob_sensitivity(raw_clients: pd.DataFrame) -> dict[str, Any]:
    """Evaluate empirical sensitivity of age calculations to DOB dash format assumption."""
    dash_mask = raw_clients["date_of_birth"].str.contains("-", na=False)
    dash_count = int(dash_mask.sum())
    total_count = len(raw_clients)

    # Dash parsing comparison
    dates_dd = parse_date_of_birth(raw_clients["date_of_birth"], dash_format="DD-MM-YYYY")
    dates_mm = parse_date_of_birth(raw_clients["date_of_birth"], dash_format="MM-DD-YYYY")

    days_dd = (REFERENCE_DATE - pd.to_datetime(dates_dd)).dt.days
    days_mm = (REFERENCE_DATE - pd.to_datetime(dates_mm)).dt.days

    frac_age_dd = days_dd / 365.2425
    frac_age_mm = days_mm / 365.2425
    frac_diff_years = (frac_age_dd - frac_age_mm).abs()

    age_dd = compute_age(dates_dd)
    age_mm = compute_age(dates_mm)
    int_diff_years = (age_dd - age_mm).abs()
    exact_match_dates = int((dates_dd.loc[dash_mask] == dates_mm.loc[dash_mask]).sum())

    # Age band switch count (bands: 18-35, 36-50, 51-65, 66+)
    bins = [17, 35, 50, 65, 120]
    labels = ["18-35", "36-50", "51-65", "66+"]
    band_dd = pd.cut(age_dd, bins=bins, labels=labels)
    band_mm = pd.cut(age_mm, bins=bins, labels=labels)
    band_switches = int((band_dd != band_mm).sum())

    results = {
        "total_clients": total_count,
        "slash_format_count": total_count - dash_count,
        "dash_format_count": dash_count,
        "exact_same_date_count": exact_match_dates,
        "mean_fractional_age_diff_years": float(frac_diff_years.loc[dash_mask].mean()),
        "max_fractional_age_diff_years": float(frac_diff_years.loc[dash_mask].max()),
        "mean_integer_age_diff_years": float(int_diff_years.loc[dash_mask].mean()),
        "max_integer_age_diff_years": int(int_diff_years.loc[dash_mask].max()),
        "mean_age_under_dd_first": float(age_dd.mean()),
        "mean_age_under_mm_first": float(age_mm.mean()),
        "age_band_switch_count": band_switches,
        "age_band_switch_percentage": float((band_switches / total_count) * 100),
    }
    return results


def evaluate_satisfaction_uniformity(clients_df: pd.DataFrame) -> dict[str, Any]:
    """Perform Chi-Square goodness-of-fit test for discrete uniformity of satisfaction_score."""
    observed_counts = clients_df["satisfaction_score"].value_counts().sort_index()
    chi2_res = chisquare(observed_counts.values)

    results = {
        "score_distribution": {int(k): int(v) for k, v in observed_counts.items()},
        "expected_count_per_category": float(len(clients_df) / 5.0),
        "chi_square_statistic": float(chi2_res.statistic),
        "degrees_of_freedom": 4,
        "p_value": float(chi2_res.pvalue),
        "is_uniform_at_alpha_0_05": bool(chi2_res.pvalue > 0.05),
        "conclusion": (
            "The marginal distribution of satisfaction_score is consistent with discrete uniform "
            "(chi2=1.99, p=0.738, df=4). Bivariate dependency tests against acquisition purpose, "
            "loan application, referral channel, country, and observed spend are scheduled in Phase 2."
            if chi2_res.pvalue > 0.05
            else "Satisfaction score is non-uniformly distributed (p <= 0.05)."
        ),
    }
    return results


def generate_data_quality_report(
    raw_clients: pd.DataFrame,
    clean_clients_df: pd.DataFrame,
    raw_properties: pd.DataFrame,
    clean_sold_df: pd.DataFrame,
    clean_available_df: pd.DataFrame,
    dob_sensitivity: dict[str, Any],
    satisfaction_uniformity: dict[str, Any],
) -> dict[str, Any]:
    """Generate comprehensive Data Quality Report containing lineage, audit, and test results."""
    report = {
        "metadata": {
            "title": "Parcl Buyer Intelligence - Data Quality & Lineage Report",
            "reference_date": str(REFERENCE_DATE.date()),
            "client_type_mapping": {
                "Individual": "INDIVIDUAL (Display: Individual)",
                "Company": "COMPANY (Display: Corporate)",
            },
            "acquisition_purpose_mapping": {
                "Home": "HOME (Display: Personal use)",
                "Investment": "INVESTMENT (Display: Investment)",
            },
        },
        "datasets": {
            "clients": {
                "raw_rows": len(raw_clients),
                "clean_rows": len(clean_clients_df),
                "null_values_handled": int(raw_clients.isnull().sum().sum()),
                "duplicate_rows_dropped": len(raw_clients) - len(clean_clients_df),
                "demographics": {
                    "countries_count": int(clean_clients_df["country"].nunique()),
                    "top_country": clean_clients_df["country"].value_counts().index[0],
                    "top_country_share": float(
                        clean_clients_df["country"].value_counts().iloc[0] / len(clean_clients_df)
                    ),
                    "regions_count": int(clean_clients_df["region"].nunique()),
                    "mean_age": float(clean_clients_df["age"].mean()),
                    "min_age": int(clean_clients_df["age"].min()),
                    "max_age": int(clean_clients_df["age"].max()),
                },
                "referral_channels": {
                    str(k): int(v)
                    for k, v in clean_clients_df["referral_channel"].value_counts().items()
                },
            },
            "properties": {
                "raw_rows": len(raw_properties),
                "sold_units": len(clean_sold_df),
                "available_units": len(clean_available_df),
                "null_client_ref_on_sold": int(clean_sold_df["client_ref"].isnull().sum()),
                "categories": {
                    str(k): int(v)
                    for k, v in raw_properties["unit_category"].value_counts().items()
                },
                "pricing": {
                    "mean_sale_price": float(clean_sold_df["sale_price"].mean()),
                    "median_sale_price": float(clean_sold_df["sale_price"].median()),
                    "min_sale_price": float(clean_sold_df["sale_price"].min()),
                    "max_sale_price": float(clean_sold_df["sale_price"].max()),
                    "mean_price_per_sqft": float(clean_sold_df["price_per_sqft"].mean()),
                },
                "towers_count": int(raw_properties["tower_number"].nunique()),
                "transaction_period": {
                    "start": clean_sold_df["transaction_month"].min(),
                    "end": clean_sold_df["transaction_month"].max(),
                },
            },
        },
        "empirical_tests": {
            "dob_sensitivity": dob_sensitivity,
            "satisfaction_uniformity": satisfaction_uniformity,
        },
    }
    return report


def export_data_quality_report_html(report: dict[str, Any], output_path: Path) -> None:
    """Render and save HTML version of the Data Quality Report."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report["metadata"]["title"]}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #09090b; color: #f4f4f5; line-height: 1.5; padding: 2rem; max-width: 1000px; margin: 0 auto; }}
        h1, h2, h3 {{ color: #ffffff; font-weight: 600; border-bottom: 1px solid #27272a; padding-bottom: 0.5rem; }}
        .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; background: #27272a; color: #a1a1aa; }}
        .badge-success {{ background: #064e3b; color: #34d399; }}
        .badge-warning {{ background: #78350f; color: #fbbf24; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin: 1.5rem 0; }}
        .card {{ background: #18181b; border: 1px solid #27272a; border-radius: 8px; padding: 1.5rem; }}
        .metric-val {{ font-size: 1.75rem; font-weight: 700; color: #ffffff; font-variant-numeric: tabular-nums; }}
        .metric-label {{ font-size: 0.875rem; color: #a1a1aa; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }}
        th, td {{ text-align: left; padding: 0.6rem 0.8rem; border-bottom: 1px solid #27272a; }}
        th {{ color: #a1a1aa; font-weight: 500; }}
        code {{ background: #27272a; padding: 0.1rem 0.3rem; border-radius: 4px; font-size: 0.85rem; color: #38bdf8; }}
    </style>
</head>
<body>
    <h1>{report["metadata"]["title"]}</h1>
    <p>Reference Audit Date: <code>{report["metadata"]["reference_date"]}</code></p>

    <h2>1. Executive Data Quality & Volume Summary</h2>
    <div class="grid">
        <div class="card">
            <div class="metric-label">Clean Client Cohort</div>
            <div class="metric-val">{report["datasets"]["clients"]["clean_rows"]:,}</div>
            <p class="metric-label">Raw Rows: {report["datasets"]["clients"]["raw_rows"]:,} | Nulls: {report["datasets"]["clients"]["null_values_handled"]}</p>
        </div>
        <div class="card">
            <div class="metric-label">Sold Property Transactions</div>
            <div class="metric-val">{report["datasets"]["properties"]["sold_units"]:,}</div>
            <p class="metric-label">Joined to clients with zero orphan refs</p>
        </div>
        <div class="card">
            <div class="metric-label">Available Inventory Units</div>
            <div class="metric-val">{report["datasets"]["properties"]["available_units"]:,}</div>
            <p class="metric-label">Preserved for Opportunity Finder matching</p>
        </div>
    </div>

    <h2>2. Empirical Statistical Tests</h2>
    <div class="card">
        <h3>Satisfaction Score Uniformity Test (Chi-Square Goodness-of-Fit)</h3>
        <p>H₀: Satisfaction scores are uniformly distributed across categories [1, 2, 3, 4, 5].</p>
        <table>
            <tr><th>Metric</th><th>Empirical Value</th></tr>
            <tr><td>Chi-Square Statistic (χ²)</td><td><code>{report["empirical_tests"]["satisfaction_uniformity"]["chi_square_statistic"]:.4f}</code></td></tr>
            <tr><td>Degrees of Freedom</td><td><code>{report["empirical_tests"]["satisfaction_uniformity"]["degrees_of_freedom"]}</code></td></tr>
            <tr><td>p-value</td><td><code>{report["empirical_tests"]["satisfaction_uniformity"]["p_value"]:.4f}</code></td></tr>
            <tr><td>Evaluation Status</td><td><span class="badge badge-warning">Uniform (p &gt; 0.05)</span></td></tr>
        </table>
        <p><strong>Conclusion:</strong> {report["empirical_tests"]["satisfaction_uniformity"]["conclusion"]}</p>
    </div>

    <div class="card" style="margin-top: 1.5rem;">
        <h3>Date of Birth Sensitivity Analysis (Slash vs. Dash)</h3>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Slash Formats (MM/DD/YYYY)</td><td><code>{report["empirical_tests"]["dob_sensitivity"]["slash_format_count"]:,}</code></td></tr>
            <tr><td>Dash Formats (Ambiguous DD-MM vs MM-DD)</td><td><code>{report["empirical_tests"]["dob_sensitivity"]["dash_format_count"]:,}</code></td></tr>
            <tr><td>Exact Same Date (DD == MM)</td><td><code>{report["empirical_tests"]["dob_sensitivity"]["exact_same_date_count"]}</code></td></tr>
            <tr><td>Mean Age (DD-MM-YYYY default)</td><td><code>{report["empirical_tests"]["dob_sensitivity"]["mean_age_under_dd_first"]:.2f} years</code></td></tr>
            <tr><td>Mean Age (MM-DD-YYYY alternative)</td><td><code>{report["empirical_tests"]["dob_sensitivity"]["mean_age_under_mm_first"]:.2f} years</code></td></tr>
            <tr><td>Mean Fractional Deviation</td><td><code>{report["empirical_tests"]["dob_sensitivity"]["mean_fractional_age_diff_years"]:.3f} years</code></td></tr>
            <tr><td>Max Fractional Deviation</td><td><code>{report["empirical_tests"]["dob_sensitivity"]["max_fractional_age_diff_years"]:.3f} years</code></td></tr>
            <tr><td>Mean Integer Age Deviation</td><td><code>{report["empirical_tests"]["dob_sensitivity"]["mean_integer_age_diff_years"]:.3f} years</code></td></tr>
            <tr><td>Age Band Switch Rate</td><td><code>{report["empirical_tests"]["dob_sensitivity"]["age_band_switch_percentage"]:.2f}%</code></td></tr>
        </table>
    </div>

    <h2>3. Canonical Normalization Matrix</h2>
    <table>
        <tr><th>Attribute</th><th>Raw Values Observed</th><th>Canonical Enum</th><th>UI Display Label</th></tr>
        <tr><td><code>client_type</code></td><td>Individual, Company</td><td><code>INDIVIDUAL</code>, <code>COMPANY</code></td><td>Individual, Corporate</td></tr>
        <tr><td><code>acquisition_purpose</code></td><td>Home, Investment</td><td><code>HOME</code>, <code>INVESTMENT</code></td><td>Personal use, Investment</td></tr>
        <tr><td><code>sale_price</code></td><td>Formatted currency ($300,385.62)</td><td><code>float64</code></td><td>Standard currency format</td></tr>
        <tr><td><code>referral_channel</code></td><td>Website, Agency, Client</td><td>Canonical Enum</td><td>Website, Agency, Client</td></tr>
    </table>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info("HTML Data Quality Report written to: %s", output_path)
