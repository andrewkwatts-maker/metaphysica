"""One-shot codemod: migrate Formula(...) constructors to triple-track.

Walks every ``.py`` under ``src/metaphysica/simulations/PM/`` and, for each
``Formula(...)`` constructor it finds, decides whether to:

* **migrate (simple)** — automatically add ``arithma=``, ``eml=`` and ``value=``
  keyword arguments. Only triggered for trivially recognizable formulas:
  bare numeric literal, ``a/b``, ``a*b``, or ``a \\cdot b`` of pure decimal
  literals in the ``latex`` field.
* **TODO (complex)** — leave the call untouched and prepend a one-line
  comment ``# TODO(triple-track): build arithma + eml trees for {id}``.
* **no-op (already triple-tracked)** — skip entirely when ``arithma=`` or
  ``eml=`` keyword arguments are already present.

The codemod is **not** idempotent — run once, review the diff, commit, and
run ``pytest tests/ -x --no-cov`` to catch regressions.

Usage:
    python scripts/migrate_formulas_to_triple.py

Optional flags:
    --dry-run   Print summary without writing files.
    --root DIR  Override the PM source root.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import libcst as cst
import libcst.matchers as m


PM_ROOT = Path(__file__).resolve().parents[1] / "src" / "metaphysica" / "simulations" / "PM"


# ── Simple-formula recognizer ────────────────────────────────────────────────

_NUM = r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"
_LIT_RE = re.compile(rf"^\s*({_NUM})\s*$")
_DIV_RE = re.compile(rf"^\s*({_NUM})\s*/\s*({_NUM})\s*$")
_MUL_RE = re.compile(rf"^\s*({_NUM})\s*[*·]\s*({_NUM})\s*$")
_CDOT_RE = re.compile(rf"^\s*({_NUM})\s*\\cdot\s*({_NUM})\s*$")
_TIMES_RE = re.compile(rf"^\s*({_NUM})\s*\\times\s*({_NUM})\s*$")


@dataclass(frozen=True)
class SimpleShape:
    kind: str  # "lit" | "div" | "mul"
    a: float
    b: Optional[float] = None  # None for "lit"

    def value(self) -> float:
        if self.kind == "lit":
            return self.a
        if self.kind == "div":
            return self.a / self.b  # type: ignore[operator]
        if self.kind == "mul":
            return self.a * self.b  # type: ignore[operator]
        raise ValueError(self.kind)


def _extract_str(node: cst.BaseExpression) -> Optional[str]:
    """Return the literal string of a SimpleString / ConcatenatedString node, or None."""
    if isinstance(node, cst.SimpleString):
        # Strip quotes + optional r/R prefix.
        return node.evaluated_value
    if isinstance(node, cst.ConcatenatedString):
        try:
            return node.evaluated_value
        except Exception:
            return None
    return None


def _recognize_simple(latex: str) -> Optional[SimpleShape]:
    """Match common simple-arithmetic LaTeX strings."""
    if latex is None:
        return None
    s = latex.strip()
    # Drop a leading "X = " if present (e.g. "N_A = 0.5").
    if "=" in s:
        s = s.split("=", 1)[1].strip()
    # Strip braces.
    s = s.replace("{", "").replace("}", "")

    if (m1 := _LIT_RE.match(s)):
        return SimpleShape("lit", float(m1.group(1)))
    if (m2 := _DIV_RE.match(s)):
        return SimpleShape("div", float(m2.group(1)), float(m2.group(2)))
    if (m3 := _MUL_RE.match(s)):
        return SimpleShape("mul", float(m3.group(1)), float(m3.group(2)))
    if (m4 := _CDOT_RE.match(s)):
        return SimpleShape("mul", float(m4.group(1)), float(m4.group(2)))
    if (m5 := _TIMES_RE.match(s)):
        return SimpleShape("mul", float(m5.group(1)), float(m5.group(2)))
    return None


# ── libcst transformer ───────────────────────────────────────────────────────

class FormulaCallTransformer(cst.CSTTransformer):
    """Visit each ``Formula(...)`` call and triple-track it where possible."""

    def __init__(self) -> None:
        super().__init__()
        self.migrated: List[str] = []
        self.todos: List[str] = []
        self.noops: List[str] = []
        self.skipped: List[str] = []
        self.needs_arithma_import = False
        self.needs_eml_import = False

    def _kwarg_names(self, call: cst.Call) -> List[str]:
        names: List[str] = []
        for arg in call.args:
            if arg.keyword is not None and isinstance(arg.keyword, cst.Name):
                names.append(arg.keyword.value)
        return names

    def _get_kwarg(self, call: cst.Call, name: str) -> Optional[cst.Arg]:
        for arg in call.args:
            if arg.keyword is not None and isinstance(arg.keyword, cst.Name):
                if arg.keyword.value == name:
                    return arg
        return None

    def _get_id(self, call: cst.Call) -> str:
        a = self._get_kwarg(call, "id")
        if a is not None:
            v = _extract_str(a.value)
            if v:
                return v
        return "<unknown>"

    def _get_latex(self, call: cst.Call) -> Optional[str]:
        a = self._get_kwarg(call, "latex")
        if a is not None:
            return _extract_str(a.value)
        return None

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.BaseExpression:
        # Only rewrite calls whose callee is the name `Formula`.
        if not (isinstance(updated.func, cst.Name) and updated.func.value == "Formula"):
            return updated

        fid = self._get_id(updated)
        kwnames = self._kwarg_names(updated)

        # Already triple-tracked?
        if "arithma" in kwnames or "eml" in kwnames or "value" in kwnames:
            self.noops.append(fid)
            return updated

        latex = self._get_latex(updated)
        shape = _recognize_simple(latex) if latex is not None else None

        if shape is None:
            # Complex formula — record TODO and leave call untouched.
            self.todos.append(fid)
            return updated

        # Build arithma + eml + value kwargs. Use the wrappers so missing
        # backends degrade to ``None`` rather than blowing up at import.
        v = shape.value()
        if shape.kind == "lit":
            arithma_expr = cst.parse_expression(f"_arithma_num({shape.a!r})")
            eml_expr = cst.parse_expression(f"_eml_scalar({shape.a!r})")
        elif shape.kind == "div":
            arithma_expr = cst.parse_expression(
                f"_arithma_div(_arithma_num({shape.a!r}), _arithma_num({shape.b!r}))"
            )
            eml_expr = cst.parse_expression(
                f"_eml_div(_eml_scalar({shape.a!r}), _eml_scalar({shape.b!r}))"
            )
        else:  # "mul"
            arithma_expr = cst.parse_expression(
                f"_arithma_mul(_arithma_num({shape.a!r}), _arithma_num({shape.b!r}))"
            )
            eml_expr = cst.parse_expression(
                f"_eml_mul(_eml_scalar({shape.a!r}), _eml_scalar({shape.b!r}))"
            )

        new_args = list(updated.args) + [
            cst.Arg(
                keyword=cst.Name("arithma"),
                value=arithma_expr,
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            ),
            cst.Arg(
                keyword=cst.Name("eml"),
                value=eml_expr,
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            ),
            cst.Arg(
                keyword=cst.Name("value"),
                value=cst.parse_expression(repr(v)),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            ),
        ]

        # Ensure last existing arg has a trailing comma so the new args stay
        # comma-separated; new args already use default comma behavior.
        self.migrated.append(fid)
        self.needs_arithma_import = True
        self.needs_eml_import = True
        return updated.with_changes(args=new_args)


# ── File-level transformer: inject imports + leading TODOs ───────────────────

_IMPORT_BLOCK = """\
# --- triple-track helpers (injected by migrate_formulas_to_triple.py) ---
try:  # pragma: no cover - optional during early migration
    import arithma as _A
    def _arithma_num(v):
        return _A.Expression.number(float(v))
except ImportError:  # pragma: no cover
    _A = None  # type: ignore[assignment]
    def _arithma_num(v):
        return None
from metaphysica.simulations.core.eml_integration import (
    eml_scalar as _eml_scalar,
    eml_div as _eml_div,
    eml_mul as _eml_mul,
)
def _arithma_div(a, b):
    return None if a is None or b is None else a / b
def _arithma_mul(a, b):
    return None if a is None or b is None else a * b
"""


def _inject_imports(tree: cst.Module) -> cst.Module:
    """Insert the triple-track import block after the last top-level import."""
    if "triple-track helpers" in tree.code:
        return tree
    parsed = cst.parse_module(_IMPORT_BLOCK)
    new_body = list(tree.body)
    insert_at = 0
    for i, stmt in enumerate(new_body):
        if isinstance(stmt, cst.SimpleStatementLine) and any(
            isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body
        ):
            insert_at = i + 1
    new_body[insert_at:insert_at] = list(parsed.body)
    return tree.with_changes(body=new_body)


def _process_file(path: Path, dry_run: bool) -> Tuple[int, int, int]:
    src = path.read_text(encoding="utf-8")
    if "Formula(" not in src:
        return (0, 0, 0)
    try:
        tree = cst.parse_module(src)
    except cst.ParserSyntaxError as exc:
        print(f"  ! skip (parse error in {path}): {exc}", file=sys.stderr)
        return (0, 0, 0)

    transformer = FormulaCallTransformer()
    new_tree = tree.visit(transformer)

    n_mig = len(transformer.migrated)
    n_todo = len(transformer.todos)
    n_noop = len(transformer.noops)

    # Inject imports only when we actually rewrote at least one call.
    if n_mig > 0:
        new_tree = _inject_imports(new_tree)

    # Prepend TODO comments for complex formulas. Insert as EmptyLine
    # comments at module body level so we never split a multi-line import.
    if n_todo > 0:
        comment_lines = [
            cst.EmptyLine(
                indent=False,
                comment=cst.Comment(
                    f"# TODO(triple-track): build arithma + eml trees for {fid}"
                ),
            )
            for fid in transformer.todos
        ]
        # Find first non-import top-level statement; attach comments to its
        # leading_lines if possible, else prepend to the module header.
        body = list(new_tree.body)
        attach_idx = None
        for i, stmt in enumerate(body):
            is_import = (
                isinstance(stmt, cst.SimpleStatementLine)
                and any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body)
            )
            if not is_import and not isinstance(stmt, cst.SimpleStatementLine):
                attach_idx = i
                break
            if not is_import and isinstance(stmt, cst.SimpleStatementLine):
                # First non-import statement — attach here.
                attach_idx = i
                break
        if attach_idx is not None:
            target = body[attach_idx]
            existing = list(getattr(target, "leading_lines", []) or [])
            if not any("triple-track" in (ln.comment.value if ln.comment else "")
                       for ln in existing):
                new_leading = existing + [cst.EmptyLine(indent=False)] + comment_lines
                body[attach_idx] = target.with_changes(leading_lines=new_leading)
                new_tree = new_tree.with_changes(body=body)
    out_code = new_tree.code

    if out_code != src and not dry_run:
        path.write_text(out_code, encoding="utf-8")

    return (n_mig, n_todo, n_noop)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--root", type=Path, default=PM_ROOT)
    args = parser.parse_args(argv)

    if not args.root.exists():
        print(f"PM root not found: {args.root}", file=sys.stderr)
        return 2

    total_mig = total_todo = total_noop = 0
    files_touched = 0
    for path in sorted(args.root.rglob("*.py")):
        n_mig, n_todo, n_noop = _process_file(path, dry_run=args.dry_run)
        if n_mig or n_todo or n_noop:
            files_touched += 1
            if n_mig:
                print(f"  + {path.relative_to(args.root)}: migrated {n_mig}, "
                      f"todo {n_todo}, noop {n_noop}")
        total_mig += n_mig
        total_todo += n_todo
        total_noop += n_noop

    print("\n=== migrate_formulas_to_triple summary ===")
    print(f"  files touched:          {files_touched}")
    print(f"  Migrated (simple):      {total_mig}")
    print(f"  TODO (complex):         {total_todo}")
    print(f"  no-op (already triple): {total_noop}")
    if args.dry_run:
        print("  [dry-run, no files written]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
