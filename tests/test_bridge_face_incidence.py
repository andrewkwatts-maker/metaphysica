"""A bridge is a directed edge of K4 on the four faces.

WHAT THIS CLOSES
----------------
``block_labelling_analysis`` narrows the face labels to the 7 arcs and finds
18 admissible line-to-block labellings per arc. Both 7 and 18 were outputs
of an enumeration with no structural reading, and the bridge index itself
was still just an integer running to twelve.

Unpacking an arc supplies all three. An arc is the complement of a Fano
line, so it is disjoint from that line. Any line through an arc point has
three points, meets the complement line once, and therefore holds exactly
one further arc point. Every line meeting the arc is thus spanned by a PAIR
of arc points; the six pairs give six distinct lines; the seventh is the
complement, on no face at all.

    4 faces          <-> vertices of K4
    6 channel-lines  <-> edges of K4
    12 bridges       <-> DIRECTED edges of K4 (ordered pairs of faces)
    3 E8 blocks      <-> perfect matchings of K4

A bridge is a flag (face, line through it), and since the line is spanned by
that face and one other, a flag is an ordered pair of distinct faces. Twelve
of them. The bridge count is K4's directed edge count rather than a separate
input, and "bridge" turns out to be literal: a connection between two faces.

The 18 follows as well. One bridge per block at each face means the three
edges at each K4 vertex carry three distinct colours -- a proper
3-edge-colouring. K4's edges split into exactly three perfect matchings and
a proper colouring is a bijection colours -> matchings, giving 3! = 6; the
complement line is unconstrained, giving 3. 6 x 3 = 18.

Nothing is assumed beyond the global-labelling premise already stated in
block_labelling_analysis. These tests check the identification against the
Fano geometry directly rather than against the report's own summary, so the
agreement with 18 is a prediction meeting an independent count.
"""
from __future__ import annotations

import itertools
import math

import pytest

from metaphysica.simulations.PM.gauge.topological_terms import (
    associative_triples,
    block_labelling_analysis,
    bridge_face_incidence,
)


def _lines():
    return [frozenset(t) for t in associative_triples()]


def test_the_identification_holds_for_every_arc():
    result = bridge_face_incidence()
    assert result.get("error") is None
    assert result["n_arcs"] == 7
    assert result["holds_for_every_arc"] is True


def test_each_arc_is_the_complement_of_a_line():
    """This is what makes every arc-meeting line a pair-line."""
    lines = _lines()
    for arc in bridge_face_incidence()["per_arc"]:
        complement = frozenset(arc["complement"])
        assert complement in lines
        assert not (set(arc["arc"]) & complement)


def test_every_line_meeting_an_arc_is_spanned_by_two_arc_points():
    """Checked against the geometry, not against the report."""
    lines = _lines()
    for arc in bridge_face_incidence()["per_arc"]:
        points = set(arc["arc"])
        for line in lines:
            hit = line & points
            assert len(hit) in (0, 2), (
                f"line {sorted(line)} meets arc {sorted(points)} in "
                f"{len(hit)} points; the K4 reading needs 0 or 2"
            )


def test_twelve_bridges_are_the_directed_edges():
    for arc in bridge_face_incidence()["per_arc"]:
        assert arc["n_flags"] == 12
        assert arc["flags_are_directed_edges"] is True
        assert arc["n_k4_edges"] == 6


def test_three_blocks_are_the_perfect_matchings():
    for arc in bridge_face_incidence()["per_arc"]:
        assert arc["n_perfect_matchings"] == 3


def test_k4_really_has_three_perfect_matchings():
    """Independent of the module, so the claim is not self-referential."""
    edges = [frozenset(e) for e in itertools.combinations(range(4), 2)]
    matchings = [m for m in itertools.combinations(edges, 2)
                 if not (m[0] & m[1])]
    assert len(matchings) == 3
    assert len(edges) == 6
    covered = {e for m in matchings for e in m}
    assert covered == set(edges), "the matchings must partition the edges"


# -- the prediction meets the independent count -----------------------------


def test_the_predicted_eighteen_matches_the_enumeration():
    """3! colourings x 3 free choices, against a 3^7 brute-force count."""
    incidence = bridge_face_incidence()
    assert incidence["predicted_labellings_per_arc"] == [18]
    assert incidence["matches_enumeration"] is True

    enumerated = block_labelling_analysis()["labellings_per_qualifying_set"]
    assert set(enumerated.values()) == {18}, (
        "the enumeration no longer gives 18 per arc; the K4 derivation and "
        "the brute-force count have parted company"
    )


def test_the_factorisation_is_the_stated_one():
    """Guards against 18 arising for some other reason."""
    for arc in bridge_face_incidence()["per_arc"]:
        assert arc["proper_edge_colourings"] == math.factorial(3) == 6
        assert arc["free_colours_for_leftover"] == 3
        assert arc["predicted_labellings"] == 6 * 3


def test_the_kill_condition_names_what_would_break_it():
    kill = bridge_face_incidence()["kill_condition"]
    assert "more than one line" in kill
    assert "12 distinct" in kill
