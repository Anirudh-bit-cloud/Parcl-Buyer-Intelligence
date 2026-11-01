"""Golden-response regression tests asserting live endpoint outputs match stored samples."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.auth import create_access_token


def assert_deep_matches(actual: Any, expected: Any, tol: float = 1e-4) -> None:
    """Recursively assert actual matches expected with float tolerance."""
    if isinstance(actual, dict) and isinstance(expected, dict):
        assert set(actual.keys()) == set(expected.keys())
        for k in actual:
            assert_deep_matches(actual[k], expected[k], tol)
    elif isinstance(actual, list) and isinstance(expected, list):
        assert len(actual) == len(expected)
        for a, e in zip(actual, expected, strict=True):
            assert_deep_matches(a, e, tol)
    elif isinstance(actual, (float, int)) and isinstance(expected, (float, int)):
        assert actual == pytest.approx(expected, rel=tol, abs=tol)
    else:
        assert actual == expected


def test_golden_samples_consistency(client: TestClient) -> None:
    """Verify live endpoint responses equal stored JSON golden samples in docs/samples/."""
    samples_dir = Path("e:/parcl-buyer-intelligence/docs/samples")
    assert samples_dir.exists(), "docs/samples directory does not exist"

    admin_token = create_access_token(subject="admin-demo", role="admin")
    analyst_token = create_access_token(subject="analyst-demo", role="analyst")
    auth_admin = {"Authorization": f"Bearer {admin_token}"}
    auth_analyst = {"Authorization": f"Bearer {analyst_token}"}

    cases = [
        ("health.json", "/api/v1/health", "GET", None, {}),
        ("meta_filters.json", "/api/v1/meta/filters", "GET", None, {}),
        ("overview.json", "/api/v1/overview", "GET", None, auth_analyst),
        ("clients_analyst_masked.json", "/api/v1/clients?page=1&page_size=5", "GET", None, auth_analyst),
        ("clients_admin_unmasked.json", "/api/v1/clients?page=1&page_size=5", "GET", None, auth_admin),
        ("client_detail_c0001.json", "/api/v1/clients/C0001", "GET", None, auth_admin),
        ("segments_catalog.json", "/api/v1/segments", "GET", None, auth_analyst),
        ("segment_detail_cluster_2.json", "/api/v1/segments/2", "GET", None, auth_analyst),
        ("behavior.json", "/api/v1/behavior", "GET", None, auth_analyst),
        ("geo.json", "/api/v1/geo", "GET", None, auth_analyst),
        ("towers.json", "/api/v1/towers", "GET", None, auth_analyst),
        ("opportunities_segment_2_office.json", "/api/v1/recommendations/opportunities?segment_id=2&category_filter=Office&limit=5", "GET", None, auth_analyst),
        ("nbo_c0001.json", "/api/v1/recommendations/nbo/C0001?top_n=5", "GET", None, auth_analyst),
        (
            "campaign_scenario.json",
            "/api/v1/campaigns/scenario",
            "POST",
            {
                "total_budget_inr": 100000.0,
                "channel_allocations": {"Website": 0.50, "Agency": 0.35, "Client": 0.15},
                "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
            },
            auth_analyst,
        ),
        (
            "predict_segment.json",
            "/api/v1/predict/segment",
            "POST",
            {
                "age": 45,
                "n_units": 3,
                "office_share": 0.33,
                "avg_floor_area": 1150.0,
                "portfolio_towers_hhi": 0.3333,
                "purchase_span_months": 6,
                "loan_applied": True,
                "client_type": "INDIVIDUAL",
                "acquisition_purpose": "INVESTMENT",
                "referral_channel": "Website",
                "country": "USA",
                "region": "California",
            },
            auth_analyst,
        ),
        ("model_selection.json", "/api/v1/model/selection", "GET", None, auth_analyst),
        ("model_compare.json", "/api/v1/model/compare", "GET", None, auth_analyst),
        ("data_quality.json", "/api/v1/governance/data-quality", "GET", None, auth_analyst),
        ("model_card.json", "/api/v1/governance/model-card", "GET", None, auth_analyst),
        ("projection.json", "/api/v1/projection", "GET", None, auth_analyst),
        ("export.json", "/api/v1/export?country=USA&assigned_cluster=0", "GET", None, auth_admin),
    ]

    for filename, path, method, body, headers in cases:
        file_path = samples_dir / filename
        assert file_path.exists(), f"Golden sample {filename} missing"
        with open(file_path, encoding="utf-8") as f:
            expected = json.load(f)

        if method == "GET":
            res = client.get(path, headers=headers)
        else:
            res = client.post(path, json=body, headers=headers)

        assert res.status_code == 200, f"Error calling {path}: {res.text}"
        actual = res.json()

        assert_deep_matches(actual, expected)
