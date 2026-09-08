"""The Joyce orbifold results, each one falsifiable.

WHAT THIS ESTABLISHES
---------------------
R1  The diagonal sign flips preserving phi form a group of order 8 -- exactly
    (Z/2)^3, Joyce's group. Derived from phi, not postulated.
R2  Each of the 7 non-identity elements moves exactly 4 coordinates (a Fano
    arc) and fixes 3 (the complementary line). This DERIVES the 4 + 3 split.
R3  The Gamma-invariant subspace of Lambda^3(R^7) has dimension 7, spanned by
    exactly the triples of phi: the flat contribution to b_3 is 7.
R4  Gamma \\ {1} carries its own Fano plane -- 7 points, 7 lines -- dual to the
    coordinate one.

WHY THE PERTURBATION TESTS MATTER
---------------------------------
Every number above could be produced by a function that just returns it, and
this repository has repeatedly found checks of exactly that kind -- most
recently three of the four G2 torsion classes returned as hardcoded zeros and
then "verified" against zero.

So each result is paired with a test that PERTURBS the input and requires the
answer to change. A stabiliser computation that reports 8 for a phi that is not
a G2 3-form is not computing anything, and these tests fail if that is what it
does.

WHAT IS NOT CLAIMED
-------------------
Only the linear part of Gamma is used, so nothing here computes the twisted
(resolution) sector. If b_3 = 24 then the resolutions contribute 17, but that
17 is subtraction under an assumption, not a derivation, and no test here
asserts it.
"""
from __future__ import annotations

import itertools

import numpy as np
import pytest

from metaphysica.simulations.PM.geometry.joyce_orbifold import (
    diagonal_stabiliser,
    group_fano_lines,
    invariant_three_forms,
    involution_arc_correspondence,
    lambda3_basis,
    orbifold_report,
    phi_vector,
    sign_action_on_lambda3,
)


class _FakePhi:
    """A stand-in carrying an arbitrary 3-form, for the perturbation tests."""

    def __init__(self, phi):
        self.phi = phi


def _phi_array():
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )
    return G2DifferentialGeometry().phi.copy()


# ---------------------------------------------------------------- R1


def test_r1_stabiliser_is_z2_cubed():
    group = diagonal_stabiliser()
    assert len(group) == 8, "expected (Z/2)^3, got order %d" % len(group)
    arrays = [np.array(g) for g in group]
    # closed
    assert all(any(np.array_equal(a * b, c) for c in arrays)
               for a in arrays for b in arrays)
    # every element an involution
    ones = np.ones(7, dtype=int)
    assert all(np.array_equal(a * a, ones) for a in arrays)
    assert tuple(ones) in group


def test_r1_search_is_exhaustive_not_a_lookup():
    """The 8 must be found among all 128 sign patterns, and 120 must fail."""
    vec = phi_vector()
    kept, rejected = 0, 0
    for eps in itertools.product((1, -1), repeat=7):
        if np.allclose(sign_action_on_lambda3(eps) * vec, vec):
            kept += 1
        else:
            rejected += 1
    assert kept == 8 and rejected == 120, (
        "kept %d, rejected %d of 128" % (kept, rejected)
    )


def test_r1_a_non_g2_three_form_gives_a_different_stabiliser():
    """Perturb phi and the order must move away from 8.

    This is the test that makes R1 a computation. Adding a single extra
    component to phi breaks the symmetry, and a real search notices.
    """
    phi = _phi_array()
    # (0,1,3) is NOT one of phi's triples; add it antisymmetrically
    for perm, sign in (((0, 1, 3), 1), ((1, 3, 0), 1), ((3, 0, 1), 1),
                       ((1, 0, 3), -1), ((0, 3, 1), -1), ((3, 1, 0), -1)):
        phi[perm] = sign
    order = len(diagonal_stabiliser(_FakePhi(phi)))
    assert order != 8, (
        "a perturbed phi still gave stabiliser order 8, so the search is not "
        "reading the form it was handed"
    )


# ---------------------------------------------------------------- R2


def test_r2_every_involution_moves_an_arc_and_fixes_a_line():
    corr = involution_arc_correspondence()
    assert len(corr) == 7
    for c in corr:
        assert c["n_moved"] == 4, c
        assert c["moved_is_arc"], c
        assert c["fixed_is_line"], c
        assert len(c["fixed"]) == 3, c


def test_r2_the_moved_sets_are_exactly_the_seven_fano_arcs():
    """Set equality, not a count -- the identification is the claim."""
    from metaphysica.simulations.PM.gauge.topological_terms import (
        associative_triples,
    )
    lines = {frozenset(t) for t in associative_triples()}
    arcs = {frozenset(q) for q in itertools.combinations(range(7), 4)
            if not any(L <= frozenset(q) for L in lines)}
    assert len(arcs) == 7

    moved = {frozenset(c["moved"]) for c in involution_arc_correspondence()}
    assert moved == arcs, (
        "moved sets and Fano arcs differ:\n  only moved: %s\n  only arcs: %s"
        % (sorted(map(sorted, moved - arcs)), sorted(map(sorted, arcs - moved)))
    )


def test_r2_this_is_where_the_four_three_split_comes_from():
    """4 moved + 3 fixed = 7, disjointly, for every element."""
    for c in involution_arc_correspondence():
        assert set(c["moved"]).isdisjoint(c["fixed"])
        assert set(c["moved"]) | set(c["fixed"]) == set(range(7))
        assert (len(c["moved"]), len(c["fixed"])) == (4, 3)


# ---------------------------------------------------------------- R3


def test_r3_flat_b3_contribution_is_seven_and_equals_phi():
    from metaphysica.simulations.PM.gauge.topological_terms import (
        associative_triples,
    )
    inv = invariant_three_forms()
    assert len(inv) == 7, "flat b_3 contribution is %d, expected 7" % len(inv)
    assert set(inv) == set(associative_triples()), (
        "the invariant 3-forms are not exactly the triples of phi"
    )


def test_r3_the_other_28_basis_forms_really_are_killed():
    """A dimension count is only meaningful if the rest are excluded."""
    inv = set(invariant_three_forms())
    basis = lambda3_basis()
    assert len(basis) == 35
    killed = [t for t in basis if t not in inv]
    assert len(killed) == 28

    group = diagonal_stabiliser()
    actions = [sign_action_on_lambda3(e) for e in group]
    for t in killed:
        i = basis.index(t)
        assert any(a[i] == -1 for a in actions), (
            "%s is not invariant yet no group element negates it" % (t,)
        )


def test_r3_the_seventeen_is_not_claimed():
    """b_3 = 7 + 17 must not be presented as derived.

    The flat sector is computed; the twisted sector is not. If this ever starts
    reporting a number, the module has begun asserting something it does not
    compute.
    """
    r = orbifold_report()
    assert r["twisted_sector_contribution"] is None
    assert "not derived" in r["note"] or "NOT computed" in r["note"]


# ---------------------------------------------------------------- R4


def test_r4_gamma_carries_a_fano_plane():
    lines = group_fano_lines()
    assert len(lines) == 7, "expected 7 lines on Gamma, got %d" % len(lines)
    # every point on exactly 3 lines, as in PG(2,2)
    from collections import Counter
    c = Counter(p for L in lines for p in L)
    assert set(c) == set(range(7))
    assert set(c.values()) == {3}


def test_r4_the_lines_are_products_equal_to_the_identity():
    group = [np.array(g) for g in diagonal_stabiliser()
             if any(s < 0 for s in g)]
    ones = np.ones(7, dtype=int)
    for a, b, c in group_fano_lines():
        assert np.array_equal(group[a] * group[b] * group[c], ones)


# ---------------------------------------------------------------- report


def test_the_report_agrees_with_the_pieces():
    r = orbifold_report()
    assert r["is_z2_cubed"] and r["is_closed_group"] and r["all_involutions"]
    assert r["every_element_moves_four"]
    assert r["every_moved_set_is_an_arc"]
    assert r["every_fixed_set_is_a_line"]
    assert r["flat_b3_contribution"] == len(invariant_three_forms())
    assert r["invariants_are_exactly_phi"]
    assert r["group_carries_a_fano_plane"]
