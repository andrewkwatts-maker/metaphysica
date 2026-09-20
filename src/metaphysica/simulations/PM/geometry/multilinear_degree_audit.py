"""Which multilinear invariants exist on Y_7, by degree arithmetic alone.

WHY THIS EXISTS
===============
The framework repeatedly wants a triple intersection form on H^3. The register
carries it as a blocked item -- "triple intersection numbers d_ijk need a
harmonic basis on an actual Y_7" -- and a proposed route wrote

    N_IJK = int_M omega_I ^ omega_J ^ omega_K,   omega in H^3

That integral is not blocked. It is **not defined**: 3 + 3 + 3 = 9, and a
9-form on a 7-manifold is identically zero. No metric, no harmonic
representative and no resolution would change that, so the item closes by
REFUTATION rather than by supplying the missing ingredient. A refutation is a
closure, and it is worth more here than a long search would have been.

Having established that, the useful question is the positive one: *which*
multilinear pairings DO exist? That is also pure degree arithmetic, so it can be
answered completely rather than guessed at. This module enumerates them.

WHAT COMES OUT, FOR THE 43 PATH (b_2 = 12, b_3 = 43)
====================================================
The admissible pairings are the ways to write 7 as an ordered sum of degrees
whose Betti numbers are all non-zero. On a compact G2 7-manifold with b_1 = 0
that is a short list, and the two that matter are:

    H^3 x H^4 -> Z          Poincare duality; 3 + 4 = 7
    H^2 x H^2 x H^3 -> Z    2 + 2 + 3 = 7

The second is the object the retired external-lattice Gram matrix was standing
in for. With b_2 = 12 and b_3 = 43 it is a 12 x 12 x 43 tensor of INTEGERS,
metric-free, and it can break isotropy where a lattice shell could not -- the
Leech and E8^3 routes failed because Co_0 and W(E8)^3 are large enough that
Schur's lemma forces the shell form proportional to the identity. An integer
tensor carries no such symmetry.

Note what is NOT on the list: any pairing of H^3 with itself. There is no
topological cubic form on H^3 of a 7-manifold, so the intrinsic route does not
escape the metric after all -- the only bilinear on H^3 alone is the Hodge
pairing int omega_I ^ *omega_J, which needs a metric. Dropping the external
lattice costs a metric-free Gram matrix, and that cost is real rather than
presentational.

THE A4 BAR
==========
Everything here counts DEGREES of differential forms. It never converts a degree
into a dimension, a group order, or a cycle count. `verdict` says which, per row.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "wedge_degree",
    "is_top_form",
    "audit_pairing",
    "admissible_pairings",
    "refuted_pairings",
    "degree_audit_report",
]

#: The dimension of the internal manifold. Not a magic number: it is the
#: dimension a G2 structure lives on, and every statement here is relative to it.
_DIM = 7


def wedge_degree(degrees: Sequence[int]) -> int:
    """The degree of a wedge product. Degrees add; that is the whole content."""
    return int(sum(degrees))


def is_top_form(degrees: Sequence[int], dim: int = _DIM) -> bool:
    """Whether the wedge is a top form, so its integral can be non-zero."""
    return wedge_degree(degrees) == dim


def audit_pairing(degrees: Sequence[int], dim: int = _DIM,
                  betti: Optional[Dict[int, int]] = None) -> Dict[str, Any]:
    """Type-check one proposed multilinear pairing by degree.

    Three outcomes, and the distinction between the last two matters:

      ADMISSIBLE    degrees sum to dim and every factor has a non-zero Betti
                    number, so the pairing exists and is non-trivial
      VANISHES      degrees sum to dim but some factor's cohomology is zero, so
                    the pairing exists and is identically zero
      NOT_DEFINED   degrees do not sum to dim. Over dim the form is zero for
                    every input; under dim the integral is not defined at all
    """
    total = wedge_degree(degrees)
    row: Dict[str, Any] = {
        "degrees": tuple(int(d) for d in degrees),
        "total_degree": total,
        "dim": dim,
        "counts": "degrees of differential forms",
    }

    if total != dim:
        row["verdict"] = "NOT_DEFINED"
        row["why"] = (
            "%s = %d, and the manifold has dimension %d. %s"
            % (" + ".join(str(d) for d in degrees), total, dim,
               "A form of degree above the dimension is identically zero."
               if total > dim else
               "A form below top degree has no canonical integral over the "
               "whole manifold.")
        )
        return row

    zero_factors = []
    if betti is not None:
        zero_factors = [d for d in degrees if betti.get(d, 0) == 0]

    if zero_factors:
        row["verdict"] = "VANISHES"
        row["why"] = (
            "degrees sum to %d correctly, but H^%s is zero, so the pairing is "
            "identically zero rather than unavailable"
            % (dim, sorted(set(zero_factors)))
        )
        return row

    row["verdict"] = "ADMISSIBLE"
    row["why"] = "degrees sum to %d and every factor is non-trivial" % dim
    if betti is not None:
        row["tensor_shape"] = tuple(betti[d] for d in degrees)
    return row


def admissible_pairings(betti: Dict[int, int], dim: int = _DIM,
                        max_factors: int = 4) -> List[Dict[str, Any]]:
    """Every multilinear pairing that exists and is non-trivial, enumerated.

    Complete for up to `max_factors` factors: partitions of `dim` into positive
    degrees whose Betti numbers are all non-zero. Reported in a canonical order
    (fewest factors first, then lexicographic) so the list never depends on
    iteration order.
    """
    live = sorted(d for d in range(1, dim + 1) if betti.get(d, 0) > 0)
    out: List[Dict[str, Any]] = []
    for k in range(2, max_factors + 1):
        for combo in itertools.combinations_with_replacement(live, k):
            if wedge_degree(combo) != dim:
                continue
            out.append(audit_pairing(combo, dim=dim, betti=betti))
    out.sort(key=lambda r: (len(r["degrees"]), r["degrees"]))
    return out


def refuted_pairings(dim: int = _DIM) -> List[Dict[str, Any]]:
    """The pairings the framework has proposed that do not typecheck.

    Kept on the books per the standing rule: a refuted route stays visible with
    its reason, so it is not re-proposed.
    """
    rows = []
    row = audit_pairing((3, 3, 3), dim=dim)
    row["proposed_as"] = "N_IJK = int_M omega_I ^ omega_J ^ omega_K on H^3"
    row["register_item"] = "triple intersection numbers d_ijk"
    row["status"] = "REFUTED_BY_DEGREE"
    row["consequence"] = (
        "the d_ijk blocker closes by refutation, not by supplying a metric. "
        "There is no topological cubic form on H^3 of a 7-manifold."
    )
    rows.append(row)

    row = audit_pairing((3, 3), dim=dim)
    row["proposed_as"] = "a topological bilinear form on H^3 alone"
    row["status"] = "REFUTED_BY_DEGREE"
    row["consequence"] = (
        "3 + 3 = 6 /= 7, so the only bilinear on H^3 is the Hodge pairing "
        "int omega_I ^ *omega_J, which is METRIC-DEPENDENT. The intrinsic route "
        "does not escape the metric; dropping the external lattice really does "
        "cost a metric-free Gram matrix."
    )
    rows.append(row)
    return rows


def degree_audit_report(betti: Optional[Dict[int, int]] = None,
                        dim: int = _DIM) -> Dict[str, Any]:
    """The full audit: what exists, what is refuted, and what it buys.

    `betti` defaults to the flat-sector-plus-resolution profile of the 43 path,
    read from the modules that derive it rather than tabulated here.
    """
    if betti is None:
        betti = _betti_43_path()

    admissible = admissible_pairings(betti, dim=dim)
    refuted = refuted_pairings(dim=dim)

    three_four = [r for r in admissible if r["degrees"] == (3, 4)]
    two_two_three = [r for r in admissible if r["degrees"] == (2, 2, 3)]

    return {
        "dim": dim,
        "betti": dict(sorted(betti.items())),
        "n_admissible": len(admissible),
        "admissible": admissible,
        "refuted": refuted,
        "poincare_pairing_available": bool(three_four),
        "metric_free_cubic_available": bool(two_two_three),
        "metric_free_cubic_shape": (
            two_two_three[0].get("tensor_shape") if two_two_three else None
        ),
        "no_cubic_form_on_h3": all(
            r["verdict"] == "NOT_DEFINED"
            for r in refuted if r["degrees"] == (3, 3, 3)
        ),
        "what_this_closes": (
            "the register's d_ijk blocker, by refutation: 3+3+3 = 9 > 7 so the "
            "object does not exist. No metric would help."
        ),
        "what_this_opens": (
            "H^2 x H^2 x H^3 -> Z at 2+2+3 = 7, a metric-free INTEGER tensor. "
            "It is the honest replacement for the retired lattice Gram matrix, "
            "and unlike a lattice shell it carries no large symmetry group to "
            "force isotropy by Schur."
        ),
        "counts": "degrees of differential forms, never dimensions or group orders",
    }


def _betti_43_path() -> Dict[int, int]:
    """Betti numbers of the 43 path, read from the deriving modules.

    b_1 = b_2flat = 0 and b_3flat = 7 come from joyce_orbifold R5; the
    resolution adds one exceptional 2-class and three 3-classes per A1 family,
    which for the canonical 12-family point gives b_2 = 12 and b_3 = 7 + 36.
    Poincare duality fixes the upper half.
    """
    from metaphysica.simulations.PM.geometry.derived_contribution_table import (
        FLAT_B2,
        FLAT_B3,
    )

    n_families = 12                       # the canonical point; 3 involutions x 4
    b2 = FLAT_B2 + n_families
    b3 = FLAT_B3 + 3 * n_families
    return {0: 1, 1: 0, 2: b2, 3: b3, 4: b3, 5: b2, 6: 0, 7: 1}
