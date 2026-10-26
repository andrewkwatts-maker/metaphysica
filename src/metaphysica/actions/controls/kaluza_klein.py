"""Control: Kaluza-Klein reduction of 5D gravity on a circle.

Metric g_mn = g4_mn + phi^2 A_m A_n, g_m5 = phi^2 A_m, g_55 = phi^2, with A, phi
functions of the four coordinates. Reference formula (mostly plus):
R_5 = R_4 - (1/4) phi^2 F_mn F^mn - (2/phi) box(phi).
Reference: Overduin and Wesson, Phys. Rep. 283 (1997) 303, section 2.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import random
from functools import lru_cache

import sympy as sp

from metaphysica.actions.correspondence import Correspondence
from metaphysica.actions.curvature import ricci_scalar

REF = "Overduin & Wesson, Phys. Rep. 283 (1997) 303, sec. 2"
X = sp.symbols("x0 x1 x2 x3")
Y = sp.Symbol("y")
COORDS5 = list(X) + [Y]


def kk_metric(g4: sp.Matrix, A, phi, drop_phi_sq: bool = False) -> sp.Matrix:
    """5x5 KK metric; `drop_phi_sq` is the failing control (g_m5 = A_m)."""
    m = sp.zeros(5, 5)
    for a in range(4):
        for b in range(4):
            m[a, b] = g4[a, b] + phi ** 2 * A[a] * A[b]
        m[a, 4] = m[4, a] = A[a] if drop_phi_sq else phi ** 2 * A[a]
    m[4, 4] = phi ** 2
    return m


def kk_inverse(g4: sp.Matrix, A, phi) -> sp.Matrix:
    """Analytic inverse of the correct KK metric."""
    ginv = g4.inv()
    Au = ginv * sp.Matrix(A)
    inv = sp.zeros(5, 5)
    inv[:4, :4] = ginv
    for a in range(4):
        inv[a, 4] = inv[4, a] = -Au[a]
    inv[4, 4] = 1 / phi ** 2 + sum(A[a] * Au[a] for a in range(4))
    return inv


def control_inverse(g4: sp.Matrix, A, phi) -> sp.Matrix:
    """Block (Schur) inverse for the control metric with g_m5 = A_m, g_55 = phi^2."""
    ginv = g4.inv()
    a = sp.Matrix(A)
    pinv = ginv - phi ** 2 * ginv * a * a.T * ginv / (1 + phi ** 2 * (a.T * ginv * a)[0])
    pb = pinv * a
    s = phi ** 2 - (a.T * pb)[0]
    inv = sp.zeros(5, 5)
    inv[:4, :4] = pinv + pb * pb.T / s
    for i in range(4):
        inv[i, 4] = inv[4, i] = -pb[i] / s
    inv[4, 4] = 1 / s
    return inv


def reference_rhs(g4: sp.Matrix, A, phi):
    """R_4 - phi^2 F^2 / 4 - 2 box(phi)/phi for the 4D metric g4."""
    n = 4
    ginv = g4.inv()
    F = sp.Matrix(n, n, lambda a, b: sp.diff(A[b], X[a]) - sp.diff(A[a], X[b]))
    Fu = ginv * F * ginv
    f2 = sum(F[a, b] * Fu[a, b] for a in range(n) for b in range(n))
    sg = sp.sqrt(-g4.det())
    box = sum(sp.diff(sg * sum(ginv[a, b] * sp.diff(phi, X[b]) for b in range(n)), X[a])
              for a in range(n)) / sg
    return ricci_scalar(g4, X, ginv) - phi ** 2 * f2 / 4 - 2 * box / phi


@lru_cache(maxsize=None)
def symbolic_residual() -> sp.Expr:
    """R_5 minus the reference, flat 4D part, A and phi arbitrary: should be 0."""
    eta = sp.diag(-1, 1, 1, 1)
    A = [sp.Function("A%d" % i)(*X) for i in range(4)]
    phi = sp.Function("phi")(*X)
    r5 = ricci_scalar(kk_metric(eta, A, phi), COORDS5, kk_inverse(eta, A, phi))
    return sp.expand(r5 - reference_rhs(eta, A, phi))


def _test_functions(light: bool = False):
    if light:  # cheap fields for the failing control, whose inverse is rational
        return (sp.diag(-1, 1, 1, 1), [X[1] / 3, 0, 0, 0], 1 + X[0] / 5 + X[1] / 7)
    g4 = sp.diag(-(1 + X[1] ** 2 / 5 + X[2] / 7), 1 + X[0] * X[3] / 6, 1 + X[1] ** 2 / 4,
                 1 + X[2] ** 2 / 3 + X[0] / 9)
    A = [X[1] / 3 + X[2] ** 2 / 5, X[0] * X[3] / 4, 1 + X[3] / 6 + X[1] * X[2] / 7, X[0] ** 2 / 8]
    phi = 1 + X[0] / 5 + X[2] * X[3] / 6 + X[1] ** 2 / 9
    return g4, A, phi


@lru_cache(maxsize=None)
def numeric_residuals(seed: int = 3, points: int = 4, drop_phi_sq: bool = False):
    """R_5 - reference at seeded points, perturbed (curved) diagonal 4D metric."""
    g4, A, phi = _test_functions(light=drop_phi_sq)
    metric = kk_metric(g4, A, phi, drop_phi_sq)
    inv = control_inverse(g4, A, phi) if drop_phi_sq else kk_inverse(g4, A, phi)
    r5 = sp.lambdify(X, ricci_scalar(metric, COORDS5, inv), "math")
    ref = sp.lambdify(X, reference_rhs(g4, A, phi), "math")
    rng = random.Random(seed)
    pts = [[rng.uniform(-0.4, 0.4) for _ in range(4)] for _ in range(points)]
    return tuple(r5(*p) - ref(*p) for p in pts)


def _symbolic_compute():
    res = symbolic_residual()
    return str(res), res == 0, "symbolic R_5 - reference, flat 4D"


def _numeric_compute(drop: bool):
    res = numeric_residuals(drop_phi_sq=drop)
    worst = max(abs(r) for r in res)
    return "%.3g" % worst, worst < 1e-9, "max residual at seeded points, R_4 term included"


@lru_cache(maxsize=None)
def newton_constant_residual():
    """G_4 from reducing (1/16 pi G5) int d5x sqrt(g5) R5 on a circle of radius L."""
    G5, G4, L, y = sp.symbols("G5 G4 L y", positive=True)
    cof = sp.integrate(1 / (16 * sp.pi * G5), (y, 0, 2 * sp.pi * L))
    sol = sp.solve(sp.Eq(cof, 1 / (16 * sp.pi * G4)), G4)[0]
    return sp.simplify(sol - G5 / (2 * sp.pi * L))


def _newton_compute():
    res = newton_constant_residual()
    return str(res), res == 0, "G_4 = G_5 / (2 pi L)"


def correspondences():
    return (
        Correspondence("kk_ricci_scalar_symbolic", "5D GR -> S1", REF, _symbolic_compute),
        Correspondence("kk_ricci_scalar_numeric", "5D GR -> S1", REF,
                       lambda: _numeric_compute(False)),
        Correspondence("kk_newton_constant", "5D GR -> S1", REF, _newton_compute),
    )


def control() -> Correspondence:
    """Failing control: g_m5 = A_m without phi^2 breaks the formula."""
    return Correspondence("kk_control_no_phi_sq", "5D GR -> S1", REF,
                          lambda: _numeric_compute(True))
