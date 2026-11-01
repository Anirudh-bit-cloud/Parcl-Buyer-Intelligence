"""Generate live sample payloads for documentation and golden-response testing."""

import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from apps.api.auth import create_access_token
from apps.api.main import app


def generate_all_samples() -> None:
    """Invoke all API endpoints and write formatted JSON responses to docs/samples/."""
    client = TestClient(app)
    out_dir = Path("e:/parcl-buyer-intelligence/docs/samples")
    out_dir.mkdir(parents=True, exist_ok=True)

    admin_token = create_access_token(subject="admin-demo", role="admin")
    analyst_token = create_access_token(subject="analyst-demo", role="analyst")
    auth_admin = {"Authorization": f"Bearer {admin_token}"}
    auth_analyst = {"Authorization": f"Bearer {analyst_token}"}

    endpoints_to_sample = [
        ("health", "/api/v1/health", "GET", None, {}),
        ("meta_filters", "/api/v1/meta/filters", "GET", None, {}),
        ("overview", "/api/v1/overview", "GET", None, auth_analyst),
        ("clients_analyst_masked", "/api/v1/clients?page=1&page_size=5", "GET", None, auth_analyst),
        ("clients_admin_unmasked", "/api/v1/clients?page=1&page_size=5", "GET", None, auth_admin),
        ("client_detail_c0001", "/api/v1/clients/C0001", "GET", None, auth_admin),
        ("segments_catalog", "/api/v1/segments", "GET", None, auth_analyst),
        ("segment_detail_cluster_2", "/api/v1/segments/2", "GET", None, auth_analyst),
        ("behavior", "/api/v1/behavior", "GET", None, auth_analyst),
        ("geo", "/api/v1/geo", "GET", None, auth_analyst),
        ("towers", "/api/v1/towers", "GET", None, auth_analyst),
        ("opportunities_segment_2_office", "/api/v1/recommendations/opportunities?segment_id=2&category_filter=Office&limit=5", "GET", None, auth_analyst),
        ("nbo_c0001", "/api/v1/recommendations/nbo/C0001?top_n=5", "GET", None, auth_analyst),
        (
            "campaign_scenario",
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
            "predict_segment",
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
        ("model_selection", "/api/v1/model/selection", "GET", None, auth_analyst),
        ("model_compare", "/api/v1/model/compare", "GET", None, auth_analyst),
        ("data_quality", "/api/v1/governance/data-quality", "GET", None, auth_analyst),
        ("model_card", "/api/v1/governance/model-card", "GET", None, auth_analyst),
        ("projection", "/api/v1/projection", "GET", None, auth_analyst),
        ("export", "/api/v1/export?country=USA&assigned_cluster=0", "GET", None, auth_admin),
    ]

    for name, path, method, body, headers in endpoints_to_sample:
        if method == "GET":
            res = client.get(path, headers=headers)
        else:
            res = client.post(path, json=body, headers=headers)

        if res.status_code != 200:
            msg = f"Failed to sample {name} ({path}): {res.status_code} {res.text}"
            raise RuntimeError(msg)

        data = res.json()
        target_file = out_dir / f"{name}.json"
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Generated {target_file.name} ({len(res.content)} bytes)")


if __name__ == "__main__":
    generate_all_samples()
