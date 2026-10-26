"""Control: compactification of M4 x K, with K Ricci-flat.

For a product metric the Ricci scalar adds: R_D = R_4 + R_K. A flat torus has
R_K = 0; S^2 of radius r has R_K = 2 / r^2. The Planck mass follows
M_Pl^2 = M_*^(D-2) Vol(K).
Reference: Polchinski, String Theory vol. 2 (1998), sec. 12.1; Overduin and
Wesson, Phys. Rep. 283 (1997) 303.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from fractions import Fraction

import sympy as sp

from metaphysica.actions.correspondence import Correspondence
from metaphysica.actions.curvature import ricci_scalar
from metaphysica.actions.model import INPUT, Action, Coefficient, Term
from metaphysica.actions.reduction import InternalSpace, Reduction, check_reduction

REF = "Polchinski, String Theory vol. 2, sec. 12.1; Overduin & Wesson 1997"
T, X1, X2, X3 = sp.symbols("t x1 x2 x3")
TH, PH, U, V = sp.symbols("theta phi u v")
R_S2 = sp.Symbol("r", positive=True)


def _four_d():
    a = sp.Function("a")(T)
    g4 = sp.diag(-1, a ** 2, a ** 2, a ** 2)
    return g4, [T, X1, X2, X3], ricci_scalar(g4, [T, X1, X2, X3], simp=sp.simplify)


def _product_excess(internal_metric: sp.Matrix, internal_coords) -> sp.Expr:
    g4, c4, r4 = _four_d()
    n = 4 + internal_metric.shape[0]
    g = sp.zeros(n, n)
    g[:4, :4] = g4
    g[4:, 4:] = internal_metric
    rd = ricci_scalar(g, c4 + list(internal_coords), simp=sp.simplify)
    return sp.simplify(rd - r4)


def torus_excess():
    return _product_excess(sp.eye(2), [U, V])


def sphere_excess():
    return _product_excess(sp.diag(R_S2 ** 2, R_S2 ** 2 * sp.sin(TH) ** 2), [TH, PH])


def _torus_compute():
    ex = torus_excess()
    return str(ex), ex == 0, "R_D - R_4 on M4 x T^2"


def _sphere_compute():
    ex = sphere_excess()
    return str(ex), sp.simplify(ex - 2 / R_S2 ** 2) == 0, "R_D - R_4 on M4 x S^2, expect 2/r^2"


def _false_sphere_compute():
    """Failing control: claim S^2 is Ricci-flat, R_D = R_4."""
    ex = sphere_excess()
    return str(ex), ex == 0, "R_D - R_4 on M4 x S^2 compared to 0"


def _planck_actions(D: int):
    ms = Coefficient("M_star^%d" % (D - 2), Fraction(D - 2), INPUT, "input")
    mp = Coefficient("M_Pl^2", Fraction(2), "DERIVED", "reduction")
    parent = Action("EH_%dD" % D, D, (D - 1, 1), (), (Term("eh", ms, ("R",)),))
    child = Action("EH_4D", 4, (3, 1), (), (Term("eh", mp, ("R",)),))
    internal = InternalSpace("K", D - 4, True, None, "Vol")
    return parent, child, internal


def planck_checks(D: int = 10, wrong: bool = False):
    parent, child, internal = _planck_actions(D)
    ms = sp.Symbol("M_star^%d" % (D - 2), positive=True)
    vol = sp.Symbol("Vol", positive=True)
    expr = ms if wrong else ms * vol
    red = Reduction(parent, child, internal, {"M_Pl^2": expr})
    return check_reduction(red)


def _planck_compute(wrong: bool):
    checks = planck_checks(wrong=wrong)
    bad = [c.id for c in checks if not c.holds]
    return "failed: %s" % bad if bad else "all hold", not bad, "M_Pl^2 = M_*^(D-2) Vol(K)"


def correspondences():
    return (
        Correspondence("rfc_torus_ricci_flat", "M4 x T^2", REF, _torus_compute),
        Correspondence("rfc_sphere_excess", "M4 x S^2", REF, _sphere_compute),
        Correspondence("rfc_planck_mass_dimension", "10D -> 4D", REF,
                       lambda: _planck_compute(False)),
    )


def controls():
    return (
        Correspondence("rfc_control_sphere_not_flat", "M4 x S^2", REF, _false_sphere_compute),
        Correspondence("rfc_control_planck_without_volume", "10D -> 4D", REF,
                       lambda: _planck_compute(True)),
    )
