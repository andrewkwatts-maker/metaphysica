#!/usr/bin/env python3
"""Explicit Cl(12,1) shadow Clifford algebra and its conjugation operator.

WHY THIS EXISTS
---------------
The modular conjugation of the shadow pair factorises (Bisognano-Wichmann) as

    J = Theta . U(R(pi)),    with  U(R(pi)) = R_perp = [[0,-1],[1,0]]

and the framework already supplies R_perp. Theta -- the antiunitary factor
that reverses shadow time -- was undefined, and an earlier proposal to set
Theta = J is circular (it would force R_perp = 1).

A constructive alternative is Theta = C . T, with C the charge-conjugation
matrix of the shadow Clifford algebra Cl(12,1) and T time reversal. That is
testable, and this module tests the Clifford half of it EXPLICITLY rather
than by quoting a table.

WHAT IS ESTABLISHED HERE
------------------------
Building the 13 gamma matrices of Cl(12,1) as 64x64 complex matrices and
forming the two standard candidate conjugations (the product of the purely
imaginary gammas, and the product of the purely real ones), BOTH satisfy

    B B* = -1

so the conjugation on a single 13D shadow's spinors is QUATERNIONIC
(symplectic Majorana), squaring to -1. This is what (s-t) = 11 = 3 mod 8
predicts, now verified by explicit matrix construction.

That -1 is not a defect: Bisognano-Wichmann requires Theta^2 = (-1)^F so that
J^2 = Theta^2 R_perp^2 = (-1)^F (-1)^F = +1, as Tomita-Takesaki demands. The
shadow signature therefore FORCES the algebraic type Theta must have.

WHAT IS NOT ESTABLISHED
-----------------------
This constructs the SPINOR-level action only. A field-theoretic Theta must
act on the shadow Hilbert space (multi-particle states), which requires the
quantum theory the framework does not yet have. Decision 2 is advanced, not
closed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

__all__ = [
    "shadow_gammas",
    "conjugation_candidates",
    "shadow_clifford_report",
]

_I2 = np.eye(2, dtype=complex)
_SX = np.array([[0, 1], [1, 0]], dtype=complex)
_SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
_SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def _kron(*mats: np.ndarray) -> np.ndarray:
    out = np.array([[1]], dtype=complex)
    for m in mats:
        out = np.kron(out, m)
    return out


def shadow_gammas() -> List[np.ndarray]:
    """The 13 gamma matrices of Cl(12,1), each 64x64.

    Index 0 is the timelike direction (gamma_0^2 = -I); indices 1..12 are
    spacelike (gamma_i^2 = +I). The spinor dimension 2^6 = 64 is the
    framework's per-shadow spinor count, whose square 64 x 64 = 4096 is the
    shadow-pair spinor.
    """
    n = 6
    spacelike: List[np.ndarray] = []
    for k in range(n):
        pre = [_SZ] * k
        post = [_I2] * (n - k - 1)
        spacelike.append(_kron(*pre, _SX, *post))
        spacelike.append(_kron(*pre, _SY, *post))

    chi = spacelike[0]
    for g in spacelike[1:]:
        chi = chi @ g
    chi = chi / np.sqrt(complex((chi @ chi)[0, 0]))
    timelike = 1j * chi  # (i*chi)^2 = -chi^2 = -I
    return [timelike] + spacelike


def conjugation_candidates(gammas: List[np.ndarray]) -> Dict[str, np.ndarray]:
    """The two standard conjugation candidates, B1 and B2.

    B1 is the product of the purely imaginary gammas, B2 of the purely real
    ones. One implements C gamma C^-1 = +gamma*, the other -gamma*.
    """
    imag = [g for g in gammas if np.allclose(g, -g.conj(), atol=1e-9)]
    real = [g for g in gammas if np.allclose(g, g.conj(), atol=1e-9)]

    def prod(ms: List[np.ndarray]) -> np.ndarray:
        out = np.eye(gammas[0].shape[0], dtype=complex)
        for m in ms:
            out = out @ m
        return out

    return {"B1_imaginary": prod(imag), "B2_real": prod(real)}


def shadow_clifford_report() -> Dict[str, Any]:
    """Verify the algebra and the reality type of its conjugation."""
    gammas = shadow_gammas()
    d = gammas[0].shape[0]

    # Clifford relations: {g_a, g_b} = 2 eta_ab, eta = diag(-1, +1, ..., +1)
    clifford_ok = True
    for i, a in enumerate(gammas):
        for j, b in enumerate(gammas):
            eta = -1.0 if (i == 0 and j == 0) else (1.0 if i == j else 0.0)
            if not np.allclose(a @ b + b @ a, 2 * eta * np.eye(d), atol=1e-9):
                clifford_ok = False
                break

    cands = conjugation_candidates(gammas)
    squares: Dict[str, float] = {}
    for name, B in cands.items():
        BB = B @ B.conj()
        lam = BB[0, 0]
        if np.allclose(BB, lam * np.eye(d), atol=1e-8):
            squares[name] = float(np.real(lam / abs(lam))) if abs(lam) else 0.0

    quaternionic = all(v < 0 for v in squares.values()) and bool(squares)

    return {
        "algebra": "Cl(12,1)",
        "dimension": 13,
        "spinor_dim": d,
        "shadow_pair_spinor": d * d,
        "clifford_relations_hold": clifford_ok,
        "signature_invariant_s_minus_t_mod_8": (12 - 1) % 8,
        "conjugation_squares": squares,
        "reality_type": "quaternionic" if quaternionic else "not quaternionic",
        "theta_consequence": (
            "The conjugation on one shadow squares to -1, so any Theta built "
            "from it carries Theta^2 = (-1)^F. That is exactly what "
            "Bisognano-Wichmann needs for J^2 = Theta^2 R_perp^2 = +1, since "
            "R_perp^2 = (-1)^F too. The shadow signature FORCES Theta's "
            "algebraic type."
        ),
        "scope": (
            "Spinor-level only. A field-theoretic Theta must act on the "
            "shadow Hilbert space, which needs the quantum theory. Decision 2 "
            "is advanced, not closed."
        ),
    }


def main() -> int:
    r = shadow_clifford_report()
    print("=" * 64)
    print(" SHADOW CLIFFORD ALGEBRA  Cl(12,1)")
    print("=" * 64)
    print(f"  spinor dimension          : {r['spinor_dim']}")
    print(f"  shadow-pair spinor        : {r['shadow_pair_spinor']}")
    print(f"  Clifford relations hold   : {r['clifford_relations_hold']}")
    print(f"  (s-t) mod 8               : {r['signature_invariant_s_minus_t_mod_8']}")
    for k, v in r["conjugation_squares"].items():
        print(f"  {k:<20} B B* = {v:+.0f} . I")
    print(f"  reality type              : {r['reality_type']}")
    print()
    print("  " + r["theta_consequence"])
    print()
    print("  SCOPE: " + r["scope"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
