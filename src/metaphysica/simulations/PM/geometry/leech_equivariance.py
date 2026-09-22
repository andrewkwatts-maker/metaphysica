"""Does a Gamma-equivariant linear map 24 -> 7 exist, and how big is the space?

THE PROPOSAL, AND THE HAZARD IN IT
==================================
"Project the deep holes of Lambda_24 to the 7D singular locus" smuggles in a
projection P: a 7x24 real matrix is **168 continuous parameters** presented as
a parameter reduction. The register retained the idea with a kill condition:
does a Gamma-EQUIVARIANT linear map exist at all? If none does, the anchor is
dead as geometry. If one does, its freedom is measured in DIMENSIONS rather
than assumed to be zero.

THE ANSWER IS EXACT, NOT NUMERICAL
==================================
Gamma = (Z/2)^3 is abelian, so every irreducible real representation is
one-dimensional and there are exactly 8 of them -- the 8 characters. For any
two real representations V, W of an abelian group whose irreducibles are all
real and one-dimensional,

    dim Hom_Gamma(V, W) = sum over characters chi of  m_chi(V) * n_chi(W)

with m, n the multiplicities. No linear algebra is needed and no tolerance
enters: the answer is an integer computed from two multiplicity vectors.

WHAT THE 7 IS, MEASURED
=======================
`joyce_orbifold.coordinate_characters` gives each of the 7 coordinates its
character. Measured: the 7 characters are **distinct**, they are the **7
NON-TRIVIAL** characters of Gamma, and the **trivial character does not
appear**. R^7 is the regular representation minus the trivial summand -- which
is forced, since Gamma acts on the 7 coordinates of T^7 with no fixed
direction.

THE CONSEQUENCE, AND IT COLLAPSES THE WHOLE QUESTION
====================================================
Because n_chi(7) = 1 for every non-trivial chi and 0 for the trivial one,

    dim Hom_Gamma(24, 7) = 24 - m_trivial(24)

**The equivariant space has dimension 24 minus the number of Gamma-INVARIANT
directions in the 24.** So:

  * it is ZERO if and only if Gamma acts TRIVIALLY on the whole 24, which is
    not an embedding at all. The kill condition cannot fire for any genuine
    action.
  * for every FAITHFUL block-sign embedding into E8^3 -- Gamma acting as
    +-1 on each of the three E8 blocks through three independent characters --
    there are no invariant directions, so the dimension is exactly **24**.

Equivariance is therefore a real reduction, 168 -> 24, by a factor of 7. It is
not the reduction to zero the proposal claimed, and 24 continuous parameters is
not a parameter-free anchor. That number is the honest cost of the proposal.

A NUMERICAL COINCIDENCE, FLAGGED BEFORE IT GETS PROMOTED
========================================================
The enumeration reports **168 faithful block-sign embeddings**, and the naive
parameter count is also **168**. These are unrelated. The first is
|GL(3,2)| = 7*6*4 = 168, the number of ordered bases of F_2^3 -- a count of
EMBEDDINGS. The second is 7 * 24, a count of real MATRIX ENTRIES. They are
equal as integers and share no object, in the same way the register's two
twelves do. Writing "the 168 parameters are the 168 embeddings" would be true
arithmetic and false geometry.

THE A4 BAR
==========
    24, 7          DIMENSIONS of real representations
    m_chi, n_chi   MULTIPLICITIES -- counts of irreducible summands
    168, 24        DIMENSIONS of a space of linear maps, i.e. counts of real
                   parameters
    |Gamma| = 8    a GROUP ORDER
    E8^3 blocks    a count of LATTICE SUMMANDS, not of dimensions

No group order is converted into a dimension anywhere, and the 24 of the
answer is a dimension of a map space, NOT the 24 of the lattice rank -- they
coincide numerically here and that coincidence is derived, not assumed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "GROUP_ORDER",
    "LEECH_RANK",
    "E8_BLOCK_RANK",
    "N_E8_BLOCKS",
    "characters",
    "multiplicities_of_the_seven",
    "block_sign_multiplicities",
    "equivariant_dimension",
    "enumerate_block_embeddings",
    "equivariance_report",
]

GROUP_ORDER: int = 8
LEECH_RANK: int = 24
E8_BLOCK_RANK: int = 8
N_E8_BLOCKS: int = 3


#: The character table is built by enumerating subsets of the 7 coordinates and
#: is asked for inside the 512-embedding enumeration; without this cache that
#: enumeration rebuilt it thousands of times.
_CHARACTER_CACHE: Optional[List[Tuple[int, ...]]] = None


def characters() -> List[Tuple[int, ...]]:
    """All 8 characters of Gamma, as value-vectors on the group elements.

    Derived from the live `diagonal_stabiliser` rather than tabulated, so the
    ordering of group elements matches `coordinate_characters` and the two
    multiplicity vectors below are indexed consistently. That consistency is
    load-bearing: pairing multiplicities against a differently-ordered
    character table would give a wrong integer with no symptom.
    """
    global _CHARACTER_CACHE
    if _CHARACTER_CACHE is not None:
        return _CHARACTER_CACHE

    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
    )

    elements = [tuple(e) for e in diagonal_stabiliser()]
    if len(elements) != GROUP_ORDER:
        raise RuntimeError(
            "the diagonal stabiliser has %d elements, not %d; Gamma is not "
            "(Z/2)^3 and this character computation does not apply"
            % (len(elements), GROUP_ORDER)
        )

    # A character of (Z/2)^3 is a choice of sign on each of 3 generators. The
    # elements are sign vectors on 7 coordinates; a character is determined by
    # its values, which we build as products over a subset of coordinates.
    # Every subset of the 7 coordinates gives a character; there are only 8
    # distinct ones, and taking them as a SET recovers the dual group.
    seen = {}
    for size in range(len(elements[0]) + 1):
        for subset in itertools.combinations(range(len(elements[0])), size):
            values = tuple(
                _product(element[i] for i in subset) for element in elements)
            seen.setdefault(values, subset)
        if len(seen) == GROUP_ORDER:
            break
    if len(seen) != GROUP_ORDER:
        raise RuntimeError(
            "found %d distinct characters, expected %d" % (len(seen),
                                                           GROUP_ORDER))
    _CHARACTER_CACHE = sorted(seen)
    return _CHARACTER_CACHE


def _product(values) -> int:
    out = 1
    for v in values:
        out *= v
    return out


def _trivial() -> Tuple[int, ...]:
    return tuple([1] * GROUP_ORDER)


def multiplicities_of_the_seven() -> Dict[Tuple[int, ...], int]:
    """n_chi for the 7 coordinate directions, measured not assumed.

    Returns a multiplicity per character. Measured on the live orbifold: 1 for
    each of the 7 non-trivial characters, 0 for the trivial one.
    """
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        coordinate_characters,
    )

    table = {chi: 0 for chi in characters()}
    for _coord, chi in sorted(coordinate_characters().items()):
        key = tuple(chi)
        if key not in table:
            raise RuntimeError(
                "coordinate character %s is not a character of Gamma as this "
                "module enumerates them; the two orderings have diverged" % (key,)
            )
        table[key] += 1
    return table


def block_sign_multiplicities(block_chars: Sequence[Tuple[int, ...]]
                              ) -> Dict[Tuple[int, ...], int]:
    """m_chi for R^24 when Gamma acts as +-1 on each E8 block.

    `block_chars` gives the character by which Gamma acts on each of the 3
    blocks. Each block contributes its character with multiplicity 8 (the rank
    of E8), because a scalar +-1 acting on a block multiplies every one of its
    8 directions by the same sign.

    A4 bar: the 8 here is the RANK of E8, a count of lattice dimensions; the 3
    is a count of lattice SUMMANDS. Neither is a group order.
    """
    if len(block_chars) != N_E8_BLOCKS:
        raise ValueError("expected %d block characters, got %d"
                         % (N_E8_BLOCKS, len(block_chars)))
    table = {chi: 0 for chi in characters()}
    for chi in block_chars:
        key = tuple(chi)
        if key not in table:
            raise ValueError("%s is not a character of Gamma" % (key,))
        table[key] += E8_BLOCK_RANK
    total = sum(table.values())
    if total != LEECH_RANK:
        raise RuntimeError(
            "the block decomposition accounts for %d dimensions, not %d"
            % (total, LEECH_RANK))
    return table


def equivariant_dimension(m_source: Dict[Tuple[int, ...], int],
                          n_target: Optional[Dict[Tuple[int, ...], int]] = None
                          ) -> int:
    """dim Hom_Gamma(V_source, V_target) = sum_chi m_chi n_chi.

    Exact integer arithmetic. There is no matrix, no rank computation and no
    tolerance, so there is no threshold that could be loosened until the answer
    came out convenient.
    """
    n_target = (n_target if n_target is not None
                else multiplicities_of_the_seven())
    return sum(m_source.get(chi, 0) * n_target.get(chi, 0)
               for chi in characters())


def _is_faithful(block_chars: Sequence[Tuple[int, ...]]) -> bool:
    """Does Gamma act faithfully through these three block characters?

    The action is (g -> (chi1(g), chi2(g), chi3(g))). It is injective exactly
    when no non-identity g has all three characters equal to +1.
    """
    for index in range(GROUP_ORDER):
        if index == _trivial_element_index():
            continue
        if all(chi[index] == 1 for chi in block_chars):
            return False
    return True


#: `diagonal_stabiliser()` recomputes the stabiliser of phi on every call, and
#: the faithfulness test asks for the identity's position once per embedding.
_IDENTITY_INDEX_CACHE: Optional[int] = None


def _trivial_element_index() -> int:
    """Where the identity sits in the element ordering `characters()` uses."""
    global _IDENTITY_INDEX_CACHE
    if _IDENTITY_INDEX_CACHE is not None:
        return _IDENTITY_INDEX_CACHE

    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
    )

    for index, element in enumerate(diagonal_stabiliser()):
        if all(s == 1 for s in element):
            _IDENTITY_INDEX_CACHE = index
            return index
    raise RuntimeError("the diagonal stabiliser contains no identity element")


def enumerate_block_embeddings() -> Dict[str, Any]:
    """Every block-sign action of Gamma on E8^3, with its equivariant dimension.

    All 8^3 = 512 assignments of a character to each of the three blocks are
    enumerated, faithful and not. Reporting the unfaithful ones too is the
    point: they are where a zero could hide, and showing that the ONLY zero
    sits at the trivial action is what settles the kill condition.
    """
    chars = characters()
    n_seven = multiplicities_of_the_seven()
    trivial = _trivial()

    rows: List[Dict[str, Any]] = []
    for block_chars in itertools.product(chars, repeat=N_E8_BLOCKS):
        m = block_sign_multiplicities(block_chars)
        dim = equivariant_dimension(m, n_seven)
        rows.append({
            "block_characters": block_chars,
            "faithful": _is_faithful(block_chars),
            "n_invariant_directions": m[trivial],
            "equivariant_dimension": dim,
        })

    faithful = [r for r in rows if r["faithful"]]
    zeros = [r for r in rows if r["equivariant_dimension"] == 0]

    return {
        "n_embeddings_enumerated": len(rows),
        "n_faithful": len(faithful),
        "faithful_dimensions": sorted({r["equivariant_dimension"]
                                       for r in faithful}),
        "all_dimensions": sorted({r["equivariant_dimension"] for r in rows}),
        "n_with_zero_dimension": len(zeros),
        "zeros_are_all_trivial_actions": all(
            not r["faithful"] and r["n_invariant_directions"] == LEECH_RANK
            for r in zeros),
        "rows": rows,
    }


def equivariance_report() -> Dict[str, Any]:
    """The kill condition, adjudicated, with the honest parameter count."""
    n_seven = multiplicities_of_the_seven()
    trivial = _trivial()
    enumeration = enumerate_block_embeddings()

    seven_is_regular_minus_trivial = (
        n_seven[trivial] == 0
        and all(v == 1 for chi, v in n_seven.items() if chi != trivial))

    faithful_dims = enumeration["faithful_dimensions"]
    killed = bool(faithful_dims) and max(faithful_dims) == 0

    return {
        "claim": ("the deep-hole projection 24 -> 7 is parameter-free; "
                  "equivariance under Gamma constrains it to nothing"),
        "verdict": "KILLED" if killed else "SURVIVES_WITH_A_MEASURED_COST",
        "naive_parameter_count": LEECH_RANK * 7,
        "equivariant_parameter_count": (faithful_dims[0] if len(
            set(faithful_dims)) == 1 else faithful_dims),
        "reduction_factor": (
            (LEECH_RANK * 7) / faithful_dims[0]
            if len(set(faithful_dims)) == 1 and faithful_dims[0] else None),
        "the_seven": {
            "multiplicities": {str(k): v for k, v in sorted(n_seven.items())},
            "is_regular_minus_trivial": seven_is_regular_minus_trivial,
            "trivial_multiplicity": n_seven[trivial],
        },
        "the_formula": (
            "Gamma is abelian with 8 one-dimensional real irreps, so "
            "dim Hom_Gamma(V, W) = sum_chi m_chi(V) n_chi(W). Since the 7 "
            "carries every NON-TRIVIAL character exactly once and the trivial "
            "character not at all, this collapses to "
            "dim Hom_Gamma(24, 7) = 24 - m_trivial(24)."
        ),
        "why_the_kill_cannot_fire": (
            "the dimension vanishes exactly when m_trivial(24) = 24, i.e. when "
            "Gamma acts TRIVIALLY on the whole 24 -- which is not an embedding. "
            "Measured over all %d block-sign actions, the only zeros are "
            "trivial actions (%s), and every FAITHFUL one gives dimension %s."
            % (enumeration["n_embeddings_enumerated"],
               enumeration["zeros_are_all_trivial_actions"],
               faithful_dims)
        ),
        "the_honest_cost": (
            "equivariance reduces the projection from %d real parameters to "
            "%s. That is a genuine reduction by a factor of %s, and it is not "
            "zero. A 24-parameter map is not a parameter-free anchor, and the "
            "proposal's claim that equivariance leaves nothing free is false."
            % (LEECH_RANK * 7, faithful_dims,
               [(LEECH_RANK * 7) // d for d in faithful_dims if d])
        ),
        "scope": (
            "this settles the block-sign embeddings into E8^3, which is the "
            "Niemeier structure the proposal named. It does NOT enumerate every "
            "embedding of (Z/2)^3 into Aut(E8^3) -- one that also permutes the "
            "three blocks would need its own computation, and would still be "
            "bounded below by the same formula."
        ),
        "enumeration": {k: v for k, v in enumeration.items() if k != "rows"},
        "a4_bar": (
            "24 and 7 are DIMENSIONS of representations; m and n are "
            "MULTIPLICITIES; 168 and the answer are DIMENSIONS of a space of "
            "linear maps; |Gamma| = 8 is a GROUP ORDER; the 3 E8 blocks are "
            "LATTICE SUMMANDS. The 24 of the answer is a map-space dimension "
            "and NOT the lattice rank -- they coincide numerically, and that "
            "coincidence is derived here rather than assumed."
        ),
    }
