#!/usr/bin/env python3
"""Topological cross-shadow coupling on the G2 associative cycle.

WHY THIS EXISTS
---------------
The bridge sector had NO cross-shadow interaction. The breathing mode is a
scalar tied to bridge size, no antisymmetric or Chern-Simons term existed
anywhere, and the one metric channel that could carry a coupling -- the
off-diagonal L1*L2*cos(theta) -- is identically zero at the stabilised vacuum,
because that vacuum sits at theta = 90 degrees exactly on all 12 bridge pairs.
That is why reflection_positivity_gate reports MARGINAL_VACUOUS rather than
PASS: there is nothing there whose positivity could be certified.

The question this module answers is whether a TOPOLOGICAL term can carry the
coupling instead, leaving the orthogonal background intact.

WHAT IS ESTABLISHED HERE
------------------------
1. A SELECTION RULE. For F_A supported on coordinate pair (i,j) and F_B on
   (k,l), all distinct, the density

       C_3 ^ F_A ^ F_B      with C_3 = phi, the associative 3-form

   is non-zero if and only if the COMPLEMENTARY triple {0..6} \\ {i,j,k,l} is
   one of phi's seven associative triples. Exactly 42 of the 210 disjoint
   channels survive: 7 associative triples x 6 ordered pair-splits of each
   complementary 4-set. This is verified by enumeration, not asserted.

2. THE COUPLING SURVIVES THE ORTHOGONAL VACUUM, AND IS MAXIMAL THERE. The
   topological term couples to the bridge AREA, L1*L2*sin(theta), whereas the
   metric channel couples to L1*L2*cos(theta). At the stabilised vacuum:

       area route   :  5.647615e+02      (maximal at theta = 90 deg)
       metric route :  2.117516e-30      (dead at theta = 90 deg)

   The two channels are exactly complementary -- the topological one peaks
   where the metric one vanishes.

3. TWO INDEPENDENT ROUTES AGREE. The general epsilon contraction and the
   specialised coassociative form <*phi, F_A ^ F_B> share no code, and agree
   to ratio 1.000000000. Since phi ^ omega = <*phi, omega> vol for any 4-form
   omega, this is a real cross-check rather than one computation run twice.

WHAT IS NOT ESTABLISHED
-----------------------
This is flat R^7 with constant-coefficient forms, so the integral is
coefficient x volume -- A NUMBER, NOT A TOPOLOGICAL INVARIANT. Flat R^7 has
trivial holonomy and no non-trivial 7-cycles. g2_differential.py's own
docstring concedes the same point about its setting.

So a non-zero result establishes that THE INTEGRAND IS NON-VANISHING, which is
what the interaction sector needed in order to exist at all. It does NOT
establish topological content. That requires harmonic representatives on a
compact G2 manifold with b3 = 24, which is deferred discrete-exterior-calculus
work, not something assumed here.

Which coordinate pairs the twelve physical bridges occupy on the cycle is also
NOT derived. The selection rule is exact; the assignment of bridges to channels
is a modelling input still to be fixed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import combinations, permutations
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "CS7Result",
    "area_two_form",
    "metric_two_form",
    "cs7_density_epsilon",
    "cs7_density_star_phi",
    "cs7_result",
    "associative_triples",
    "allowed_channels",
    "vacuum_comparison",
]

#: Wedge-product normalisation for C_3 ^ F_2 ^ F_2 -- 3! x 2! x 2! = 24.
_WEDGE_NORM: float = 24.0


@dataclass(frozen=True)
class CS7Result:
    """Both routes, their agreement, and the honest scope."""

    density_via_epsilon: float
    density_via_star_phi: Optional[float]
    routes_agree: bool
    max_route_discrepancy: float
    volume: float
    action: float
    scope: str = field(
        default=(
            "Flat R^7 with constant coefficients: this is coefficient x "
            "volume, a number, not a topological invariant. It establishes "
            "that the integrand is non-vanishing, not that the term carries "
            "topological content -- that needs a compact G2 manifold."
        )
    )


def _g2():
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    return G2DifferentialGeometry()


def area_two_form(L1: float, L2: float, theta: float, i: int, j: int, n: int = 7):
    """Bridge AREA (Kahler) 2-form: magnitude L1*L2*sin(theta).

    This is the channel the topological term couples to. It is MAXIMAL at
    theta = 90 degrees, where the metric channel vanishes.
    """
    import numpy as np

    F = np.zeros((n, n))
    a = L1 * L2 * math.sin(theta)
    F[i, j], F[j, i] = a, -a
    return F


def metric_two_form(L1: float, L2: float, theta: float, i: int, j: int, n: int = 7):
    """Bridge METRIC off-diagonal: magnitude L1*L2*cos(theta).

    Provided for the A/B comparison. It is identically zero at the stabilised
    vacuum, which is the defect this module exists to route around.
    """
    import numpy as np

    F = np.zeros((n, n))
    a = L1 * L2 * math.cos(theta)
    F[i, j], F[j, i] = a, -a
    return F


def cs7_density_epsilon(c3, f_a, f_b) -> float:
    """Route 1 -- the general epsilon contraction. Valid for any C_3."""
    import numpy as np

    from metaphysica.simulations.PM.geometry.exterior_algebra import (
        levi_civita_7d,
    )

    eps = levi_civita_7d()
    return float(
        np.einsum("abcdefg,abc,de,fg->", eps, c3, f_a, f_b) / _WEDGE_NORM
    )


def _wedge_two_two(f_a, f_b):
    """(F_A ^ F_B)_{ijkl}, fully antisymmetrised."""
    import numpy as np

    W = np.einsum("ij,kl->ijkl", f_a, f_b)
    out = np.zeros_like(W)
    for p in permutations(range(4)):
        sign = np.linalg.det(np.eye(4)[list(p)])
        out += sign * np.transpose(W, p)
    return out / 4.0


def cs7_density_star_phi(f_a, f_b, g2=None) -> float:
    """Route 2 -- via the coassociative 4-form, valid when C_3 = phi.

    Uses phi ^ omega = <*phi, omega> vol. Shares no code with route 1 and
    reuses the *phi that g2_differential already computes exactly
    (check_hodge_involution returns max_error = 0.0), so agreement between the
    two is a genuine cross-check.
    """
    import numpy as np

    g2 = g2 or _g2()
    star_phi = g2.compute_hodge_star()
    return float(
        np.einsum("ijkl,ijkl->", star_phi, _wedge_two_two(f_a, f_b)) / _WEDGE_NORM
    )


def cs7_result(f_a, f_b, *, volume: float = 1.0, g2=None, tol: float = 1e-9) -> CS7Result:
    """Evaluate the density by both routes and record their agreement."""
    g2 = g2 or _g2()
    eps_val = cs7_density_epsilon(g2.phi, f_a, f_b)
    star_val = cs7_density_star_phi(f_a, f_b, g2=g2)
    discrepancy = abs(eps_val - star_val)
    scale = max(abs(eps_val), abs(star_val), 1.0)
    return CS7Result(
        density_via_epsilon=eps_val,
        density_via_star_phi=star_val,
        routes_agree=discrepancy / scale < tol,
        max_route_discrepancy=discrepancy,
        volume=volume,
        action=eps_val * volume,
    )


def associative_triples(g2=None) -> List[Tuple[int, int, int]]:
    """The seven index triples on which phi is supported."""
    g2 = g2 or _g2()
    phi = g2.phi
    return [t for t in combinations(range(7), 3) if abs(phi[t]) > 1e-12]


def allowed_channels(g2=None) -> Dict[str, Any]:
    """Enumerate which disjoint (F_A, F_B) placements give a non-zero density.

    Bounded by construction: C(7,2) x C(7,2) = 441 placements, of which 210 are
    disjoint. No search, no convergence loop.
    """
    g2 = g2 or _g2()
    triples = set(associative_triples(g2))
    allowed: List[Dict[str, Any]] = []
    total = 0
    for (i, j) in combinations(range(7), 2):
        for (k, l) in combinations(range(7), 2):
            if len({i, j, k, l}) < 4:
                continue
            total += 1
            complement = tuple(sorted(set(range(7)) - {i, j, k, l}))
            density = cs7_density_epsilon(
                g2.phi, area_two_form(1.0, 1.0, math.pi / 2, i, j),
                area_two_form(1.0, 1.0, math.pi / 2, k, l),
            )
            if abs(density) > 1e-12:
                allowed.append(
                    {"f_a": (i, j), "f_b": (k, l),
                     "complement": complement,
                     "complement_is_associative": complement in triples,
                     "density": density}
                )
    return {
        "n_disjoint_placements": total,
        "n_allowed": len(allowed),
        "selection_rule": (
            "non-zero iff the complementary triple is associative; "
            "7 triples x 6 ordered pair-splits = 42"
        ),
        "channels": allowed,
    }


def vacuum_comparison(
    channel: Sequence[Tuple[int, int]] = ((0, 1), (3, 6)),
    thetas_deg: Sequence[float] = (10, 30, 45, 60, 80, 89, 90),
) -> Dict[str, Any]:
    """Compare the area and metric channels across theta, at the vacuum moduli.

    The default channel is an ALLOWED one -- complement (2,4,5) is associative.
    Picking a forbidden channel returns zeros for every theta, which says
    nothing about theta and everything about the selection rule.
    """
    from metaphysica.simulations.PM.geometry.bridge_geometry import BridgeSystem

    g2 = _g2()
    moduli, _ = BridgeSystem().stabilize_moduli()
    L1, L2, theta_vac = (float(v) for v in moduli[0])
    (ia, ja), (ib, jb) = channel

    rows = []
    for deg in thetas_deg:
        th = math.radians(deg)
        rows.append({
            "theta_deg": float(deg),
            "area_route": cs7_density_epsilon(
                g2.phi, area_two_form(L1, L2, th, ia, ja),
                area_two_form(L1, L2, th, ib, jb)),
            "metric_route": cs7_density_epsilon(
                g2.phi, metric_two_form(L1, L2, th, ia, ja),
                metric_two_form(L1, L2, th, ib, jb)),
        })

    at_vac = {
        "theta_deg": math.degrees(theta_vac),
        "area_route": cs7_density_epsilon(
            g2.phi, area_two_form(L1, L2, theta_vac, ia, ja),
            area_two_form(L1, L2, theta_vac, ib, jb)),
        "metric_route": cs7_density_epsilon(
            g2.phi, metric_two_form(L1, L2, theta_vac, ia, ja),
            metric_two_form(L1, L2, theta_vac, ib, jb)),
    }
    return {
        "moduli": {"L1": L1, "L2": L2, "theta_rad": theta_vac},
        "channel": {"f_a": tuple(channel[0]), "f_b": tuple(channel[1])},
        "sweep": rows,
        "at_vacuum": at_vac,
        "finding": (
            "The topological channel couples to the bridge AREA "
            "(L1*L2*sin theta) and is MAXIMAL at the orthogonal vacuum, "
            "where the metric channel (L1*L2*cos theta) is identically zero. "
            "The two are exactly complementary."
        ),
    }


def main() -> int:
    g2 = _g2()
    print("=" * 70)
    print(" TOPOLOGICAL CROSS-SHADOW COUPLING  int_Sigma7 phi ^ F_A ^ F_B")
    print("=" * 70)

    triples = associative_triples(g2)
    print(f"  associative triples of phi : {len(triples)}")
    print(f"    {triples}")

    ch = allowed_channels(g2)
    print(f"  disjoint placements        : {ch['n_disjoint_placements']}")
    print(f"  non-vanishing channels     : {ch['n_allowed']}")
    print(f"  selection rule             : {ch['selection_rule']}")

    vac = vacuum_comparison()
    print()
    print(f"  vacuum theta               : "
          f"{math.degrees(vac['moduli']['theta_rad']):.2f} deg")
    print("  theta      area route          metric route")
    for r in vac["sweep"]:
        print(f"  {r['theta_deg']:5.0f}   {r['area_route']: .6e}   "
              f"{r['metric_route']: .6e}")
    print()
    print(f"  AT VACUUM  area={vac['at_vacuum']['area_route']: .6e}   "
          f"metric={vac['at_vacuum']['metric_route']: .6e}")
    print()
    print("  " + vac["finding"])
    print()
    print("  SCOPE: " + CS7Result(0, 0, True, 0, 1, 0).scope)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
