"""The Joyce orbifold T^7/Gamma, derived from phi rather than postulated.

WHY THIS EXISTS
---------------
Almost everything the framework would like to compute about its G2 manifold --
the triple intersection numbers d_ijk, the M2 tadpole, the Yukawa overlap
integrals -- needs an EXPLICIT Y_7, and the framework has none. It carries
Betti numbers and combinatorics, not a metric.

The way past that is to stop needing Y_7. Joyce's compact G2 manifolds are
resolutions of the flat orbifold T^7/Gamma, and the flat orbifold is entirely
explicit: a finite group acting linearly on R^7, so everything here is finite
group theory and linear algebra on Lambda^3(R^7). No metric is required and
none is assumed.

WHAT IS DERIVED HERE
--------------------
Four results, each computed from the framework's own phi (read through
`associative_triples`, not restated):

  R1  The diagonal sign flips preserving phi form a group of order 8 --
      exactly (Z/2)^3, which is Joyce's group. It is FORCED by phi, not chosen,
      so the Joyce construction is motivated rather than assumed.

  R2  Each of the 7 non-identity elements flips exactly 4 coordinates, and
      those 4-sets are precisely the 7 Fano ARCS (the 4-subsets containing no
      line). Each flipped set is the complement of a Fano line.

      This DERIVES the 4 + 3 split the four-face structure rests on: the four
      faces are the coordinates an involution MOVES, the three blocks are the
      coordinates it FIXES. Previously a labelling convention; now the
      moved/fixed decomposition of a group element.

  R3  The Gamma-invariant subspace of Lambda^3(R^7) has dimension exactly 7,
      spanned by exactly the 7 triples of phi. So the flat (untwisted)
      contribution to b_3 is 7.

  R4  The 7 non-identity elements are the non-zero vectors of F_2^3, i.e. the
      points of PG(2,2), and the triples whose product is the identity are its
      lines: 7 of them. So a SECOND Fano plane sits on Gamma itself, dual to
      the coordinate one via  element <-> arc <-> complement line.

WHAT IS NOT DERIVED -- READ THIS BEFORE QUOTING b_3 = 7 + 17
------------------------------------------------------------
R3 gives the flat sector only. If b_3 = 24 then the resolution of the singular
loci must contribute 24 - 7 = 17, but **17 is obtained by subtraction under the
assumption b_3 = 24**; it is not computed, and nothing here proves b_3 = 24.

Only the LINEAR part of Gamma is used. Joyce's Gamma also carries half-shift
translations, and those are what fix the singular loci and hence the twisted
sector. So these results constrain the linear action and the flat sector and
say nothing yet about the 17.

The counts (8, 7, 7, 7) were checked against two different sign conventions for
phi -- the framework's all-(+1) convention and the (+,+,+,+,-,-,-) convention --
and are the same in both, so they are structural rather than an artifact of the
labelling.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import itertools
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

__all__ = [
    "lambda3_basis",
    "phi_vector",
    "sign_action_on_lambda3",
    "diagonal_stabiliser",
    "involution_arc_correspondence",
    "invariant_three_forms",
    "group_fano_lines",
    "orbifold_report",
]

#: The dimension of the space phi lives in. dim Lambda^3(R^7) = C(7,3) = 35,
#: which splits under G2 as 1 + 7 + 27.
_N_COORDS = 7


def _g2():
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    return G2DifferentialGeometry()


def lambda3_basis() -> List[Tuple[int, int, int]]:
    """The 35 coordinate 3-forms dx^i ^ dx^j ^ dx^k with i < j < k."""
    return list(itertools.combinations(range(_N_COORDS), 3))


def phi_vector(g2=None) -> np.ndarray:
    """phi as a 35-vector in the ordered Lambda^3 basis.

    Read from the framework's own phi so this module cannot drift from it, and
    so the results below are statements about the framework's G2 structure
    rather than about a convention chosen here.
    """
    g2 = g2 or _g2()
    phi = g2.phi
    return np.array([float(phi[t]) for t in lambda3_basis()])


def sign_action_on_lambda3(eps: Sequence[int]) -> np.ndarray:
    """How a diagonal sign flip on R^7 acts on the 35 basis 3-forms.

    dx^i ^ dx^j ^ dx^k picks up eps_i eps_j eps_k, so the action is diagonal
    and its entries are products of three signs.
    """
    return np.array([eps[i] * eps[j] * eps[k] for (i, j, k) in lambda3_basis()])


def diagonal_stabiliser(g2=None) -> List[Tuple[int, ...]]:
    """R1: every diagonal sign flip on R^7 that preserves phi.

    Returns the group elements as tuples of +-1. The result is a group of order
    8 isomorphic to (Z/2)^3 -- Joyce's group -- and it is derived from phi here
    rather than assumed.

    The search is exhaustive over all 2^7 = 128 sign patterns, so there is no
    tolerance to tune and nothing to converge.
    """
    vec = phi_vector(g2)
    out = []
    for eps in itertools.product((1, -1), repeat=_N_COORDS):
        if np.allclose(sign_action_on_lambda3(eps) * vec, vec):
            out.append(eps)
    return out


def involution_arc_correspondence(g2=None) -> List[Dict[str, Any]]:
    """R2: each non-identity element flips an ARC and fixes a LINE.

    For every non-identity element of the stabiliser, report which coordinates
    it moves and which it fixes, and whether the moved set is a Fano arc (a
    4-subset containing no line) whose complement is a line.

    This is where the 4 + 3 split comes from: 4 moved coordinates (the faces)
    and 3 fixed ones (the blocks).
    """
    from metaphysica.simulations.PM.gauge.topological_terms import (
        associative_triples,
    )

    g2 = g2 or _g2()
    lines = {frozenset(t) for t in associative_triples(g2)}
    all_pts = set(range(_N_COORDS))

    out = []
    for eps in diagonal_stabiliser(g2):
        moved = frozenset(i for i, s in enumerate(eps) if s < 0)
        if not moved:
            continue                      # identity
        fixed = frozenset(all_pts - moved)
        contains_line = any(L <= moved for L in lines)
        out.append({
            "element": eps,
            "moved": tuple(sorted(moved)),
            "fixed": tuple(sorted(fixed)),
            "n_moved": len(moved),
            "moved_is_arc": len(moved) == 4 and not contains_line,
            "fixed_is_line": fixed in lines,
        })
    return out


def invariant_three_forms(g2=None) -> List[Tuple[int, int, int]]:
    """R3: the Gamma-invariant coordinate 3-forms -- the flat part of b_3.

    A basis 3-form survives the quotient exactly when every group element acts
    on it with +1. The result is the 7 triples of phi itself, so the flat
    contribution to b_3 is 7.

    This is the UNTWISTED sector only. The resolution of the singular loci
    contributes separately and is not computed here -- see the module
    docstring before quoting b_3 = 7 + 17.
    """
    group = diagonal_stabiliser(g2)
    basis = lambda3_basis()
    actions = [sign_action_on_lambda3(eps) for eps in group]
    return [basis[i] for i in range(len(basis))
            if all(a[i] == 1 for a in actions)]


def group_fano_lines(g2=None) -> List[Tuple[int, int, int]]:
    """R4: the Fano plane carried by Gamma itself.

    The 7 non-identity elements are the non-zero vectors of F_2^3, so they are
    the points of PG(2,2). Its lines are the triples that sum to zero, which in
    multiplicative notation means the three elements multiply to the identity.

    Returns index triples into the non-identity element list.
    """
    nz = [np.array(eps) for eps in diagonal_stabiliser(g2)
          if any(s < 0 for s in eps)]
    ident = np.ones(_N_COORDS, dtype=int)
    return [(a, b, c) for a, b, c in itertools.combinations(range(len(nz)), 3)
            if np.array_equal(nz[a] * nz[b] * nz[c], ident)]


def orbifold_report(g2=None) -> Dict[str, Any]:
    """All four results, with what is derived and what is not."""
    g2 = g2 or _g2()
    group = diagonal_stabiliser(g2)
    corr = involution_arc_correspondence(g2)
    inv = invariant_three_forms(g2)
    lines = group_fano_lines(g2)

    from metaphysica.simulations.PM.gauge.topological_terms import (
        associative_triples,
    )
    triples = set(associative_triples(g2))

    ident = tuple([1] * _N_COORDS)
    as_arrays = [np.array(e) for e in group]
    closed = all(
        any(np.array_equal(a * b, c) for c in as_arrays)
        for a in as_arrays for b in as_arrays
    )

    return {
        # R1
        "stabiliser_order": len(group),
        "is_z2_cubed": len(group) == 8,
        "is_closed_group": bool(closed),
        "all_involutions": all(
            np.array_equal(a * a, np.ones(_N_COORDS, dtype=int))
            for a in as_arrays
        ),
        "identity_present": ident in group,
        # R2
        "n_nonidentity": len(corr),
        "every_element_moves_four": all(c["n_moved"] == 4 for c in corr),
        "every_moved_set_is_an_arc": all(c["moved_is_arc"] for c in corr),
        "every_fixed_set_is_a_line": all(c["fixed_is_line"] for c in corr),
        "correspondence": corr,
        # R3
        "flat_b3_contribution": len(inv),
        "invariant_three_forms": inv,
        "invariants_are_exactly_phi": set(inv) == triples,
        # R4
        "group_fano_line_count": len(lines),
        "group_carries_a_fano_plane": len(lines) == 7,
        # honesty
        "twisted_sector_contribution": None,
        "note": (
            "Linear part of Gamma only. The flat sector contributes "
            "%d to b_3; the twisted (resolution) sector is NOT computed here, "
            "so if b_3 = 24 the remaining 17 is obtained by subtraction under "
            "that assumption and is not derived. Nothing here proves b_3 = 24."
            % len(inv)
        ),
    }


if __name__ == "__main__":  # pragma: no cover
    r = orbifold_report()
    print("=" * 66)
    print(" JOYCE ORBIFOLD T^7/Gamma -- derived from phi")
    print("=" * 66)
    print(" R1  stabiliser order          : %d  (Z/2)^3: %s"
          % (r["stabiliser_order"], r["is_z2_cubed"]))
    print("     closed group / involutions: %s / %s"
          % (r["is_closed_group"], r["all_involutions"]))
    print(" R2  non-identity elements     : %d" % r["n_nonidentity"])
    print("     each moves 4 coordinates  : %s" % r["every_element_moves_four"])
    print("     each moved set is an arc  : %s" % r["every_moved_set_is_an_arc"])
    print("     each fixed set is a line  : %s" % r["every_fixed_set_is_a_line"])
    for c in r["correspondence"]:
        print("       moves %-12s fixes %-9s"
              % (str(c["moved"]), str(c["fixed"])))
    print(" R3  flat b_3 contribution     : %d" % r["flat_b3_contribution"])
    print("     invariants are exactly phi: %s" % r["invariants_are_exactly_phi"])
    print(" R4  lines on Gamma            : %d  Fano plane: %s"
          % (r["group_fano_line_count"], r["group_carries_a_fano_plane"]))
    print()
    print(" NOTE: %s" % r["note"])
