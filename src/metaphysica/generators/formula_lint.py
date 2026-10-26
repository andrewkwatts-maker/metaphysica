"""Lints for action-like LaTeX: the measure, the Planck power, retired wording.

Pure functions over ``(id, latex)``; each returns a list of ``Finding``. Rows of
an aligned formula (split at ``\\\\``) are linted separately, so a 13D reduction
on the next row is not judged against the 26D integral above it.

Signature table. ``DIMENSION_SIGNATURES`` is the one table the lints read. It
restates the chain comment in
``simulations/PM/geometry/geometric_anchors_core.py``
(``26D(24,2) -> 13D(12,1) -> 6D(5,1) -> 4D(3,1)``, written (space, time));
``tests/test_formula_lint.py`` fails if that comment and this table drift apart.
D = 11 is the M-theory reference (10,1), not on the chain.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple

from metaphysica.generators import superseded_scan

#: spacetime dimension -> (space, time) dimensions.
DIMENSION_SIGNATURES: Dict[int, Tuple[int, int]] = {
    26: (24, 2), 13: (12, 1), 11: (10, 1), 6: (5, 1), 4: (3, 1),
}

_ROW_SPLIT = re.compile(r"\\\\|\\end\{[a-z*]+\}")
_MEASURE = re.compile(r"\\int\b[^$]*?\bd\s*\^\s*(?:\{(\d+)\}|(\d+))\s*[A-Za-z]")
_PLANCK = re.compile(r"M_(?:\{\*\}|\*|\\ast|\{\\ast\})\s*\^\s*(?:\{(\d+)\}|(\d+))")
_RICCI = re.compile(r"(?<![A-Za-z\\])R(?![A-Za-z])")
_SKIP = re.compile(r"^(?:\s|\\[,;:!]|\\ |\\quad|\\qquad)*")


@dataclass(frozen=True)
class Finding:
    """One lint result: which lint, which formula, and what is wrong."""
    lint: str
    formula_id: str
    message: str


def _rows(latex: str) -> List[str]:
    return [r for r in _ROW_SPLIT.split(latex) if r.strip()]


def _measures(row: str) -> Iterator[Tuple[int, int]]:
    """Yield (D, end offset) for each ``\\int ... d^{D}x`` in the row."""
    for m in _MEASURE.finditer(row):
        yield int(m.group(1) or m.group(2)), m.end() - 1


def _balanced(text: str, start: int) -> Optional[str]:
    """Content of the ``{...}`` group opening at text[start], or None if unclosed."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
    return None


def _next_sqrt(row: str, pos: int) -> Optional[str]:
    """Argument of the ``\\sqrt{...}`` that opens the integrand after pos, else None."""
    rest = row[pos:]
    rest = rest[_SKIP.match(rest).end():]
    if not rest.startswith("\\sqrt{"):
        return None
    return _balanced(rest, len("\\sqrt"))


def _has_abs(arg: str) -> bool:
    return any(tok in arg for tok in ("|", "\\vert", "\\lvert", "\\left|"))


def _vielbein_follows(row: str, pos: int) -> bool:
    rest = row[pos:]
    rest = rest[_SKIP.match(rest).end():]
    return bool(re.match(r"(?:e\b|\\det)", rest))


def _measure_problem(dim: int, arg: Optional[str], row: str, pos: int) -> Optional[str]:
    two_times = DIMENSION_SIGNATURES[dim][1] >= 2
    if arg is None:
        if _vielbein_follows(row, pos) or not _RICCI.search(row[pos:]):
            return None
        return "d^{%d}x with curvature but no sqrt measure" % dim
    if two_times:
        ok, need = _has_abs(arg), "sqrt|G|"
    else:
        ok, need = arg.lstrip().startswith("-") or _has_abs(arg), "sqrt{-g}"
    if ok:
        return None
    kind = "two times" if two_times else "one time"
    return "d^{%d}x has %s: measure must be %s, found sqrt{%s}" % (dim, kind, need, arg)


def check_measure(formula_id: str, latex: str) -> List[Finding]:
    """The measure of ``\\int d^{D}x`` must fit the signature of D."""
    out: List[Finding] = []
    for row in _rows(latex):
        for dim, pos in _measures(row):
            if dim not in DIMENSION_SIGNATURES:
                continue
            problem = _measure_problem(dim, _next_sqrt(row, pos + 1), row, pos + 1)
            if problem:
                out.append(Finding("measure", formula_id, problem))
    return out


def check_planck_exponent(formula_id: str, latex: str) -> List[Finding]:
    """``M_*^{n}`` after ``\\int d^{D}`` must have n = D - 2."""
    out: List[Finding] = []
    for row in _rows(latex):
        dims = [d for d, _ in _measures(row)]
        if not dims:
            continue
        start = next(_measures(row))[1]
        for m in _PLANCK.finditer(row, start):
            n = int(m.group(1) or m.group(2))
            if n != dims[0] - 2:
                out.append(Finding("planck_exponent", formula_id,
                                   "M_*^%d under d^{%d}x: expected %d" % (n, dims[0], dims[0] - 2)))
    return out


def check_superseded(formula_id: str, latex: str, plain_text: str = "") -> List[Finding]:
    """No superseded vocabulary in the formula's latex or plain text."""
    return [Finding("superseded", formula_id, "superseded wording in %s" % label)
            for label, text in (("latex", latex), ("plain_text", plain_text))
            if text and superseded_scan.is_hit(text)]


def lint_formula(formula_id: str, latex: str, plain_text: str = "") -> List[Finding]:
    """Run every lint on one formula."""
    return (check_measure(formula_id, latex)
            + check_planck_exponent(formula_id, latex)
            + check_superseded(formula_id, latex, plain_text))
