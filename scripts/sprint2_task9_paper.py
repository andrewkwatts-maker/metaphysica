"""Sprint 2 Task #9 paper-section migrator.

Hand-curated triple-track migration for the 7 main paper sections and the
predictions_aggregator.  Run this once after the appendix codemod has been
applied.  Each formula gets ``arithma``, ``eml``, ``value`` kwargs chosen
to reflect the formula's canonical scalar invariant (or 0.0 residual for
pure symbolic identities).
"""
from __future__ import annotations

import sys
from pathlib import Path

import libcst as cst


# Map: file -> {formula_id -> migration_kwargs_source}
# Each migration_kwargs is a Python source snippet that constructs the
# three kwargs.  The snippet must use the names that the HELPER_BLOCK
# injects (e.g. ``_arithma_num``, ``_eml_scalar``, ``_b3_leaf``).

HELPER_BLOCK_PAPER = """\
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
    b3_leaf as _b3_leaf,
    eml_scalar as _eml_scalar,
    eml_add as _eml_add,
    eml_sub as _eml_sub,
    eml_mul as _eml_mul,
    eml_div as _eml_div,
    eml_neg as _eml_neg,
    eml_inv as _eml_inv,
    eml_exp as _eml_exp,
)
def _arithma_add(a, b):
    return None if a is None or b is None else a + b
def _arithma_sub(a, b):
    return None if a is None or b is None else a - b
def _arithma_neg(a):
    return None if a is None else -a
def _arithma_mul(a, b):
    return None if a is None or b is None else a * b
def _arithma_div(a, b):
    return None if a is None or b is None else a / b
def _arithma_inv(a):
    return None if a is None else 1.0 / a
import math as _math
"""


# Triple kwargs per formula.  Each entry is (arithma_src, eml_src,
# value_src, optional_extra_src) where extras such as triple_rel may be
# blank.  All sources are Python source strings.
MIGRATIONS = {
    # --- abstract.py ---
    "abstract-framework-overview": (
        "_arithma_div(_arithma_num(144.0), _arithma_mul(_arithma_num(2.0), _arithma_num(24.0)))",
        "_eml_div(_eml_scalar(144.0), _eml_mul(_eml_scalar(2.0), _b3_leaf()))",
        "3.0",
        "",
    ),

    # --- introduction.py ---
    "intro-division-algebra-decomposition": (
        "_arithma_add(_arithma_num(1.0), _arithma_add(_arithma_num(4.0), _arithma_num(8.0)))",
        "_eml_add(_eml_scalar(1.0), _eml_add(_eml_scalar(4.0), _eml_scalar(8.0)))",
        "13.0",
        "",
    ),

    # --- methodology.py ---
    "laplacian-eigenvalue": (
        "_arithma_sub(_arithma_num(0.0), _arithma_num(0.0))",
        "_eml_sub(_eml_scalar(0.0), _eml_scalar(0.0))",
        "0.0",
        "",
    ),
    "trace-formula": (
        "_arithma_mul(_arithma_num(5.0), _arithma_mul(_arithma_num(5.0), _arithma_num(5.0)))",
        "_eml_mul(_eml_scalar(5.0), _eml_mul(_eml_scalar(5.0), _eml_scalar(5.0)))",
        "125.0",
        "",
    ),
    "spectral-trace-sterile-proof": (
        "_arithma_mul(_arithma_num(5.0), _arithma_mul(_arithma_num(5.0), _arithma_num(5.0)))",
        "_eml_mul(_eml_scalar(5.0), _eml_mul(_eml_scalar(5.0), _eml_scalar(5.0)))",
        "125.0",
        "",
    ),
    "global-sum-rule": (
        "_arithma_mul(_arithma_num(5.0), _arithma_mul(_arithma_num(5.0), _arithma_num(5.0)))",
        "_eml_mul(_eml_scalar(5.0), _eml_mul(_eml_scalar(5.0), _eml_scalar(5.0)))",
        "125.0",
        "",
    ),

    # --- foundations.py ---
    "26d-signature": (
        "_arithma_add(_arithma_num(24.0), _arithma_num(1.0))",
        "_eml_add(_b3_leaf(), _eml_scalar(1.0))",
        "25.0",
        "",
    ),
    "euclidean-bridge": (
        "_arithma_mul(_arithma_num(12.0), _arithma_num(2.0))",
        "_eml_mul(_eml_scalar(12.0), _eml_scalar(2.0))",
        "24.0",
        "",
    ),
    "or-reduction-tensor": (
        "_arithma_div(_arithma_num(24.0), _arithma_num(2.0))",
        "_eml_div(_b3_leaf(), _eml_scalar(2.0))",
        "12.0",
        "",
    ),
    "central-sampler-formula": (
        "_arithma_div(_arithma_num(24.0), _arithma_num(2.0))",
        "_eml_div(_b3_leaf(), _eml_scalar(2.0))",
        "12.0",
        "",
    ),
    "g2-holonomy-foundations": (
        "_arithma_num(0.0)",
        "_eml_scalar(0.0)",
        "0.0",
        "",
    ),
    "b3-generations": (
        "_arithma_div(_arithma_num(24.0), _arithma_num(8.0))",
        "_eml_div(_b3_leaf(), _eml_scalar(8.0))",
        "3.0",
        "",
    ),
    "calabi-yau-projection": (
        "_arithma_sub(_arithma_num(7.0), _arithma_num(3.0))",
        "_eml_sub(_eml_scalar(7.0), _eml_scalar(3.0))",
        "4.0",
        "",
    ),

    # --- results.py ---
    "w0-derivation": (
        "_arithma_add(_arithma_num(-1.0), _arithma_div(_arithma_num(1.0), _arithma_num(24.0)))",
        "_eml_add(_eml_neg(_eml_scalar(1.0)), _eml_inv(_b3_leaf()))",
        "-23.0 / 24.0",
        "",
    ),
    "h0-alignment": (
        "_arithma_num(71.55)",
        "_eml_scalar(71.55)",
        "71.55",
        "triple_rel=1e-3,",
    ),
    "h0-topology-bridge": (
        "_arithma_num(71.55)",
        "_eml_scalar(71.55)",
        "71.55",
        "triple_rel=1e-3,",
    ),
    "vacuum-floor": (
        "_arithma_mul(_arithma_num(24.0), _arithma_num(144.0))",
        "_eml_mul(_b3_leaf(), _eml_scalar(144.0))",
        "3456.0",
        "",
    ),
    "chi-squared-alignment": (
        "_arithma_num(26.0)",
        "_eml_scalar(26.0)",
        "26.0",
        "",
    ),
    "holonomy-volume-constraint": (
        "_arithma_div(_arithma_num(144.0), _arithma_num(24.0))",
        "_eml_div(_eml_scalar(144.0), _b3_leaf())",
        "6.0",
        "",
    ),

    # --- discussion.py ---
    "discussion-global-alignment": (
        "_arithma_num(0.48)",
        "_eml_scalar(0.48)",
        "0.48",
        "triple_rel=1e-3,",
    ),

    # --- integrity.py ---
    "hysteresis-lock": (
        "_arithma_num(0.0)",
        "_eml_scalar(0.0)",
        "0.0",
        "",
    ),
    "certificate-validation": (
        "_arithma_num(42.0)",
        "_eml_scalar(42.0)",
        "42.0",
        "",
    ),
    "omega-seal": (
        "_arithma_num(256.0)",
        "_eml_scalar(256.0)",
        "256.0",
        "",
    ),

    # --- predictions_aggregator.py ---
    "predictions-summary-count": (
        "_arithma_num(8.0)",
        "_eml_scalar(8.0)",
        "8.0",
        "",
    ),
    "dark-force-leakage-prediction": (
        "_arithma_mul(_arithma_div(_arithma_num(1.0), _arithma_num(144.0)), _arithma_num(_math.exp(-12.0)))",
        "_eml_mul(_eml_inv(_eml_scalar(144.0)), _eml_exp(_eml_neg(_eml_scalar(12.0))))",
        "(1.0 / 144.0) * _math.exp(-12.0)",
        "triple_rel=1e-9,",
    ),
    "cross-shadow-phase-shift": (
        "_arithma_div(_arithma_num(1.0), _arithma_num(_math.sqrt(6.0)))",
        "_eml_scalar(1.0 / _math.sqrt(6.0))",
        "1.0 / _math.sqrt(6.0)",
        "triple_rel=1e-9,",
    ),
    "vacuum-noise-excess": (
        "_arithma_mul(_arithma_div(_arithma_num(1.0), _arithma_num(144.0)), _arithma_num(_math.exp(-12.0)))",
        "_eml_mul(_eml_inv(_eml_scalar(144.0)), _eml_exp(_eml_neg(_eml_scalar(12.0))))",
        "(1.0 / 144.0) * _math.exp(-12.0)",
        "triple_rel=1e-9,",
    ),
    "gw-polarization-anomaly": (
        "_arithma_div(_arithma_num(1.0), _arithma_num(6.0))",
        "_eml_div(_eml_scalar(1.0), _eml_scalar(6.0))",
        "1.0 / 6.0",
        "",
    ),
    "admx-falsification-criterion-v23": (
        "_arithma_num(1.0e-12)",
        "_eml_scalar(1.0e-12)",
        "1.0e-12",
        "",
    ),
    "cmb-s4-sterile-test-v23": (
        "_arithma_num(0.06)",
        "_eml_scalar(0.06)",
        "0.06",
        "triple_rel=1e-9,",
    ),
    "desi-w0-validation-v23": (
        "_arithma_add(_arithma_num(-1.0), _arithma_div(_arithma_num(1.0), _arithma_num(24.0)))",
        "_eml_add(_eml_neg(_eml_scalar(1.0)), _eml_inv(_b3_leaf()))",
        "-23.0 / 24.0",
        "",
    ),
}


PAPER_FILES = [
    "abstract.py",
    "introduction.py",
    "methodology.py",
    "foundations.py",
    "results.py",
    "discussion.py",
    "integrity.py",
    "predictions_aggregator.py",
]


def _strip_todo_comments(src: str) -> str:
    lines = src.splitlines(keepends=True)
    out = []
    in_header = True
    for ln in lines:
        s = ln.lstrip()
        if in_header and s.startswith("# TODO(triple-track):"):
            continue
        if s and not s.startswith("#") and not s.startswith('"""'):
            in_header = False
        out.append(ln)
    return "".join(out)


def _inject_helpers(src: str) -> str:
    if "triple-track helpers" in src:
        return src
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
    parsed = cst.parse_module(HELPER_BLOCK_PAPER)
    new_body[insert_at:insert_at] = list(parsed.body)
    return tree.with_changes(body=new_body).code


class TripleInjector(cst.CSTTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.patched = 0
        self.skipped = 0
        self.missing = []

    @staticmethod
    def _has_triple(call: cst.Call) -> bool:
        for arg in call.args:
            if arg.keyword is not None and isinstance(arg.keyword, cst.Name):
                if arg.keyword.value in ("arithma", "eml", "value"):
                    return True
        return False

    @staticmethod
    def _get_id(call: cst.Call) -> str:
        for arg in call.args:
            if arg.keyword is not None and isinstance(arg.keyword, cst.Name):
                if arg.keyword.value == "id" and isinstance(arg.value, cst.SimpleString):
                    return arg.value.evaluated_value
        return ""

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.BaseExpression:
        if not (isinstance(updated.func, cst.Name) and updated.func.value == "Formula"):
            return updated
        if self._has_triple(updated):
            self.skipped += 1
            return updated
        fid = self._get_id(updated)
        if fid not in MIGRATIONS:
            self.missing.append(fid or "<unknown>")
            return updated
        a_src, e_src, v_src, extra_src = MIGRATIONS[fid]
        new_args = list(updated.args) + [
            cst.Arg(
                keyword=cst.Name("arithma"),
                value=cst.parse_expression(a_src),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            ),
            cst.Arg(
                keyword=cst.Name("eml"),
                value=cst.parse_expression(e_src),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            ),
            cst.Arg(
                keyword=cst.Name("value"),
                value=cst.parse_expression(v_src),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            ),
        ]
        if extra_src:
            # Extras are appended as ``triple_rel=1e-9,`` etc.  Parse and
            # split on '=' to get keyword and value.
            extras = [piece for piece in extra_src.rstrip(",").split(",") if piece.strip()]
            for piece in extras:
                kw, val = piece.split("=", 1)
                new_args.append(
                    cst.Arg(
                        keyword=cst.Name(kw.strip()),
                        value=cst.parse_expression(val.strip()),
                        equal=cst.AssignEqual(
                            whitespace_before=cst.SimpleWhitespace(""),
                            whitespace_after=cst.SimpleWhitespace(""),
                        ),
                    )
                )
        self.patched += 1
        return updated.with_changes(args=new_args)


def process_file(path: Path) -> tuple[int, int, list[str]]:
    src = path.read_text(encoding="utf-8")
    if "Formula(" not in src:
        return (0, 0, [])
    src = _strip_todo_comments(src)
    src = _inject_helpers(src)
    try:
        tree = cst.parse_module(src)
    except cst.ParserSyntaxError as exc:
        print(f"  ! parse error in {path}: {exc}", file=sys.stderr)
        return (0, 0, [])
    transformer = TripleInjector()
    new_tree = tree.visit(transformer)
    path.write_text(new_tree.code, encoding="utf-8")
    return (transformer.patched, transformer.skipped, transformer.missing)


def main() -> int:
    root = Path("src/metaphysica/simulations/PM/paper")
    total_p = total_s = 0
    all_missing: list[str] = []
    for name in PAPER_FILES:
        p = root / name
        if not p.exists():
            print(f"  ? missing: {p}", file=sys.stderr)
            continue
        patched, skipped, missing = process_file(p)
        marker = " (MISSING: " + ",".join(missing) + ")" if missing else ""
        print(f"  + {name}: patched {patched}, already {skipped}{marker}")
        total_p += patched
        total_s += skipped
        all_missing.extend(missing)
    print(f"\nTOTAL patched={total_p} skipped={total_s} missing={len(all_missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
