"""Control: the volume modulus of M_4 x (b K_n), K_n flat, is a Brans-Dicke scalar.

The reduction is computed, not typed. Metric G = g_4 + b(x) delta_ij dy^i dy^j with
g_4 = diag(-1, a^2, a^2, a^2), a and b functions of t. L_red = sqrt(-G) R_G (per unit internal
volume, computed through `curvature.ricci_scalar`). phi is the factor sqrt(-G)/sqrt(-g_4) that
multiplies R_4, and L_BD = sqrt(-g_4) [phi R_4 - (omega/phi) g^mn d_m phi d_n phi]. omega is
the value for which the Euler-Lagrange expressions of L_red and L_BD agree for a and b, so total
derivatives drop. Result: omega(n) = -1 + 1/n. For test matter on the 4D block,
gamma_PPN = (1 + omega)/(2 + omega) (Will, Living Rev. Rel. 17 (2014) 4, sec. 5.3) = 1/(n + 1).
Correspondence: n = 1 gives omega = 0, the Kaluza-Klein dilaton (Overduin & Wesson, Phys. Rep.
283 (1997) 303). Failing control: the claim gamma_PPN = 1 (GR) at any finite n.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from functools import lru_cache

import sympy as sp
from sympy.calculus.euler import euler_equations

from metaphysica.actions.correspondence import Correspondence
from metaphysica.actions.curvature import ricci_scalar
from metaphysica.actions.model import Check

REF = ("Overduin & Wesson, Phys. Rep. 283 (1997) 303; Will, Living Rev. Rel. 17 (2014) 4, "
       "sec. 5.3 (Brans-Dicke gamma)")
T = sp.Symbol("t")
OMEGA = sp.Symbol("omega")


def _fields():
    return sp.Function("a", positive=True)(T), sp.Function("b", positive=True)(T)


def _four_d(a):
    g4 = sp.diag(-1, a ** 2, a ** 2, a ** 2)
    coords = [T] + list(sp.symbols("x1 x2 x3"))
    return g4, coords


def reduced_lagrangian(n: int) -> sp.Expr:
    """sqrt(-G) R_G on M_4 x (b T^n), per unit coordinate volume of T^n."""
    if int(n) != n or n < 1:
        raise ValueError("internal dimension must be a positive integer, got %r" % n)
    a, b = _fields()
    g4, c4 = _four_d(a)
    G = sp.diag(*(list(g4.diagonal()) + [b] * n))
    coords = c4 + list(sp.symbols("y1:%d" % (n + 1)))
    return sp.sqrt(-G.det()) * ricci_scalar(G, coords, sp.diag(*[1 / e for e in G.diagonal()]))


def brans_dicke_lagrangian(n: int, omega) -> sp.Expr:
    """sqrt(-g) [phi R_4 - (omega/phi)(d phi)^2], phi = sqrt(-G)/sqrt(-g_4) computed."""
    a, b = _fields()
    g4, c4 = _four_d(a)
    G = sp.diag(*(list(g4.diagonal()) + [b] * n))
    phi = sp.simplify(sp.sqrt(-G.det()) / sp.sqrt(-g4.det()))
    inv = sp.diag(*[1 / e for e in g4.diagonal()])
    dphi2 = inv[0, 0] * sp.diff(phi, T) ** 2
    return sp.sqrt(-g4.det()) * (phi * ricci_scalar(g4, c4, inv) - omega / phi * dphi2)


@lru_cache(maxsize=None)
def omega(n: int) -> sp.Expr:
    """The Brans-Dicke parameter for which both Lagrangians have equal Euler-Lagrange terms."""
    a, b = _fields()
    diff = sp.expand(reduced_lagrangian(n) - brans_dicke_lagrangian(n, OMEGA))
    eqs = [sp.simplify(e.lhs) for e in euler_equations(diff, [a, b], T)]
    sols = set()
    for e in eqs:
        if e != 0:
            sols.update(sp.solve(e, OMEGA))
    if len(sols) != 1:
        raise ArithmeticError("no unique omega for n = %d: %s" % (n, sols))
    w = sols.pop()
    if any(sp.simplify(e.subs(OMEGA, w)) != 0 for e in eqs):
        raise ArithmeticError("omega = %s leaves a residual for n = %d" % (w, n))
    return sp.nsimplify(w)


def gamma_ppn(n: int) -> sp.Expr:
    w = omega(n)
    return sp.simplify((1 + w) / (2 + w))


def _kk_compute():
    w = omega(1)
    return str(w), w == 0, "omega(1) from the reduction; KK dilaton has omega = 0"


def correspondence() -> Correspondence:
    return Correspondence("volume_modulus_kk_omega", "gravity on M4 x b T^n", REF, _kk_compute)


def _gr_claim(n: int):
    g = gamma_ppn(n)
    return str(g), g == 1, "gamma_PPN(%d) compared to the GR value 1" % n


def control(n: int = 1) -> Correspondence:
    """Failing control: an unstabilised volume modulus reproduces GR (gamma_PPN = 1)."""
    return Correspondence("volume_modulus_control_gr", "gravity on M4 x b T^n", REF,
                          lambda: _gr_claim(n))


def ppn_check(name: str, n: int, bound) -> Check:
    """|gamma_PPN(n) - 1| <= bound, the bound supplied by the caller from its data source."""
    g = gamma_ppn(n)
    dev = abs(float(g) - 1)
    return Check("ppn_gamma:%s" % name, str(g), dev <= float(bound), True, REF,
                 "unstabilised modulus of %d internal dimensions: |gamma - 1| = %.3g, bound %s"
                 % (n, dev, bound))
