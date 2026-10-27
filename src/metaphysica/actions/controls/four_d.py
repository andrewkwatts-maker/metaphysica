"""Controls: textbook 4D physics, each computed in sympy with a failing control.

References: Carroll, Spacetime and Geometry (2004), ch. 7 (Schwarzschild),
ch. 7.1 and 8 (weak field, FLRW); Peskin and Schroeder (1995) ch. 2 (Maxwell)
and ch. 4 (dimension counting). Conventions: mostly plus.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from fractions import Fraction

import sympy as sp

from metaphysica.actions.correspondence import Correspondence
from metaphysica.actions.curvature import einstein_tensor, ricci_tensor
from metaphysica.actions.dimensions import check_action
from metaphysica.actions.model import INPUT, Action, Coefficient, Field, Term

T, R, TH, PH = sp.symbols("t r theta phi")
M = sp.Symbol("M", positive=True)
X4_ = X4 = sp.symbols("x0 x1 x2 x3")
CT, CX, CY, CZ = sp.symbols("t x y z")


def _zero(matrix) -> bool:
    return all(sp.simplify(e) == 0 for e in matrix)


def _schwarzschild(power: int):
    f = 1 - 2 * M / R
    g = sp.diag(-f, f ** -power, R ** 2, R ** 2 * sp.sin(TH) ** 2)
    ric = ricci_tensor(g, [T, R, TH, PH], simp=sp.simplify)
    return ric


def _schwarzschild_compute(power: int):
    ric = _schwarzschild(power)
    return str(ric.applyfunc(sp.simplify).tolist()), _zero(ric), "R_mn = 0 for g_rr = f^-%d" % power


def _weak_field_residual(sign: int):
    eps = sp.Symbol("eps")
    phi = sp.Function("Phi")(CX, CY, CZ)
    g = sp.diag(-(1 + 2 * sign * eps * phi), *([1 - 2 * sign * eps * phi] * 3))
    g00 = einstein_tensor(g, [CT, CX, CY, CZ])[0, 0]
    first = sp.simplify(sp.diff(g00, eps).subs(eps, 0))
    lap = sum(sp.diff(phi, c, 2) for c in (CX, CY, CZ))
    return sp.simplify(first - 2 * lap)


def _weak_field_compute(sign: int):
    res = _weak_field_residual(sign)
    return str(res), res == 0, "G_00 = 2 lap(Phi); with G_00 = 8 pi G rho gives lap(Phi) = 4 pi G rho"


def _flrw_residual(spatial_power: int):
    a = sp.Function("a")(T)
    g = sp.diag(-1, a ** spatial_power, a ** spatial_power, a ** spatial_power)
    g00 = einstein_tensor(g, [T, CX, CY, CZ])[0, 0]
    return sp.simplify(g00 - 3 * (sp.diff(a, T) / a) ** 2)


def _flrw_compute(spatial_power: int):
    res = _flrw_residual(spatial_power)
    ok = res == 0
    if ok:
        G, rho, H = sp.symbols("G rho H", positive=True)
        h2 = sp.solve(sp.Eq(3 * H ** 2, 8 * sp.pi * G * rho), H ** 2)[0]
        ok = sp.simplify(h2 - 8 * sp.pi * G * rho / 3) == 0
    return str(res), ok, "G_00 = 3 (adot/a)^2, so H^2 = 8 pi G rho / 3"


def _maxwell_residual(control: bool, eta=None):
    eta = sp.diag(-1, 1, 1, 1) if eta is None else eta
    n_dim = eta.shape[0]
    X4 = X4_ if n_dim == 4 else sp.symbols("x0:%d" % n_dim)
    A = [sp.Function("A%d" % i)(*X4) for i in range(n_dim)]
    dA = [[sp.Derivative(A[n], X4[m]) for n in range(n_dim)] for m in range(n_dim)]  # d_m A_n
    def F(m, n):
        return dA[m][n] - dA[n][m]
    def up(m, n):
        return eta[m, m] * eta[n, n] * F(m, n)
    if control:
        lag = -sp.Rational(1, 4) * sum(eta[m, m] * eta[n, n] * dA[m][n] ** 2
                                       for m in range(n_dim) for n in range(n_dim))
    else:
        lag = -sp.Rational(1, 4) * sum(F(m, n) * up(m, n) for m in range(n_dim) for n in range(n_dim))
    out = []
    for n in range(n_dim):
        el = sum(sp.diff(sp.diff(lag, dA[m][n]).doit(), X4[m]) for m in range(n_dim))
        divf = sum(sp.diff(up(m, n), X4[m]) for m in range(n_dim))
        out.append(sp.expand((el + divf).doit()))
    return out


def _maxwell_compute(control: bool):
    res = _maxwell_residual(control)
    return str(res), all(r == 0 for r in res), "E-L of -F^2/4 equals -d_m F^{mn}"


def _fields(D: int):
    return (Field("g", "metric", 1, Fraction(0)), Field("A", "vector", D, Fraction(D - 2, 2)),
            Field("psi", "spinor", 4, Fraction(D - 1, 2)),
            Field("h", "scalar", 1, Fraction(D - 2, 2)))


def standard_model_like_action() -> Action:
    mpl = Coefficient("M_Pl^2", Fraction(2), INPUT, "input:M_Pl")
    one = Coefficient("1/4", Fraction(0), INPUT, "convention")
    unit = Coefficient("1", Fraction(0), INPUT, "convention")
    lam = Coefficient("lambda", Fraction(0), INPUT, "input:lambda")
    terms = (Term("eh", mpl, ("R",)), Term("maxwell", one, ("A", "d", "A", "d")),
             Term("dirac", unit, ("psi", "psi", "d")), Term("quartic", lam, ("h",) * 4))
    return Action("sm_like_4d", 4, (3, 1), _fields(4), terms)


def six_d_quartic_action() -> Action:
    lam = Coefficient("lambda", Fraction(0), INPUT, "input:lambda")
    return Action("phi4_6d", 6, (5, 1), _fields(6), (Term("quartic", lam, ("h",) * 4),))


def _dim_compute(action: Action):
    checks = check_action(action)
    bad = [c.id for c in checks if not c.holds]
    return "failed: %s" % bad if bad else "all hold", not bad, "EH + Maxwell + Dirac + Higgs"


REF_CARROLL = "Carroll, Spacetime and Geometry (2004), ch. 5-8"
REF_PS = "Peskin & Schroeder (1995), ch. 2 and 4"


def correspondences():
    return (
        Correspondence("schwarzschild_ricci_flat", "4D GR", REF_CARROLL,
                       lambda: _schwarzschild_compute(1)),
        Correspondence("weak_field_poisson", "4D GR", REF_CARROLL,
                       lambda: _weak_field_compute(1)),
        Correspondence("flrw_friedmann", "4D GR", REF_CARROLL, lambda: _flrw_compute(2)),
        Correspondence("maxwell_equations", "4D Maxwell", REF_PS, lambda: _maxwell_compute(False)),
        Correspondence("dimensions_4d", "4D action", REF_PS,
                       lambda: _dim_compute(standard_model_like_action())),
    )


def controls():
    return (
        Correspondence("schwarzschild_control_wrong_grr", "4D GR", REF_CARROLL,
                       lambda: _schwarzschild_compute(2)),
        Correspondence("weak_field_control_wrong_sign", "4D GR", REF_CARROLL,
                       lambda: _weak_field_compute(-1)),
        Correspondence("flrw_control_a_not_a_squared", "4D GR", REF_CARROLL,
                       lambda: _flrw_compute(1)),
        Correspondence("maxwell_control_scalar_lagrangian", "4D Maxwell", REF_PS,
                       lambda: _maxwell_compute(True)),
        Correspondence("dimensions_control_phi4_in_6d", "6D action", REF_PS,
                       lambda: _dim_compute(six_d_quartic_action())),
    )
