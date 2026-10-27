"""Matter and reduction checks computed from an Action (and a Reduction).

References: Polchinski, String Theory vol. 2 (1998) app. B (Clifford algebra and spinors in
D dimensions); Peskin and Schroeder (1995) ch. 3 (Dirac equation); Overduin and Wesson,
Phys. Rep. 283 (1997) 303 (Planck-mass relation under reduction).
`reduction.py` supplies `expression_dim`; the mapped expression is compared exactly here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import List

import numpy as np
import scipy.sparse as sps
import sympy as sp

from metaphysica.actions.established import EstablishedCheck
from metaphysica.actions.model import MOSTLY_MINUS, Action
from metaphysica.actions.reduction import Reduction
from metaphysica.actions.established_gravity import gravity_term

REF_POL = "Polchinski, String Theory vol. 2 (1998), app. B; Peskin & Schroeder (1995) ch. 3"
REF_OW = "Overduin & Wesson, Phys. Rep. 283 (1997) 303, sec. 2-3"
REF_CARROLL = "Carroll (2004) ch. 4 (minimal coupling, equivalence principle)"
_PAULI = {"x": sps.csr_matrix([[0, 1], [1, 0]], dtype=complex),
          "y": sps.csr_matrix([[0, -1j], [1j, 0]], dtype=complex),
          "z": sps.csr_matrix([[1, 0], [0, -1]], dtype=complex)}


def euclidean_gammas(D: int) -> List[sps.csr_matrix]:
    """D hermitian matrices with {g_a, g_b} = 2 delta_ab, of size 2^(D//2) (sparse)."""
    m = D // 2
    eye = sps.identity(2, dtype=complex, format="csr")
    out = []
    for j in range(m):
        for axis in ("x", "y"):
            mats = [_PAULI["z"]] * j + [_PAULI[axis]] + [eye] * (m - j - 1)
            out.append(_kron(mats))
    if D % 2:
        out.append(_kron([_PAULI["z"]] * m))
    return out


def _kron(mats):
    acc = mats[0]
    for x in mats[1:]:
        acc = sps.kron(acc, x, format="csr")
    return acc


def lorentzian_gammas(action: Action) -> List[sps.csr_matrix]:
    """{g^a, g^b} = 2 eta^ab for the action's signature and sign convention."""
    p, q = action.signature
    sign = -1 if action.convention == MOSTLY_MINUS else 1
    gam = euclidean_gammas(action.dim)
    out = []
    for i, g in enumerate(gam):
        timelike = i < q
        out.append(g * (1j if timelike != (sign < 0) else 1))
    return out


def clifford_defect(gam, eta) -> float:
    worst, n = 0.0, len(gam)
    for a in range(n):
        for b in range(a, n):
            anti = gam[a] @ gam[b] + gam[b] @ gam[a]
            want = 2 * eta[a] * (a == b) * sps.identity(gam[0].shape[0], format="csr")
            worst = max(worst, abs(anti - want).max())
    return worst


def dirac_compute(action: Action, wrong_gamma_size: bool = False):
    term = next(t for t in action.terms if t.factors.count("d") and not t.open
                and sum(action.field(f).kind == "spinor" for f in t.factors if f != "d") >= 2)
    psi = action.field(next(f for f in term.factors if f != "d"))
    p, q = action.signature
    sign = -1 if action.convention == MOSTLY_MINUS else 1
    eta = [-sign] * q + [sign] * p
    gam = lorentzian_gammas(action)
    defect = clifford_defect(gam, eta)
    rng = random.Random(7)
    k = [rng.randint(-5, 5) for _ in range(action.dim)]
    slash = sum((ki * g for ki, g in zip(k, gam)), sps.csr_matrix(gam[0].shape, dtype=complex))
    k2 = sum(e * ki * ki for e, ki in zip(eta, k))
    disp = abs(slash @ slash - k2 * sps.identity(gam[0].shape[0], format="csr")).max()
    size = gam[0].shape[0] // (2 if psi.chirality == "weyl" else 1)
    size += 1 if wrong_gamma_size else 0
    mass_dim = (Fraction(action.dim) - Fraction(term.coefficient.mass_dim) - 1) / 2
    ok = (defect < 1e-12 and disp < 1e-9 and psi.components == size
          and Fraction(psi.mass_dim) == mass_dim == Fraction(action.dim - 1, 2))
    return ("clifford %.1e, (k.g)^2-k^2 %.1e, components %d vs %d, dim %s" % (
        defect, disp, psi.components, size, psi.mass_dim)), ok, \
        "Dirac eq. massless dispersion k^2 = 0; spinor dimension (D-1)/2 = %s" % mass_dim


def universal_coupling_compute(action: Action):
    metrics = [f.name for f in action.fields if f.kind == "metric"]
    nonmin = [t.id for t in action.terms if "R" in t.factors and len(t.factors) > 1 and not t.open]
    opened = [t.id for t in action.terms if t.open]
    ok = len(metrics) == 1 and not nonmin
    return "metrics=%s, non-minimal R-couplings=%s" % (metrics, nonmin), ok, (
        "one metric couples to every matter term; OPEN terms not examined: %s" % opened)


def _planck_compute(red: Reduction, vol_power: int = 1):
    p_term, c_term = gravity_term(red.parent), gravity_term(red.child)
    vol = sp.Symbol(red.internal.volume_symbol, positive=True)
    psym = sp.Symbol(p_term.coefficient.symbol, positive=True)
    want = psym * vol ** vol_power
    got = red.coefficient_map.get(c_term.coefficient.symbol)
    names = {s.name: s for s in (psym, vol)}
    got = sp.sympify(got, locals=names) if got is not None else None
    dims_ok = (Fraction(p_term.coefficient.mass_dim) == red.parent.dim - 2
               and Fraction(c_term.coefficient.mass_dim) == red.child.dim - 2)
    ok = got is not None and sp.simplify(got - want) == 0 and dims_ok
    return "%s = %s" % (c_term.coefficient.symbol, got), ok, (
        "M_c^(Dc-2) = M^(D-2) Vol; exponents %s and %s vs D-2 = %d and Dc-2 = %d" % (
            p_term.coefficient.mass_dim, c_term.coefficient.mass_dim,
            red.parent.dim - 2, red.child.dim - 2))


def _child_dim_compute(red: Reduction, shift: int = 0):
    want = red.parent.dim - red.internal.dim + shift
    return red.child.dim, red.child.dim == want, "D_child = D - dim(internal) = %d" % want


def reduction_checks(red: Reduction) -> List[EstablishedCheck]:
    """Checks for one reduction; they run on the child action."""
    return [EstablishedCheck("kk_planck_mass_relation:" + red.child.id, "reduction", REF_OW,
                             ("gravity",), lambda a: _planck_compute(red)),
            EstablishedCheck("kk_child_dimension:" + red.child.id, "reduction", REF_OW,
                             ("gravity",), lambda a: _child_dim_compute(red))]


def reduction_controls(red: Reduction) -> List[EstablishedCheck]:
    return [EstablishedCheck("control_planck_volume_squared", "reduction", REF_OW,
                             ("gravity",), lambda a: _planck_compute(red, 2)),
            EstablishedCheck("control_child_dimension_off_by_one", "reduction", REF_OW,
                             ("gravity",), lambda a: _child_dim_compute(red, 1))]


def checks() -> List[EstablishedCheck]:
    return [EstablishedCheck("matter_dirac_equation", "matter", REF_POL,
                             ("spinor_kinetic",), dirac_compute),
            EstablishedCheck("matter_universal_coupling", "matter", REF_CARROLL,
                             ("gravity", "spinor_kinetic"), universal_coupling_compute)]


def controls() -> List[EstablishedCheck]:
    return [EstablishedCheck("control_dirac_wrong_component_count", "matter", REF_POL,
                             ("spinor_kinetic",), lambda a: dirac_compute(a, True))]
