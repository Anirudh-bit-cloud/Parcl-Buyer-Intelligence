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


def generate_all_samples(out_dir: Path | None = None) -> Path:
    """Invoke all API route endpoints and write formatted responses + MANIFEST.json to docs/samples/."""
    client = TestClient(app)
    if out_dir is None:
        out_dir = Path("docs/samples")
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
        "avg_floor_area": 1129.18,
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
    # (sample_id, manifest_key, url_path, http_method, payload, headers, is_canonical, format_type)
    sample_definitions = [
        ("root", "/", "/", "GET", None, {}, True, "json"),
        ("api_v1", "/api/v1", "/api/v1", "GET", None, {}, True, "json"),
        ("health", "/api/v1/health", "/api/v1/health", "GET", None, {}, True, "json"),
        ("meta_filters", "/api/v1/meta/filters", "/api/v1/meta/filters", "GET", None, {}, True, "json"),
        ("overview", "/api/v1/overview", "/api/v1/overview", "GET", None, auth_analyst, True, "json"),
        ("clients", "/api/v1/clients", "/api/v1/clients?page=1&page_size=5", "GET", None, auth_analyst, True, "json"),
        ("client_detail_c0001", "/api/v1/clients/C0001", "/api/v1/clients/C0001", "GET", None, auth_admin, True, "json"),
        ("segments_catalog", "/api/v1/segments", "/api/v1/segments", "GET", None, auth_analyst, True, "json"),
        ("segment_detail_cluster_2", "/api/v1/segments/2", "/api/v1/segments/2", "GET", None, auth_analyst, True, "json"),
        ("behavior", "/api/v1/behavior", "/api/v1/behavior", "GET", None, auth_analyst, True, "json"),
        ("geo", "/api/v1/geo", "/api/v1/geo", "GET", None, auth_analyst, True, "json"),
        ("towers", "/api/v1/towers", "/api/v1/towers", "GET", None, auth_analyst, True, "json"),
        (
            "opportunities_segment_2_office",
            "/api/v1/recommendations/opportunities",
            "/api/v1/recommendations/opportunities?segment_id=2&category_filter=Office&limit=5",
            "GET",
            None,
            auth_analyst,
            True,
            "json",
        ),
        (
            "nbo_c0001",
            "/api/v1/recommendations/nbo/C0001",
            "/api/v1/recommendations/nbo/C0001?top_n=5",
            "GET",
            None,
            auth_analyst,
            True,
            "json",
        ),
        ("campaign_scenario", "/api/v1/campaigns/scenario", "/api/v1/campaigns/scenario", "POST", scenario_payload, auth_analyst, True, "json"),
        ("campaign_allocate", "/api/v1/campaigns/allocate", "/api/v1/campaigns/allocate", "POST", scenario_payload, auth_analyst, True, "json"),
        ("campaign_simulate", "/api/v1/campaigns/simulate", "/api/v1/campaigns/simulate", "POST", scenario_payload, auth_analyst, True, "json"),
        ("predict_segment", "/api/v1/predict/segment", "/api/v1/predict/segment", "POST", predict_payload, auth_analyst, True, "json"),
        ("model_selection", "/api/v1/model/selection", "/api/v1/model/selection", "GET", None, auth_analyst, True, "json"),
        ("model_compare", "/api/v1/model/compare", "/api/v1/model/compare", "GET", None, auth_analyst, True, "json"),
        ("data_quality", "/api/v1/governance/data-quality", "/api/v1/governance/data-quality", "GET", None, auth_analyst, True, "json"),
        ("model_card", "/api/v1/governance/model-card", "/api/v1/governance/model-card", "GET", None, auth_analyst, True, "json"),
        ("projection", "/api/v1/projection", "/api/v1/projection", "GET", None, auth_analyst, True, "json"),
        # Additional samples requested by user:
        (
            "clients_analyst_masked",
            "/api/v1/clients [analyst]",
            "/api/v1/clients?page=1&page_size=5",
            "GET",
            None,
            auth_analyst,
            False,
            "json",
        ),
        (
            "clients_admin_unmasked",
            "/api/v1/clients [admin]",
            "/api/v1/clients?page=1&page_size=5",
            "GET",
            None,
            auth_admin,
            False,
            "json",
        ),
        (
            "export",
            "/api/v1/export",
            "/api/v1/export?country=USA&assigned_cluster=0&format=csv",
            "GET",
            None,
            auth_admin,
            False,
            "csv",
        ),
        (
            "demo_token",
            "/api/v1/auth/demo-token",
            "/api/v1/auth/demo-token",
            "POST",
            {"role": "analyst"},
            {},
            False,
            "json_redacted_token",
        ),
    ]

    samples_manifest: dict[str, dict[str, Any]] = {}
    canonical_routes_list: list[dict[str, Any]] = []

    for name, route_key, path, method, body, headers, is_canonical, fmt in sample_definitions:
        if method == "GET":
            res = client.get(path, headers=headers)
        else:
            res = client.post(path, json=body, headers=headers)

        if res.status_code != 200:
            msg = f"Failed to sample {name} ({path}): {res.status_code} {res.text}"
            raise RuntimeError(msg)

        if fmt == "csv":
            target_file = out_dir / f"{name}.csv"
            content_bytes = res.text.encode("utf-8")
        elif fmt == "json_redacted_token":
            target_file = out_dir / f"{name}.json"
            data = res.json()
            data["access_token"] = "<REDACTED_DEMO_JWT_TOKEN>"
            content_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        else:
            target_file = out_dir / f"{name}.json"
            data = res.json()
            content_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

        target_file.write_bytes(content_bytes)
        file_sha256 = hashlib.sha256(content_bytes).hexdigest()

        rel_path = f"docs/samples/{target_file.name}"
        sample_info = {
            "route_key": route_key,
            "route_path": path,
            "http_method": method,
            "file_path": rel_path,
            "filename": target_file.name,
            "sha256": file_sha256,
            "byte_size": len(content_bytes),
            "is_canonical_23_route": is_canonical,
        }
        samples_manifest[route_key] = sample_info

        if is_canonical:
            canonical_routes_list.append({
                "index": len(canonical_routes_list) + 1,
                "name": name,
                "route_key": route_key,
                "route_path": path,
                "method": method,
                "file": target_file.name,
                "file_path": rel_path,
                "sha256": file_sha256,
                "byte_size": len(content_bytes),
            })

        print(f"Generated {target_file.name} ({len(content_bytes)} bytes, sha256: {file_sha256[:12]}...)")

    git_sha = get_git_commit()
    timestamp_iso = datetime.now(UTC).isoformat()

    manifest_payload = {
        "generator_command": "python scripts/generate_samples.py",
        "git_commit": git_sha,
        "timestamp_utc": timestamp_iso,
        "canonical_route_count": len(canonical_routes_list),
        "total_sample_files": len(sample_definitions),
        "canonical_23_routes": canonical_routes_list,
        "samples": samples_manifest,
    }

    manifest_path = out_dir / "MANIFEST.json"
    manifest_bytes = json.dumps(manifest_payload, indent=2, ensure_ascii=False).encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)
    print(f"\nManifest successfully written to {manifest_path} (git sha: {git_sha[:10]}, canonical routes: {len(canonical_routes_list)})")
    return out_dir


if __name__ == "__main__":
    generate_all_samples()
