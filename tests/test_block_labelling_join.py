"""The R^24 bridge structure and the R^7 coupling structure, joined.

WHAT THIS IS
------------
Two combinatorial structures sat in the codebase with nothing connecting
them. ``leech_lattice`` maps bridge b to the Leech coordinate pair
(2b, 2b+1) and groups the 12 bridges into 4 faces of 3. ``topological_terms``
resolves the allowed channels into 7 disjoint triangles and finds maximal
coupling on exactly 35 = C(7,4) of the C(21,12) = 293930 placements. Nothing
mapped a bridge index to a G2 coordinate pair, and the register listed that
as the load-bearing gap.

The shapes already match. Each triangle is indexed by an omitted Fano point
and its three vertices are the three lines through that point, so a maximal
placement is 4 points x 3 lines = 12 slots against 4 faces x 3 bridges = 12.
A face corresponds to a chosen point, its bridges to the lines through it.

ONE ASSUMPTION IS ADDED, AND IT IS STATED
-----------------------------------------
That the E8 block a bridge carries is a property of the CHANNEL rather than
of the face observing it: one global labelling of the 7 lines by 3 blocks,
shared by every face. Since a face holds one bridge per block, the 3 lines
through each chosen point must get 3 distinct blocks.

WHAT COMES OUT
--------------
Enumerating all 3^7 = 2187 labellings yields two things that were previously
put in by hand:

  n_faces = 4    Four is the MAXIMUM number of simultaneously rainbow
                 points; five, six and seven are impossible. The framework
                 previously read n_faces off h^{1,1} = 4 of the TCS #187
                 building block, which four_face_structure itself classifies
                 FITTED and dependent on having selected that manifold.

  genericity     The 28 line-containing 4-point sets admit ZERO labellings;
                 each of the 7 arcs admits 18. The face_genericity fork
                 narrowed 35 -> 7 by requiring no three labels collinear and
                 carried the note that this was "a stated criterion, not a
                 derivation". It is now a consequence.

WHAT IS NOT CLAIMED HERE
------------------------
This enumeration narrows 293930 -> 35 -> 7 and stops. It does not reach a
single combinatorial answer, and these tests assert that the count keeps
saying so rather than presenting 7 as a unique result.

That the 7 are PHYSICALLY equivalent is a separate result, proved in
assignment_uniqueness_report and tested in test_assignment_uniqueness: the
block partition is canonical given the arc, the spare colour is incident to
no bridge, and the arcs form one orbit under PSL(3,2). The distinction is
worth keeping sharp -- this module counts combinatorial options, that one
decides which of them are observable.
"""
from __future__ import annotations

import itertools

import pytest

from metaphysica.simulations.PM.gauge.topological_terms import (
    associative_triples,
    block_labelling_analysis,
)


def _lines():
    return [frozenset(t) for t in associative_triples()]


def _is_arc(points, lines):
    return not any(set(line) <= set(points) for line in lines)


# -- the Fano input is what we think it is ----------------------------------


def test_the_seven_triples_form_a_fano_plane():
    """Everything below rests on this, so it is checked rather than assumed."""
    lines = _lines()
    assert len(lines) == 7
    points = {p for line in lines for p in line}
    assert points == set(range(7))
    for p in points:
        through = [line for line in lines if p in line]
        assert len(through) == 3, f"point {p} lies on {len(through)} lines"
    for a, b in itertools.combinations(lines, 2):
        assert len(a & b) == 1, "two lines must meet in exactly one point"


# -- the derived results -----------------------------------------------------


def test_four_faces_is_the_maximum_not_an_input():
    """Five or more simultaneously rainbow points would break this."""
    result = block_labelling_analysis()
    assert result["max_rainbow_points"] == 4
    assert result["n_faces_is_forced"] is True


def test_no_five_point_set_admits_a_global_labelling():
    """The kill condition, computed directly rather than read from the report."""
    lines = _lines()
    lines_through = {p: [i for i, line in enumerate(lines) if p in line]
                     for p in range(7)}
    for colouring in itertools.product(range(3), repeat=7):
        rainbow = {p for p in range(7)
                   if len({colouring[i] for i in lines_through[p]}) == 3}
        assert len(rainbow) <= 4, (
            f"labelling {colouring} makes {sorted(rainbow)} rainbow -- 4 is "
            f"no longer the maximum and n_faces = 4 loses this support"
        )


def test_genericity_is_derived_not_stated():
    """The 28 line-containing 4-sets must admit nothing."""
    result = block_labelling_analysis()
    assert result["qualifying_sets_are_exactly_the_arcs"] is True
    assert result["genericity_is_derived"] is True
    assert result["n_qualifying"] == 7
    assert result["n_point_sets_of_that_size"] == 35


def test_every_qualifying_set_is_an_arc_and_every_arc_qualifies():
    """Checked against the geometry, not against the report's own claim."""
    lines = _lines()
    result = block_labelling_analysis()
    qualifying = {tuple(q) for q in result["qualifying_point_sets"]}
    arcs = {q for q in itertools.combinations(range(7), 4) if _is_arc(q, lines)}
    assert qualifying == arcs


def test_a_line_containing_quadruple_admits_no_labelling():
    """Direct check on a specific bad set, so the result is not circular."""
    lines = _lines()
    line = sorted(lines[0])
    quad = tuple(sorted(line + [p for p in range(7) if p not in line][:1]))
    assert not _is_arc(quad, lines), "fixture is not line-containing"
    lines_through = {p: [i for i, ln in enumerate(lines) if p in ln]
                     for p in range(7)}
    for colouring in itertools.product(range(3), repeat=7):
        assert not all(
            len({colouring[i] for i in lines_through[p]}) == 3 for p in quad
        ), f"{quad} contains a Fano line yet admits labelling {colouring}"


# -- the honesty of what remains --------------------------------------------


def test_the_join_reports_combinatorial_options_not_physical_ones():
    """It narrows 293930 -> 35 -> 7 and must not present 7 as a unique answer.

    The 7 are combinatorially distinct and this count must keep saying so.
    That they are PHYSICALLY equivalent is a separate result proved in
    assignment_uniqueness_report, and the wording here has to point at it
    rather than either overclaiming uniqueness or leaving the reader with
    "underdetermined" when the freedom is entirely gauge.
    """
    result = block_labelling_analysis()
    assert result["n_qualifying"] > 1
    assert set(result["labellings_per_qualifying_set"].values()) == {18}
    freedom = result["residual_freedom"]
    assert "COMBINATORIALLY" in freedom and "PHYSICALLY" in freedom
    assert "assignment_uniqueness_report" in freedom


def test_the_assumption_is_stated():
    """The global-labelling premise is an input and must be visible."""
    result = block_labelling_analysis()
    assumption = result["assumption"]
    assert "Stated, not derived" in assumption
    assert "channel" in assumption


def test_the_kill_condition_names_both_ways_it_can_fail():
    result = block_labelling_analysis()
    kill = result["kill_condition"]
    assert "5 or more" in kill
    assert "28 line-containing" in kill
