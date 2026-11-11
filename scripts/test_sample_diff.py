"""Test byte-for-byte reproducibility of regenerated samples against disk."""

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

repo_root = Path("e:/parcl-buyer-intelligence")
sys.path.insert(0, str(repo_root))

from scripts.generate_samples import generate_all_samples  # noqa: E402

docs_samples = repo_root / "docs/samples"
temp_dir = Path(tempfile.mkdtemp())
print(f"Regenerating all samples into temp directory: {temp_dir}\n")

try:
    generate_all_samples(out_dir=temp_dir)

    mismatches = []
    files_checked = 0

    print("\n" + "=" * 80)
    print("BYTE-FOR-BYTE DIFF: REGENERATED SAMPLES VS DISK SAMPLES")
    print("=" * 80)

    for disk_file in sorted(docs_samples.glob("*")):
        if disk_file.name == "MANIFEST.json":
            m_disk = json.loads(disk_file.read_text(encoding="utf-8"))
            m_temp = json.loads((temp_dir / disk_file.name).read_text(encoding="utf-8"))
            m_disk_copy = dict(m_disk)
            m_temp_copy = dict(m_temp)
            m_disk_copy.pop("timestamp_utc", None)
            m_temp_copy.pop("timestamp_utc", None)
            if m_disk_copy == m_temp_copy:
                print(f"  [MATCH] {disk_file.name} (identical canonical & samples structure, git sha, route count)")
            else:
                mismatches.append(f"{disk_file.name}: payload mismatch")
            continue

        temp_file = temp_dir / disk_file.name
        if not temp_file.exists():
            mismatches.append(f"{disk_file.name}: Missing in regenerated output")
            continue

        disk_bytes = disk_file.read_bytes()
        temp_bytes = temp_file.read_bytes()
        disk_sha = hashlib.sha256(disk_bytes).hexdigest()
        temp_sha = hashlib.sha256(temp_bytes).hexdigest()

        files_checked += 1
        if disk_sha == temp_sha:
            print(f"  [MATCH] {disk_file.name:<32} {len(disk_bytes):>7} bytes  sha256: {disk_sha[:16]}... (0 byte diff)")
        else:
            mismatches.append(f"{disk_file.name}: SHA mismatch (disk={disk_sha[:16]}, temp={temp_sha[:16]})")

    print(f"\nTotal sample files checked: {files_checked}")
    print(f"Total discrepancies: {len(mismatches)}")
    if mismatches:
        for m in mismatches:
            print("  - Discrepancy:", m)
    else:
        print("RESULT: 100% BYTE-FOR-BYTE REPRODUCIBLE IDENTICAL SAMPLES (ZERO DIFF).")

finally:
    shutil.rmtree(temp_dir)
