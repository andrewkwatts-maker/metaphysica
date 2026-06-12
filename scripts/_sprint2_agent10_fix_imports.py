"""Repair: relocate the misplaced ``triple_kwargs`` import to module top.

The first pass of ``_sprint2_agent10_migrate.py`` inserted the shared
``from metaphysica.simulations.core.triple_helpers import triple_kwargs``
line by scanning text-level imports, which incorrectly matched method-
body imports (e.g. ``from datetime import datetime`` inside
``get_gate_checks``) and even import statements inside an enclosing
``try:`` block. The result was a misplaced import that broke parsing.

This script:

1. Removes every stray ``from metaphysica.simulations.core.triple_helpers
   import triple_kwargs`` line in each target file.
2. Re-inserts a single import via libcst at the proper top-level
   position (after the last top-level import).
"""
from __future__ import annotations

from pathlib import Path
from typing import List

import libcst as cst


REPO_ROOT = Path(__file__).resolve().parents[1]
PM_ROOT = REPO_ROOT / "src" / "metaphysica" / "simulations" / "PM"
SECTORS = ("derivations", "validation")

IMPORT_LINE = "from metaphysica.simulations.core.triple_helpers import triple_kwargs\n"


def _strip_stray_imports(src: str) -> str:
    """Remove all occurrences of the misplaced import line (any indent)."""
    out: List[str] = []
    for ln in src.splitlines(keepends=True):
        if "from metaphysica.simulations.core.triple_helpers import triple_kwargs" in ln:
            continue
        out.append(ln)
    return "".join(out)


def _insert_top_level_import(src: str) -> str:
    """Insert the import once, after the last top-level import statement."""
    try:
        tree = cst.parse_module(src)
    except cst.ParserSyntaxError:
        # Parse failed — fall back to manual placement near the top.
        return IMPORT_LINE + src

    body = list(tree.body)
    last_import_idx = -1
    for i, stmt in enumerate(body):
        if isinstance(stmt, cst.SimpleStatementLine) and any(
            isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body
        ):
            last_import_idx = i

    new_import = cst.parse_statement(IMPORT_LINE.strip())
    if last_import_idx >= 0:
        body.insert(last_import_idx + 1, new_import)
    else:
        body.insert(0, new_import)

    return tree.with_changes(body=body).code


def _process(path: Path) -> bool:
    src = path.read_text(encoding="utf-8")
    if "triple_helpers" not in src and "triple_kwargs" not in src:
        return False
    stripped = _strip_stray_imports(src)
    fixed = _insert_top_level_import(stripped)
    if fixed != src:
        path.write_text(fixed, encoding="utf-8")
        return True
    return False


def main() -> int:
    touched = 0
    for sector in SECTORS:
        for path in sorted((PM_ROOT / sector).glob("*.py")):
            if path.name == "__init__.py":
                continue
            if _process(path):
                touched += 1
                print(f"  fixed {sector}/{path.name}")
    print(f"\ntotal files fixed: {touched}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
