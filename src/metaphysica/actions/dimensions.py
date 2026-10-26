"""Canonical field dimensions in D and the per-term dimension check.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from fractions import Fraction
from typing import List

from metaphysica.actions.model import OPEN, Action, Check


def canonical_dim(kind: str, D: int) -> Fraction:
    """Canonical mass dimension of a field of `kind` in D dimensions."""
    if kind in ("scalar", "vector"):
        return Fraction(D - 2, 2)
    if kind == "spinor":
        return Fraction(D - 1, 2)
    if kind == "metric":
        return Fraction(0)
    if kind.startswith("form:"):
        return Fraction(D - 2, 2)  # gauge potential A_p, canonical normalisation
    raise ValueError("no canonical dimension for kind %r" % kind)


def check_action(action: Action) -> List[Check]:
    """Each term balances to D, every coefficient names a source, OPEN only if term.open."""
    src = "dimensions:%s" % action.id
    out: List[Check] = []
    for t in action.terms:
        dim = action.term_dim(t)
        out.append(Check("dim:%s:%s" % (action.id, t.id), str(dim), dim == action.dim,
                         True, src, "term dimension %s, required %d" % (dim, action.dim)))
        named = bool(t.coefficient.provider) or t.coefficient.source == OPEN
        out.append(Check("source:%s:%s" % (action.id, t.id), t.coefficient.source, named,
                         True, src, "coefficient %s provider %r"
                         % (t.coefficient.symbol, t.coefficient.provider)))
        ok = t.coefficient.source != OPEN or t.open
        out.append(Check("open:%s:%s" % (action.id, t.id), t.coefficient.source, ok,
                         True, src, "OPEN coefficient on a term not marked open" if not ok
                         else "ok"))
    return out
