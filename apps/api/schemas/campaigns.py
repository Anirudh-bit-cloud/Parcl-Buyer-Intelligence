"""Pydantic v2 schemas for the Grounded Marketing Scenario Calculator."""

from pydantic import BaseModel, ConfigDict, Field

from apps.api.schemas.common import ActiveFilters, ResponseMetadata


class ScenarioRequest(BaseModel):
    """Marketing capital allocation scenario request."""

    model_config = ConfigDict(extra="ignore")

    total_budget_inr: float = Field(
        default=100000.0,
        gt=0,
        description="Total marketing capital allocated across channels (₹).",
        examples=[100000.0],
    )
    channel_allocations: dict[str, float] = Field(
        default={"Website": 0.50, "Agency": 0.35, "Client": 0.15},
        description="Budget proportion per referral channel (must sum to 1.0).",
        examples=[{"Website": 0.50, "Agency": 0.35, "Client": 0.15}],
    )
    channel_cpas_inr: dict[str, float] = Field(
        default={"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
        description="Illustrative user-provided Cost-Per-Acquisition targets per channel (₹).",
        examples=[{"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0}],
    )


class HistoricalChannelMetrics(BaseModel):
    """Empirical channel benchmarks from microdata."""

    model_config = ConfigDict(extra="ignore")

    historical_client_count: int = Field(examples=[1103])
    historical_share: float = Field(examples=[0.5515])
    historical_mean_sales_per_client_inr: float = Field(examples=[1274770.93])
    historical_mean_sales_display: str = Field(examples=["₹12,74,771"])
    historical_median_sales_per_client_inr: float = Field(examples=[1238162.97])
    historical_median_sales_display: str = Field(examples=["₹12,38,163"])
    mean_units: float = Field(examples=[3.68])
    loan_rate: float = Field(examples=[0.3663])


class ChannelScenarioResult(BaseModel):
    """Channel-level modeled acquisition metrics."""

    model_config = ConfigDict(extra="ignore")

    channel_name: str = Field(examples=["Website"])
    allocated_budget_inr: float = Field(examples=[50000.0])
    allocated_budget_display: str = Field(examples=["₹50,000"])
    budget_share: float = Field(examples=[0.50])
    illustrative_cpa_inr: float = Field(examples=[1200.0])
    illustrative_cpa_display: str = Field(examples=["₹1,200"])
    modeled_clients_acquired: float = Field(examples=[41.67])
    modeled_gross_sales_volume_inr: float = Field(
        description="Modeled gross sales volume (GMV) in INR, NOT profit.",
        examples=[53115455.42],
    )
    modeled_gross_sales_display: str = Field(examples=["₹5,31,15,455"])
    historical_channel_metrics: HistoricalChannelMetrics


class ChannelIndependenceFinding(BaseModel):
    """Statistical verification that channels do not exhibit segment targeting viability."""

    model_config = ConfigDict(extra="ignore")

    spend_difference_pct: float = Field(default=2.83, examples=[2.83])
    spend_anova_f: float = Field(default=2.1176, examples=[2.1176])
    spend_anova_p: float = Field(default=0.1206, examples=[0.1206])
    segment_mix_chi2: float = Field(default=0.7500, examples=[0.7500])
    segment_mix_p: float = Field(default=0.9933, examples=[0.9933])
    segment_mix_dof: int = Field(default=6, examples=[6])
    conclusion: str = Field(
        examples=[
            "The empirical data DOES NOT SUPPORT segment-specific channel targeting. "
            "Segment mix across channels is statistically indistinguishable (chi2=0.7500, p=0.9933)."
        ]
    )


class ScenarioResponse(BaseModel):
    """Complete modeled marketing scenario output with all channels returned."""

    model_config = ConfigDict(extra="ignore")

    calculator_type: str = Field(
        default="Marketing Scenario Calculator (Illustrative)",
        examples=["Marketing Scenario Calculator (Illustrative)"],
    )
    total_budget_inr: float = Field(examples=[100000.0])
    total_budget_display: str = Field(examples=["₹1,00,000"])
    total_modeled_clients: float = Field(examples=[60.0])
    total_modeled_gross_sales_volume_inr: float = Field(
        description="Modeled gross sales volume (GMV) in INR, NOT net profit.",
        examples=[75881028.0],
    )
    total_modeled_gross_sales_display: str = Field(examples=["₹7,58,81,028"])
    revenue_label_notice: str = Field(
        examples=[
            "Figures reflect modeled gross sales volume (GMV) in INR (₹), NOT net profit. "
            "Assumes every acquired client buys at historical average sales, with no conversion funnel or attribution."
        ]
    )
    channel_targeting_empirical_finding: ChannelIndependenceFinding
    channel_breakdown: dict[str, ChannelScenarioResult]
    active_filters: ActiveFilters
    metadata: ResponseMetadata



class ScenarioCompareRequest(BaseModel):
    """Payload to compare two distinct marketing budget allocation scenarios."""

    model_config = ConfigDict(extra="ignore")

    scenario_a: ScenarioRequest
    scenario_b: ScenarioRequest


class ScenarioCompareResponse(BaseModel):
    """Side-by-side comparison of two scenarios with differential ROI."""

    model_config = ConfigDict(extra="ignore")

    scenario_a: ScenarioResponse
    scenario_b: ScenarioResponse
    budget_delta_inr: float
    clients_delta: float
    sales_delta_inr: float
    incremental_roi: float
