"""Curvature helpers in sympy: Christoffel, Ricci, Ricci scalar, Einstein tensor.

Convention: R^r_{s m n} = d_m G^r_{n s} - d_n G^r_{m s} + G^r_{m l} G^l_{n s}
- G^r_{n l} G^l_{m s}; Ricci R_{s n} = R^r_{s r n}; a sphere has positive R.
Note: this belongs in Arithma once its calculus bodies land.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence

import sympy as sp


def _identity(expr):
    return expr


def christoffel(metric: sp.Matrix, coords: Sequence, inverse: Optional[sp.Matrix] = None,
                simp: Callable = _identity):
    """Christoffel symbols G[r][m][n] = Gamma^r_{mn}; `inverse` skips inversion."""
    n = len(coords)
    inv = inverse if inverse is not None else metric.inv()
    d = [[[sp.diff(metric[a, b], coords[c]) for c in range(n)] for b in range(n)]
         for a in range(n)]
    gam = [[[0] * n for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for m in range(n):
            for k in range(m, n):
                val = sum(inv[r, s] * (d[s][m][k] + d[s][k][m] - d[m][k][s])
                          for s in range(n)) / 2
                gam[r][m][k] = gam[r][k][m] = simp(val)
    return gam


def ricci_tensor(metric: sp.Matrix, coords: Sequence, inverse: Optional[sp.Matrix] = None,
                 simp: Callable = _identity) -> sp.Matrix:
    n = len(coords)
    g = christoffel(metric, coords, inverse, simp)
    ric = sp.zeros(n, n)
    for s in range(n):
        for v in range(s, n):
            val = 0
            for r in range(n):
                val += sp.diff(g[r][v][s], coords[r]) - sp.diff(g[r][r][s], coords[v])
                for lam in range(n):
                    val += g[r][r][lam] * g[lam][v][s] - g[r][v][lam] * g[lam][r][s]
            ric[s, v] = ric[v, s] = simp(val)
    return ric


def ricci_scalar(metric: sp.Matrix, coords: Sequence, inverse: Optional[sp.Matrix] = None,
                 simp: Callable = _identity):
    inv = inverse if inverse is not None else metric.inv()
    ric = ricci_tensor(metric, coords, inv, simp)
    n = len(coords)
    return simp(sum(inv[a, b] * ric[a, b] for a in range(n) for b in range(n)))


def einstein_tensor(metric: sp.Matrix, coords: Sequence) -> sp.Matrix:
    """G_{ab} = R_{ab} - (1/2) g_{ab} R, simplified deliberately."""
    inv = metric.inv()
    n = len(coords)
    ric = ricci_tensor(metric, coords, inv, sp.simplify)
    rs = sp.simplify(sum(inv[a, b] * ric[a, b] for a in range(n) for b in range(n)))
    return (ric - metric * rs / 2).applyfunc(sp.simplify)
