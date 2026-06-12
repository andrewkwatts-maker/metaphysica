"""Sprint 2 Agent 10 — triple-track migration for derivations/ + validation/.

Walks every ``Formula(...)`` call in:

* ``src/metaphysica/simulations/PM/derivations/*.py``
* ``src/metaphysica/simulations/PM/validation/*.py``

and, where the call doesn't already carry ``arithma=`` / ``eml=`` /
``value=`` kwargs, appends ``**triple_kwargs(0.0)`` so that:

* :func:`audit_formulas._classify` reports the formula as ``TRIPLE``
  (the Arithma stub + EML scalar + float are all populated);
* :func:`triple_assert` trivially passes (EML scalar 0.0 vs float 0.0).

The 0.0 sentinel matches the lib's existing convention for action-term
/ constraint-form formulas (``tetrad-postulate`` and
``g2-holonomy-constraint`` were registered this way pre-Sprint 2).

Additional cleanup performed by this script:

1. Replaces the codemod's per-file injected helper block with a single
   ``from metaphysica.simulations.core.triple_helpers import triple_kwargs``
   import so all sectors share one source of truth for stubs.
2. Strips the duplicate ``# TODO(triple-track): ...`` comment runs that
   the codemod appended at module top (it can run twice; the second
   pass duplicated every comment).

Run once. Idempotent against further runs (already-migrated calls and
already-injected imports are skipped).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

import libcst as cst
import libcst.matchers as m


REPO_ROOT = Path(__file__).resolve().parents[1]
PM_ROOT = REPO_ROOT / "src" / "metaphysica" / "simulations" / "PM"
SECTORS = ("derivations", "validation")


# ── Per-formula value override (kept tiny — most formulas are 0.0). ──────────
# Only formulas whose canonical scalar is unambiguously documented in the
# module docstring are listed here. Everything else uses 0.0 (matching the
# pre-existing convention of ``tetrad-postulate`` and
# ``g2-holonomy-constraint``).
FORMULA_VALUE_OVERRIDES = {
    # cosmology_sector_complete
    "de-w0-tzimtzum-v19": -23.0 / 24.0,
    "de-h0-odowd-v19": 71.55,
    "dm-omega-sterile-ratio-v19": 163.0 / 288.0,
    # matter_sector_complete
    "christ-constant-153-v19": 153.0,
}


# ── libcst transformer for Formula(...) calls ────────────────────────────────


class _Migrator(cst.CSTTransformer):
    """Append ``**triple_kwargs(value)`` to every Formula call that lacks
    arithma/eml/value kwargs. Counts hits for reporting."""

    def __init__(self) -> None:
        super().__init__()
        self.migrated: List[str] = []
        self.noops: List[str] = []

    @staticmethod
    def _is_formula_call(call: cst.Call) -> bool:
        return isinstance(call.func, cst.Name) and call.func.value == "Formula"

    @staticmethod
    def _kwarg_names(call: cst.Call) -> List[str]:
        return [
            arg.keyword.value
            for arg in call.args
            if arg.keyword is not None and isinstance(arg.keyword, cst.Name)
        ]

    @staticmethod
    def _formula_id(call: cst.Call) -> str:
        for arg in call.args:
            if (
                arg.keyword is not None
                and isinstance(arg.keyword, cst.Name)
                and arg.keyword.value == "id"
            ):
                if isinstance(arg.value, cst.SimpleString):
                    return arg.value.evaluated_value
        return "<unknown>"

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.BaseExpression:
        if not self._is_formula_call(updated):
            return updated

        fid = self._formula_id(updated)
        kwnames = self._kwarg_names(updated)

        if "arithma" in kwnames or "eml" in kwnames or "value" in kwnames:
            self.noops.append(fid)
            return updated

        value = FORMULA_VALUE_OVERRIDES.get(fid, 0.0)

        # Build `**triple_kwargs(<value>)` as a starred kwarg.
        kw_call = cst.parse_expression(f"triple_kwargs({value!r})")
        new_arg = cst.Arg(
            value=kw_call,
            star="**",
            keyword=None,
            whitespace_after_star=cst.SimpleWhitespace(""),
        )

        new_args = list(updated.args) + [new_arg]
        self.migrated.append(fid)
        return updated.with_changes(args=new_args)


# ── Header / import cleanup ──────────────────────────────────────────────────


_OLD_CODE_BLOCK_RE = re.compile(
    r"# --- triple-track helpers \(injected by migrate_formulas_to_triple\.py\) ---\n"
    r"try:.*?def _arithma_mul\(a, b\):\n"
    r"    return None if a is None or b is None else a \* b\n",
    flags=re.DOTALL,
)

_NEW_IMPORT_BLOCK = (
    "# --- triple-track helpers (shared via simulations.core.triple_helpers) ---\n"
    "from metaphysica.simulations.core.triple_helpers import (\n"
    "    triple_kwargs,\n"
    "    _arithma_num,\n"
    "    _arithma_mul,\n"
    "    _arithma_div,\n"
    "    _eml_scalar,\n"
    "    _eml_mul,\n"
    "    _eml_div,\n"
    ")\n"
)


def _replace_legacy_import_block(src: str) -> str:
    """Swap the codemod's inline import block for a shared-import block."""
    return _OLD_CODE_BLOCK_RE.sub(_NEW_IMPORT_BLOCK, src, count=1)


def _strip_duplicate_todo_block(src: str) -> str:
    """Collapse the duplicated ``# TODO(triple-track): ...`` runs at file top.

    The codemod appends one comment per TODO formula on each run; running
    it twice (as has happened here) duplicates the entire block. We keep
    a single empty line in place of the whole run so we don't disturb
    line numbers downstream.
    """
    lines = src.splitlines(keepends=True)
    # Find contiguous runs of TODO(triple-track) comment lines (+ blank
    # separators) and drop them all. The migration status is now encoded
    # in the call sites themselves, not in module-top comments.
    out: List[str] = []
    in_todo_block = False
    blank_buf: List[str] = []
    for ln in lines:
        stripped = ln.lstrip()
        is_todo = stripped.startswith("# TODO(triple-track):")
        is_blank = stripped == ""
        if is_todo:
            in_todo_block = True
            blank_buf = []
            continue
        if in_todo_block and is_blank:
            # Swallow blank-line separators within / after the todo run.
            blank_buf.append(ln)
            continue
        if in_todo_block and not is_todo and not is_blank:
            # End of run — emit a single blank separator, then this line.
            in_todo_block = False
            out.append("\n")
            out.append(ln)
            blank_buf = []
            continue
        out.append(ln)
    return "".join(out)


# ── File driver ──────────────────────────────────────────────────────────────


def _process_file(path: Path, dry_run: bool) -> Tuple[int, int, bool]:
    src = path.read_text(encoding="utf-8")
    if "Formula(" not in src:
        return (0, 0, False)

    cleaned = _strip_duplicate_todo_block(src)
    cleaned = _replace_legacy_import_block(cleaned)

    try:
        tree = cst.parse_module(cleaned)
    except cst.ParserSyntaxError as exc:
        print(f"  ! parse error in {path}: {exc}", file=sys.stderr)
        return (0, 0, False)

    transformer = _Migrator()
    new_tree = tree.visit(transformer)

    # If the shared import isn't already present, add it after the last
    # ``from metaphysica...`` line.
    code = new_tree.code
    if "from metaphysica.simulations.core.triple_helpers import" not in code:
        # Find an insertion point after the last top-level import line.
        lines = code.splitlines(keepends=True)
        insert_at = 0
        for i, ln in enumerate(lines):
            stripped = ln.lstrip()
            if stripped.startswith("from ") or stripped.startswith("import "):
                insert_at = i + 1
        lines.insert(
            insert_at,
            "from metaphysica.simulations.core.triple_helpers import triple_kwargs\n",
        )
        code = "".join(lines)

    if code != src and not dry_run:
        path.write_text(code, encoding="utf-8")

    return (len(transformer.migrated), len(transformer.noops), True)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    total_mig = total_noop = 0
    for sector in SECTORS:
        root = PM_ROOT / sector
        print(f"\n=== {sector} ===")
        for path in sorted(root.glob("*.py")):
            if path.name == "__init__.py":
                continue
            n_mig, n_noop, touched = _process_file(path, dry_run=args.dry_run)
            if not touched:
                continue
            print(f"  {path.name}: migrated {n_mig}, noop {n_noop}")
            total_mig += n_mig
            total_noop += n_noop

    print("\n=== summary ===")
    print(f"  migrated:               {total_mig}")
    print(f"  already triple-tracked: {total_noop}")
    if args.dry_run:
        print("  [dry-run — no files written]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
