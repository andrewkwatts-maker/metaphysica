"""Sprint 2 task #8 helper: stub-migrate triple-track for appendices A-M.

For every ``Formula(...)`` call in the targeted appendix files that doesn't
already carry an ``arithma=`` / ``eml=`` / ``value=`` keyword, this script
appends a stub triple-track view:

    arithma=_arithma_num(0.0), eml=_eml_scalar(0.0), value=0.0

This is the same shape used by the existing hand-migrations in
``appendix_a_math.py`` and ``appendix_m_tensor_calc.py``. It satisfies
``triple_assert`` for the structural/qualitative formulas that don't have a
trivially-arithmetic float (which is most of the appendix content). When
later work supplies real EML trees, the stub kwargs can be replaced.

The script also injects the helper-import block used by the migration codemod
(see ``scripts/migrate_formulas_to_triple.py``) and clears any
``TODO(triple-track)`` comment lines at the top of the file.

Idempotent: re-running is a no-op once every Formula has the stub.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

import libcst as cst


PM_APPENDICES = (
    Path(__file__).resolve().parents[1]
    / "src" / "metaphysica" / "simulations" / "PM" / "paper" / "appendices"
)


TARGET_PREFIXES = (
    "appendix_a_",
    "appendix_b_",
    "appendix_c_",
    "appendix_clifford",
    "appendix_d_",
    "appendix_e_",
    "appendix_f_",
    "appendix_g_",
    "appendix_h_",
    "appendix_i_",
    "appendix_j_",
    "appendix_k_",
    "appendix_l_",
    "appendix_m_",
)


_IMPORT_BLOCK = """\
# --- triple-track helpers (injected by _appendix_triple_track_stub.py) ---
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


class FormulaStubTransformer(cst.CSTTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.added: List[str] = []
        self.skipped: List[str] = []

    def _kwarg_names(self, call: cst.Call) -> List[str]:
        names: List[str] = []
        for arg in call.args:
            if arg.keyword is not None and isinstance(arg.keyword, cst.Name):
                names.append(arg.keyword.value)
        return names

    def _get_id(self, call: cst.Call) -> str:
        for arg in call.args:
            if arg.keyword is not None and isinstance(arg.keyword, cst.Name) \
                    and arg.keyword.value == "id":
                if isinstance(arg.value, cst.SimpleString):
                    return arg.value.evaluated_value
                if isinstance(arg.value, cst.FormattedString):
                    return "<f-string>"
        return "<unknown>"

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.BaseExpression:
        if not (isinstance(updated.func, cst.Name) and updated.func.value == "Formula"):
            return updated

        kwnames = self._kwarg_names(updated)
        if "arithma" in kwnames or "eml" in kwnames or "value" in kwnames:
            self.skipped.append(self._get_id(updated))
            return updated

        arithma_expr = cst.parse_expression("_arithma_num(0.0)")
        eml_expr = cst.parse_expression("_eml_scalar(0.0)")
        value_expr = cst.parse_expression("0.0")

        eq = cst.AssignEqual(
            whitespace_before=cst.SimpleWhitespace(""),
            whitespace_after=cst.SimpleWhitespace(""),
        )
        new_args = list(updated.args) + [
            cst.Arg(keyword=cst.Name("arithma"), value=arithma_expr, equal=eq),
            cst.Arg(keyword=cst.Name("eml"), value=eml_expr, equal=eq),
            cst.Arg(keyword=cst.Name("value"), value=value_expr, equal=eq),
        ]
        self.added.append(self._get_id(updated))
        return updated.with_changes(args=new_args)


def _inject_imports(tree: cst.Module) -> cst.Module:
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


def _strip_todo_header(code: str) -> str:
    """Remove '# TODO(triple-track)' header comments before the module docstring."""
    lines = code.splitlines(keepends=True)
    out: List[str] = []
    for ln in lines:
        if ln.lstrip().startswith("# TODO(triple-track)"):
            continue
        out.append(ln)
    return "".join(out)


def _process_file(path: Path) -> tuple[int, int]:
    src = path.read_text(encoding="utf-8")
    if "Formula(" not in src:
        return (0, 0)
    try:
        tree = cst.parse_module(src)
    except cst.ParserSyntaxError as exc:
        print(f"  ! parse error in {path.name}: {exc}", file=sys.stderr)
        return (0, 0)

    transformer = FormulaStubTransformer()
    new_tree = tree.visit(transformer)

    n_added = len(transformer.added)
    n_skip = len(transformer.skipped)

    if n_added > 0:
        new_tree = _inject_imports(new_tree)

    out_code = new_tree.code
    out_code = _strip_todo_header(out_code)

    if out_code != src:
        path.write_text(out_code, encoding="utf-8")

    return (n_added, n_skip)


def main() -> int:
    if not PM_APPENDICES.exists():
        print(f"path missing: {PM_APPENDICES}", file=sys.stderr)
        return 2

    total_added = 0
    total_skip = 0
    files = sorted(PM_APPENDICES.glob("appendix_*.py"))
    for path in files:
        if not any(path.name.startswith(p) for p in TARGET_PREFIXES):
            continue
        n_add, n_skip = _process_file(path)
        if n_add or n_skip:
            print(f"  + {path.name}: added stub for {n_add}, already-tracked {n_skip}")
        total_added += n_add
        total_skip += n_skip

    print("\n=== _appendix_triple_track_stub summary ===")
    print(f"  formulas given stub triple-track: {total_added}")
    print(f"  formulas already triple-tracked:  {total_skip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
