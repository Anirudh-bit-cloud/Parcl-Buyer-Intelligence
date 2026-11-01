"""Configuration settings for Parcl Buyer Intelligence Platform."""

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientTypeEnum(StrEnum):
    """Canonical client type enumeration."""

    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"


class AcquisitionPurposeEnum(StrEnum):
    """Canonical acquisition purpose enumeration."""

    HOME = "HOME"
    INVESTMENT = "INVESTMENT"


class ReferralChannelEnum(StrEnum):
    """Empirical referral channels observed in data."""

    WEBSITE = "Website"
    AGENCY = "Agency"
    CLIENT = "Client"


class ListingStatusEnum(StrEnum):
    """Property listing status."""

    SOLD = "Sold"
    AVAILABLE = "Available"


class Settings(BaseSettings):
    """Global configuration settings."""

    model_config = SettingsConfigDict(env_prefix="PARCL_", env_file=".env", extra="ignore")

    # Project directories
    project_root: Path = Field(
        default_factory=lambda: Path("e:/parcl-buyer-intelligence").resolve()
    )
    raw_data_dir: Path = Field(
        default_factory=lambda: Path("e:/parcl-buyer-intelligence/data/raw").resolve()
    )
    interim_data_dir: Path = Field(
        default_factory=lambda: Path("e:/parcl-buyer-intelligence/data/interim").resolve()
    )
    processed_data_dir: Path = Field(
        default_factory=lambda: Path("e:/parcl-buyer-intelligence/data/processed").resolve()
    )
    models_dir: Path = Field(
        default_factory=lambda: Path("e:/parcl-buyer-intelligence/data/models").resolve()
    )

    # Raw file paths
    clients_raw_path: Path = Field(
        default_factory=lambda: Path("e:/parcl-buyer-intelligence/data/raw/clients.csv").resolve()
    )
    properties_raw_path: Path = Field(
        default_factory=lambda: Path(
            "e:/parcl-buyer-intelligence/data/raw/properties.csv"
        ).resolve()
    )

    # Processed file paths
    clients_clean_path: Path = Field(
        default_factory=lambda: Path(
            "e:/parcl-buyer-intelligence/data/processed/clients_clean.parquet"
        ).resolve()
    )
    transactions_clean_path: Path = Field(
        default_factory=lambda: Path(
            "e:/parcl-buyer-intelligence/data/processed/transactions_clean.parquet"
        ).resolve()
    )
    available_properties_path: Path = Field(
        default_factory=lambda: Path(
            "e:/parcl-buyer-intelligence/data/processed/available_properties.parquet"
        ).resolve()
    )
    client_features_path: Path = Field(
        default_factory=lambda: Path(
            "e:/parcl-buyer-intelligence/data/processed/client_features.parquet"
        ).resolve()
    )
    data_quality_report_json: Path = Field(
        default_factory=lambda: Path(
            "e:/parcl-buyer-intelligence/data/interim/data_quality_report.json"
        ).resolve()
    )
    data_quality_report_html: Path = Field(
        default_factory=lambda: Path(
            "e:/parcl-buyer-intelligence/data/interim/data_quality_report.html"
        ).resolve()
    )

    # Reproducibility & modeling parameters
    random_seed: int = 42
    n_init_kmeans: int = 50
    dob_dash_format: Literal["DD-MM-YYYY", "MM-DD-YYYY"] = "DD-MM-YYYY"
    min_k: int = 2
    max_k: int = 12
    bootstrap_iterations: int = 100
    weak_cluster_silhouette_threshold: float = 0.25

    # Display mappings for UI consistency with PRD
    client_type_display_map: dict[str, str] = {
        ClientTypeEnum.INDIVIDUAL.value: "Individual",
        ClientTypeEnum.COMPANY.value: "Corporate",
    }
    acquisition_purpose_display_map: dict[str, str] = {
        AcquisitionPurposeEnum.HOME.value: "Personal use",
        AcquisitionPurposeEnum.INVESTMENT.value: "Investment",
    }


settings = Settings()
