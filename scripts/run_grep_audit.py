import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

repo_root = Path("e:/parcl-buyer-intelligence")

INCLUDED_EXTS = {".html", ".json", ".md", ".py", ".toml", ".yaml", ".yml"}
EXCLUDED_DIRS = {
    ".git",
    ".hypothesis",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "venv",
}

HISTORY_FILES = {
    "walkthrough_phase_1.md",
    "walkthrough_phase_2.md",
    "walkthrough_phase_3.md",
    "phase_3_amendment.md",
    "walkthrough_phase_4.md",
    "walkthrough_phase_5.md",
    "walkthrough_phase_5_amendment.md",
    "walkthrough_phase_5_amendment_2.md",
    "task_list.md",
}

TARGET_STRINGS = [
    "$",
    "X-User-Role",
    "Access-Control-Allow-Origin: *",
    "calibrat",
    "0.738",
    "USD",
    "High-Frequency Speculators",
    "Single-Market Families",
    "High-Income Luxury Seekers",
    "Arjun",
    "demographics explain",
    "25.51",
    "~20%",
]

print("=== GREP AUDIT CONFIGURATION ===")
print(f"Root: {repo_root}")
print(f"Included Extensions: {sorted(INCLUDED_EXTS)}")
print(f"Excluded Directories: {sorted(EXCLUDED_DIRS)}")

results_code = {s: [] for s in TARGET_STRINGS}
results_history = {s: [] for s in TARGET_STRINGS}

for root, dirs, files in os.walk(repo_root):
    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
    for file in files:
        file_path = Path(root) / file
        if file_path.suffix.lower() not in INCLUDED_EXTS:
            continue

        rel_path = str(file_path.relative_to(repo_root))
        is_history = file_path.name in HISTORY_FILES

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            for target in TARGET_STRINGS:
                if target in line:
                    entry = (rel_path, idx, line.strip())
                    if is_history:
                        results_history[target].append(entry)
                    else:
                        results_code[target].append(entry)

print("\n=== ACTIVE CODEBASE & CURRENT ARTIFACT AUDIT HITS ===")
for target in TARGET_STRINGS:
    hits = results_code[target]
    print(f"\nTarget '{target}': {len(hits)} hits in active codebase")
    file_map = {}
    for path, line_no, text in hits:
        file_map.setdefault(path, []).append((line_no, text))
    for path, occurrences in file_map.items():
        line_nums = [ln for ln, _ in occurrences]
        print(f"  - {path}: lines {line_nums}")
        if len(occurrences) <= 3:
            for ln, t in occurrences:
                print(f"      L{ln}: {t[:100]}")

print("\n=== WALKTHROUGH & TASK-LIST HISTORY ARTIFACT AUDIT HITS ===")
for target in TARGET_STRINGS:
    hits = results_history[target]
    print(f"Target '{target}': {len(hits)} hits in historical artifacts")
    file_map = {}
    for path, line_no, text in hits:
        file_map.setdefault(path, []).append((line_no, text))
    for path, occurrences in file_map.items():
        line_nums = [ln for ln, _ in occurrences]
        print(f"  - {path}: lines {line_nums}")
