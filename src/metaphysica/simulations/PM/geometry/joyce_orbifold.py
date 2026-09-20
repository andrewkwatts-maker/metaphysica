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
    "coordinate_characters",
    "invariant_p_forms",
    "flat_betti_report",
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


def coordinate_characters(g2=None) -> Dict[int, Tuple[int, ...]]:
    """Each coordinate's character under Gamma, as a tuple of signs.

    This is the object that makes every flat Betti number fall out at once, and
    the reason they are what they are.
    """
    group = diagonal_stabiliser(g2)
    return {i: tuple(eps[i] for eps in group) for i in range(_N_COORDS)}


def invariant_p_forms(p: int, g2=None) -> List[Tuple[int, ...]]:
    """The Gamma-invariant coordinate p-forms. Generalises R3 to any degree.

    A basis p-form e_{i1} ^ ... ^ e_{ip} survives the quotient exactly when the
    product of its coordinates' characters is trivial.
    """
    group = diagonal_stabiliser(g2)
    out = []
    for idx in itertools.combinations(range(_N_COORDS), p):
        if all(_prod(eps[i] for i in idx) == 1 for eps in group):
            out.append(idx)
    return out


def _prod(values) -> int:
    out = 1
    for v in values:
        out *= v
    return out


def flat_betti_report(g2=None) -> Dict[str, Any]:
    """R5: the flat cohomology of T^7/Gamma, derived from the characters.

    WHY b_2 FLAT = 0, AND WHY IT WAS NOT SAFE TO ASSERT IT
    ======================================================
    derived_contribution_table carried `FLAT_B2 = 0` with the comment that both
    it and b_3 = 7 are "DERIVED in joyce_orbifold". Only b_3 was: this module
    had no Lambda^2 function at all. The claim was true and its stated
    provenance was false, which is the more dangerous of the two failure modes
    because it reads as settled. Computed here.

    THE MECHANISM, AND IT SETTLES EVERY DEGREE AT ONCE
    ==================================================
    (Z/2)^3 has exactly 8 characters: the trivial one and 7 non-trivial ones.
    Measured, the 7 coordinates of T^7 realise the 7 NON-TRIVIAL characters
    BIJECTIVELY -- one each, none trivial. Everything follows:

      b_1 flat = 0   no coordinate carries the trivial character.

      b_2 flat = 0   chi_i * chi_j is trivial iff chi_i = chi_j iff i = j, and a
                     2-form needs i /= j. So there is no invariant 2-form --
                     not "none were found", but none can exist.

      b_3 flat = 7   chi_i chi_j chi_k trivial means the three characters sum to
                     zero in (Z/2)^3. The 7 non-trivial characters ARE the 7
                     points of PG(2,2), and zero-sum triples are exactly its 7
                     LINES. So the invariant 3-forms are the Fano lines -- which
                     is why they coincide with phi's own support, and why R3 and
                     R4 were always the same fact seen twice.

    So the coordinate index set is a copy of the Fano plane, and that single
    fact -- not phi, and not the real form -- is what fixes the flat sector.
    """
    chars = coordinate_characters(g2)
    distinct = sorted(set(chars.values()))
    group = diagonal_stabiliser(g2)
    trivial = tuple([1] * len(group))

    inv = {p: invariant_p_forms(p, g2) for p in range(_N_COORDS + 1)}
    betti = {p: len(v) for p, v in inv.items()}

    # Two self-checks that can fail, and both are non-trivial consequences
    # rather than restatements of the computation:
    #   Poincare duality b_p = b_{7-p} on a closed orientable 7-manifold, and
    #   chi = 0, which is forced in any odd dimension.
    poincare = all(betti[p] == betti[_N_COORDS - p]
                   for p in range(_N_COORDS + 1))
    euler = sum((-1) ** p * betti[p] for p in range(_N_COORDS + 1))

    return {
        "group_order": len(group),
        "poincare_duality_holds": poincare,
        "euler_characteristic": euler,
        "euler_is_zero_as_odd_dimension_requires": euler == 0,
        "n_distinct_coordinate_characters": len(distinct),
        "any_coordinate_is_trivial": trivial in distinct,
        "characters_realise_all_nontrivial_bijectively": (
            len(distinct) == _N_COORDS
            and len(distinct) == len(group) - 1
            and trivial not in distinct
        ),
        "flat_betti": betti,
        "b1_flat": len(inv[1]),
        "b2_flat": len(inv[2]),
        "b3_flat": len(inv[3]),
        "invariant_two_forms": inv[2],
        "invariant_three_forms": inv[3],
        "b3_flat_equals_fano_lines": (
            sorted(inv[3]) == sorted(group_fano_lines(g2))
        ),
        "why_b2_is_zero": (
            "chi_i * chi_j is trivial only when chi_i = chi_j, and the seven "
            "coordinate characters are distinct, so no i /= j pair is "
            "invariant. b_2 flat = 0 is forced, not observed."
        ),
        "provenance_correction": (
            "derived_contribution_table's FLAT_B2 = 0 was commented as DERIVED "
            "in joyce_orbifold, which had no Lambda^2 computation. The value "
            "was right; the citation was not. Derived here as R5."
        ),
    }


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
