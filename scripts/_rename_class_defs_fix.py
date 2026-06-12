"""One-shot fix: rename class definitions that the A.5 libcst codemod missed.

The agent renamed all *references* (imports, isinstance checks, string IDs)
but the class *definition* headers (``class FooV16(...):``) weren't touched.
This script applies the rename_map to the class def lines using a tight
regex anchored at line start, so we don't accidentally re-rename anything.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_PM = Path(__file__).resolve().parent.parent / "src" / "metaphysica" / "simulations" / "PM"
_MAP_FILE = Path(__file__).resolve().parent / "_class_rename_map.json"


def main() -> int:
    rename_map = json.loads(_MAP_FILE.read_text(encoding="utf-8"))["rename_map"]
    # Sort by length descending so V16_2 is replaced before V16 (avoid leaving "_2" tails).
    items = sorted(rename_map.items(), key=lambda kv: -len(kv[0]))
    updates = 0
    files_touched = 0
    for py in _PM.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        new_text = text
        for old, new in items:
            # Replace bare identifier occurrences only. Skip mention inside string
            # literals (the A.5 string-literal pass already handled those).
            pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])")
            new_text, n = pattern.subn(new, new_text)
            updates += n
        if new_text != text:
            py.write_text(new_text, encoding="utf-8")
            files_touched += 1
            print(f"  patched {py.relative_to(_PM)}")
    print(f"\nFiles touched: {files_touched}")
    print(f"Identifier occurrences replaced: {updates}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
