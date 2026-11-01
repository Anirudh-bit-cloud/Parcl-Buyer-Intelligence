"""Model Governance, Selection, Comparison, and Data Quality router."""

import json

from fastapi import APIRouter

from apps.api.config import api_settings
from apps.api.schemas.common import ResponseMetadata
from apps.api.schemas.governance import (
    BetaCalibrationPoint,
    DataQualitySummaryResponse,
    ModelCardResponse,
    PRDHypothesisVerdictItem,
)
from apps.api.schemas.model_selection import (
    ModelCompareResponse,
    ModelSelectionResponse,
    ModelVariantBenchmarkItem,
)
from apps.api.services.model_service import model_service

router = APIRouter(tags=["Model Governance & Benchmarks"])


@router.get(
    "/api/v1/model/selection",
    response_model=ModelSelectionResponse,
    summary="Model Selection Battery & Temperature Beta Calibration Grid",
)
async def get_model_selection() -> ModelSelectionResponse:
    """Retrieve optimal k benchmarks, Kneedle elbow, and full temperature beta calibration grid."""
    res = model_service.get_model_selection_response()
    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=True,
        untested_assumptions_notice="Model B3 selected per pre-registered decision rule; k=2 is strong macrostructure, k=4 is weak substructure.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )
    return ModelSelectionResponse(
        production_variant=res["production_variant"],
        k_selected=res["k_selected"],
        kneedle_elbow=res["kneedle_elbow"],
        k2_silhouette=res["k2_silhouette"],
        k2_davies_bouldin=res["k2_davies_bouldin"],
        k4_silhouette=res["k4_silhouette"],
        k4_davies_bouldin=res["k4_davies_bouldin"],
        cophenetic_correlation=res["cophenetic_correlation"],
        kmeans_k_metrics=res["kmeans_k_metrics"],
        beta_calibration_grid=[BetaCalibrationPoint(**p) for p in res["beta_calibration_grid"]],
        metadata=metadata,
    )


@router.get(
    "/api/v1/model/compare",
    response_model=ModelCompareResponse,
    summary="Multi-Variant Benchmark Comparison Table (Models A, B1-B4)",
)
async def get_model_compare() -> ModelCompareResponse:
    """Compare candidate model variants (Model A, B1, B2, B3, B4) on silhouette, Davies-Bouldin, and stability."""
    res = model_service.get_model_compare_response()
    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=True,
        untested_assumptions_notice="All variants evaluated under identical random seed and pre-registered metric battery.",
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )
    return ModelCompareResponse(
        evaluated_variants=[ModelVariantBenchmarkItem(**v) for v in res["evaluated_variants"]],
        justification_summary=res["justification_summary"],
        metadata=metadata,
    )


@router.get(
    "/api/v1/governance/data-quality",
    response_model=DataQualitySummaryResponse,
    summary="Data Quality Audit & Lineage Report",
)
async def get_data_quality_report() -> DataQualitySummaryResponse:
    """Retrieve data quality metrics, lineage, missing values, and empirical sensitivity audits."""
    dq_path = api_settings.interim_dir / "data_quality_report.json"
    with open(dq_path, encoding="utf-8") as f:
        report = json.load(f)

    emp = report.get("empirical_tests", {})
    dob = emp.get("dob_sensitivity", {})

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=False,
        untested_assumptions_notice=(
            "Integer age computed at configured reference date 2025-12-31 is invariant to DD/MM date ambiguity (0 age switches). "
            "Satisfaction score marginal distribution is consistent with discrete uniform (chi2=1.990, p=0.7376)."
        ),
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return DataQualitySummaryResponse(
        raw_clients_count=report["datasets"]["clients"]["raw_rows"],
        raw_properties_count=report["datasets"]["properties"]["raw_rows"],
        clean_sold_transactions=report["datasets"]["properties"]["sold_units"],
        clean_current_inventory=report["datasets"]["properties"]["available_units"],
        towers_count=report["datasets"]["properties"]["towers_count"],
        reference_date=api_settings.reference_date_str,
        dob_sensitivity_age_switches=dob.get("age_band_switch_count", 0),
        satisfaction_chi2=1.990,
        satisfaction_uniform_p=0.7376,
        datasets=report["datasets"],
        metadata=metadata,
    )


@router.get(
    "/api/v1/governance/model-card",
    response_model=ModelCardResponse,
    summary="Model Card: Benchmarks, Stability, and PRD Truth Matrix",
)
async def get_model_card() -> ModelCardResponse:
    """Retrieve production model card benchmarks, cluster stability, and PRD hypothesis verification."""
    prd_matrix = [
        PRDHypothesisVerdictItem(
            prd_cluster="C1",
            prd_hypothesis_name="Global Investors",
            prd_stated_features="Country: international, purpose: investment, high spend",
            data_reality_finding=(
                "Domestic USA buyers (n=1,538) spend 3.34% more on average than international buyers (n=462) "
                "(₹12,69,852.05 vs ₹12,28,827.94; two-sample Welch's t=2.2443, p=0.0251, Cohen's d=0.1181). "
                "Investment purpose share is virtually identical between US (30.56%, 470/1538) and "
                "international (31.39%, 145/462) buyers (chi2=0.1139, p=0.7358, dof=1)."
            ),
            empirical_verdict="NOT SUPPORTED",
            statistical_test_evidence="Two-sample Welch's t = 2.2443 (p=0.0251), Cohen's d = 0.1181; chi2 = 0.1139 (p=0.7358, dof=1)",
        ),
        PRDHypothesisVerdictItem(
            prd_cluster="C2",
            prd_hypothesis_name="First-Time Buyers",
            prd_stated_features="Single unit, starter homes, low budget, high loan dependence",
            data_reality_finding=(
                "No client has < 3 units in the dataset (cohort range 3-11 units, mean 4.05; 100% multi-unit buyers). "
                "Mortgage financing rate is ~36.8% across the cohort. Zero single-unit entry-level buyers exist."
            ),
            empirical_verdict="NOT SUPPORTED",
            statistical_test_evidence="Minimum units = 3 (100% multi-unit); Single-unit buyers = 0 (0.0%)",
        ),
        PRDHypothesisVerdictItem(
            prd_cluster="C3",
            prd_hypothesis_name="Corporate Buyers",
            prd_stated_features="Institutional company structure, bulk commercial portfolio holdings",
            data_reality_finding=(
                "Corporate clients represent only 5.15% of all buyers (103 out of 2,000). Mean units purchased is "
                "virtually indistinguishable between companies and individuals (mean 3.6990 vs 3.6500, "
                "One-way ANOVA F(1, 1998) = 0.3333, p = 0.5638; two-sample t(1998) = -0.5773, p = 0.5638). "
                "Corporate status does not form an isolated segment."
            ),
            empirical_verdict="NOT SUPPORTED",
            statistical_test_evidence="Company share = 5.15% (103/2000 clients); One-way ANOVA F(1, 1998) = 0.3333 (p=0.5638)",
        ),
        PRDHypothesisVerdictItem(
            prd_cluster="C4",
            prd_hypothesis_name="Luxury Investors",
            prd_stated_features="Top price/sqft, maximum luxury spend, elite customer satisfaction",
            data_reality_finding=(
                "Q3 spend threshold is ₹14,41,974 and Q3 price/sqft is ₹313.04. Only 72 clients (3.60% of cohort) "
                "jointly meet Q3 spend, Q3 price/sqft, and satisfaction >= 4. Unit prices are largely uniform across "
                "the entire portfolio (mean ₹3,45,072, narrow std dev)."
            ),
            empirical_verdict="NOT SUPPORTED",
            statistical_test_evidence="Joint Q3 luxury overlap = 3.60% (72/2000 clients); Q3 spend = ₹14,41,974, Q3 price/sqft = ₹313.04",
        ),
    ]

    beta_grid = model_service.get_beta_calibration_grid()

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=True,
        untested_assumptions_notice=(
            "Model B3 downweights geographic one-hot features by 0.5x; k=2 is the strong mathematical split "
            "(silhouette=0.5072) produced by the quantile-transform gap; k=4 is weak substructure (silhouette=0.1211 < 0.25); "
            "all 4 PRD hypothesis clusters are empirically not supported."
        ),
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return ModelCardResponse(
        production_variant="Model_B3_Downweighted_Geo",
        k_selected=4,
        k2_silhouette=0.5072,
        k2_davies_bouldin=0.8066,
        k4_silhouette=0.1211,
        k4_davies_bouldin=2.6079,
        cophenetic_correlation=0.9066,
        bootstrap_stability_mean_ari=0.7730,
        sensitivity_ari_without_all_proxies=0.2013,
        beta_calibration_grid=[BetaCalibrationPoint(**p) for p in beta_grid],
        prd_truth_matrix=prd_matrix,
        metadata=metadata,
    )
