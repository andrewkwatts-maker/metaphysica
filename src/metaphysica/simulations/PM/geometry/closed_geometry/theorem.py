"""The certificate's building blocks: the Theorem record, the expression
spec that yields all three triple-track views, and the helpers every
theorem shares (the active family member, off-family wording).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from metaphysica.simulations.core.triple_helpers import (
    _arithma_add,
    _arithma_mul,
    _arithma_num,
    _arithma_pow,
    _arithma_sub,
    _eml_add,
    _eml_mul,
    _eml_pow,
    _eml_scalar,
    _eml_sub,
)

_TOPOLOGICAL = (
    "topological: independent of the metric and of the real form of phi")


@dataclass(frozen=True)
class Theorem:
    """One entry of the certificate. Every callable reads the evidence, so
    nothing in the published text is typed by hand. `references` holds keys
    into references.REFERENCES; `terms` defines each symbol the LaTeX uses."""

    id: str
    label: str
    title: str
    counts: str
    proof: str
    test: str
    falsifier: str
    evidence: Callable[[], Dict[str, Any]]
    holds: Callable[[Dict[str, Any]], bool]
    statement: Callable[[Dict[str, Any]], str]
    track: Callable[[Dict[str, Any]], Tuple[float, "Spec"]]
    latex: Callable[[Dict[str, Any]], str]
    steps: Callable[[Dict[str, Any]], List[str]]
    terms: Dict[str, Dict[str, str]]
    references: Tuple[str, ...] = ()
    scope: str = _TOPOLOGICAL
    #: False for a statement about the whole family, which holds -- and is
    #: published -- whichever member the seed fork selects.
    seed_following: bool = True


# ------------------------------------------------------------ expression specs

#: A closed-form expression: a number, or (op, left, right). One spec builds
#: the EML tree, the arithma tree and the display string, so the three can
#: never describe different formulas.
Spec = Any

_OPS = {
    "add": (_eml_add, _arithma_add, lambda a, b: a + b),
    "sub": (_eml_sub, _arithma_sub, lambda a, b: a - b),
    "mul": (_eml_mul, _arithma_mul, lambda a, b: a * b),
    "pow": (_eml_pow, _arithma_pow, lambda a, b: a ** b),
}


def build(spec: Spec) -> Tuple[Any, Any, str, float]:
    """(EML tree, arithma tree, display text, float) of one spec."""
    if isinstance(spec, (int, float)):
        return (_eml_scalar(spec), _arithma_num(spec),
                "eml_scalar(%s)" % spec, float(spec))
    op, left, right = spec
    el, al, tl, vl = build(left)
    er, ar, tr, vr = build(right)
    e_fn, a_fn, f_fn = _OPS[op]
    return (e_fn(el, er), a_fn(al, ar), "ops.%s(%s, %s)" % (op, tl, tr),
            float(f_fn(vl, vr)))


# ------------------------------------------------------------ the active member

def _active() -> Tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]:
    """(path, profile, representative point) -- point is None off the family."""
    from metaphysica.simulations.PM.geometry.b3_path import (
        PATHS,
        resolve_path,
    )
    from metaphysica.simulations.PM.geometry.joyce_resolution import (
        representative_point,
    )

    path = resolve_path()
    profile = PATHS[path]
    if not profile.get("reachable_by_joyce"):
        return path, profile, None
    return path, profile, representative_point(profile["n_t3"] // 4)


def _off_family(ev: Dict[str, Any]) -> str:
    return ("The active seed %s, (b_2, b_3) = %s, is not reachable by the "
            "construction: no admissible assignment realises it, so nothing "
            "here derives it." % (ev["path"], ev["declared"]))


def _fmt(seq: Dict[int, int]) -> str:
    return ", ".join(str(seq[k]) for k in sorted(seq))
