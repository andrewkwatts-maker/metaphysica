"""Gravity checks computed from the action's R term, signature and convention.

Textbook references: Carroll, Spacetime and Geometry (2004), ch. 5-8 and 7.4;
Myers and Perry (1986) for the D-dimensional vacuum solution.
Engine normalisation: the R term is s (M^(D-2)/2) R with sign s = Term.sign.
The Einstein-Hilbert sign that gives attractive gravity is +1 for a mostly-plus metric
and -1 for mostly minus (R changes sign under g -> -g); both are computed below.
Extra time directions (q > 1) are flat spectators.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import List, Tuple

import sympy as sp

from metaphysica.actions.curvature import ricci_scalar, ricci_tensor
from metaphysica.actions.established import EstablishedCheck
from metaphysica.actions.model import MOSTLY_MINUS, Action, Term

REF_C = "Carroll, Spacetime and Geometry (2004), ch. 5-8"
REF_MP = "Myers & Perry, Ann. Phys. 172 (1986) 304 (D-dim Schwarzschild)"
REF_GW = "Carroll (2004) ch. 7.2-7.3; LIGO/Virgo GW170817 (speed of gravity = c)"
MAX_SCHWARZSCHILD_DIM = 13  # D=13 takes ~40 s; D=26 over 20 min (sphere Ricci in sympy)
T_ = sp.Symbol("t")
EPS = sp.Symbol("eps")


def gravity_term(action: Action) -> Term:
    return next(t for t in action.terms if t.factors == ("R",) and not t.open)


def _pq(action: Action) -> Tuple[int, int]:
    p, q = action.signature
    if p < 3:
        raise ValueError("gravity checks need at least 3 space dimensions, got %d" % p)
    return p, q


def _ricci_entry(g, coords, n, s, v):
    val = 0
    for r in range(n):
        for expr, var, sign in ((g(r, v, s), r, 1), (g(r, r, s), v, -1)):
            if expr != 0:
                val += sign * sp.diff(expr, coords[var])
        for lam in range(n):
            x, y = g(r, r, lam), g(lam, v, s)
            if x != 0 and y != 0:
                val += x * y
            x, y = g(r, v, lam), g(lam, r, s)
            if x != 0 and y != 0:
                val -= x * y
    return val


def sparse_diag_ricci(entries, coords):
    """Ricci tensor of a diagonal metric using only the nonzero Christoffels (same
    convention as `curvature.ricci_tensor`); fast enough for D = 26."""
    n = len(entries)
    gam = {}  # (r, min(a, b), max(a, b)) -> Gamma^r_{ab}
    for a in range(n):
        for c in range(n):
            d = sp.diff(entries[a], coords[c])
            if d == 0:
                continue
            gam[a, min(a, c), max(a, c)] = sp.factor(d / (2 * entries[a]))
            if a != c:
                gam[c, a, a] = sp.factor(-d / (2 * entries[c]))
    g = lambda r, a, b: gam.get((r, min(a, b), max(a, b)), 0)
    ric = sp.zeros(n, n)
    for s in range(n):
        for v in range(s, n):
            ric[s, v] = ric[v, s] = _ricci_entry(g, coords, n, s, v)
    return ric


def _is_zero(expr) -> bool:
    """Exact zero test of an explicit rational function: evaluate in exact rationals at
    seeded points (a nonzero rational function vanishing at all of them is negligible)."""
    rng = random.Random(11)
    syms = sorted(expr.free_symbols, key=str)
    for _ in range(4):
        pt = {x: sp.Rational(rng.randint(2, 9), rng.randint(10, 19)) for x in syms}
        if sp.nsimplify(expr.subs(pt)) != 0:
            return False
    return True


def _diag_ricci(entries, coords):
    g = sp.diag(*entries)
    inv = sp.diag(*[1 / e for e in entries])
    return g, inv, sparse_diag_ricci(entries, coords)


def _einstein_diag(entries, coords):
    g, inv, ric = _diag_ricci(entries, coords)
    rs = sp.simplify(sum(inv[a, a] * ric[a, a] for a in range(len(entries))))
    return ric - g * rs / 2


def eh_sign(action: Action) -> int:
    """s * c: the term sign times the curvature factor of the action's convention.

    c is computed: the sign of the Ricci scalar of the convention's metric over that of
    the mostly-plus metric of the same geometry."""
    t, x1, x2 = sp.symbols("t x1 x2")
    a = sp.Function("a")(t)
    plus = sp.diag(-1, a ** 2, a ** 2)
    metric = -plus if action.convention == MOSTLY_MINUS else plus
    r_conv = ricci_scalar(metric, [t, x1, x2], metric.inv(), sp.simplify)
    r_plus = ricci_scalar(plus, [t, x1, x2], plus.inv(), sp.simplify)
    return gravity_term(action).sign * int(sp.sign(sp.simplify(r_conv / r_plus)))


def _sphere(radius, n):
    """Entries of the metric of S^n scaled by radius^2 in rational coordinates x_k = cos(th_k):
    g_kk = radius^2 prod_{j<k}(1-x_j^2) / (1-x_k^2). Rational, so cancellation is exact."""
    xs = sp.symbols("u1:%d" % (n + 1))
    ents, prod = [], radius ** 2
    for k in range(n):
        ents.append(sp.cancel(prod / (1 - xs[k] ** 2)))
        prod = prod * (1 - xs[k] ** 2)
    return ents, list(xs)


def schwarzschild_compute(action: Action, power: int = 1):
    """Ricci tensor of the D-dim Schwarzschild-Tangherlini metric (extra times flat)."""
    p, q = _pq(action)
    r, mu = sp.symbols("r mu", positive=True)
    f = 1 - (mu / r) ** (p - 2)
    sph, th = _sphere(r, p - 1)
    ents = [-f] + [-1] * (q - 1) + [f ** -power] + sph
    coords = [T_] + list(sp.symbols("y1:%d" % q)) + [r] + th
    _, _, ric = _diag_ricci(ents, coords)
    bad = [i for i in range(len(ents)) if not _is_zero(ric[i, i])]
    return ("R_ab = 0" if not bad else "R_ab != 0 at %s" % bad[:4]), not bad, \
        "D=%d vacuum, g_rr = f^-%d, f = 1-(mu/r)^%d" % (action.dim, power, p - 2)


def weak_field(action: Action, psi_scale: int = 0):
    """(G_12 at first order, G_00 minus the Poisson form) for the static ansatz."""
    p, q = _pq(action)
    x = sp.symbols("x1:%d" % (p + 1))
    phi, psi = (sp.Function(n)(x[0], x[1]) for n in ("Phi", "Psi"))
    coords = [T_] + list(sp.symbols("y1:%d" % q)) + list(x)
    ents = [-(1 + 2 * EPS * phi)] + [-1] * (q - 1) + [1 - 2 * EPS * psi] * p
    ein = _einstein_diag(ents, coords)
    lin = lambda e: sp.simplify(sp.diff(e, EPS).subs(EPS, 0))
    g12, g00 = lin(ein[q, q + 1]), lin(ein[0, 0])
    psi_sol = phi / (p - 2 + psi_scale)
    g12 = sp.simplify(g12.subs(psi, psi_sol).doit())
    lap = sum(sp.diff(phi, c, 2) for c in x[:2])
    g00 = sp.simplify(g00.subs(psi, psi_sol).doit() - sp.Rational(p - 1, p - 2) * lap)
    return g12, g00


def weak_field_compute(action: Action, psi_scale: int = 0):
    g12, g00 = weak_field(action, psi_scale)
    term, p = gravity_term(action), action.signature[0]
    s = eh_sign(action)
    dim_ok = Fraction(term.coefficient.mass_dim) == action.dim - 2
    g_n = sp.Rational(p - 2, p - 1) / (4 * sp.pi) * s  # times 1/M^(D-2)
    ok = g12 == 0 and g00 == 0 and s == 1 and dim_ok
    if action.dim == 4 and ok:
        ok = sp.simplify(g_n - 1 / (8 * sp.pi)) == 0
    detail = ("G_12=%s, G_00-%s lap Phi=%s; sign s*c=%d; coefficient dim %s vs D-2=%d; "
              "G_N = %s / M^%d" % (g12, sp.Rational(p - 1, p - 2), g00, s,
                                   term.coefficient.mass_dim, action.dim - 2, g_n,
                                   action.dim - 2))
    return "G_N = %s" % g_n, ok, detail


def flrw_compute(action: Action, spatial_power: int = 2):
    p, q = _pq(action)
    a = sp.Function("a")(T_)
    coords = [T_] + list(sp.symbols("y1:%d" % q)) + list(sp.symbols("x1:%d" % (p + 1)))
    ents = [-1] * q + [a ** spatial_power] * p
    ein = _einstein_diag(ents, coords)
    want = sp.Rational(p * (p - 1), 2) * (sp.diff(a, T_) / a) ** 2
    res = sp.simplify(ein[0, 0] - want)
    s = eh_sign(action)
    return str(res), res == 0 and s == 1, (
        "G_00 = p(p-1)/2 H^2 with p=%d, sign s*c=%d; H^2 = 2 rho/(p(p-1) M^(D-2)) "
        "(4D: 8 pi G rho/3)" % (p, s))


def _wave_speed_sq(c2):
    t, x, y, z, k, w, e = sp.symbols("t x y z k omega e")
    h = sp.exp(sp.I * (k * z - w * t))
    g = sp.Matrix([[-c2, 0, 0, 0], [0, 1, e * h, 0], [0, e * h, 1, 0], [0, 0, 0, 1]])
    r12 = ricci_tensor(g, [t, x, y, z], g.inv())[1, 2]
    lin = sp.simplify(sp.diff(r12, e).subs(e, 0) / h)
    return sp.simplify(sp.solve(sp.Eq(lin, 0), w ** 2)[0] / k ** 2)


def gravitational_wave_compute(action: Action, c2=1):
    """Speed of the linearised TT wave (4D block; the Ricci of a product with flat space is
    blockwise) and the polarisation count of symmetric traceless tensors on D-2 dims."""
    _pq(action)
    v2 = _wave_speed_sq(c2)
    n = action.dim - 2
    pols = len([(i, j) for i in range(n) for j in range(i, n)]) - 1
    want = action.dim * (action.dim - 3) // 2
    return "v^2=%s, polarisations=%d" % (v2, pols), v2 == 1 and pols == want, \
        "R_12 linear in h gives omega^2 = %s k^2 (massless iff 1); D(D-3)/2 = %d" % (v2, want)


def checks() -> List[EstablishedCheck]:
    return [
        EstablishedCheck("gr_schwarzschild_vacuum", "gravity", REF_MP, ("gravity",),
                         schwarzschild_compute, MAX_SCHWARZSCHILD_DIM),
        EstablishedCheck("gr_weak_field_poisson", "gravity", REF_C, ("gravity",),
                         weak_field_compute),
        EstablishedCheck("gr_flrw_friedmann", "gravity", REF_C, ("gravity",), flrw_compute),
        EstablishedCheck("gr_waves_massless_speed_c", "gravity", REF_GW, ("gravity",),
                         gravitational_wave_compute),
    ]


def controls() -> List[EstablishedCheck]:
    return [
        EstablishedCheck("control_schwarzschild_wrong_grr", "gravity", REF_MP, ("gravity",),
                         lambda a: schwarzschild_compute(a, 2)),
        EstablishedCheck("control_weak_field_wrong_potential_ratio", "gravity", REF_C,
                         ("gravity",), lambda a: weak_field_compute(a, 1)),
        EstablishedCheck("control_flrw_a_not_a_squared", "gravity", REF_C, ("gravity",),
                         lambda a: flrw_compute(a, 1)),
        EstablishedCheck("control_waves_speed_not_c", "gravity", REF_GW, ("gravity",),
                         lambda a: gravitational_wave_compute(a, sp.Rational(121, 100))),
    ]
