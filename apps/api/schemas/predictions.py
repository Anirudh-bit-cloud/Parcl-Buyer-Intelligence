"""Pydantic v2 schemas for segment prediction and portfolio feature requirements."""

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ResponseMetadata


class SegmentPredictionRequest(BaseModel):
    """Predictive inference payload requiring behavioral portfolio attributes.

    PORTFOLIO REQUIREMENT NOTICE:
    Model B3 operates on behavioral portfolio features (unit volume, commercial share,
    tower diversification, purchase timeline). Portfolio inputs are strictly required
    because the production model was trained on them.
    """

    model_config = ConfigDict(extra="ignore")

    age: int = Field(ge=18, le=120, description="Completed age in years.", examples=[45])
    n_units: int = Field(ge=1, le=50, description="Total units acquired in portfolio.", examples=[3])
    office_share: float = Field(ge=0.0, le=1.0, description="Commercial office proportion [0..1].", examples=[0.33])
    avg_floor_area: float = Field(gt=100.0, description="Average unit size in sqft.", examples=[1150.0])
    portfolio_towers_hhi: float = Field(
        ge=0.0, le=1.0, description="Tower concentration Herfindahl-Hirschman Index.", examples=[0.3333]
    )
    purchase_span_months: int = Field(ge=0, description="Months elapsed between first and latest purchase.", examples=[6])
    loan_applied: bool = Field(description="Mortgage financing flag.", examples=[True])
    client_type: str = Field(description="INDIVIDUAL or COMPANY.", examples=["INDIVIDUAL"])
    acquisition_purpose: str = Field(description="HOME or INVESTMENT.", examples=["INVESTMENT"])
    referral_channel: str = Field(description="Website, Agency, or Client.", examples=["Website"])
    country: str = Field(default="USA", description="Country of origin.", examples=["USA"])
    region: str = Field(default="California", description="State or administrative region.", examples=["California"])


class SegmentPredictionResponse(BaseModel):
    """Inference output with assigned segment and calibrated soft membership probabilities."""

    model_config = ConfigDict(extra="ignore")

    predicted_segment_id: int = Field(examples=[2])
    predicted_segment_name: str = Field(examples=["Commercial Office Allocators"])
    calibrated_soft_probabilities: dict[str, float] = Field(
        examples=[{"Cluster_0": 0.0058, "Cluster_1": 0.34, "Cluster_2": 0.6509, "Cluster_3": 0.0033}]
    )
    temperature_beta: float = Field(default=1.0, examples=[1.0])
    is_ambiguous_prediction: bool = Field(
        description="True if max soft probability < 0.50 (absence of strict majority).",
        examples=[False],
    )
    is_ambiguous_margin: bool = Field(
        default=False,
        description="True if top-2 softmax probability margin (p_1 - p_2) < 0.10.",
        examples=[False],
    )
    portfolio_requirement_rationale: str = Field(
        default=(
            "Model B3 requires portfolio inputs (n_units, office_share, tower HHI, purchase_span_months) "
            "because the underlying clustering model was trained on these behavioral and portfolio architecture features."
        )
    )
    metadata: ResponseMetadata
