"""Scan repository text files for prohibited or stale strings."""

from pathlib import Path

PROHIBITED = [
    "$",
    "USD",
    "X-User-Role",
    "Access-Control-Allow-Origin: *",
    "High-Frequency Speculators",
    "Single-Market Families",
    "High-Income Luxury Seekers",
    "Arjun",
    "demographics explain",
    "25.51",
    "0.738",
    "~20%",
    "1.2.",
]

EXTENSIONS = {".py", ".md", ".json", ".txt", ".toml", ".yml", ".yaml"}
EXCLUDE_DIRS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", ".venv", "venv", ".hypothesis"}

root = Path("e:/parcl-buyer-intelligence")

results = {p: [] for p in PROHIBITED}

for file_path in root.rglob("*"):
    if file_path.is_file() and file_path.suffix in EXTENSIONS:
        if any(part in EXCLUDE_DIRS for part in file_path.parts):
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for term in PROHIBITED:
                if term in content:
                    lines = [i + 1 for i, line in enumerate(content.splitlines()) if term in line]
                    results[term].append((file_path.relative_to(root), lines))
        except Exception:
            pass

print("=== STALE CLAIM AUDIT REPORT ===")
for term, matches in results.items():
    print(f"\nPattern: '{term}' -> {len(matches)} files found")
    for fpath, lnums in matches:
        print(f"  {fpath}: lines {lnums[:10]}")
