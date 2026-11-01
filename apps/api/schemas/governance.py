"""Pydantic v2 schemas for governance, data quality, model card, and beta calibration."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ResponseMetadata


class BetaCalibrationPoint(BaseModel):
    """Grid point in centroid-softmax temperature beta grid."""

    model_config = ConfigDict(extra="ignore")

    beta: float = Field(examples=[1.12])
    mean_agreement_log_likelihood: float = Field(
        default=-0.6021,
        description="Out-of-fold agreement log-likelihood with production partition.",
        examples=[-0.6021],
    )
    mean_log_likelihood: float = Field(
        default=-0.6021,
        description="Alias for mean_agreement_log_likelihood.",
        examples=[-0.6021],
    )
    ambiguity_pct: float = Field(description="Percentage of clients with max probability < 0.50.", examples=[0.55])
    is_chosen: bool = Field(examples=[True])

    def __init__(self, **data: Any) -> None:
        if "mean_agreement_log_likelihood" in data and "mean_log_likelihood" not in data:
            data["mean_log_likelihood"] = data["mean_agreement_log_likelihood"]
        elif "mean_log_likelihood" in data and "mean_agreement_log_likelihood" not in data:
            data["mean_agreement_log_likelihood"] = data["mean_log_likelihood"]
        super().__init__(**data)


class DataQualitySummaryResponse(BaseModel):
    """Lineage, missing values, DOB sensitivity, and satisfaction uniformity audit."""

    model_config = ConfigDict(extra="ignore")

    raw_clients_count: int = Field(examples=[2000])
    raw_properties_count: int = Field(examples=[10000])
    clean_sold_transactions: int = Field(examples=[7305])
    clean_current_inventory: int = Field(examples=[313])
    towers_count: int = Field(examples=[20])
    reference_date: str = Field(examples=["2025-12-31"])
    dob_sensitivity_age_switches: int = Field(examples=[0])
    satisfaction_chi2: float = Field(examples=[1.990])
    satisfaction_uniform_p: float = Field(examples=[0.7376])
    datasets: dict[str, Any]
    metadata: ResponseMetadata


class PRDHypothesisVerdictItem(BaseModel):
    """PRD Hypothesis validation record grounded in empirical Phase 3 findings."""

    model_config = ConfigDict(extra="ignore")

    prd_cluster: str = Field(examples=["C1"])
    prd_hypothesis_name: str = Field(examples=["Global Investors"])
    prd_stated_features: str = Field(examples=["Country: international, purpose: investment, high spend"])
    data_reality_finding: str = Field(
        examples=["Domestic USA buyers spend 3.34% more on average than international buyers (₹12,73,500 vs ₹12,32,374)."]
    )
    empirical_verdict: str = Field(examples=["NOT SUPPORTED"])
    statistical_test_evidence: str = Field(
        examples=["Two-sample t = 2.2253 (p=0.0262), Cohen's d = 0.1181; chi2 = 0.1120 (p=0.7379)"]
    )


class ModelCardResponse(BaseModel):
    """Authoritative model selection benchmarks, stability ARI, beta grid, and PRD hypothesis matrix."""

    model_config = ConfigDict(extra="ignore")

    production_variant: str = Field(examples=["Model_B3_Downweighted_Geo"])
    k_selected: int = Field(examples=[4])
    k2_silhouette: float = Field(examples=[0.5072])
    k2_davies_bouldin: float = Field(examples=[0.8066])
    k4_silhouette: float = Field(examples=[0.1211])
    k4_davies_bouldin: float = Field(examples=[2.6079])
    cophenetic_correlation: float = Field(examples=[0.9066])
    bootstrap_stability_mean_ari: float = Field(examples=[0.7730])
    sensitivity_ari_without_all_proxies: float = Field(examples=[0.2013])
    beta_calibration_grid: list[BetaCalibrationPoint]
    prd_truth_matrix: list[PRDHypothesisVerdictItem]
    metadata: ResponseMetadata
