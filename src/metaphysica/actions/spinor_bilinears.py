"""Bilinears of one Weyl spinor in signature (s, t): which survive, by rule and by explicit gammas.

Generic and theory-agnostic. Four bilinears of one anticommuting Weyl spinor Psi:
- hermitian kinetic Psi-bar Gamma^M D_M Psi and hermitian mass Psi-bar Psi, with the Dirac
  adjoint Psi-bar = Psi^dagger A, A the product of the t timelike gammas (the Spin(s, t)
  invariant sesquilinear form). A Gamma_* = (-1)^t Gamma_* A in even D, so A pairs equal
  chiralities iff t is even: the kinetic block survives iff t is odd, the mass block iff t is
  even.
- holomorphic kinetic Psi^T C Gamma^M D_M Psi and holomorphic mass Psi^T C Psi. C pairs equal
  chiralities iff D = 0 mod 4 (then C Gamma^M pairs opposite ones), and C Gamma^M pairs equal
  chiralities iff D = 2 mod 4. On one chirality the surviving matrix is symmetric for
  D = 0, 2 mod 8 and antisymmetric for D = 4, 6 mod 8, for either choice of C (the two differ
  by Gamma_*, which is +-1 on one chirality). For anticommuting Psi a symmetric kinetic matrix
  survives and an antisymmetric one is a total derivative, (1/2) d(Psi^T M Psi); an
  antisymmetric mass matrix survives and a symmetric one vanishes identically.
Verdicts: "nonzero", "zero", "total_derivative".
References: Van Proeyen, "Tools for supersymmetry" (1999), Tables 1 and 3; Polchinski vol. 2
App. B; Bars, two-time physics (the hermitian Weyl kinetic term vanishes at t = 2).
`explicit_weyl_bilinears` computes the same from sparse gamma matrices and is the test oracle
(`docs/plan/programme/evidence/weyl_bilinear.py`, `weyl_holomorphic.py`).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from functools import reduce
from typing import Dict, List

from metaphysica.actions.model import CURVATURE, DERIVATIVE, HERMITIAN, HOLOMORPHIC, Action, Check

NONZERO, ZERO, TOTAL_DERIVATIVE = "nonzero", "zero", "total_derivative"
FORMS = (HERMITIAN, HOLOMORPHIC)
PARTS = ("kinetic", "mass")
C_CHOICES = ("symmetric", "antisymmetric")  # C = product of the symmetric or antisymmetric gammas
REF = "Van Proeyen, Tools for supersymmetry (1999), Tables 1, 3; Polchinski vol. 2 App. B"
_TOL = 1e-12


def _dimension(s: int, t: int) -> int:
    if s < 0 or t < 0 or s + t < 2:
        raise ValueError("signature (%d, %d) is not a spacetime" % (s, t))
    if (s + t) % 2:
        raise ValueError("no Weyl spinor in odd dimension D = %d" % (s + t))
    return s + t


def c_pairs_equal_chirality(D: int) -> bool:
    """C maps a chirality to itself under transposition iff D = 0 mod 4 (else C Gamma^M does)."""
    return D % 4 == 0


def weyl_block_symmetric(D: int) -> bool:
    """The matrix surviving on one chirality (C or C Gamma^M) is symmetric iff D = 0, 2 mod 8."""
    return D % 8 in (0, 2)


def _verdict(survives: bool, symmetric: bool, kinetic: bool) -> str:
    if not survives:
        return ZERO
    if kinetic:
        return NONZERO if symmetric else TOTAL_DERIVATIVE
    return ZERO if symmetric else NONZERO


def weyl_bilinears(s: int, t: int) -> Dict[str, Dict[str, str]]:
    """{form: {part: verdict}} for one anticommuting Weyl spinor of Cl(s, t), by rule."""
    D = _dimension(s, t)
    sym = weyl_block_symmetric(D)
    c_same = c_pairs_equal_chirality(D)
    return {
        HERMITIAN: {"kinetic": NONZERO if t % 2 else ZERO, "mass": ZERO if t % 2 else NONZERO},
        HOLOMORPHIC: {"kinetic": _verdict(not c_same, sym, True),
                      "mass": _verdict(c_same, sym, False)},
    }


# --- explicit oracle ---------------------------------------------------------------------

def _gammas(s: int, t: int):
    """Sparse gammas of Cl(s, t), mostly plus (timelike ones square to -1), and Gamma_*."""
    import numpy as np
    import scipy.sparse as sp

    sx = sp.csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex))
    sy = sp.csr_matrix(np.array([[0, -1j], [1j, 0]], dtype=complex))
    sz = sp.csr_matrix(np.array([[1, 0], [0, -1]], dtype=complex))
    i2 = sp.identity(2, dtype=complex, format="csr")
    kron = lambda ms: reduce(lambda a, b: sp.kron(a, b, format="csr"), ms)  # noqa: E731
    k = (s + t) // 2
    eu = []
    for i in range(k):
        eu.append(kron([sz] * i + [sx] + [i2] * (k - i - 1)))
        eu.append(kron([sz] * i + [sy] + [i2] * (k - i - 1)))
    return eu[:s] + [1j * g for g in eu[s:]], kron([sz] * k)


def _amax(m) -> float:
    m = m.tocsr()
    return float(abs(m).max()) if m.nnz else 0.0


def _sym_class(m) -> str:
    if _amax(m) < _TOL:
        return "zero"
    if _amax(m - m.T) < _TOL:
        return "sym"
    if _amax(m + m.T) < _TOL:
        return "antisym"
    raise ArithmeticError("block is neither symmetric nor antisymmetric")


def _charge_conjugation(gam: List, choice: str):
    """C from the chosen gammas; checks C Gamma C^-1 = eta Gamma^T with one eta for every M."""
    if choice not in C_CHOICES:
        raise ValueError("C choice %r; use one of %s" % (choice, C_CHOICES))
    want_sym = choice == "symmetric"
    fac = [g for g in gam if (_amax(g - g.T) < _TOL) == want_sym]
    C = reduce(lambda a, b: a @ b, fac)
    cinv = C.getH()  # a product of unitary matrices
    eta = 1 if _amax(C @ gam[0] @ cinv - gam[0].T) < _TOL else -1
    for g in gam:
        if _amax(C @ g @ cinv - eta * g.T) > _TOL:
            raise ArithmeticError("C Gamma C^-1 = eta Gamma^T fails")
    return C


def _holomorphic(gam, pl, choice: str) -> Dict[str, str]:
    C = _charge_conjugation(gam, choice)
    kin = {_sym_class(pl.T @ C @ g @ pl) for g in gam}
    if len(kin) != 1:
        raise ArithmeticError("kinetic blocks differ between directions: %s" % sorted(kin))
    k, m = kin.pop(), _sym_class(pl.T @ C @ pl)
    return {"kinetic": _verdict(k != "zero", k == "sym", True),
            "mass": _verdict(m != "zero", m == "sym", False)}


def explicit_weyl_bilinears(s: int, t: int, c_choice: str = "symmetric") -> Dict[str, Dict[str, str]]:
    """The same verdicts as `weyl_bilinears`, from explicit sparse gamma matrices (oracle)."""
    import scipy.sparse as sp

    _dimension(s, t)
    gam, chi = _gammas(s, t)
    n = gam[0].shape[0]
    pl = (sp.identity(n, dtype=complex, format="csr") + chi) / 2
    adj = reduce(lambda a, b: a @ b, gam[s:]) if t else sp.identity(n, dtype=complex)
    kin = max(_amax(pl.getH() @ adj @ g @ pl) for g in gam)
    mass = _amax(pl.getH() @ adj @ pl)
    return {
        HERMITIAN: {"kinetic": NONZERO if kin > _TOL else ZERO,
                    "mass": NONZERO if mass > _TOL else ZERO},
        HOLOMORPHIC: _holomorphic(gam, pl, c_choice),
    }


# --- action check ------------------------------------------------------------------------

def _one_weyl_bilinear(action: Action, term):
    """The Weyl field of a bilinear in one Weyl spinor, or None for any other term."""
    fields = [f for f in term.factors if f not in (CURVATURE, DERIVATIVE)]
    if CURVATURE in term.factors or len(fields) != 2 or len(set(fields)) != 1:
        return None
    f = action.field(fields[0])
    return f if f.kind == "spinor" and f.chirality == "weyl" else None


def check_spinor_bilinears(action: Action) -> List[Check]:
    """Each kinetic or mass bilinear of one Weyl spinor must survive in the action's signature.

    The term's `bilinear` names the form; None means the hermitian Psi-bar form.
    """
    s, t = action.signature
    out = []
    for term in action.terms:
        f = _one_weyl_bilinear(action, term)
        if f is None:
            continue
        form = term.bilinear or HERMITIAN
        part = "kinetic" if term.derivatives > 0 or DERIVATIVE in term.factors else "mass"
        verdict = weyl_bilinears(s, t)[form][part]
        out.append(Check("spinor_bilinear:%s:%s" % (action.id, term.id), verdict,
                         verdict == NONZERO, True, REF,
                         "%s %s bilinear of the Weyl field %s in signature (%d, %d): %s"
                         % (form, part, f.name, s, t, verdict)))
    return out
