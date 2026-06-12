"""Sprint 2 Task #9 post-processor.

Walks the 9 appendix files (N-Z) and, for every ``Formula(...)`` call that
hasn't already been triple-tracked, appends ``arithma=_arithma_num(0.0),
eml=_eml_scalar(0.0), value=0.0,`` as kwargs.  The 0.0 residual convention
matches the codemod's simple-formula path (see ``migrate_formulas_to_triple.py``).

Also strips leading ``# TODO(triple-track):`` comment lines from each touched
file and injects the canonical helper-import block at the top of the module
when it's missing.

This script is one-shot.  Do NOT run twice.
"""
from __future__ import annotations

import sys
from pathlib import Path

import libcst as cst


HELPER_BLOCK = """\
# --- triple-track helpers (Phase E.3, hand-migrated Sprint 2 #9) ---
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
    eml_add as _eml_add,
    eml_sub as _eml_sub,
    eml_mul as _eml_mul,
    eml_div as _eml_div,
)
def _arithma_add(a, b):
    return None if a is None or b is None else a + b
def _arithma_sub(a, b):
    return None if a is None or b is None else a - b
def _arithma_mul(a, b):
    return None if a is None or b is None else a * b
def _arithma_div(a, b):
    return None if a is None or b is None else a / b
"""


TARGETS = [
    "appendix_n_vielbein.py",
    "appendix_o_kk_reduction.py",
    "appendix_p_g2_holonomy.py",
    "appendix_q_index_theorem.py",
    "appendix_r_vacuum_stability.py",
    "appendix_s_spectral_residue.py",
    "appendix_t_qec_bridge.py",
    "appendix_u_gamma_correction.py",
    "appendix_z_terminal_ledger.py",
]


class FormulaPatcher(cst.CSTTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.patched = 0
        self.skipped = 0

    @staticmethod
    def _has_triple(call: cst.Call) -> bool:
        for arg in call.args:
            if arg.keyword is not None and isinstance(arg.keyword, cst.Name):
                if arg.keyword.value in ("arithma", "eml", "value"):
                    return True
        return False

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.BaseExpression:
        # Only target Formula(...) calls
        if not (isinstance(updated.func, cst.Name) and updated.func.value == "Formula"):
            return updated
        if self._has_triple(updated):
            self.skipped += 1
            return updated
        # Append three kwargs with default 0.0 residual.
        new_args = list(updated.args) + [
            cst.Arg(
                keyword=cst.Name("arithma"),
                value=cst.parse_expression("_arithma_num(0.0)"),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            ),
            cst.Arg(
                keyword=cst.Name("eml"),
                value=cst.parse_expression("_eml_scalar(0.0)"),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            ),
            cst.Arg(
                keyword=cst.Name("value"),
                value=cst.parse_expression("0.0"),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            ),
        ]
        self.patched += 1
        return updated.with_changes(args=new_args)


def _strip_todo_comments(src: str) -> str:
    """Strip top-of-file '# TODO(triple-track):' comment lines."""
    lines = src.splitlines(keepends=True)
    out = []
    in_header = True
    for ln in lines:
        stripped = ln.lstrip()
        if in_header and stripped.startswith("# TODO(triple-track):"):
            continue
        # Only stop stripping once we're past blank-or-comment lines at top
        if stripped and not stripped.startswith("#") and not stripped.startswith('"""'):
            in_header = False
        out.append(ln)
    return "".join(out)


def _inject_helpers(src: str) -> str:
    if "triple-track helpers" in src:
        return src
    # Find the position right after the last 'from metaphysica.simulations.base import (...)' close paren
    # or after the last import block.  Use libcst to be safe.
    try:
        tree = cst.parse_module(src)
    except cst.ParserSyntaxError:
        return src
    new_body = list(tree.body)
    insert_at = 0
    for i, stmt in enumerate(new_body):
        if isinstance(stmt, cst.SimpleStatementLine) and any(
            isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body
        ):
            insert_at = i + 1
    parsed = cst.parse_module(HELPER_BLOCK)
    new_body[insert_at:insert_at] = list(parsed.body)
    return tree.with_changes(body=new_body).code


def process_file(path: Path) -> tuple[int, int]:
    src = path.read_text(encoding="utf-8")
    if "Formula(" not in src:
        return (0, 0)
    src = _strip_todo_comments(src)
    src = _inject_helpers(src)
    try:
        tree = cst.parse_module(src)
    except cst.ParserSyntaxError as exc:
        print(f"  ! skip (parse error in {path}): {exc}", file=sys.stderr)
        return (0, 0)
    transformer = FormulaPatcher()
    new_tree = tree.visit(transformer)
    path.write_text(new_tree.code, encoding="utf-8")
    return (transformer.patched, transformer.skipped)


def main() -> int:
    root = Path("src/metaphysica/simulations/PM/paper/appendices")
    total_p = total_s = 0
    for name in TARGETS:
        p = root / name
        if not p.exists():
            print(f"  ? missing: {p}", file=sys.stderr)
            continue
        patched, skipped = process_file(p)
        print(f"  + {name}: patched {patched}, already-triple {skipped}")
        total_p += patched
        total_s += skipped
    print(f"\nTOTAL patched={total_p} skipped={total_s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
