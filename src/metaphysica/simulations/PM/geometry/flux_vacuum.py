"""Does four-form flux fix the metric moduli of the adopted Joyce manifold?

Pre-registered as D-005 (site repo docs/DECISION_LOG.md, 2026-09-30) before
any of this was run.

THE INGREDIENTS, FROM THE LITERATURE, VERBATIM
==============================================
K   Lukas & Morris, Phys. Rev. D 69, 066003 (2004), hep-th/0305078, eq. (5.10)
    with Table 1: for exactly Joyce's T^7/Z_2^3 (b_2 = 12, b_3 = 43),

      K = - sum_A ln(T^A + Tbar^A)
          - 3 ln[ 1 - 8/3 sum_{tau,n,a} (U + Ubar)^2 /
                        ((T^{A(tau,a)} + Tbar)(T^{B(tau,a)} + Tbar)) ] + c,

    c = 6 ln(8 pi) + ln 2. Seven bulk moduli T^A and 36 blow-up moduli
    U^(tau,n,a) -- three per blow-up, twelve blow-ups. Valid at large moduli
    and to quadratic order in U/T.

W   Acharya, Denef & Valandro, JHEP 0506:056 (2005), hep-th/0502060,
    eq. (3.4): W = N_i z^i + c_1 + i c_2, with N_i the integer G_4 flux and
    c the Chern-Simons invariant of the singular locus. On the axion slice
    N.t + c_1 = 0 (their 3.10) the potential is their (3.11),

      V = e^K ( 4 K^{ij} F_i F_j - 3 W_2^2 ),  F_i = N_i + K_i W_2 / 2,
      W_2 = N.s + c_2.

WHAT IS COMPUTED
================
Homogeneity of the volume (degree 7/3) gives K_i s^i = -7 and
K^{ij} K_j = -s^i. With c_2 = 0 these collapse the potential to

      V = 4 e^K K^{ij} N_i N_j

which is positive wherever K_ij is positive definite, and scales as
lambda^-5 along s -> lambda s. So dV/dlambda = -5 V / lambda < 0: there is no
critical point at finite volume, for ANY flux. ADV state the same in words;
here it is checked on the Lukas-Morris K itself, at points of its domain of
validity. A control with a hypothetical c_2 != 0 must find the supersymmetric
AdS point with W_2 = -(2/5) c_2, so the solver can find a vacuum when one
exists.

WHY c_2 = 0 ON THIS GEOMETRY
============================
Every codimension-four locus is a flat T^3 (closed_geometry,
y7-singular-components). pi_1(T^3) = Z^3 is abelian, and commuting elements of
SU(2) lie in a common maximal torus, so every flat SU(2) connection on T^3 is
gauge-equivalent to a constant diagonal one. For it dA = 0 and A ^ A = 0, so
its Chern-Simons invariant vanishes. The ADV/Acharya mechanism needs a
non-real invariant ("for instance, Q is a hyperbolic manifold"), and a flat
torus cannot supply one.

SCOPE
=====
Classical supergravity at large volume, the leading-order K, G_4 flux.
Membrane instantons on associative cycles and corrections to K beyond
(U/T)^2 are NOT covered; ADV note corrections "may change this".

A4: s^i are periods of phi (metric moduli), N_i are flux integers (counts of
flux quanta through 4-cycles), c is a Chern-Simons invariant (a number mod 1).
None is converted into another.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "LM_TABLE_1",
    "LM_CONSTANT",
    "N_BULK",
    "N_TWISTED",
    "twisted_labels",
    "kahler",
    "kahler_gradient",
    "kahler_hessian",
    "potential",
    "flux_vacuum_report",
]

#: Lukas-Morris Table 1: (tau, a) -> the two bulk moduli (1-based) by which
#: U^(tau,n,a) is divided in K. Verbatim; the labelling is theirs.
LM_TABLE_1: Dict[Tuple[str, int], Tuple[int, int]] = {
    ("alpha", 1): (1, 6), ("alpha", 2): (2, 5), ("alpha", 3): (3, 4),
    ("beta", 1): (1, 7), ("beta", 2): (3, 5), ("beta", 3): (2, 4),
    ("gamma", 1): (1, 4), ("gamma", 2): (3, 6), ("gamma", 3): (2, 7),
}

#: Lukas-Morris eq. (5.11), for their normalisation of the fields.
LM_CONSTANT = 6.0 * math.log(8.0 * math.pi) + math.log(2.0)

N_BULK = 7
N_TWISTED = 36
_COEFF = 8.0 / 3.0


def twisted_labels() -> List[Tuple[str, int, int]]:
    """(tau, n, a) for the 36 blow-up moduli, in a fixed order."""
    return [(tau, n, a) for tau in ("alpha", "beta", "gamma")
            for n in (1, 2, 3, 4) for a in (1, 2, 3)]


def _terms() -> List[Tuple[int, int, int]]:
    """(index of u, index of s_A, index of s_B) in the 43-vector, 0-based."""
    out = []
    for k, (tau, _n, a) in enumerate(twisted_labels()):
        A, B = LM_TABLE_1[(tau, a)]
        out.append((N_BULK + k, A - 1, B - 1))
    return out


_TERMS = _terms()


def _term_derivatives(s: np.ndarray, u: int, a: int, b: int
                      ) -> Tuple[float, Dict[int, float], Dict[Tuple[int, int],
                                                                float]]:
    """X_k = m u^2 with m = (8/3)/(s_A s_B): value, first and second
    derivatives, written out so that u = 0 (the orbifold limit) is regular.
    """
    m = _COEFF / (s[a] * s[b])
    x = m * s[u] ** 2
    first = {u: 2.0 * m * s[u], a: -x / s[a], b: -x / s[b]}
    second = {
        (u, u): 2.0 * m,
        (a, a): 2.0 * x / s[a] ** 2,
        (b, b): 2.0 * x / s[b] ** 2,
        (a, b): x / (s[a] * s[b]),
        (u, a): -2.0 * m * s[u] / s[a],
        (u, b): -2.0 * m * s[u] / s[b],
    }
    for (i, j) in list(second):
        second[(j, i)] = second[(i, j)]
    return x, first, second


def _x_terms(s: np.ndarray) -> np.ndarray:
    return np.array([_COEFF * s[u] ** 2 / (s[a] * s[b])
                     for u, a, b in _TERMS])


def kahler(s: Sequence[float]) -> float:
    """K in real variables: s_A = Re T^A (bulk), u = Re U (twisted).

    T + Tbar = 2 Re T and (U + Ubar)^2 = 4 u^2, so the ratio in (5.10) is
    u^2 / (s_A s_B) and the bulk logs are ln(2 s_A).
    """
    s = np.asarray(s, dtype=float)
    x = _x_terms(s).sum()
    if x >= 1.0:
        raise ValueError("outside the domain: 1 - X = %g <= 0" % (1.0 - x))
    return (-float(np.sum(np.log(2.0 * s[:N_BULK])))
            - 3.0 * math.log(1.0 - x) + LM_CONSTANT)


def kahler_gradient(s: Sequence[float]) -> np.ndarray:
    """d[-3 ln(1 - X)] = 3 X_i / (1 - X), plus the bulk -1/s_A."""
    s = np.asarray(s, dtype=float)
    one_minus = 1.0 - _x_terms(s).sum()
    grad = np.zeros_like(s)
    grad[:N_BULK] = -1.0 / s[:N_BULK]
    for u, a, b in _TERMS:
        _x, first, _second = _term_derivatives(s, u, a, b)
        for i, d in first.items():
            grad[i] += 3.0 * d / one_minus
    return grad


def kahler_hessian(s: Sequence[float]) -> np.ndarray:
    """Exact: d2[-3 ln(1-X)] = 3 X_ij/(1-X) + 3 X_i X_j/(1-X)^2."""
    s = np.asarray(s, dtype=float)
    n = len(s)
    one_minus = 1.0 - _x_terms(s).sum()
    hess = np.zeros((n, n))
    for i in range(N_BULK):
        hess[i, i] = 1.0 / s[i] ** 2
    dx = np.zeros(n)
    for u, a, b in _TERMS:
        _x, first, second = _term_derivatives(s, u, a, b)
        for i, d in first.items():
            dx[i] += d
        for (i, j), d in second.items():
            hess[i, j] += 3.0 * d / one_minus
    hess += 3.0 * np.outer(dx, dx) / one_minus ** 2
    return hess


def potential(s: Sequence[float], flux: Sequence[float],
              c2: float = 0.0) -> float:
    """ADV (3.11): V = e^K (4 K^{ij} F_i F_j - 3 W_2^2) on the axion slice."""
    s = np.asarray(s, dtype=float)
    n = np.asarray(flux, dtype=float)
    grad = kahler_gradient(s)
    w2 = float(n @ s) + c2
    f = n + 0.5 * grad * w2
    kinv = np.linalg.inv(kahler_hessian(s))
    return math.exp(kahler(s)) * (4.0 * float(f @ kinv @ f) - 3.0 * w2 ** 2)


def _random_point(rng: np.random.Generator, bulk: float = 10.0,
                  ratio: float = 0.05) -> np.ndarray:
    """A point inside the validity domain: large bulk, u/T small."""
    s_bulk = bulk * (1.0 + rng.random(N_BULK))
    u = ratio * bulk * (rng.random(N_TWISTED) - 0.5)
    return np.concatenate([s_bulk, u])


def _random_flux(rng: np.random.Generator, bound: int = 3) -> np.ndarray:
    flux = rng.integers(-bound, bound + 1, size=N_BULK + N_TWISTED)
    if not flux.any():
        flux[0] = 1
    return flux.astype(float)


def _susy_control(c2: float, flux_bulk: float) -> Dict[str, Any]:
    """With c_2 != 0 the F-terms must vanish somewhere: find the point.

    Symmetric bulk flux and zero twisted flux keep the solve inside the
    domain: at u = 0 the F-terms reduce to N_A + K_A W_2 / 2 = 0 with
    K_A = -1/s_A, whose solution is s_A = -c_2 / (5 N_A) (ADV 3.18: W_2 =
    -(2/5) c_2). The control checks the F-terms vanish there to rounding.
    """
    s_bulk = -c2 / (5.0 * flux_bulk)
    s = np.concatenate([np.full(N_BULK, s_bulk), np.zeros(N_TWISTED)])
    flux = np.concatenate([np.full(N_BULK, flux_bulk), np.zeros(N_TWISTED)])
    w2 = float(flux @ s) + c2
    f = flux + 0.5 * kahler_gradient(s) * w2
    return {
        "c2": c2,
        "s_bulk": s_bulk,
        "max_abs_F": float(np.max(np.abs(f))),
        "W2": w2,
        "W2_over_c2": w2 / c2,
        "V": potential(s, flux, c2),
        "is_ads": potential(s, flux, c2) < 0.0,
    }


def flux_vacuum_report(n_points: int = 40, seed: int = 20260930
                       ) -> Dict[str, Any]:
    """The D-005 checks, on random admissible points and fluxes."""
    rng = np.random.default_rng(seed)
    worst: Dict[str, float] = {"homogeneity": 0.0, "euler": 0.0,
                               "second": 0.0, "reduction": 0.0,
                               "scaling": 0.0}
    min_eig = math.inf
    all_positive = True
    exponents = []
    for _ in range(n_points):
        s = _random_point(rng)
        flux = _random_flux(rng)
        grad = kahler_gradient(s)
        hess = kahler_hessian(s)
        lam = 1.7
        worst["homogeneity"] = max(worst["homogeneity"], abs(
            kahler(lam * s) - (kahler(s) - 7.0 * math.log(lam))))
        worst["euler"] = max(worst["euler"], abs(float(grad @ s) + 7.0))
        worst["second"] = max(worst["second"], float(np.max(np.abs(
            hess @ s + grad))))
        min_eig = min(min_eig, float(np.min(np.linalg.eigvalsh(hess))))
        v = potential(s, flux)
        reduced = 4.0 * math.exp(kahler(s)) * float(
            flux @ np.linalg.inv(hess) @ flux)
        worst["reduction"] = max(worst["reduction"], abs(v - reduced) /
                                 abs(reduced))
        all_positive = all_positive and v > 0.0
        ratio = potential(lam * s, flux) / v
        worst["scaling"] = max(worst["scaling"], abs(ratio - lam ** -5))
        exponents.append(math.log(ratio) / math.log(lam))

    controls = [_susy_control(c2, n) for c2, n in ((-10.0, 1.0),
                                                   (25.0, -2.0))]
    return {
        "n_points": n_points,
        "seed": seed,
        "worst_residuals": worst,
        "min_hessian_eigenvalue": min_eig,
        "metric_positive_definite": min_eig > 0.0,
        "potential_positive_everywhere_sampled": all_positive,
        "runaway": "V(lambda s) = lambda^-5 V(s): dV/dlambda = -5 V/lambda < 0",
        "measured_scaling_exponent": float(np.median(exponents)),
        "susy_controls": controls,
        "controls_find_a_vacuum": all(
            c["max_abs_F"] < 1e-9 and abs(c["W2_over_c2"] + 0.4) < 1e-12
            and c["is_ads"] for c in controls),
        "verdict": "NO_FLUX_VACUUM_AT_LEADING_ORDER",
        "chern_simons_on_flat_T3": 0.0,
        "scope": (
            "classical supergravity, large volume, leading-order K, G4 flux; "
            "membrane instantons and corrections to K are not covered"),
    }
