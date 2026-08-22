#!/usr/bin/env python3
"""Reflection-positivity gate for the bridge / shadow-coupling sector.

WHY THIS EXISTS
---------------
Reflection positivity (RP) is the Osterwalder-Schrader condition that turns a
Euclidean measure into a Hilbert space with a positive-definite inner product.
It is exactly the condition that FAILS for ghost, higher-derivative and
generically two-time theories, which makes it the only falsifiable structural
test currently available to this framework: if the bridge sector is not
reflection positive under shadow exchange, the modular/Tomita-Takesaki reading
of the OR operator is dead, cheaply and early.

WHAT THIS IS NOT
----------------
This is a finite-dimensional ALGEBRAIC gate, not a field-theoretic proof. It
tests the Gaussian (quadratic) sector defined by the 12 bridge-pair metrics.
Passing does not establish RP for the full theory; failing does rule it out for
the quadratic sector, which is enough to kill the modular route.

TWO CORRECTIONS TO THE OBVIOUS FORMULATION (2026-08-21)
-------------------------------------------------------
1. R_perp CANNOT be the RP involution. RP requires a reflection, theta^2 = +1.
   R_perp = [[0,-1],[1,0]] satisfies R_perp^2 = -I, so it has ORDER 4. Using it
   would also be self-defeating for a second reason: <B_i, R_perp B_j> for a
   quarter-turn is ANTISYMMETRIC, so its symmetric part vanishes identically and
   the matrix can never be positive definite. That is a false alarm - an
   algebraic artefact, not a ghost. The correct involution is the shadow SWAP
   S = [[0,1],[1,0]], which satisfies S^2 = +I.

2. The right object is not a bare Gram matrix but the CROSS-SHADOW BLOCK of the
   covariance. For a Gaussian measure with covariance C and a reflection theta
   exchanging two halves, RP holds iff the cross block C_AB is positive
   semi-definite. That is the quantity computed here.

WHAT THE GATE IS ACTUALLY FOR (2026-08-21 finding)
--------------------------------------------------
At the framework's vacuum every bridge is orthogonal (theta = pi/2), so every
cross-shadow coupling L1*L2*cos(theta) is zero and the gate reports
MARGINAL_VACUOUS. That could look useless. It is not, because of this:

    the racetrack potential depends on theta ONLY through the area
    T = L1*L2*sin(theta), and sin is symmetric about pi/2.

Therefore V(theta) = V(pi - theta) EXACTLY: the framework's own moduli
dynamics cannot distinguish an acute bridge from its obtuse mirror. Verified
by calling racetrack_potential directly at 30/45/60/75/89 degrees against
their supplements - identical to 12 significant figures.

Reflection positivity CAN distinguish them: cos(theta) flips sign, so the
obtuse branch carries a negative cross-coupling and is a ghost. The declared
moduli bounds are (0.1, pi - 0.1), i.e. up to 174 degrees, so RP forbids
50% of the currently-allowed range.

So the gate's value is as a BRANCH SELECTOR on a direction the potential
leaves degenerate, not as a test of the vacuum. That is a genuine constraint
the framework does not otherwise impose.

WHERE THE BREATHING COUPLING IS NOT
-----------------------------------
Searched: the breathing mode in this codebase is a SCALAR field tied to the
bridge SIZE (the Kahler modulus T = area), not to the angle. No antisymmetric
or Chern-Simons cross-shadow term exists anywhere (the only F ^ F is the
standard axial anomaly in appendix Q, unrelated). So cross-shadow coupling is
currently: zero at the vacuum, carried by the shear direction theta, and
unconstrained in sign by the potential.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

__all__ = [
    "shadow_swap",
    "bridge_cross_block",
    "reflection_positivity_report",
]

# Numerical tolerance for calling an eigenvalue non-negative.
_TOL = 1e-12


def shadow_swap(n_pairs: int = 12) -> np.ndarray:
    """The RP involution: exchange shadow A and shadow B coordinatewise.

    Each bridge pair contributes coordinates (y1_i, y2_i) with y1 in shadow A
    and y2 in shadow B, so the exchange is block-diagonal with 2x2 blocks
    [[0,1],[1,0]]. Unlike R_perp this squares to +I, as a reflection must.
    """
    S = np.zeros((2 * n_pairs, 2 * n_pairs))
    for i in range(n_pairs):
        S[2 * i, 2 * i + 1] = 1.0
        S[2 * i + 1, 2 * i] = 1.0
    return S


def bridge_cross_block(metrics_2d: List[np.ndarray]) -> np.ndarray:
    """Cross-shadow coupling block C_AB extracted from the bridge metrics.

    For each pair the 2x2 metric is
        [[L1^2,            L1 L2 cos(theta)],
         [L1 L2 cos(theta), L2^2           ]]
    whose OFF-DIAGONAL entry is precisely the shadow-A to shadow-B coupling.
    Collecting them gives the diagonal cross block, one entry per pair.
    """
    n = len(metrics_2d)
    C_AB = np.zeros((n, n))
    for i, g in enumerate(metrics_2d):
        C_AB[i, i] = float(g[0, 1])
    return C_AB


def reflection_positivity_report(
    metrics_2d: Optional[List[np.ndarray]] = None,
) -> Dict[str, Any]:
    """Run the gate. Returns a machine-readable verdict.

    Args:
        metrics_2d: the 12 bridge 2x2 metrics. If omitted, they are read from
            the live BridgeSystem so the gate tracks the framework's own moduli.
    """
    if metrics_2d is None:
        from metaphysica.simulations.PM.geometry.bridge_geometry import BridgeSystem
        metrics_2d = [b.metric_2d for b in BridgeSystem().bridges]

    n_pairs = len(metrics_2d)
    S = shadow_swap(n_pairs)

    # --- involution sanity: the thing we reflect with must be a reflection ---
    involution_ok = bool(np.allclose(S @ S, np.eye(2 * n_pairs)))

    # --- the R_perp counter-check, kept so the false alarm stays documented ---
    Rp = np.zeros_like(S)
    for i in range(n_pairs):
        Rp[2 * i, 2 * i + 1] = -1.0
        Rp[2 * i + 1, 2 * i] = 1.0
    rperp_is_involution = bool(np.allclose(Rp @ Rp, np.eye(2 * n_pairs)))
    rperp_sym_part_norm = float(np.linalg.norm((Rp + Rp.T) / 2.0))

    # --- the actual gate ---------------------------------------------------
    C_AB = bridge_cross_block(metrics_2d)
    sym = (C_AB + C_AB.T) / 2.0
    eigs = np.linalg.eigvalsh(sym)
    min_eig = float(eigs.min())
    psd = bool(min_eig >= -_TOL)

    # per-pair diagnosis: which bridge (if any) carries a negative coupling
    offenders = [
        {"pair": i, "coupling": float(C_AB[i, i])}
        for i in range(n_pairs)
        if C_AB[i, i] < -_TOL
    ]

    # --- vacuity check -----------------------------------------------------
    # A PASS is worthless if the thing under test is identically zero. The
    # framework's bridges are orthogonal (theta = pi/2 exactly), so every
    # cross-shadow coupling is L1*L2*cos(pi/2) = 0 and the cross block is the
    # zero matrix - which is trivially PSD. Report that as MARGINAL_VACUOUS,
    # not PASS: the gate is sitting exactly on the RP boundary and is testing
    # a sector with no coupling in it.
    max_abs = float(np.max(np.abs(C_AB))) if C_AB.size else 0.0
    vacuous = max_abs <= 1e-12
    if vacuous:
        verdict = "MARGINAL_VACUOUS"
    elif psd:
        verdict = "PASS"
    else:
        verdict = "FAIL"

    # --- the constraint the gate actually derives --------------------------
    # Per pair the cross block is the scalar L1*L2*cos(theta), so
    #     RP  <=>  cos(theta) >= 0  <=>  theta <= 90 degrees.
    # The framework sits at exactly 90 deg: the last angle at which RP holds.
    constraint = {
        "statement": "reflection positivity requires bridge angle theta <= 90 deg",
        "reason": "cross block per pair is L1*L2*cos(theta); PSD iff cos(theta) >= 0",
        "framework_theta_deg": 90.0,
        "position": "boundary - RP holds marginally, with zero coupling",
        "falsifiable": "any obtuse bridge angle (theta > 90 deg) introduces a ghost mode",
    }

    return {
        "gate": "reflection_positivity_bridge_sector",
        "n_pairs": n_pairs,
        "involution": {
            "operator": "shadow swap S, blockwise [[0,1],[1,0]]",
            "S_squared_is_identity": involution_ok,
            "note": (
                "R_perp is NOT usable here: R_perp^2 = -I (order 4), and its "
                "Gram form is antisymmetric so its symmetric part vanishes "
                "identically - it would fail for algebraic reasons rather than "
                "physical ones."
            ),
            "r_perp_is_involution": rperp_is_involution,
            "r_perp_symmetric_part_norm": rperp_sym_part_norm,
        },
        "cross_block_eigenvalues": [float(x) for x in eigs],
        "min_eigenvalue": min_eig,
        "positive_semidefinite": psd,
        "verdict": verdict,
        "vacuous": vacuous,
        "max_abs_coupling": max_abs,
        "derived_constraint": constraint,
        "offending_pairs": offenders,
        "scope": (
            "Quadratic/Gaussian sector only, from the 12 bridge-pair metrics. "
            "PASS does not establish RP for the full theory; FAIL rules it out "
            "for the quadratic sector and closes the modular route."
        ),
    }


def write_report(
    report: Optional[Dict[str, Any]] = None, out_path: Optional[Path] = None
) -> Path:
    """Emit AutoGenerated/reflection_positivity.json.

    Every other wired gate writes a machine-readable report; this one only
    printed, which is why it was never wired into the build.
    """
    if report is None:
        report = reflection_positivity_report()
    if out_path is None:
        raw = os.environ.get("METAPHYSICA_OUT")
        base = Path(raw).resolve() if raw else Path(__file__).resolve().parents[5]
        out_path = base / "AutoGenerated" / "reflection_positivity.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    verdict = report.get("verdict", "UNKNOWN")
    payload: Dict[str, Any] = {
        "schema_version": 1,
        "count": 1,
        "n_pass": 1 if verdict == "PASS" else 0,
        "n_fail": 1 if verdict == "FAIL" else 0,
        "verdict": verdict,
        "report": report,
        "note": (
            "Reflection positivity on the bridge / shadow-coupling sector. "
            "MARGINAL_VACUOUS is reported -- rather than PASS -- when the "
            "cross block is identically zero, because a gate cannot certify "
            "positivity of something that is not there. The framework sits "
            "at theta = 90 degrees exactly, where cos(theta) = 0 switches "
            "the metric cross-coupling off, which is precisely that case."
        ),
    }
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out_path


def main() -> int:
    rep = reflection_positivity_report()
    print("=" * 64)
    print(" REFLECTION-POSITIVITY GATE - bridge / shadow-coupling sector")
    print("=" * 64)
    print(f"  bridge pairs            : {rep['n_pairs']}")
    print(f"  involution S^2 = I      : {rep['involution']['S_squared_is_identity']}")
    print(f"  (R_perp is involution?) : {rep['involution']['r_perp_is_involution']}"
          "   <- must be False; R_perp has order 4")
    print(f"  min eigenvalue          : {rep['min_eigenvalue']:.6e}")
    print(f"  positive semi-definite  : {rep['positive_semidefinite']}")
    print(f"  VERDICT                 : {rep['verdict']}")
    if rep["offending_pairs"]:
        print("  offending pairs:")
        for o in rep["offending_pairs"]:
            print(f"    pair {o['pair']:2d}: coupling = {o['coupling']:.6e}")
    print()
    print("  " + rep["scope"])
    out = write_report(rep)
    print()
    print(f"  Report written to: {out}")
    # MARGINAL_VACUOUS is an honest verdict, not a build failure.
    return 1 if rep["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
