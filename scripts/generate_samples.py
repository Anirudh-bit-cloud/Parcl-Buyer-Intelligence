"""Generate live sample payloads for documentation, MANIFEST.json, and golden-response testing."""

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from apps.api.auth import create_access_token
from apps.api.main import app


def get_git_commit() -> str:
    """Retrieve current git commit hash, or return fallback if not in git repo."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "git-commit-unavailable"


def generate_all_samples() -> None:
    """Invoke all 23 API route endpoints and write formatted JSON responses + MANIFEST.json to docs/samples/."""
    client = TestClient(app)
    out_dir = Path("e:/parcl-buyer-intelligence/docs/samples")
    out_dir.mkdir(parents=True, exist_ok=True)

    admin_token = create_access_token(subject="admin-demo", role="admin")
    analyst_token = create_access_token(subject="analyst-demo", role="analyst")
    auth_admin = {"Authorization": f"Bearer {admin_token}"}
    auth_analyst = {"Authorization": f"Bearer {analyst_token}"}

    scenario_payload = {
        "total_budget_inr": 100000.0,
        "channel_allocations": {"Website": 0.50, "Agency": 0.35, "Client": 0.15},
        "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
    }

    predict_payload = {
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
    }

    # 23 Canonical Routes Inventory
    routes_23 = [
        ("root", "/", "GET", None, {}),
        ("api_v1", "/api/v1", "GET", None, {}),
        ("health", "/api/v1/health", "GET", None, {}),
        ("meta_filters", "/api/v1/meta/filters", "GET", None, {}),
        ("overview", "/api/v1/overview", "GET", None, auth_analyst),
        ("clients", "/api/v1/clients?page=1&page_size=5", "GET", None, auth_analyst),
        ("client_detail_c0001", "/api/v1/clients/C0001", "GET", None, auth_admin),
        ("segments_catalog", "/api/v1/segments", "GET", None, auth_analyst),
        ("segment_detail_cluster_2", "/api/v1/segments/2", "GET", None, auth_analyst),
        ("behavior", "/api/v1/behavior", "GET", None, auth_analyst),
        ("geo", "/api/v1/geo", "GET", None, auth_analyst),
        ("towers", "/api/v1/towers", "GET", None, auth_analyst),
        (
            "opportunities_segment_2_office",
            "/api/v1/recommendations/opportunities?segment_id=2&category_filter=Office&limit=5",
            "GET",
            None,
            auth_analyst,
        ),
        ("nbo_c0001", "/api/v1/recommendations/nbo/C0001?top_n=5", "GET", None, auth_analyst),
        ("campaign_scenario", "/api/v1/campaigns/scenario", "POST", scenario_payload, auth_analyst),
        ("campaign_allocate", "/api/v1/campaigns/allocate", "POST", scenario_payload, auth_analyst),
        ("campaign_simulate", "/api/v1/campaigns/simulate", "POST", scenario_payload, auth_analyst),
        ("predict_segment", "/api/v1/predict/segment", "POST", predict_payload, auth_analyst),
        ("model_selection", "/api/v1/model/selection", "GET", None, auth_analyst),
        ("model_compare", "/api/v1/model/compare", "GET", None, auth_analyst),
        ("data_quality", "/api/v1/governance/data-quality", "GET", None, auth_analyst),
        ("model_card", "/api/v1/governance/model-card", "GET", None, auth_analyst),
        ("projection", "/api/v1/projection", "GET", None, auth_analyst),
    ]

    # Additional sample variants for comprehensive testing
    extra_samples = [
        ("clients_analyst_masked", "/api/v1/clients?page=1&page_size=5", "GET", None, auth_analyst),
        ("clients_admin_unmasked", "/api/v1/clients?page=1&page_size=5", "GET", None, auth_admin),
        ("export", "/api/v1/export?country=USA&assigned_cluster=0", "GET", None, auth_admin),
    ]

    all_to_generate = routes_23 + extra_samples
    samples_manifest: dict[str, dict[str, Any]] = {}

    for name, path, method, body, headers in all_to_generate:
        if method == "GET":
            res = client.get(path, headers=headers)
        else:
            res = client.post(path, json=body, headers=headers)

        if res.status_code != 200:
            msg = f"Failed to sample {name} ({path}): {res.status_code} {res.text}"
            raise RuntimeError(msg)

        data = res.json()
        target_file = out_dir / f"{name}.json"
        content_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        target_file.write_bytes(content_bytes)

        file_sha256 = hashlib.sha256(content_bytes).hexdigest()
        is_canonical_23 = any(r[0] == name for r in routes_23)

        sample_info = {
            "route_path": path,
            "http_method": method,
            "filename": f"{name}.json",
            "sha256": file_sha256,
            "byte_size": len(content_bytes),
            "is_canonical_23_route": is_canonical_23,
        }
        samples_manifest[name] = sample_info
        print(f"Generated {target_file.name} ({len(content_bytes)} bytes, sha256: {file_sha256[:12]}...)")

    git_sha = get_git_commit()
    timestamp_iso = datetime.now(UTC).isoformat()

    manifest_payload = {
        "generator_command": "python scripts/generate_samples.py",
        "git_commit": git_sha,
        "timestamp_utc": timestamp_iso,
        "canonical_route_count": len(routes_23),
        "total_sample_files": len(all_to_generate),
        "canonical_23_routes": [
            {
                "index": idx + 1,
                "name": name,
                "route": path,
                "method": method,
                "file": f"{name}.json",
                "sha256": samples_manifest[name]["sha256"],
            }
            for idx, (name, path, method, _, _) in enumerate(routes_23)
        ],
        "all_samples": samples_manifest,
    }

    manifest_path = out_dir / "MANIFEST.json"
    manifest_bytes = json.dumps(manifest_payload, indent=2, ensure_ascii=False).encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)
    print(f"\nManifest successfully written to {manifest_path} (git sha: {git_sha[:10]}, canonical routes: 23)")


if __name__ == "__main__":
    generate_all_samples()
