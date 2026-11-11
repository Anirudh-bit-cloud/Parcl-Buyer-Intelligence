"""Tests for ingestion and end-to-end pipeline execution."""

from pathlib import Path

import pytest
from parcl_core.cleaning import (
    evaluate_dob_sensitivity,
)
from parcl_core.ingest import load_raw_clients, load_raw_properties
from parcl_core.pipeline import run_phase_1


def test_load_raw_datasets() -> None:
    """Test raw dataset loaders return valid DataFrames with expected counts."""
    clients = load_raw_clients()
    properties = load_raw_properties()
    assert len(clients) == 2000
    assert len(properties) == 10000


def test_load_raw_file_not_found(tmp_path: Path) -> None:
    """Test FileNotFoundError is raised when raw file path does not exist."""
    fake_path = tmp_path / "non_existent.csv"
    with pytest.raises(FileNotFoundError):
        load_raw_clients(fake_path)
    with pytest.raises(FileNotFoundError):
        load_raw_properties(fake_path)


def test_evaluate_dob_sensitivity() -> None:
    """Test DOB sensitivity calculation on raw clients."""
    clients = load_raw_clients()
    res = evaluate_dob_sensitivity(clients)
    assert res["total_clients"] == 2000
    assert res["slash_format_count"] == 1145
    assert res["dash_format_count"] == 855
    assert res["exact_same_date_count"] == 65
    assert 0.30 <= res["mean_fractional_age_diff_years"] <= 0.35
    assert 0.85 <= res["max_fractional_age_diff_years"] <= 0.90


def test_run_phase_1_execution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test end-to-end Phase 1 execution produces all expected artifacts in temp dir."""
    from parcl_core.config import settings

    monkeypatch.setattr(settings, "interim_data_dir", tmp_path / "interim")
    monkeypatch.setattr(settings, "processed_data_dir", tmp_path / "processed")
    outputs = run_phase_1()
    for _key, file_path in outputs.items():
        assert Path(file_path).exists(), f"Output file missing: {file_path}"


def test_run_phase_2_execution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test end-to-end Phase 2 execution produces features and bivariate outputs in temp dir."""
    from parcl_core.config import settings
    from parcl_core.pipeline import run_phase_2

    monkeypatch.setattr(settings, "processed_data_dir", tmp_path / "processed")
    outputs = run_phase_2()
    for _key, file_path in outputs.items():
        assert Path(file_path).exists(), f"Output file missing: {file_path}"
