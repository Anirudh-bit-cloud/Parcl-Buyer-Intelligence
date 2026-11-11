from pathlib import Path

test_file = Path("apps/api/tests/test_invariants.py")
text = test_file.read_text(encoding="utf-8")

old_block = '''    surrogate_rules = " ".join(metrics.get("surrogate_rules", []))'''
new_block = '''    surrogate_rules = str(metrics.get("surrogate_rules", ""))'''

if old_block in text:
    text = text.replace(old_block, new_block)
    test_file.write_text(text, encoding="utf-8")
    print("Fixed surrogate_rules extraction in test_invariants.py")
else:
    print("old_block not found")
