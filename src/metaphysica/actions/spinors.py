"""Spinor dimension counts and the Weyl-mass term check.

Generic and theory-agnostic. Real-structure table: Polchinski, String Theory vol. 2
(1998), App. B; Van Proeyen, "Tools for supersymmetry" (1999), Table 3.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import List

from metaphysica.actions.model import CURVATURE, DERIVATIVE, Action, Check

REF = "Polchinski vol. 2 App. B; Van Proeyen, Tools for supersymmetry (1999), Table 3"
MAJORANA_CLASSES = (0, 1, 2, 6, 7)  # (s - t) mod 8 where a real (pseudo-)Majorana rep exists


def dirac_dim(D: int) -> int:
    """Complex components of a Dirac spinor in D dimensions."""
    if D < 1:
        raise ValueError("dimension must be positive, got %d" % D)
    return 2 ** (D // 2)


def weyl_dim(D: int) -> int:
    """Components of a Weyl spinor; defined only for even D."""
    if D % 2:
        raise ValueError("no Weyl spinor in odd dimension D = %d" % D)
    return dirac_dim(D) // 2


def majorana_allowed(s: int, t: int) -> bool:
    """A real (Majorana or pseudo-Majorana) spinor exists in signature (s, t)."""
    return (s - t) % 8 in MAJORANA_CLASSES


def majorana_weyl_allowed(s: int, t: int) -> bool:
    """Majorana-Weyl needs even D and (s - t) = 0 mod 8."""
    return (s + t) % 2 == 0 and (s - t) % 8 == 0


def majorana_real_components(s: int, t: int, weyl: bool = False) -> int:
    """Real components of a Majorana (or Majorana-Weyl) spinor; raises if not allowed."""
    if weyl:
        if not majorana_weyl_allowed(s, t):
            raise ValueError("no Majorana-Weyl spinor in signature (%d, %d)" % (s, t))
        return dirac_dim(s + t) // 2
    if not majorana_allowed(s, t):
        raise ValueError("no Majorana spinor in signature (%d, %d)" % (s, t))
    return dirac_dim(s + t)


def product_spinor_dim(D1: int, D2: int) -> int:
    """Dirac dimension of the spinor on M^{D1} x M^{D2} built from the factors' spinors."""
    d = dirac_dim(D1) * dirac_dim(D2)
    return 2 * d if (D1 % 2 and D2 % 2) else d


def _is_bilinear_mass(term) -> bool:
    kinetic = term.derivatives > 0 or DERIVATIVE in term.factors
    return not kinetic and len(term.factors) >= 2 and CURVATURE not in term.factors


def check_spinor_terms(action: Action) -> List[Check]:
    """A mass or quartic term built only from a Weyl field in even D vanishes."""
    src = "spinors:%s" % action.id
    out = []
    for t in action.terms:
        if not _is_bilinear_mass(t) or len(set(t.factors)) != 1:
            continue
        f = action.field(t.factors[0])
        if f.kind != "spinor" or f.chirality != "weyl" or action.dim % 2:
            continue
        out.append(Check("weyl_mass:%s:%s" % (action.id, t.id), len(t.factors), False, True,
                         src, "mass term vanishes for a Weyl spinor"))
    return out
