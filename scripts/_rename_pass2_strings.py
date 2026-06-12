"""Pass 2: strip `_v16_2` / `_v17_2` suffixes from string literals in PM modules.

Targets string literals only (libcst SimpleString). Does NOT touch docstring
prose or comments. The codemod walks the same set of source files as pass 1
plus the known cross-reference in `base/sections.py`.

Rationale: registry IDs like `id="abstract_v17_2"` should match the new class
name `Abstract`; consumers of those IDs (sections.py, certificates.py) must be
updated together to avoid breaking lookups.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import libcst as cst

LIB_ROOT = Path(r"H:\Github\metaphysica\src\metaphysica")
PM_ROOT = LIB_ROOT / "simulations" / "PM"

# Strip _v16_2 or _v17_2 anywhere in a string-literal payload. The pattern is
# specific enough (digits + underscore version) that false positives are
# unlikely. We deliberately do NOT touch `_v16_0`, `_v16_1` etc — those are
# out of scope for this rename.
STRIP_RE = re.compile(r"(_v16_2|_v17_2)\b")


class StringStripper(cst.CSTTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.changes = 0

    def leave_SimpleString(self, original: cst.SimpleString, updated: cst.SimpleString) -> cst.SimpleString:
        raw = updated.value  # includes quotes
        new_raw = STRIP_RE.sub("", raw)
        if new_raw != raw:
            self.changes += 1
            return updated.with_changes(value=new_raw)
        return updated

    def leave_FormattedStringText(
        self, original: cst.FormattedStringText, updated: cst.FormattedStringText
    ) -> cst.FormattedStringText:
        # Cover f-strings' literal text portions.
        raw = updated.value
        new_raw = STRIP_RE.sub("", raw)
        if new_raw != raw:
            self.changes += 1
            return updated.with_changes(value=new_raw)
        return updated


def iter_targets() -> list[Path]:
    targets = sorted(PM_ROOT.rglob("*.py"))
    extras = [
        LIB_ROOT / "simulations" / "base" / "sections.py",
    ]
    for p in extras:
        if p.exists() and p not in targets:
            targets.append(p)
    return targets


def main() -> int:
    files_changed = 0
    total_changes = 0
    failures: list[tuple[Path, str]] = []
    for path in iter_targets():
        src = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = cst.parse_module(src)
        except cst.ParserSyntaxError as exc:
            failures.append((path, f"parse error: {exc}"))
            continue
        transformer = StringStripper()
        new_tree = tree.visit(transformer)
        if transformer.changes:
            path.write_text(new_tree.code, encoding="utf-8")
            files_changed += 1
            total_changes += transformer.changes
            print(f"  {transformer.changes:4d}  {path.relative_to(LIB_ROOT)}")

    print(f"\nPass 2 done: {files_changed} files modified, {total_changes} string-literal updates.")
    if failures:
        print("\nFailures:")
        for p, msg in failures:
            print(f"  {p}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
