"""Compact orientable surfaces: Gauss-Bonnet and which genus admits a Ricci-flat metric.

Generic and theory-agnostic. Gauss-Bonnet: int_S K dA = 2 pi chi(S), chi = 2 - 2g, and in two
dimensions K = R / 2 (Ricci tensor R_ab = K g_ab). A Ricci-flat metric has K = 0 everywhere,
so chi = 0 and the genus is 1: the flat torus. Genus 0 (S^2) has total curvature 4 pi and is
the failing control. Reference: do Carmo, Differential Geometry of Curves and Surfaces (1976),
sec. 4-5.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Sequence, Tuple

import sympy as sp

from metaphysica.actions.curvature import ricci_scalar
from metaphysica.actions.model import Check

REF = "Gauss-Bonnet; do Carmo, Differential Geometry of Curves and Surfaces (1976), sec. 4-5"
TH, PH, U, V = sp.symbols("theta phi u v", real=True)
RADIUS = sp.Symbol("r", positive=True)


def euler_characteristic(genus: int) -> int:
    if int(genus) != genus or genus < 0:
        raise ValueError("genus must be a non-negative integer, got %r" % genus)
    return 2 - 2 * int(genus)


def total_curvature(genus: int) -> sp.Expr:
    """int K dA = 2 pi chi for a compact orientable surface of this genus."""
    return 2 * sp.pi * euler_characteristic(genus)


def ricci_flat_genus() -> int:
    """The genus whose total curvature is zero, solved from Gauss-Bonnet."""
    g = sp.Symbol("g", integer=True, nonnegative=True)
    sols = sp.solve(sp.Eq(2 * sp.pi * (2 - 2 * g), 0), g)
    if len(sols) != 1:
        raise ArithmeticError("Gauss-Bonnet gives %s Ricci-flat genera" % sols)
    return int(sols[0])


def integrated_curvature(metric: sp.Matrix, coords: Sequence,
                         ranges: Sequence[Tuple[sp.Expr, sp.Expr]]) -> sp.Expr:
    """int (R/2) sqrt(det g) d^2x over the coordinate box `ranges` of an explicit metric."""
    if metric.shape != (2, 2) or len(coords) != 2 or len(ranges) != 2:
        raise ValueError("a surface needs a 2x2 metric, two coordinates and two ranges")
    density = sp.simplify(ricci_scalar(metric, coords, simp=sp.simplify) / 2
                          * sp.sqrt(sp.factor(metric.det())))
    out = density
    for c, (lo, hi) in zip(coords, ranges):
        out = sp.integrate(out, (c, lo, hi))
    return sp.simplify(out)


def genus_from_metric(metric, coords, ranges) -> sp.Expr:
    """g = 1 - chi / 2 with chi = (int K dA) / (2 pi)."""
    return sp.simplify(1 - integrated_curvature(metric, coords, ranges) / (4 * sp.pi))


def sphere():
    """Round S^2 of radius r: metric, coordinates, ranges."""
    return (sp.diag(RADIUS ** 2, RADIUS ** 2 * sp.sin(TH) ** 2), [TH, PH],
            [(0, sp.pi), (0, 2 * sp.pi)])


def flat_torus():
    """Unit square flat torus: metric, coordinates, ranges."""
    return sp.eye(2), [U, V], [(0, 1), (0, 1)]


def ricci_flat_check(name: str, genus: int) -> Check:
    """A compact orientable surface of this genus admits a Ricci-flat metric (can fail)."""
    want = ricci_flat_genus()
    return Check("ricci_flat_surface:%s" % name, genus, genus == want, True, REF,
                 "Gauss-Bonnet: total curvature %s; Ricci-flat needs genus %d"
                 % (total_curvature(genus), want))
