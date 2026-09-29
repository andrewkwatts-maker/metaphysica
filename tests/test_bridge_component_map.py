"""The bulk's 12 bridges and the resolved manifold's 12 A1 components are one
3 x 4 structure, and it exists exactly on the all-plain members (D-008).

Pre-registered 2026-09-30 in the site repo's docs/DECISION_LOG.md before the
computation. MEASURED the same day: at the canonical point the singular lines
(0,1,2), (0,3,4), (1,3,5) fix the arc {0,1,3,6} with complement (2,4,5); each
of K4's three perfect matchings holds exactly one singular side; 4 bridges per
block against 4 components per involution. Over the 364 n = 3 classes of the
first generating triple: 280 all-plain classes admit the bijection, the 84
Example-4 classes admit none -- zero exceptions.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.bridge_component_map import (
    canonical_arc,
    correspondence,
    k4_blocks,
    n3_family_selection,
)


def test_the_canonical_point_fixes_its_arc():
    c = correspondence()
    geo = c["canonical_arc"]
    assert geo["arc"] == (0, 1, 3, 6)
    assert geo["complement"] == (2, 4, 5)
    assert geo["missed_point"] == 6


def test_each_block_holds_exactly_one_singular_side():
    c = correspondence()
    assert c["one_singular_side_per_block"]
    involutions = list(c["block_involution"].values())
    assert len(set(map(tuple, involutions))) == 3


def test_bridges_and_components_match_three_by_four():
    c = correspondence()
    assert set(c["bridges_per_block"].values()) == {4}
    assert set(c["components_per_involution"].values()) == {4}
    assert c["n_bridges"] == c["n_components"] == 12
    assert c["bijection"]


def test_concurrent_lines_fix_no_arc():
    """The check can fail: three lines through one point form no triangle."""
    assert canonical_arc([(0, 1, 2), (0, 3, 4), (0, 5, 6)]) is None


def test_every_arc_has_three_blocks_of_two_edges():
    blocks = k4_blocks((0, 1, 3, 6), (2, 4, 5))
    assert sorted(blocks) == [2, 4, 5]
    assert all(len(edges) == 2 for edges in blocks.values())


@pytest.fixture(scope="module")
def selection():
    return n3_family_selection()


def test_the_correspondence_holds_exactly_on_the_all_plain_members(selection):
    assert selection["holds"], selection["violations"]
    assert selection["tally"] == {"all_plain/bijection": 280,
                                  "not_all_plain/none": 84}
    assert selection["selects"] == (12, 43)
