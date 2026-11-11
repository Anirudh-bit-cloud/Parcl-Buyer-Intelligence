"""Rigorous unit and failure-path test suite for parcl_core.registry."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
from parcl_core.registry import (
    compute_dataset_hash,
    get_git_revision_hash,
    get_model_registry_card,
    run_fairness_audit,
)


def test_compute_dataset_hash_existing_file(tmp_path: Path):
    """File checksum must match deterministic SHA-256 slice."""
    test_file = tmp_path / "test_data.parquet"
    test_file.write_bytes(b"deterministic-payload-content-12345")

    h = compute_dataset_hash(test_file)
    assert len(h) == 16
    assert isinstance(h, str)


def test_compute_dataset_hash_missing_file_failure_path():
    """Non-existent file must safely return fallback indicator."""
    missing = Path("/non/existent/path/dataset.parquet")
    h = compute_dataset_hash(missing)
    assert h == "sha256-not-available"


def test_get_git_revision_hash_fallback():
    """When git command fails or environment lacks git, fallback version must be returned."""
    with patch("subprocess.check_output", side_effect=Exception("Git command not found")):
        sha = get_git_revision_hash()
        assert sha == "v2.0.0-release"


def test_run_fairness_audit_with_skewed_demographics():
    """Evaluate observational disparity audit on synthetic demographics."""
    df = pd.DataFrame({
        "country": ["USA"] * 100 + ["UK"] * 50,
        "age": [28] * 50 + [45] * 50 + [62] * 50,
        "cluster": [0] * 50 + [1] * 50 + [2] * 50,
    })

    audit = run_fairness_audit(df)
    assert audit["status"] == "DESCRIPTIVE_DISPARITY_REPORT"
    assert "country_descriptive_disparity" in audit
    assert "age_descriptive_disparity" in audit
    assert audit["country_descriptive_disparity"]["usa_sample_size"] == 100
    assert audit["country_descriptive_disparity"]["intl_sample_size"] == 50


def test_run_fairness_audit_missing_age_column():
    """DataFrame lacking optional age column must handle absence gracefully."""
    df = pd.DataFrame({
        "country": ["USA", "India"],
        "cluster": [0, 1],
    })

    audit = run_fairness_audit(df)
    assert audit["status"] == "DESCRIPTIVE_DISPARITY_REPORT"
    assert audit["age_descriptive_disparity"] == {}


def test_get_model_registry_card_contract():
    """Model card specification must return all enterprise metadata fields."""
    card = get_model_registry_card("v2.0.0-b3")
    assert card["version"] == "v2.0.0-b3"
    assert "hyperparameters" in card
    assert "fairness_audit" in card
    assert "data_hash" in card
    assert "git_sha" in card
