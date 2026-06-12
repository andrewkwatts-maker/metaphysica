"""Pass 1: rename class identifiers using libcst.

Reads `_class_rename_map.json` and rewrites every `Name` node whose .value
matches an old class name to the new name. Operates on Python files in:

  - src/metaphysica/simulations/PM/**/*.py
  - src/metaphysica/simulations/__init__.py
  - src/metaphysica/simulations/run_all_simulations.py
  - src/metaphysica/simulations/base/sections.py

NOTE: this pass touches identifiers only (class defs, bases, type hints,
isinstance, aliases). String literals are pass 2.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import libcst as cst

LIB_ROOT = Path(r"H:\Github\metaphysica\src\metaphysica")
PM_ROOT = LIB_ROOT / "simulations" / "PM"
MAP_PATH = Path(__file__).parent / "_class_rename_map.json"


class RenameTransformer(cst.CSTTransformer):
    def __init__(self, rename_map: dict[str, str]) -> None:
        super().__init__()
        self.rename_map = rename_map
        self.changes = 0

    def leave_Name(self, original: cst.Name, updated: cst.Name) -> cst.Name:
        new = self.rename_map.get(updated.value)
        if new is not None and new != updated.value:
            self.changes += 1
            return updated.with_changes(value=new)
        return updated


def iter_targets() -> list[Path]:
    targets: list[Path] = sorted(PM_ROOT.rglob("*.py"))
    extra = [
        LIB_ROOT / "simulations" / "__init__.py",
        LIB_ROOT / "simulations" / "run_all_simulations.py",
        LIB_ROOT / "simulations" / "base" / "sections.py",
    ]
    for p in extra:
        if p.exists() and p not in targets:
            targets.append(p)
    return targets


def main() -> int:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    rename_map: dict[str, str] = data["rename_map"]

    files_changed = 0
    total_changes = 0
    failures: list[tuple[Path, str]] = []

    for path in iter_targets():
        try:
            src = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            src = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = cst.parse_module(src)
        except cst.ParserSyntaxError as exc:
            failures.append((path, f"parse error: {exc}"))
            continue
        transformer = RenameTransformer(rename_map)
        new_tree = tree.visit(transformer)
        if transformer.changes:
            path.write_text(new_tree.code, encoding="utf-8")
            files_changed += 1
            total_changes += transformer.changes
            print(f"  {transformer.changes:4d} change(s)  {path.relative_to(LIB_ROOT)}")

    print(f"\nPass 1 done: {files_changed} files modified, {total_changes} identifier renames.")
    if failures:
        print("\nFailures:")
        for p, msg in failures:
            print(f"  {p}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
