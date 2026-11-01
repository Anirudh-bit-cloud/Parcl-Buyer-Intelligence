"""Data ingestion module for loading and validating raw CSV files."""

import logging
from pathlib import Path

import pandas as pd
import pandera.errors

from parcl_core.config import settings
from parcl_core.schemas import RawClientsSchema, RawPropertiesSchema, validate_dataframe

logger = logging.getLogger(__name__)


def load_raw_clients(path: Path | None = None) -> pd.DataFrame:
    """Load raw clients.csv and validate against RawClientsSchema.

    Args:
        path: Optional path to clients.csv. If None, uses settings.clients_raw_path.

    Returns:
        Validated raw pd.DataFrame.

    Raises:
        FileNotFoundError: If the raw file does not exist.
        pandera.errors.SchemaErrors: If schema validation fails.
    """
    target_path = path or settings.clients_raw_path
    if not target_path.exists():
        raise FileNotFoundError(f"Raw clients file not found at: {target_path}")

    logger.info("Loading raw clients from: %s", target_path)
    df = pd.read_csv(target_path)

    try:
        validated_df = validate_dataframe(df, RawClientsSchema)
        logger.info("Raw clients successfully validated. Row count: %d", len(validated_df))
        return validated_df
    except pandera.errors.SchemaErrors as exc:
        logger.error("Schema validation failed for clients: %s", exc.failure_cases)
        raise


def load_raw_properties(path: Path | None = None) -> pd.DataFrame:
    """Load raw properties.csv and validate against RawPropertiesSchema.

    Args:
        path: Optional path to properties.csv. If None, uses settings.properties_raw_path.

    Returns:
        Validated raw pd.DataFrame.

    Raises:
        FileNotFoundError: If the raw file does not exist.
        pandera.errors.SchemaErrors: If schema validation fails.
    """
    target_path = path or settings.properties_raw_path
    if not target_path.exists():
        raise FileNotFoundError(f"Raw properties file not found at: {target_path}")

    logger.info("Loading raw properties from: %s", target_path)
    df = pd.read_csv(target_path)

    try:
        validated_df = validate_dataframe(df, RawPropertiesSchema)
        logger.info("Raw properties successfully validated. Row count: %d", len(validated_df))
        return validated_df
    except pandera.errors.SchemaErrors as exc:
        logger.error("Schema validation failed for properties: %s", exc.failure_cases)
        raise
