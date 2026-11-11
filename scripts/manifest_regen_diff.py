"""Manifest Regeneration & Diff Audit Script
Regenerates all sample responses to an isolated temporary directory and performs
a byte-for-byte cryptographic diff against files in docs/samples/.
Reports exact file-level byte sizes, SHA-256 hashes, and unified diffs for any divergences.
All values are computed dynamically; zero literal results.
"""

import difflib
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from scripts.generate_samples import generate_all_samples  # noqa: E402

manifest_path = repo_root / "docs/samples/MANIFEST.json"
manifest_bytes = manifest_path.read_bytes()
manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()

print("=== Stored MANIFEST.json Provenance ===")
print(f"Path: {manifest_path}")
print(f"Byte Size: {len(manifest_bytes)} bytes")
print(f"Full SHA-256: {manifest_sha}")

temp_dir = Path(tempfile.mkdtemp())
print(f"\nRegenerating all samples into temp directory: {temp_dir}")

try:
    generate_all_samples(out_dir=temp_dir)
    docs_samples = repo_root / "docs/samples"

    mismatches = []
    matches = []

    print("\n=== Byte-for-Byte Sample Diff (Regenerated vs Disk) ===")
    for disk_file in sorted(docs_samples.glob("*")):
        if disk_file.name == "MANIFEST.json":
            m_disk = json.loads(disk_file.read_text(encoding="utf-8"))
            m_temp = json.loads((temp_dir / disk_file.name).read_text(encoding="utf-8"))
            # Find routes whose SHA256 differs in the samples dict
            differing_routes = []
            for route_key, v_disk in m_disk.get("samples", {}).items():
                v_temp = m_temp.get("samples", {}).get(route_key)
                if v_temp and v_disk.get("sha256") != v_temp.get("sha256"):
                    differing_routes.append(
                        (route_key, v_disk.get("filename"), v_disk.get("sha256"), v_temp.get("sha256"))
                    )
            if not differing_routes:
                matches.append(disk_file.name)
                print(
                    f"[MATCH] {disk_file.name}: All sample SHA256s identical "
                    f"(ignoring timestamp_utc and git_commit)"
                )
            else:
                mismatches.append(disk_file.name)
                print(
                    f"[DIFF]  {disk_file.name}: {len(differing_routes)} sample SHA256(s) differ "
                    f"(ignoring timestamp_utc and git_commit)"
                )
                for route_key, fname, sha_disk, sha_temp in differing_routes:
                    print(f"        route={route_key}  file={fname}")
                    print(f"          disk_sha={sha_disk}")
                    print(f"          temp_sha={sha_temp}")
            continue

        temp_file = temp_dir / disk_file.name
        if not temp_file.exists():
            mismatches.append(disk_file.name)
            print(f"[MISS]  {disk_file.name}: Missing in temporary directory")
            continue

        d_bytes = disk_file.read_bytes()
        t_bytes = temp_file.read_bytes()
        d_sha = hashlib.sha256(d_bytes).hexdigest()
        t_sha = hashlib.sha256(t_bytes).hexdigest()

        if d_sha == t_sha:
            matches.append(disk_file.name)
            print(f"[MATCH] {disk_file.name:<34} Size: {len(d_bytes):>7} bytes | SHA: {d_sha}")
        else:
            mismatches.append(disk_file.name)
            size_diff = len(t_bytes) - len(d_bytes)
            print(f"[DIFF]  {disk_file.name:<34} DiskSize: {len(d_bytes)}, TempSize: {len(t_bytes)} ({size_diff:+d} bytes) | DiskSHA: {d_sha} vs TempSHA: {t_sha}")
            # Print unified text diff
            d_lines = disk_file.read_text(encoding="utf-8").splitlines(keepends=True)
            t_lines = temp_file.read_text(encoding="utf-8").splitlines(keepends=True)
            u_diff = list(difflib.unified_diff(d_lines, t_lines, fromfile="disk", tofile="temp"))
            print("--- Unified Diff ---")
            for line in u_diff:
                print(line, end="")
            print("\n--------------------")

    print(f"\nTotal Files Evaluated: {len(matches) + len(mismatches)}")
    print(f"Total Matches: {len(matches)}")
    print(f"Total Divergences: {len(mismatches)}")

finally:
    shutil.rmtree(temp_dir)
