"""Pydantic v2 schemas for unsupervised model selection and multi-variant comparison."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ResponseMetadata
from apps.api.schemas.governance import BetaCalibrationPoint


class ModelVariantBenchmarkItem(BaseModel):
    """Candidate model specification and benchmark scores at k=4."""

    model_config = ConfigDict(extra="ignore")

    variant_name: str = Field(examples=["Model_B3_Downweighted_Geo"])
    feature_dimensions: int = Field(examples=[84])
    silhouette_k4: float = Field(examples=[0.1211])
    davies_bouldin_k4: float = Field(examples=[2.6079])
    calinski_harabasz_k4: float = Field(examples=[1177.13])
    stability_mean_ari: float = Field(examples=[0.7730])
    is_production_choice: bool = Field(examples=[True])
    selection_verdict: str = Field(examples=["SELECTED PRODUCTION MODEL"])


class ModelSelectionResponse(BaseModel):
    """Optimal k selection battery, elbow metrics, and beta calibration grid."""

    model_config = ConfigDict(extra="ignore")

    production_variant: str = Field(examples=["Model_B3_Downweighted_Geo"])
    k_selected: int = Field(examples=[4])
    kneedle_elbow: int = Field(examples=[5])
    k2_silhouette: float = Field(examples=[0.5072])
    k2_davies_bouldin: float = Field(examples=[0.8066])
    k4_silhouette: float = Field(examples=[0.1211])
    k4_davies_bouldin: float = Field(examples=[2.6079])
    cophenetic_correlation: float = Field(examples=[0.9066])
    kmeans_k_metrics: list[dict[str, Any]]
    beta_calibration_grid: list[BetaCalibrationPoint]
    metadata: ResponseMetadata


class ModelCompareResponse(BaseModel):
    """Cross-variant benchmark comparison table across Model A and Models B1-B4."""

    model_config = ConfigDict(extra="ignore")

    evaluated_variants: list[ModelVariantBenchmarkItem]
    justification_summary: str = Field(
        examples=[
            "Model B3 downweights geographic features by 0.5x, achieving stable separation (DB=2.6079, ARI=0.7730) "
            "without allowing 84 sparse spatial one-hot columns to overpower behavioral features."
        ]
    )
    metadata: ResponseMetadata
