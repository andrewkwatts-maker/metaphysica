"""Are the runaway and the slope bound exact in U/T? (C2/C3 scope, PR-2)

Pre-registered as PR-2 in D-017 (site repo docs/DECISION_LOG.md, 2026-10-01)
before any of this was run. Design: the handoff lane note
docs/handoff/2026-10-01/lanes/pr1_pr2_pr3.md, section "PR-2 / PR-3". The
sampling, variants, tolerances and kill below were written before the first
run and are not tuned afterwards.

THE HYPOTHESIS
==============
flux_vacuum (D-005, D-010) measured on the Lukas-Morris K that the flux
potential runs away, V(lambda s) = lambda^-5 V(s), and that its canonical
slope is never below 5 sqrt(2/7). That K is valid only to quadratic order in
U/T. Both results use homogeneity and nothing else: if e^-K is homogeneous of
degree 7 in s (the G2 volume, degree 7/3 in the periods), then

    K(lambda s) = K(s) - 7 ln lambda,    K_i s^i = -7,
    K_ij s^j = -K_i,                      K_ijk s^k = -2 K_ij,

and from them V = 4 e^K K^ij N_i N_j on the axion slice, V ~ lambda^-5, and
s.grad ln V in [-7, -5] with |s|_g = sqrt(7/2). Every x_k = (8/3) u_k^2 /
(s_A s_B) has degree 0, so ANY correction built from the x_k keeps all of it.
Prediction: no identity fails on any variant, and both falsifiers fail.

THE FAMILY
==========
    K = - k sum_A ln(2 s_A) + delta sum_A 1/s_A - 3 ln P(X)
        + beta sum_k w_k h(x_k) + LM_CONSTANT,
    P(X) = 1 - X - a2 X^2 - a3 X^3,     X = sum_k x_k.

(k, delta, a2, a3, beta) = (1, 0, 0, 0, 0) is flux_vacuum's K exactly.
Derivatives are analytic to third order. Per term, in the term's own
variables (u, a, b),

    d_u^i d_a^j d_b^l x = (8/3) D_i (-1)^j j! a^(-1-j) (-1)^l l! b^(-1-l),
    D = (u^2, 2u, 2, 0),

so u = 0 (the orbifold limit) is regular.

VARIANTS (fixed before the first run)
=====================================
  * baseline: flux_vacuum's K;
  * the log replaced: (a2, a3) in {(0.5, 0), (0, 0.5), (-0.5, 0.25), (1, -1)};
  * a degree-0 term added: h in {x^2, x^2/(1+x), e^-x - 1 + x}, each with
    beta = +1 and with beta = -1, weights w_k = (k + 1)/18, k = 0..35
    (non-uniform and deterministic; the design leaves beta and w_k open, so
    both signs are run rather than one being chosen).
Falsifiers, which must FAIL: delta = 1 (a degree -1 term) and bulk weight
k = 1/9 (e^-K of degree 7/9).

SAMPLING (fixed before the first run)
=====================================
Seed 20260930, a fresh generator per variant, so every variant sees the same
draws until its first rejection. Two bands of N_BAND = 60 points each (60
covers flux_vacuum's 40 identity points and acceleration_report's 60):
  A  flux_vacuum._random_point (bulk in [10, 20], u in [-0.25, 0.25]), so
     X <~ 0.06 -- the region flux_vacuum already measured;
  B  the same draw, then X_target ~ U(0.3, 0.6) and u rescaled so that
     X = X_target.
Band B exists because of the trap the design names: at u = 0 no variant
changes K_ij or K_ijk, and band A barely leaves u = 0. A band-B draw is
discarded and redrawn when P(X) <= 0 or K_ij is not positive definite (the
registration keeps the metric positive definite); discards are counted, and
a band gives up after MAX_DRAWS_PER_POINT * N_BAND draws (a guard, not a
tolerance). Flux: flux_vacuum._random_flux (integers in [-3, 3]), drawn after
the point. lambda = 1.7, as in flux_vacuum.

CHECKS AND TOLERANCE
====================
At every point: the four homogeneity identities above; K_ij positive definite
(Cholesky of D K D, D = diag(s_A, sqrt(s_a s_b))); the reduction of ADV (3.11)
to 4 e^K Q; V(lambda s)/V(s) = lambda^-5; V > 0; the canonical slope
>= 5 sqrt(2/7) (1 - 1e-6) (flux_vacuum.acceleration_report's test). Controls:
flux_vacuum's two c_2 != 0 supersymmetric points at u = 0 re-run with the
variant's K, and the same control at the first five band-B points with flux
N = (c_2/5) dK (F = 0 and W_2 = -(2/5) c_2 there exactly when K_i s^i = -7),
both with flux_vacuum's thresholds (|F| < 1e-9, |W_2/c_2 + 2/5| < 1e-12).

"Beyond rounding" (the design: "tolerance 1e-12 scaled"): a residual fails when
it exceeds ROUNDING = 1e-12 times the sum of the magnitudes of the terms that
cancel in it -- the running-error scale, i.e. the same expression evaluated
with every coefficient and factor replaced by its absolute value. In the
reduction the cancelling terms are 4Q, 4 W_2^2, 7 W_2^2 and 3 W_2^2, so its
scale is e^K (4Q + 14 W_2^2); the lambda^-5 ratio carries both potentials'
relative scales.

Cross-checks: the baseline against flux_vacuum (K, dK, d2K, V, and the slope
against flux_vacuum.canonical_slope, which differentiates numerically) and
every variant's derivatives against central differences (relative step 1e-6,
canonical_slope's; agreement 1e-7 of the largest entry, the threshold of
test_flux_vacuum's derivative test).

KILL
====
Any identity or control failing beyond rounding, or the slope bound failing,
on any variant (falsifiers excluded). Each falsifier must fail at least one.

A4: s are periods, N flux integers, X and x_k pure numbers; none is converted.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.linalg import LinAlgError, cho_factor, cho_solve

from metaphysica.simulations.PM.geometry import flux_vacuum as fv

__all__ = [
    "SEED",
    "ROUNDING",
    "LAMBDA",
    "SLOPE_BOUND",
    "SLOPE_REL",
    "N_BAND",
    "BAND_B",
    "N_FIELDS",
    "KahlerModel",
    "KahlerPoint",
    "Metric",
    "LUKAS_MORRIS",
    "variants",
    "falsifiers",
    "precondition",
    "metric_at",
    "potential_reduced",
    "potential_adv",
    "potential_n1",
    "n1_scale",
    "log_potential_gradient",
    "slope",
    "rescale_to_x",
    "band_a_points",
    "band_b_points",
    "point_checks",
    "susy_control_u0",
    "susy_control_general",
    "finite_difference_check",
    "flux_vacuum_cross_check",
    "variant_report",
    "homogeneity_report",
]

SEED = 20260930
ROUNDING = 1e-12
LAMBDA = 1.7
SLOPE_BOUND = 5.0 * math.sqrt(2.0 / 7.0)
SLOPE_REL = 1e-6
N_BAND = 60
BAND_B = (0.3, 0.6)
MAX_DRAWS_PER_POINT = 100
FD_STEP = 1e-6
FD_AGREEMENT = 1e-7
_CONTROL_F = 1e-9
_CONTROL_W = 1e-12

N_BULK = fv.N_BULK
N_TWISTED = fv.N_TWISTED
N_FIELDS = N_BULK + N_TWISTED
_C = 8.0 / 3.0
_IDX = np.array(fv._TERMS, dtype=int)            # (36, 3): u, s_A, s_B
_U, _A, _B = _IDX[:, 0], _IDX[:, 1], _IDX[:, 2]
_FLAT1 = _IDX.ravel()
_FLAT2 = (_IDX[:, :, None] * N_FIELDS + _IDX[:, None, :]).ravel()


def _counts(seq: Tuple[int, ...]) -> Tuple[int, int, int]:
    return seq.count(0), seq.count(1), seq.count(2)


_ORDERS = {n: [(p, _counts(p)) for p in itertools.product(range(3), repeat=n)]
           for n in (1, 2, 3)}


def _scatter1(local: np.ndarray) -> np.ndarray:
    """Sum per-term (36, 3) entries into a 43-vector."""
    return np.bincount(_FLAT1, weights=local.ravel(), minlength=N_FIELDS)


def _scatter2(local: np.ndarray) -> np.ndarray:
    """Sum per-term (36, 3, 3) entries into a 43 x 43 matrix."""
    return np.bincount(_FLAT2, weights=local.ravel(),
                       minlength=N_FIELDS ** 2).reshape(N_FIELDS, N_FIELDS)


def _local_x(s: np.ndarray, order: int) -> List[np.ndarray]:
    """x_k and its derivatives in (u, a, b) up to `order`: arrays of shape
    (36,), (36, 3), (36, 3, 3), (36, 3, 3, 3)."""
    u, a, b = s[_U], s[_A], s[_B]
    one = np.ones_like(u)
    du = (u * u, 2.0 * u, 2.0 * one, 0.0 * one)
    ea = tuple((-1.0) ** j * math.factorial(j) * a ** (-1 - j)
               for j in range(4))
    eb = tuple((-1.0) ** j * math.factorial(j) * b ** (-1 - j)
               for j in range(4))
    out = [_C * du[0] * ea[0] * eb[0]]
    for n in range(1, order + 1):
        arr = np.empty((len(u),) + (3,) * n)
        for p, (i, j, l) in _ORDERS[n]:
            arr[(slice(None),) + p] = _C * du[i] * ea[j] * eb[l]
        out.append(arr)
    return out


def _log_p(x: float, a2: float, a3: float) -> Tuple[float, ...]:
    """F = -3 ln P(X) and its first three derivatives in X."""
    p = 1.0 - x - a2 * x ** 2 - a3 * x ** 3
    p1 = -1.0 - 2.0 * a2 * x - 3.0 * a3 * x ** 2
    p2 = -2.0 * a2 - 6.0 * a3 * x
    p3 = -6.0 * a3
    if p <= 0.0:
        return (math.nan,) * 4
    return (-3.0 * math.log(p),
            -3.0 * p1 / p,
            -3.0 * (p2 / p - p1 ** 2 / p ** 2),
            -3.0 * (p3 / p - 3.0 * p1 * p2 / p ** 2 + 2.0 * p1 ** 3 / p ** 3))


def _h_x2(x):
    return x * x, 2.0 * x, 2.0 + 0.0 * x, 0.0 * x


def _h_x2_over_1px(x):
    q = 1.0 + x
    return x * x / q, 1.0 - 1.0 / q ** 2, 2.0 / q ** 3, -6.0 / q ** 4


def _h_exp(x):
    e = np.exp(-x)
    return e - 1.0 + x, 1.0 - e, e, -e


#: The degree-0 functions h(x) of the design, with h, h', h'', h'''.
H_FUNCTIONS: Dict[str, Callable] = {
    "x^2": _h_x2,
    "x^2/(1+x)": _h_x2_over_1px,
    "exp(-x)-1+x": _h_exp,
}


def _ident(z):
    return z


@dataclass(frozen=True)
class KahlerModel:
    """One member of the family; see the module docstring."""

    name: str
    k: float = 1.0
    delta: float = 0.0
    a2: float = 0.0
    a3: float = 0.0
    beta: float = 0.0
    h: Optional[str] = None
    weights: Optional[Tuple[float, ...]] = None

    def w(self) -> np.ndarray:
        if self.weights is None:
            return np.ones(N_TWISTED)
        return np.asarray(self.weights, dtype=float)

    def poly(self, x: float) -> float:
        return 1.0 - x - self.a2 * x ** 2 - self.a3 * x ** 3

    def x_total(self, s: Sequence[float]) -> float:
        return float(_local_x(np.asarray(s, dtype=float), 0)[0].sum())

    def in_domain(self, s: Sequence[float]) -> bool:
        s = np.asarray(s, dtype=float)
        if np.any(s[:N_BULK] <= 0.0):
            return False
        x = self.x_total(s)
        return x < 1.0 and self.poly(x) > 0.0

    def at(self, s: Sequence[float], order: int = 3) -> "KahlerPoint":
        return KahlerPoint(self, s, order)

    def value(self, s: Sequence[float]) -> float:
        return self.at(s, 0).value()

    def gradient(self, s: Sequence[float]) -> np.ndarray:
        return self.at(s, 1).gradient()

    def hessian(self, s: Sequence[float]) -> np.ndarray:
        return self.at(s, 2).hessian()

    def hessian_derivative(self, s: Sequence[float],
                           v: Sequence[float]) -> np.ndarray:
        return self.at(s, 3).hessian_derivative(np.asarray(v, dtype=float))

    def third_contract(self, s: Sequence[float], a: Sequence[float],
                       b: Sequence[float]) -> np.ndarray:
        return self.at(s, 3).third_contract(np.asarray(a, dtype=float),
                                            np.asarray(b, dtype=float))


class KahlerPoint:
    """K and its derivatives at one point, sharing the per-term arrays."""

    def __init__(self, model: KahlerModel, s: Sequence[float],
                 order: int = 3) -> None:
        self.model = model
        self.s = np.asarray(s, dtype=float)
        loc = _local_x(self.s, order)
        self.x = loc[0]
        self.d = loc[1:]
        self.X = float(self.x.sum())
        self.F = _log_p(self.X, model.a2, model.a3)
        sb = self.s[:N_BULK]
        k, dl = model.k, model.delta
        self.bulk = (
            (-k * np.log(2.0 * sb), dl / sb),
            (-k / sb, -dl / sb ** 2),
            (k / sb ** 2, 2.0 * dl / sb ** 3),
            (-2.0 * k / sb ** 3, -6.0 * dl / sb ** 4),
        )
        if model.beta and model.h is not None:
            hs = H_FUNCTIONS[model.h](self.x)
            self.hc = tuple(model.beta * model.w() * hn for hn in hs)
        else:
            self.hc = None

    # -- value -------------------------------------------------------------
    def value(self) -> float:
        if np.any(self.s[:N_BULK] <= 0.0) or not math.isfinite(self.F[0]) \
                or self.X >= 1.0:
            raise ValueError("outside the domain: X = %g, P = %g"
                             % (self.X, self.model.poly(self.X)))
        out = float(np.sum(self.bulk[0][0]) + np.sum(self.bulk[0][1]))
        out += self.F[0] + fv.LM_CONSTANT
        if self.hc is not None:
            out += float(np.sum(self.hc[0]))
        return out

    def value_scale(self) -> float:
        out = float(np.sum(np.abs(self.bulk[0][0]))
                    + np.sum(np.abs(self.bulk[0][1])))
        out += abs(self.F[0]) + abs(fv.LM_CONSTANT)
        if self.hc is not None:
            out += float(np.sum(np.abs(self.hc[0])))
        return out

    # -- derivatives -------------------------------------------------------
    def _bulk_vec(self, n: int, f) -> np.ndarray:
        return f(self.bulk[n][0]) + f(self.bulk[n][1])

    def gradient(self, absolute: bool = False) -> np.ndarray:
        f = np.abs if absolute else _ident
        d1 = f(self.d[0])
        g = np.zeros(N_FIELDS)
        g[:N_BULK] = self._bulk_vec(1, f)
        g += f(self.F[1]) * _scatter1(d1)
        if self.hc is not None:
            g += _scatter1(f(self.hc[1])[:, None] * d1)
        return g

    def hessian(self, absolute: bool = False) -> np.ndarray:
        f = np.abs if absolute else _ident
        d1, d2 = f(self.d[0]), f(self.d[1])
        xi = _scatter1(d1)
        h = np.zeros((N_FIELDS, N_FIELDS))
        h[np.arange(N_BULK), np.arange(N_BULK)] = self._bulk_vec(2, f)
        h += f(self.F[2]) * np.outer(xi, xi) + f(self.F[1]) * _scatter2(d2)
        if self.hc is not None:
            loc = (f(self.hc[2])[:, None, None] * d1[:, :, None]
                   * d1[:, None, :] + f(self.hc[1])[:, None, None] * d2)
            h += _scatter2(loc)
        return h

    def hessian_derivative(self, v: np.ndarray,
                           absolute: bool = False) -> np.ndarray:
        """sum_k K_ijk v^k: the derivative of K_ij along v."""
        f = np.abs if absolute else _ident
        v = f(np.asarray(v, dtype=float))
        d1, d2, d3 = f(self.d[0]), f(self.d[1]), f(self.d[2])
        vl = v[_IDX]
        xi, xij = _scatter1(d1), _scatter2(d2)
        xv = float(xi @ v)
        x2v = xij @ v
        x3v = _scatter2(np.einsum("kpqr,kr->kpq", d3, vl))
        out = np.zeros((N_FIELDS, N_FIELDS))
        out[np.arange(N_BULK), np.arange(N_BULK)] = (
            self._bulk_vec(3, f) * v[:N_BULK])
        out += f(self.F[3]) * xv * np.outer(xi, xi)
        out += f(self.F[2]) * (np.outer(x2v, xi) + np.outer(xi, x2v)
                               + xv * xij)
        out += f(self.F[1]) * x3v
        if self.hc is not None:
            c1, c2, c3 = (f(self.hc[n]) for n in (1, 2, 3))
            d1v = np.einsum("kp,kp->k", d1, vl)
            d2v = np.einsum("kpq,kq->kp", d2, vl)
            d3v = np.einsum("kpqr,kr->kpq", d3, vl)
            loc = ((c3 * d1v)[:, None, None] * d1[:, :, None] * d1[:, None, :]
                   + c2[:, None, None] * (d2v[:, :, None] * d1[:, None, :]
                                          + d1[:, :, None] * d2v[:, None, :]
                                          + d1v[:, None, None] * d2)
                   + c1[:, None, None] * d3v)
            out += _scatter2(loc)
        return out

    def third_contract(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """T(a, b)_k = sum_ij K_ijk a^i b^j (K_ijk is totally symmetric)."""
        return self.hessian_derivative(a) @ b


LUKAS_MORRIS = KahlerModel("lukas_morris")

_WEIGHTS = tuple((k + 1) / 18.0 for k in range(N_TWISTED))


def variants() -> List[KahlerModel]:
    """The registered variant list: baseline, four P(X), three h x two signs."""
    out = [LUKAS_MORRIS]
    for a2, a3 in ((0.5, 0.0), (0.0, 0.5), (-0.5, 0.25), (1.0, -1.0)):
        out.append(KahlerModel("P: a2=%g a3=%g" % (a2, a3), a2=a2, a3=a3))
    for h in H_FUNCTIONS:
        for beta in (1.0, -1.0):
            out.append(KahlerModel("h=%s beta=%+g" % (h, beta), beta=beta,
                                   h=h, weights=_WEIGHTS))
    return out


def falsifiers() -> List[KahlerModel]:
    """Degree-breaking members: each must fail at least one identity."""
    return [KahlerModel("falsifier: delta=1", delta=1.0),
            KahlerModel("falsifier: k=1/9", k=1.0 / 9.0)]


# ---------------------------------------------------------------- the metric

def precondition(s: Sequence[float]) -> np.ndarray:
    """D = diag(s_A, sqrt(s_a s_b)): D K D is O(1) at every scale."""
    s = np.asarray(s, dtype=float)
    d = np.empty(N_FIELDS)
    d[:N_BULK] = s[:N_BULK]
    d[_U] = np.sqrt(s[_A] * s[_B])
    return d


class Metric:
    """K_ij factored once, in the preconditioned frame D K D."""

    def __init__(self, hess: np.ndarray, d: np.ndarray) -> None:
        self.hess = hess
        self.d = d
        self.scaled = d[:, None] * hess * d[None, :]
        try:
            self.cho = cho_factor(self.scaled)
            self.positive_definite = True
        except LinAlgError:
            self.cho = None
            self.positive_definite = False

    def solve(self, rhs: np.ndarray) -> np.ndarray:
        """K^-1 rhs (LU when K is not positive definite)."""
        r = self.d[:, None] * rhs if rhs.ndim == 2 else self.d * rhs
        if self.cho is not None:
            z = cho_solve(self.cho, r)
        else:
            z = np.linalg.solve(self.scaled, r)
        return self.d[:, None] * z if rhs.ndim == 2 else self.d * z

    def min_eigenvalue(self) -> float:
        return float(np.linalg.eigvalsh(self.scaled)[0])

    def condition(self) -> float:
        ev = np.linalg.eigvalsh(self.scaled)
        return float(abs(ev[-1]) / abs(ev[0])) if ev[0] else math.inf


def metric_at(point: KahlerPoint) -> Metric:
    return Metric(point.hessian(), precondition(point.s))


# ------------------------------------------------------------ the potentials

def potential_reduced(model: KahlerModel, s: Sequence[float],
                      flux: Sequence[float], w1: float = 0.0) -> float:
    """4 e^K [K^ij N_i N_j + W_1^2] (the form H3a states)."""
    p = model.at(s, 2)
    n = np.asarray(flux, dtype=float)
    q = float(n @ metric_at(p).solve(n))
    return 4.0 * math.exp(p.value()) * (q + w1 ** 2)


def potential_adv(model: KahlerModel, s: Sequence[float],
                  flux: Sequence[float], c2: float = 0.0
                  ) -> Tuple[float, float]:
    """ADV (3.11) on the axion slice, and its running-error scale
    e^K (4 Q + 14 W_2^2)."""
    p = model.at(s, 2)
    s = p.s
    n = np.asarray(flux, dtype=float)
    met = metric_at(p)
    grad = p.gradient()
    w2 = float(n @ s) + c2
    f = n + 0.5 * grad * w2
    q = float(n @ met.solve(n))
    ek = math.exp(p.value())
    v = ek * (4.0 * float(f @ met.solve(f)) - 3.0 * w2 ** 2)
    return v, ek * (4.0 * abs(q) + 14.0 * w2 ** 2)


def potential_n1(model: KahlerModel, s: Sequence[float], t: Sequence[float],
                 flux: Sequence[float], c1: float = 0.0,
                 c2: float = 0.0) -> float:
    """The N = 1 formula in complex form, z = t + i s, W = N.z + c1 + i c2:
    V = e^K (K^{i jbar} D_i W conj(D_j W) - 3 |W|^2), K^{i jbar} = 4 K^ij,
    D_i W = N_i - (i/2) K_i W."""
    p = model.at(s, 2)
    n = np.asarray(flux, dtype=float)
    t = np.asarray(t, dtype=float)
    w = complex(float(n @ t) + c1, float(n @ p.s) + c2)
    dw = n - 0.5j * p.gradient() * w
    met = metric_at(p)
    kinv_dw = met.solve(dw.real) + 1j * met.solve(dw.imag)
    form = 4.0 * complex(np.conj(dw) @ kinv_dw)
    return math.exp(p.value()) * (form.real - 3.0 * abs(w) ** 2)


def n1_scale(model: KahlerModel, s: Sequence[float], flux: Sequence[float],
             w1: float, c2: float = 0.0) -> float:
    """Running-error scale of the N = 1 reduction: e^K (4Q + 14 W_2^2 +
    10 W_1^2) (4Q, 4W_2^2, 7W_2^2, 3W_2^2, 7W_1^2, 3W_1^2 cancel)."""
    p = model.at(s, 2)
    n = np.asarray(flux, dtype=float)
    q = float(n @ metric_at(p).solve(n))
    w2 = float(n @ p.s) + c2
    return math.exp(p.value()) * (4.0 * abs(q) + 14.0 * w2 ** 2
                                  + 10.0 * w1 ** 2)


def log_potential_gradient(model: KahlerModel, s: Sequence[float],
                           flux: Sequence[float], w1: float = 0.0,
                           toy_p: float = 0.0, point: KahlerPoint = None,
                           metric: Metric = None
                           ) -> Tuple[np.ndarray, np.ndarray]:
    """(d_s ln V, d_t ln V) for V = 4 e^K [Q + W_1^2]:
    d_s ln V = K_s - T(y, y)/(Q + W_1^2), y = K^-1 N; d_t ln V =
    2 W_1 N/(Q + W_1^2). `toy_p` multiplies V by prod_A s_A^p (the H3a/H3e
    falsifier); 0 is the physical potential."""
    p = point if point is not None else model.at(s, 3)
    met = metric if metric is not None else metric_at(p)
    n = np.asarray(flux, dtype=float)
    y = met.solve(n)
    den = float(n @ y) + w1 ** 2
    gs = p.gradient() - p.third_contract(y, y) / den
    if toy_p:
        gs[:N_BULK] += toy_p / p.s[:N_BULK]
    gt = 2.0 * w1 * n / den
    return gs, gt


def slope(model: KahlerModel, s: Sequence[float], flux: Sequence[float],
          w1: float = 0.0, toy_p: float = 0.0, point: KahlerPoint = None,
          metric: Metric = None) -> float:
    """|grad V|_G / V on all fields, G = K/2 on both blocks."""
    p = point if point is not None else model.at(s, 3)
    met = metric if metric is not None else metric_at(p)
    gs, gt = log_potential_gradient(model, s, flux, w1, toy_p, p, met)
    return math.sqrt(2.0 * (float(gs @ met.solve(gs))
                            + float(gt @ met.solve(gt))))


# ------------------------------------------------------------------ sampling

def rescale_to_x(s: Sequence[float], x_target: float) -> np.ndarray:
    """Scale the twisted block so that X = x_target (X is quadratic in u)."""
    s = np.array(s, dtype=float)
    x = float(_local_x(s, 0)[0].sum())
    s[N_BULK:] *= math.sqrt(x_target / x)
    return s


def band_a_points(rng: np.random.Generator, n: int = N_BAND
                  ) -> List[Tuple[np.ndarray, np.ndarray]]:
    """flux_vacuum's own sampling: X <~ 0.06."""
    return [(fv._random_point(rng), fv._random_flux(rng)) for _ in range(n)]


def band_b_points(model: KahlerModel, rng: np.random.Generator,
                  n: int = N_BAND) -> Tuple[List[Tuple[np.ndarray,
                                                       np.ndarray]], int]:
    """X ~ U(0.3, 0.6), redrawn while P <= 0 or K_ij is not positive
    definite. Returns the points and the number of discarded draws."""
    out: List[Tuple[np.ndarray, np.ndarray]] = []
    discarded = 0
    while len(out) < n:
        if discarded > MAX_DRAWS_PER_POINT * n:
            raise RuntimeError("band B gave up after %d discards" % discarded)
        s = rescale_to_x(fv._random_point(rng), rng.uniform(*BAND_B))
        if not model.in_domain(s) or \
                not metric_at(model.at(s, 2)).positive_definite:
            discarded += 1
            continue
        out.append((s, fv._random_flux(rng)))
    return out, discarded


# -------------------------------------------------------------------- checks

def _ratio(res: float, scale: float) -> float:
    """Residual in units of ROUNDING * scale (> 1 fails)."""
    if scale == 0.0:
        return 0.0 if res == 0.0 else math.inf
    return abs(res) / (ROUNDING * scale)


def point_checks(model: KahlerModel, s: np.ndarray,
                 flux: np.ndarray) -> Dict[str, Any]:
    """Every PR-2 check at one point. Residuals are in units of the rounding
    allowance: a value above 1 is a failure beyond rounding."""
    p = model.at(s, 3)
    met = metric_at(p)
    g, ga = p.gradient(), p.gradient(True)
    h, ha = p.hessian(), p.hessian(True)
    m, ma = p.hessian_derivative(s), p.hessian_derivative(s, True)
    abs_s = np.abs(s)
    lam_s = model.at(LAMBDA * s, 0)
    hom = lam_s.value() - p.value() + 7.0 * math.log(LAMBDA)
    hom_scale = lam_s.value_scale() + p.value_scale() + 7.0 * math.log(LAMBDA)
    v, v_scale = potential_adv(model, s, flux)
    v_lam, v_lam_scale = potential_adv(model, LAMBDA * s, flux)
    reduced = potential_reduced(model, s, flux)
    ratio = v_lam / v
    out = {
        "X": p.X,
        "residual_over_rounding": {
            "homogeneity": _ratio(hom, hom_scale),
            "euler": _ratio(float(g @ s) + 7.0, float(ga @ abs_s) + 7.0),
            "second": _ratio(float(np.max(np.abs(h @ s + g))),
                             float(np.max(ha @ abs_s + ga))),
            "third": _ratio(float(np.max(np.abs(m + 2.0 * h))),
                            float(np.max(ma + 2.0 * ha))),
            "reduction": _ratio(v - reduced, v_scale),
            "scaling": _ratio(ratio - LAMBDA ** -5, abs(ratio) * (
                v_lam_scale / abs(v_lam) + v_scale / abs(v))),
        },
        "raw": {
            "homogeneity": abs(hom),
            "euler": abs(float(g @ s) + 7.0),
            "second": float(np.max(np.abs(h @ s + g))),
            "third": float(np.max(np.abs(m + 2.0 * h))),
            "reduction_relative": abs(v - reduced) / abs(reduced),
            "scaling": abs(ratio - LAMBDA ** -5),
        },
        "positive_definite": met.positive_definite,
        "min_eigenvalue_DKD": met.min_eigenvalue(),
        "condition_DKD": met.condition(),
        "V": v,
        "V_positive": v > 0.0,
        "scaling_exponent": math.log(ratio) / math.log(LAMBDA)
        if ratio > 0 else math.nan,
        "slope": slope(model, s, flux, point=p, metric=met),
    }
    out["identities_hold"] = all(r <= 1.0 for r in
                                 out["residual_over_rounding"].values())
    out["slope_bound_holds"] = out["slope"] >= SLOPE_BOUND * (1 - SLOPE_REL)
    return out


def susy_control_u0(model: KahlerModel, c2: float,
                    flux_bulk: float) -> Dict[str, Any]:
    """flux_vacuum._susy_control with the variant's K: at u = 0 and
    s_A = -c_2/(5 N) the F-terms vanish and W_2 = -(2/5) c_2."""
    s_bulk = -c2 / (5.0 * flux_bulk)
    s = np.concatenate([np.full(N_BULK, s_bulk), np.zeros(N_TWISTED)])
    flux = np.concatenate([np.full(N_BULK, flux_bulk), np.zeros(N_TWISTED)])
    return _control(model, s, flux, c2)


def susy_control_general(model: KahlerModel, s: np.ndarray,
                         c2: float) -> Dict[str, Any]:
    """The same control at any point: with N = (c_2/5) dK, F = 0 and
    W_2 = -(2/5) c_2 exactly when K_i s^i = -7. (N need not be integral:
    the control is hypothetical, as c_2 != 0 is.)"""
    flux = (c2 / 5.0) * model.gradient(s)
    return _control(model, s, flux, c2)


def _control(model: KahlerModel, s: np.ndarray, flux: np.ndarray,
             c2: float) -> Dict[str, Any]:
    w2 = float(flux @ s) + c2
    f = flux + 0.5 * model.gradient(s) * w2
    v, _scale = potential_adv(model, s, flux, c2)
    out = {"c2": c2, "X": model.x_total(s),
           "max_abs_F": float(np.max(np.abs(f))),
           "W2_over_c2": w2 / c2, "V": v, "is_ads": v < 0.0}
    out["finds_the_vacuum"] = bool(
        out["max_abs_F"] < _CONTROL_F
        and abs(out["W2_over_c2"] + 0.4) < _CONTROL_W and out["is_ads"])
    return out


def finite_difference_check(model: KahlerModel,
                            s: np.ndarray) -> Dict[str, float]:
    """Analytic dK, d2K, d3K against central differences (relative step
    FD_STEP per coordinate, scaled by D); each entry is the largest
    disagreement over the largest analytic entry."""
    s = np.asarray(s, dtype=float)
    p = model.at(s, 3)
    steps = FD_STEP * precondition(s)
    grad_fd = np.empty(N_FIELDS)
    hess_fd = np.empty((N_FIELDS, N_FIELDS))
    third_fd = np.empty((N_FIELDS, N_FIELDS, N_FIELDS))
    third = np.empty((N_FIELDS, N_FIELDS, N_FIELDS))
    for i in range(N_FIELDS):
        e = np.zeros(N_FIELDS)
        e[i] = steps[i]
        up, dn = model.at(s + e, 2), model.at(s - e, 2)
        grad_fd[i] = (up.value() - dn.value()) / (2 * steps[i])
        hess_fd[i] = (up.gradient() - dn.gradient()) / (2 * steps[i])
        third_fd[i] = (up.hessian() - dn.hessian()) / (2 * steps[i])
        unit = np.zeros(N_FIELDS)
        unit[i] = 1.0
        third[i] = p.hessian_derivative(unit)

    def rel(a, b):
        return float(np.max(np.abs(a - b)) / np.max(np.abs(b)))

    return {"gradient": rel(grad_fd, p.gradient()),
            "hessian": rel(hess_fd, p.hessian()),
            "third": rel(third_fd, third)}


def flux_vacuum_cross_check(n: int = 10, seed: int = SEED) -> Dict[str, Any]:
    """The baseline model against flux_vacuum itself, in both bands."""
    rng = np.random.default_rng(seed)
    pts = band_a_points(rng, n) + band_b_points(LUKAS_MORRIS, rng, n)[0]
    worst = dict.fromkeys(("kahler", "gradient", "hessian", "potential",
                           "slope_vs_canonical_slope"), 0.0)
    for s, flux in pts:
        p = LUKAS_MORRIS.at(s, 3)
        g, h = p.gradient(), p.hessian()
        worst["kahler"] = max(worst["kahler"], abs(
            p.value() - fv.kahler(s)) / p.value_scale())
        worst["gradient"] = max(worst["gradient"], float(np.max(np.abs(
            g - fv.kahler_gradient(s))) / np.max(np.abs(g))))
        worst["hessian"] = max(worst["hessian"], float(np.max(np.abs(
            h - fv.kahler_hessian(s))) / np.max(np.abs(h))))
        v, _scale = potential_adv(LUKAS_MORRIS, s, flux)
        worst["potential"] = max(worst["potential"], abs(
            v - fv.potential(s, flux)) / abs(v))
        sl = slope(LUKAS_MORRIS, s, flux)
        worst["slope_vs_canonical_slope"] = max(
            worst["slope_vs_canonical_slope"],
            abs(sl - fv.canonical_slope(s, flux)) / sl)
    return {
        "n_points": len(pts),
        "worst_relative": worst,
        "agrees": (all(worst[k] < 1e3 * ROUNDING for k in
                       ("kahler", "gradient", "hessian", "potential"))
                   and worst["slope_vs_canonical_slope"] < SLOPE_REL),
        "thresholds": "K, dK, d2K, V: 1e-9 relative (different summation "
                      "order and an LU inverse in flux_vacuum); slope: 1e-6 "
                      "(canonical_slope differentiates numerically)",
    }


def _non_vacuity(model: KahlerModel, pts) -> float:
    """Largest relative change of K_ij against the baseline over `pts`."""
    if model == LUKAS_MORRIS:
        return 0.0
    worst = 0.0
    for s, _flux in pts:
        h0 = LUKAS_MORRIS.hessian(s)
        worst = max(worst, float(np.max(np.abs(model.hessian(s) - h0))
                                 / np.max(np.abs(h0))))
    return worst


def variant_report(model: KahlerModel, n: int = N_BAND,
                   seed: int = SEED) -> Dict[str, Any]:
    """Run every check on both bands for one member of the family."""
    rng = np.random.default_rng(seed)
    bands = {"A": band_a_points(rng, n)}
    bands["B"], discarded = band_b_points(model, rng, n)
    per_band: Dict[str, Any] = {}
    all_ok = True
    for name, pts in bands.items():
        rows = [point_checks(model, s, flux) for s, flux in pts]
        keys = rows[0]["residual_over_rounding"].keys()
        worst = {k: max(r["residual_over_rounding"][k] for r in rows)
                 for k in keys}
        band = {
            "n_points": len(rows),
            "X_range": [min(r["X"] for r in rows), max(r["X"] for r in rows)],
            "worst_residual_over_rounding": worst,
            "worst_raw": {k: max(r["raw"][k] for r in rows)
                          for k in rows[0]["raw"]},
            "all_positive_definite": all(r["positive_definite"]
                                         for r in rows),
            "min_eigenvalue_DKD": min(r["min_eigenvalue_DKD"] for r in rows),
            "max_condition_DKD": max(r["condition_DKD"] for r in rows),
            "all_V_positive": all(r["V_positive"] for r in rows),
            "median_scaling_exponent": float(np.median(
                [r["scaling_exponent"] for r in rows])),
            "min_slope": min(r["slope"] for r in rows),
            "identities_hold": all(r["identities_hold"] for r in rows),
            "slope_bound_holds": all(r["slope_bound_holds"] for r in rows),
            "max_relative_change_of_K_ij_vs_baseline":
                _non_vacuity(model, pts),
        }
        band["passes"] = (band["identities_hold"] and band["slope_bound_holds"]
                          and band["all_positive_definite"]
                          and band["all_V_positive"])
        all_ok &= band["passes"]
        per_band[name] = band
    controls = [susy_control_u0(model, c2, nb)
                for c2, nb in ((-10.0, 1.0), (25.0, -2.0))]
    controls += [susy_control_general(model, s, c2)
                 for s, _flux in bands["B"][:5] for c2 in (-10.0, 25.0)]
    controls_ok = all(c["finds_the_vacuum"] for c in controls)
    failed = sorted({k for b in per_band.values()
                     for k, v in b["worst_residual_over_rounding"].items()
                     if v > 1.0}
                    | ({"slope_bound"} if not all(
                        b["slope_bound_holds"] for b in per_band.values())
                       else set())
                    | ({"controls"} if not controls_ok else set()))
    return {
        "model": model.name,
        "parameters": {"k": model.k, "delta": model.delta, "a2": model.a2,
                       "a3": model.a3, "beta": model.beta, "h": model.h},
        "bands": per_band,
        "band_B_discarded_draws": discarded,
        "controls": controls,
        "controls_find_the_vacuum": controls_ok,
        "failed_checks": failed,
        "passes": all_ok and controls_ok,
    }


def homogeneity_report(n: int = N_BAND, seed: int = SEED) -> Dict[str, Any]:
    """PR-2: every variant and both falsifiers, plus the cross-checks."""
    reports = [variant_report(m, n, seed) for m in variants()]
    falsified = [variant_report(m, n, seed) for m in falsifiers()]
    rng = np.random.default_rng(seed)
    fd_points = band_b_points(LUKAS_MORRIS, rng, 1)[0] + \
        [(np.concatenate([np.full(N_BULK, 7.0), np.zeros(N_TWISTED)]), None)]
    fd = {m.name: [finite_difference_check(m, s) for s, _f in fd_points]
          for m in variants() + falsifiers()}
    fd_worst = max(v for rows in fd.values() for r in rows for v in r.values())
    holds = all(r["passes"] for r in reports)
    return {
        "seed": seed,
        "n_per_band": n,
        "lambda": LAMBDA,
        "rounding": ROUNDING,
        "variants": reports,
        "falsifiers": falsified,
        "falsifiers_fail": all(f["failed_checks"] for f in falsified),
        "flux_vacuum_cross_check": flux_vacuum_cross_check(seed=seed),
        "finite_differences": {"worst_relative": fd_worst,
                               "agree": fd_worst < FD_AGREEMENT,
                               "per_model": fd},
        "prediction_holds": holds,
        "kill_fired": not holds,
    }
