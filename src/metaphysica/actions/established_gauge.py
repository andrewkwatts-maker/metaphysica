"""Gauge checks: Maxwell, Yang-Mills SU(3)xSU(2)xU(1), anomaly cancellation, Higgs mechanism.

All need a closed gauge term; on the PM ladder that term (A4:L_SM) is OPEN, so they are
BLOCKED there. They run on `sm_gauge_action()`, the controls' own action.
References: Peskin and Schroeder (1995) ch. 2, 15, 20, 21; Bilal, arXiv:0802.0634
(anomalies); Georgi, Lie Algebras in Particle Physics (1999).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from fractions import Fraction as Fr
from typing import List, Sequence, Tuple

import sympy as sp

from metaphysica.actions.controls import four_d
from metaphysica.actions.established import EstablishedCheck
from metaphysica.actions.model import INPUT, Action, Coefficient, Term

REF_PS = "Peskin & Schroeder (1995), ch. 2, 15, 20, 21"
REF_AN = "Bilal, arXiv:0802.0634 (anomalies); Peskin & Schroeder ch. 19-20"
REF_GE = "Georgi, Lie Algebras in Particle Physics (1999), ch. 6-7"

# One SM generation as left-handed Weyl fields: (dim SU(3), dim SU(2), hypercharge Y).
SM_GENERATION = (("Q", 3, 2, Fr(1, 6)), ("u^c", 3, 1, Fr(-2, 3)), ("d^c", 3, 1, Fr(1, 3)),
                 ("L", 1, 2, Fr(-1, 2)), ("e^c", 1, 1, Fr(1)))


def sm_gauge_action() -> Action:
    """The 4D SM-like control action plus a closed SU(3)xSU(2)xU(1) gauge term."""
    base = four_d.standard_model_like_action()
    coef = Coefficient("1/4g^2", base.terms[1].coefficient.mass_dim, INPUT, "input:g")
    ym = Term("ym_sm", coef, ("A", "d", "A", "d"))
    return Action("sm_gauge_4d", 4, (3, 1), base.fields, base.terms + (ym,), base.convention)


def maxwell_compute(action: Action, control: bool = False):
    p, q = action.signature
    sign = -1 if action.convention == "mostly_minus" else 1
    eta = sp.diag(*([-sign] * q + [sign] * p))
    res = four_d._maxwell_residual(control, eta)
    return str(res), all(r == 0 for r in res), "E-L of -F^2/4 equals -d_m F^{mn} in D=%d" % action.dim


def _gell_mann() -> List[sp.Matrix]:
    i, o = sp.I, sp.Integer(0)
    m = [sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]]), sp.Matrix([[0, -i, 0], [i, 0, 0], [0, 0, 0]]),
         sp.Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 0]]), sp.Matrix([[0, 0, 1], [0, 0, 0], [1, 0, 0]]),
         sp.Matrix([[0, 0, -i], [0, 0, 0], [i, 0, 0]]), sp.Matrix([[0, 0, 0], [0, 0, 1], [0, 1, 0]]),
         sp.Matrix([[0, 0, 0], [0, 0, -i], [0, i, 0]]),
         sp.Matrix([[1, 0, 0], [0, 1, 0], [0, 0, -2]]) / sp.sqrt(3)]
    return m


def _pauli() -> List[sp.Matrix]:
    return [sp.Matrix([[0, 1], [1, 0]]), sp.Matrix([[0, -sp.I], [sp.I, 0]]),
            sp.Matrix([[1, 0], [0, -1]])]


def structure_defects(gens: Sequence[sp.Matrix], symmetric: bool = False) -> Tuple[int, int, int]:
    """(closure, antisymmetry, Jacobi) defects of f_abc from [T_a,T_b] = i f_abc T_c,
    T = lambda/2 and Tr(T_a T_b) = delta/2. `symmetric` uses anticommutators (control)."""
    t = [g / 2 for g in gens]
    n = len(t)
    f = {}
    for a, b, c in itertools.product(range(n), repeat=3):
        com = t[a] * t[b] + t[b] * t[a] if symmetric else t[a] * t[b] - t[b] * t[a]
        f[a, b, c] = sp.simplify(2 * (com * t[c]).trace() / (sp.I if not symmetric else 1))
    closure = sum(1 for a, b in itertools.product(range(n), repeat=2)
                  if sp.simplify((t[a] * t[b] - t[b] * t[a]) - sp.I * sum(
                      (f[a, b, c] * t[c] for c in range(n)), sp.zeros(*t[0].shape))) != sp.zeros(*t[0].shape))
    anti = sum(1 for k in f if sp.simplify(f[k] + f[k[1], k[0], k[2]]) != 0)
    jac = sum(1 for a, b, c, d in itertools.product(range(n), repeat=4)
              if sp.simplify(sum(f[a, b, e] * f[e, c, d] + f[b, c, e] * f[e, a, d]
                                 + f[c, a, e] * f[e, b, d] for e in range(n))) != 0)
    return closure, anti, jac


def yang_mills_compute(action: Action, symmetric: bool = False):
    bad = {name: structure_defects(g, symmetric)
           for name, g in (("SU(2)", _pauli()), ("SU(3)", _gell_mann()))}
    ok = all(d == (0, 0, 0) for d in bad.values())
    return "defects %s" % bad, ok, "[T_a,T_b] = i f_abc T_c, f antisymmetric, Jacobi; U(1) abelian"


def anomaly_sums(content) -> dict:
    """Left-handed Weyl content -> the six anomaly sums (all must vanish)."""
    y3 = sum(c * w * y ** 3 for _, c, w, y in content)
    grav = sum(c * w * y for _, c, w, y in content)
    su3 = sum(Fr(1, 2) * w * y for _, c, w, y in content if c == 3)
    su2 = sum(Fr(1, 2) * c * y for _, c, w, y in content if w == 2)
    doublets = sum(c for _, c, w, y in content if w == 2)
    return {"U1^3": y3, "grav^2 U1": grav, "SU3^2 U1": su3, "SU2^2 U1": su2,
            "witten_parity": doublets % 2}


def anomaly_compute(action: Action, drop: str = ""):
    content = [f for f in SM_GENERATION if f[0] != drop]
    sums = anomaly_sums(content)
    n3 = sum(w for n, c, w, y in content if c == 3 and not n.endswith("^c"))
    nbar = sum(w for n, c, w, y in content if c == 3 and n.endswith("^c"))
    sums["SU3^3"] = n3 - nbar  # 3 and 3bar contribute +1 and -1 to the cubic index
    return str({k: str(v) for k, v in sums.items()}), all(v == 0 for v in sums.values()), \
        "one generation (x3 identical), Q(3,2,1/6) u^c d^c L e^c"


def higgs_compute(action: Action, doublet: bool = True):
    g, gp, v, mu, lam = sp.symbols("g gp v mu lam", positive=True)
    w = sp.symbols("W1 W2 W3 B", real=True)
    if doublet:
        gens = [m / 2 for m in _pauli()]
        gen = sum((g * w[a] * gens[a] for a in range(3)), sp.zeros(2, 2)) + gp * w[3] * sp.Rational(1, 2) * sp.eye(2)
        vec = sp.Matrix([0, v / sp.sqrt(2)])
    else:  # singlet with Y = 0: no gauge boson couples
        gen, vec = sp.zeros(1, 1), sp.Matrix([v])
    quad = sp.expand((gen * vec).H * (gen * vec))[0]
    mass = sp.hessian(sp.simplify(quad), w) if quad != 0 else sp.zeros(4, 4)
    lam_ = sp.Symbol("lam_")
    eig = sp.roots(sp.Poly(sp.factor(mass.charpoly(lam_).as_expr()), lam_))
    null = int(eig.get(0, 0))
    h = sp.Symbol("h", positive=True)
    vmin = sp.solve(sp.diff(-mu ** 2 * h ** 2 / 2 + lam * h ** 4 / 4, h), h)
    ok = null == 1 and any(sp.simplify(s ** 2 - mu ** 2 / lam) == 0 for s in vmin)
    return "massless gauge bosons=%d, masses^2=%s" % (null, sorted(map(str, eig))), ok, \
        "|D H|^2 on the vev: W+-, Z massive, photon massless; V min at v^2 = mu^2/lam"


def checks() -> List[EstablishedCheck]:
    return [
        EstablishedCheck("gauge_maxwell", "gauge", REF_PS, ("vector_kinetic",), maxwell_compute),
        EstablishedCheck("gauge_yang_mills_su3_su2_u1", "gauge", REF_GE, ("gauge_sm",),
                         yang_mills_compute),
        EstablishedCheck("gauge_anomaly_cancellation", "gauge", REF_AN, ("gauge_sm",),
                         anomaly_compute),
        EstablishedCheck("gauge_higgs_mechanism", "gauge", REF_PS,
                         ("gauge_sm", "scalar_potential"), higgs_compute),
    ]


def controls() -> List[EstablishedCheck]:
    return [
        EstablishedCheck("control_maxwell_scalar_lagrangian", "gauge", REF_PS,
                         ("vector_kinetic",), lambda a: maxwell_compute(a, True)),
        EstablishedCheck("control_yang_mills_symmetric_structure", "gauge", REF_GE,
                         ("gauge_sm",), lambda a: yang_mills_compute(a, True)),
        EstablishedCheck("control_anomaly_missing_e_c", "gauge", REF_AN, ("gauge_sm",),
                         lambda a: anomaly_compute(a, "e^c")),
        EstablishedCheck("control_higgs_singlet", "gauge", REF_PS,
                         ("gauge_sm", "scalar_potential"), lambda a: higgs_compute(a, False)),
    ]
