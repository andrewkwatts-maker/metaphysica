"""Integer flux on the 43-form basis: what it freezes, and what it provably cannot.

THE SHAPE, AND WHERE THE PERIODS COME FROM
==========================================
    W(n) = sum_{I=1..43} n_I Pi_I ,   n in Z^43

with the periods Pi_I read from the LEADING-ORDER K_IJ that `metric_pairing`
builds -- Pi_I := K_II, the self-pairing of basis class I. That definition is
stated rather than assumed: K_IJ is diagonal at leading order, so K_II is the
only invariant a single class carries, and nothing here introduces a second
normalisation.

THE STRUCTURAL RESULT, AND IT DECIDES THE WHOLE QUESTION
========================================================
Measured on the live pairing: at leading order K_IJ is diagonal with exactly
**two distinct entries** --

    flat    (7 classes)    L^7 / |Gamma|  =  L^7 / 8
    twisted (36 classes)   orbit_size * L^3 * ||eta||^2  =  32 pi^2 L^3

-- and its **only free symbol is L**. The resolution parameter **t does not
appear in K_IJ at leading order at all.**

That is not an accident of bookkeeping, and the twenty-second pass already
found the reason: ||eta_EH||^2 = 8 pi^2 EXACTLY for every bolt radius, because
in four dimensions the L^2 norm of a 2-form is invariant under g -> t^2 g. The
twisted sector takes its entire t-dependence from the T^3 volume and the 1-form
legs, and at leading order that leaves L alone.

**Consequence: a flux potential built from the leading-order K_IJ can freeze at
most the single scale L, and can freeze NO t-modulus, because there is no t in
it to freeze.** This is a statement about the leading order, not about the
theory: the exact K_IJ certainly depends on t, and the O(t^2) cross-blocks that
`block_structure` reports are precisely where that dependence starts.

43 INTEGERS COLLAPSE TO 2
=========================
Because all 7 flat entries are equal and all 36 twisted entries are equal, W
depends on n only through

    A = sum over FLAT indices of n_I        B = sum over TWISTED indices of n_I

so the 43-dimensional flux lattice enters through two integers. Any claim that
a specific 43-vector does something a different vector with the same (A, B)
does not is false at this order.

STATIONARITY, AND WHAT IT IS AND IS NOT
=======================================
dW/dL = 0 gives 7 A L^6 / 8 + 96 pi^2 B L^2 = 0, so

    L_*^4 = - 768 pi^2 B / (7 A)

which is real and positive exactly when A and B have OPPOSITE SIGNS, and is a
minimum of W there. So L is frozen at a discrete set of values indexed by the
integer ratio B/A.

**This is stationarity of W, which is NOT a vacuum of the scalar potential.**
A vacuum needs V = e^K (K^{IJ} D_I W D_J W - 3|W|^2) or its G_2 analogue, hence
the Kahler potential and its derivatives, and the framework does not have them.
Every result below says `stationarity_of_W` and never says `vacuum`. Reporting
otherwise would be inventing the object the FLAVOUR and METRIC_DEPENDENT layers
are blocked on.

WHAT THIS DOES TO THE CLOSURE LEDGER: NOTHING, AND THE NULL IS THE RESULT
========================================================================
The correct targets are the **2 FLUX_DEPENDENT and 7 METRIC_DEPENDENT** rows.
Measured, none of them is frozen here:

  * the 7 METRIC_DEPENDENT rows are moduli VEVs and quantities built from them
    (`racetrack_Re_T`, `axion.theta_i`, `alpha_shadow`, `delta_b3_asymmetry`,
    `alpha_R_squared_phenom`, `alpha_T_phenomenological`, `vev_coefficient`,
    `H0_local`). They are t-like, and t is absent from the leading-order K_IJ.
  * the 2 FLUX_DEPENDENT rows are a gauge coupling and a weight. Freezing an
    overall torus scale does not supply either; they additionally need
    threshold data the framework does not have.
  * L itself is not a ledger row. Freezing it is real and is recorded, but it
    is not a reduction of the 22 continuous knobs.

So **the continuous count stays at 22**, and the reason is structural rather
than unfinished work. A measured null here is worth as much as a reduction,
and this one comes with an explicit condition under which it would change: it
takes the O(t^2) cross-blocks, not more integer flux vectors.

The proposal's claim that flux validates the 15 non-knobs conflates two ledger
layers and is not entertained here: the 15 include EXPERIMENTAL measured
anchors, and no flux quantum supplies a measured constant.

EVERY OUTPUT IS LEADING-ORDER-IN-T, tagged at every consumer.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "N_BASIS",
    "periods",
    "flux_invariants",
    "superpotential",
    "stationary_scale",
    "scan_flux_vectors",
    "moduli_in_the_pairing",
    "ledger_targets",
    "flux_report",
]

N_BASIS: int = 43


def _basis_kinds() -> List[str]:
    """'flat' or 'twisted' for each of the 43 classes, in K_IJ's own order."""
    from metaphysica.simulations.PM.geometry.twisted_form_basis import build_basis

    basis = build_basis()
    return ([rep["kind"] for rep in basis["flat"]]
            + [rep["kind"] for rep in basis["twisted"]])


def periods(orbit_convention: Optional[str] = None):
    """Pi_I := K_II, the self-pairing of each basis class. Symbolic in L.

    Read from `metric_pairing.pairing_matrix`, never retyped, so the
    `twisted_norm_convention` fork reaches this module without a second switch.
    """
    from metaphysica.simulations.PM.geometry.metric_pairing import pairing_matrix

    K = pairing_matrix(orbit_convention)
    if K.shape != (N_BASIS, N_BASIS):
        raise RuntimeError(
            "K_IJ is %s, not %dx%d; the basis and this module have diverged"
            % (K.shape, N_BASIS, N_BASIS))
    return [K[i, i] for i in range(N_BASIS)]


def moduli_in_the_pairing(orbit_convention: Optional[str] = None
                          ) -> Dict[str, Any]:
    """Which symbols the leading-order K_IJ actually contains.

    The load-bearing measurement of this module. If `t` ever appears here, the
    null result below stops holding and flux CAN start freezing a t-modulus.
    """
    from metaphysica.simulations.PM.geometry.metric_pairing import (
        pairing_matrix,
        pairing_symbols,
    )

    L, t = pairing_symbols()
    K = pairing_matrix(orbit_convention)
    symbols = set()
    for i in range(K.shape[0]):
        for j in range(K.shape[1]):
            symbols |= K[i, j].free_symbols

    distinct = sorted({str(K[i, i]) for i in range(K.shape[0])})
    return {
        "free_symbols": sorted(str(s) for s in symbols),
        "contains_L": L in symbols,
        "contains_t": t in symbols,
        "distinct_diagonal_entries": distinct,
        "n_distinct_diagonal_entries": len(distinct),
        "is_diagonal": all(K[i, j] == 0
                           for i in range(K.shape[0])
                           for j in range(K.shape[1]) if i != j),
        "why_t_is_absent": (
            "||eta_EH||^2 = 8 pi^2 exactly for every bolt radius -- in four "
            "dimensions the L^2 norm of a 2-form is scale-invariant -- so the "
            "twisted block carries no t, and at leading order neither does "
            "anything else in K_IJ"
        ),
        "order": "leading-order-in-t",
    }


def flux_invariants(n: Sequence[int]) -> Dict[str, Any]:
    """The only two combinations of n that W can see at leading order."""
    if len(n) != N_BASIS:
        raise ValueError("a flux vector has %d entries, got %d"
                         % (N_BASIS, len(n)))
    if any(int(x) != x for x in n):
        raise ValueError("flux quanta must be integers; got %r" % (list(n),))

    kinds = _basis_kinds()
    a = sum(int(x) for x, k in zip(n, kinds) if k == "flat")
    b = sum(int(x) for x, k in zip(n, kinds) if k == "twisted")
    return {
        "A_flat_sum": a,
        "B_twisted_sum": b,
        "counts_what": ("A and B are SUMS OF FLUX QUANTA over the flat and "
                        "twisted blocks -- integers, not dimensions"),
        "degeneracy": (
            "W depends on n only through (A, B), so every flux vector sharing "
            "them is indistinguishable at this order"
        ),
    }


def superpotential(n: Sequence[int], orbit_convention: Optional[str] = None):
    """W(n) = sum_I n_I Pi_I, symbolic in L. Leading order in t."""
    import sympy as sp

    pis = periods(orbit_convention)
    return sp.simplify(sum(sp.Integer(int(x)) * pi for x, pi in zip(n, pis)))


def stationary_scale(n: Sequence[int], orbit_convention: Optional[str] = None
                     ) -> Dict[str, Any]:
    """Solve dW/dL = 0 over the positive reals, for one integer flux vector.

    Returns the stationary scale when one exists. This is STATIONARITY OF W and
    is not a vacuum of the scalar potential; the module docstring says why, and
    the key name says it at every call site.
    """
    import sympy as sp

    from metaphysica.simulations.PM.geometry.metric_pairing import pairing_symbols

    L, _t = pairing_symbols()
    W = superpotential(n, orbit_convention)
    dW = sp.diff(W, L)
    roots = sp.solve(sp.Eq(dW, 0), L)
    positive = [r for r in roots if r.is_real and r.is_positive]

    inv = flux_invariants(n)
    second = sp.diff(W, L, 2)
    nature = None
    if positive:
        value = sp.simplify(second.subs(L, positive[0]))
        nature = ("minimum" if value.is_positive else
                  "maximum" if value.is_negative else "inflection")

    return {
        "A_flat_sum": inv["A_flat_sum"],
        "B_twisted_sum": inv["B_twisted_sum"],
        "W": str(W),
        "dW_dL": str(dW),
        "stationarity_of_W": bool(positive),
        "L_star": str(sp.simplify(positive[0])) if positive else None,
        "nature": nature,
        "requires_opposite_signs": (
            "L_*^4 = -768 pi^2 B / (7 A), so a positive real solution needs A "
            "and B of opposite sign"
        ),
        "not_a_vacuum": (
            "stationarity of W is not a vacuum of the scalar potential, which "
            "would need the Kahler potential and its derivatives. The "
            "framework does not have them."
        ),
        "order": "leading-order-in-t",
    }


def scan_flux_vectors(bound: int = 2,
                      orbit_convention: Optional[str] = None) -> Dict[str, Any]:
    """Sweep (A, B) over a box and report where stationarity of W exists.

    Sweeps the INVARIANTS rather than all 43-vectors, because W cannot
    distinguish vectors with the same (A, B) -- enumerating (2*bound+1)^43
    vectors would be a very expensive way to recompute the same function.
    """
    import sympy as sp

    from metaphysica.simulations.PM.geometry.metric_pairing import pairing_symbols

    L, _t = pairing_symbols()
    pis = periods(orbit_convention)
    kinds = _basis_kinds()
    flat_pi = next(pi for pi, k in zip(pis, kinds) if k == "flat")
    twisted_pi = next(pi for pi, k in zip(pis, kinds) if k == "twisted")

    rows = []
    for a, b in itertools.product(range(-bound, bound + 1), repeat=2):
        W = a * flat_pi + b * twisted_pi
        roots = sp.solve(sp.Eq(sp.diff(W, L), 0), L)
        positive = [r for r in roots if r.is_real and r.is_positive]
        rows.append({"A": a, "B": b,
                     "stationarity_of_W": bool(positive),
                     "L_star": str(sp.simplify(positive[0])) if positive
                     else None})

    with_point = [r for r in rows if r["stationarity_of_W"]]
    return {
        "bound": bound,
        "n_invariant_pairs": len(rows),
        "n_with_stationary_point": len(with_point),
        "all_have_opposite_signs": all(r["A"] * r["B"] < 0 for r in with_point),
        "rows": rows,
        "what_is_swept": (
            "the INVARIANTS (A, B), not 43-vectors: W is blind to any "
            "difference between flux vectors sharing them at this order"
        ),
        "order": "leading-order-in-t",
    }


def ledger_targets() -> Dict[str, Any]:
    """The 2 FLUX_DEPENDENT and 7 METRIC_DEPENDENT rows, and what freezes them.

    Read live from `closure_ledger`, so a reclassification reaches this report
    instead of leaving a stale list behind.
    """
    from metaphysica.simulations.core.closure_ledger import closure_ledger

    ledger = closure_ledger()
    flux_rows = [r["name"] for r in ledger if r["layer"] == "FLUX_DEPENDENT"]
    metric_rows = [r["name"] for r in ledger if r["layer"] == "METRIC_DEPENDENT"]
    pairing = moduli_in_the_pairing()

    return {
        "flux_dependent_rows": flux_rows,
        "n_flux_dependent": len(flux_rows),
        "metric_dependent_rows": metric_rows,
        "n_metric_dependent": len(metric_rows),
        "frozen_by_leading_order_flux": [],
        "why_none": (
            "the leading-order K_IJ contains only %s. The METRIC_DEPENDENT "
            "rows are moduli VEVs and quantities built from them, which are "
            "t-like, and t is absent. The FLUX_DEPENDENT rows are a gauge "
            "coupling and a weight, which additionally need threshold data. "
            "The one modulus that IS frozen, the overall torus scale L, is not "
            "a ledger row."
            % pairing["free_symbols"]
        ),
        "what_would_change_it": (
            "the O(t^2) cross-blocks, which `metric_pairing.block_structure` "
            "reports and which are the first place t enters K_IJ. Not more "
            "flux vectors: 43 integers already collapse to 2 at this order."
        ),
        "order": "leading-order-in-t",
    }


def flux_report(orbit_convention: Optional[str] = None) -> Dict[str, Any]:
    """The whole measurement: what freezes, what cannot, and the null recorded."""
    pairing = moduli_in_the_pairing(orbit_convention)
    targets = ledger_targets()
    example = [1] * 7 + [-1] * 36        # A = 7, B = -36: opposite signs
    stationary = stationary_scale(example, orbit_convention)
    sweep = scan_flux_vectors(2, orbit_convention)

    return {
        "n_basis": N_BASIS,
        "pairing": pairing,
        "moduli_frozen": ["L"] if stationary["stationarity_of_W"] else [],
        "moduli_not_frozen": ["t"],
        "example_flux_vector": {"A": 7, "B": -36,
                                "description": "+1 on every flat class, -1 on "
                                               "every twisted class"},
        "example_stationarity": stationary,
        "invariant_sweep": {k: v for k, v in sweep.items() if k != "rows"},
        "ledger": targets,
        "tightening": 0,
        "verdict": (
            "NO TIGHTENING. Flux quantization at leading order freezes the "
            "overall torus scale L and nothing else, because the leading-order "
            "K_IJ contains no t. None of the 2 FLUX_DEPENDENT or 7 "
            "METRIC_DEPENDENT rows is frozen, so the continuous count stays at "
            "22. The null is structural and carries the condition that would "
            "change it: the O(t^2) cross-blocks."
        ),
        "order": "leading-order-in-t",
    }
