"""Nothing physical is left undetermined in the bridge-to-channel map.

WHERE THIS SITS
---------------
The narrowing ran C(21,12) = 293930 -> 35 -> 7 arcs, each admitting 18
line-to-block labellings, and stopped there. 7 x 18 = 126 possibilities were
recorded as "still underdetermined", which is the right thing to say about a
combinatorial count and the wrong thing to say about the physics. Every one
of the three remaining freedoms is a relabelling.

  1. THE BLOCK PARTITION IS CANONICAL, GIVEN THE ARC. Each K4 edge {p, q}
     spans a Fano line, and that line meets the arc's complement line in
     exactly one point. Grouping the six edges by which complement point
     they hit gives fibres that are precisely the three perfect matchings of
     K4. So the arc fixes the partition of bridges into E8 blocks; the 3!
     counted earlier is only which complement point gets called block 0, and
     a block's name is not an observable.

  2. THE SPARE FACTOR OF 3 TOUCHES NOTHING. The other factor in 18 = 3! x 3
     is the colour of the complement line, which lies on no face, is
     incident to no bridge, and enters no coupling.

  3. THE SEVEN ARCS ARE ONE ORBIT. Aut(Fano) = PSL(3,2) has order 168, is
     transitive on the 7 lines and hence on the 7 arcs, and the arc
     stabiliser of order 168/7 = 24 acts as the full symmetric group on that
     arc's four faces. No arc is singled out by the incidence geometry, and
     the face labels are free as well.

So the assignment is unique up to the symmetry group of the structure, which
is the ordinary sense in which a geometric object is determined.

CONDITIONAL, AND THE TESTS SAY SO
The uniqueness rests on nothing else in the framework distinguishing a Fano
direction. A preferred imaginary octonion, or a shadow asymmetry singling
out one coordinate, would break PSL(3,2) and make the choice of arc physical
again. Nothing currently does this. The claim is conditional and the report
must keep saying it is.
"""
from __future__ import annotations

import itertools

import pytest

from metaphysica.simulations.PM.gauge.topological_terms import (
    assignment_uniqueness_report,
    associative_triples,
)


def _lines():
    return {frozenset(t) for t in associative_triples()}


def _arcs(lines):
    return [frozenset(q) for q in itertools.combinations(range(7), 4)
            if not any(set(L) <= set(q) for L in lines)]


# -- the symmetry group ------------------------------------------------------


def test_the_automorphism_group_is_psl_3_2():
    report = assignment_uniqueness_report()
    assert report["automorphism_group_order"] == 168


def test_the_group_is_computed_not_asserted():
    """Recount the automorphisms directly from the line set."""
    lines = _lines()
    autos = [p for p in itertools.permutations(range(7))
             if {frozenset(p[i] for i in L) for L in lines} == lines]
    assert len(autos) == 168


def test_the_seven_arcs_form_a_single_orbit():
    report = assignment_uniqueness_report()
    assert report["n_arcs"] == 7
    assert report["arc_orbit_size"] == 7
    assert report["arcs_form_one_orbit"] is True


def test_orbit_stabiliser_balances():
    """168 = 7 x 24. If this fails the group action has been miscounted."""
    report = assignment_uniqueness_report()
    assert report["arc_stabiliser_order"] == 24
    assert report["orbit_stabiliser_checks"] is True
    assert (report["arc_orbit_size"] * report["arc_stabiliser_order"]
            == report["automorphism_group_order"])


def test_the_stabiliser_permutes_the_faces_freely():
    """Order 24 acting on 4 faces must be the full S4, not a subgroup of it."""
    report = assignment_uniqueness_report()
    assert report["stabiliser_is_full_symmetric_on_faces"] is True


# -- the canonical partition -------------------------------------------------


def test_the_block_partition_is_canonical_given_the_arc():
    assert assignment_uniqueness_report()[
        "block_partition_is_canonical_given_the_arc"] is True


def test_the_matchings_are_the_complement_point_fibres():
    """Checked against the geometry rather than the report's own summary.

    This is the step that turns 3! from a physical freedom into a naming
    freedom, so it is verified independently.
    """
    lines = _lines()
    for arc in _arcs(lines):
        complement = frozenset(set(range(7)) - set(arc))
        fibres = {}
        for p, q in itertools.combinations(sorted(arc), 2):
            line = next(L for L in lines if p in L and q in L)
            hit = line & complement
            assert len(hit) == 1
            fibres.setdefault(next(iter(hit)), []).append(frozenset((p, q)))
        assert len(fibres) == 3, "three complement points, three fibres"
        for point, edges in fibres.items():
            assert len(edges) == 2, f"fibre over {point} is not a pair"
            assert not (edges[0] & edges[1]), "fibre edges must be disjoint"
            assert edges[0] | edges[1] == set(arc), "must cover all four faces"


# -- what is claimed, and what is not ---------------------------------------


def test_no_physical_freedom_is_claimed_to_remain():
    report = assignment_uniqueness_report()
    assert report["physical_freedom_remaining"] == 0
    assert len(report["residual_freedoms"]) == 3
    assert "unique up to the symmetry group" in report["conclusion"]


def test_the_claim_is_conditional_and_says_so():
    """Uniqueness holds only while nothing distinguishes a Fano direction."""
    kill = assignment_uniqueness_report()["kill_condition"]
    assert "distinguishes a Fano direction" in kill
    assert "conditional" in kill
    assert "168" in kill


def test_uniqueness_would_fail_if_the_group_were_intransitive():
    """Mutation in spirit: the result depends on transitivity, not on 168.

    A group of the right order that failed to be transitive on arcs would
    leave the choice physical, so the report must not conclude from the
    order alone.
    """
    report = assignment_uniqueness_report()
    assert report["arcs_form_one_orbit"] is True
    assert report["arc_orbit_size"] == report["n_arcs"], (
        "the conclusion rests on transitivity; if the orbit ever splits, "
        "physical_freedom_remaining must stop being 0"
    )
