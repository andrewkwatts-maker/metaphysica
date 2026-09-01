"""Is the face grouping arbitrary among alternatives, or among relabellings?

WHY THIS MATTERS
----------------
``four_face_structure`` classifies its construction FITTED, and one leg of
that argument is that stride-4 {i, i+4, i+8} is "one of 576 cross-E8-valid
options (not unique)" and "a labeling choice, not a mathematical necessity".
Both statements are true. The question they leave open is whether the 576
are physically distinct alternatives -- in which case picking one is a
fitted choice -- or relabellings of a single object, in which case picking
one is a coordinate convention and nothing observable depends on it.

They are the second. Renaming the four bridges inside E8 block 1 and inside
block 2 is an action of S4 x S4 of order 4! * 4! = 576, and it carries
stride-4 onto every cross-E8-valid grouping and onto nothing else, with
trivial stabiliser. The set is a torsor: 576 group elements, 576 groupings,
a regular action.

This answers only that leg. h^{1,1} = 4 still comes from having selected
TCS #187, and the cross-E8 property is still imposed rather than derived,
so the classification does not simply become DERIVED. These tests pin the
orbit result and pin the fact that the rest is still outstanding, so a
future reader cannot quietly promote the whole classification on the
strength of this one piece.
"""
from __future__ import annotations

import itertools
import math

import pytest

from metaphysica.simulations.PM.geometry.four_face_structure import (
    canonical_grouping,
    cross_e8_valid_groupings,
    e8_block_of,
    generation_count_report,
    grouping_orbit_report,
    relabel_within_blocks,
    stride4_grouping,
)


def test_the_action_is_regular_on_the_valid_groupings():
    report = grouping_orbit_report()
    assert report["orbit_size"] == 576
    assert report["n_cross_e8_valid"] == 576
    assert report["orbit_is_everything"] is True
    assert report["stabiliser_order"] == 1
    assert report["action_is_regular"] is True
    assert report["group_order"] == math.factorial(4) ** 2


def test_every_valid_grouping_is_stride4_after_renaming():
    """Computed independently of the report, so the claim is not circular."""
    valid = set(cross_e8_valid_groupings())
    base = stride4_grouping()
    reachable = {
        relabel_within_blocks(base, p1, p2)
        for p1 in itertools.permutations(range(4))
        for p2 in itertools.permutations(range(4))
    }
    assert reachable == valid


def test_relabelling_preserves_cross_e8_validity():
    """A relabelling that left the valid set would not be a symmetry of it."""
    from metaphysica.simulations.PM.geometry.four_face_structure import (
        is_cross_e8_valid,
    )

    base = stride4_grouping()
    for p1 in itertools.permutations(range(4)):
        moved = relabel_within_blocks(base, p1, tuple(range(4)))
        assert is_cross_e8_valid(moved)


def test_relabelling_stays_inside_its_own_block():
    """The action must not move a bridge between E8 blocks.

    If it did, the orbit result would be about a different group and would
    say nothing about coordinate freedom within the block structure.
    """
    base = stride4_grouping()
    for p1 in itertools.permutations(range(4)):
        for p2 in itertools.permutations(range(4)):
            moved = relabel_within_blocks(base, p1, p2)
            blocks_before = sorted(e8_block_of(b) for f in base for b in f)
            blocks_after = sorted(e8_block_of(b) for f in moved for b in f)
            assert blocks_before == blocks_after


def test_block_zero_is_held_fixed():
    """Permuting block 0 too would only compose with relabelling the faces."""
    base = stride4_grouping()
    moved = relabel_within_blocks(base, (1, 0, 2, 3), (0, 1, 2, 3))
    block0_before = {b for f in base for b in f if e8_block_of(b) == 0}
    block0_after = {b for f in moved for b in f if e8_block_of(b) == 0}
    assert block0_before == block0_after


def test_the_report_does_not_overclaim():
    """The other legs of FITTED must stay named as outstanding."""
    report = grouping_orbit_report()
    unaffected = report["does_not_affect"]
    assert "TCS #187" in unaffected
    assert "imposed rather than derived" in unaffected


# -- the generation count ---------------------------------------------------


def test_three_is_reached_by_two_independent_routes():
    report = generation_count_report()
    assert report["n_e8_blocks"] == 3, "Leech 24 = 8 + 8 + 8"
    assert report["lines_through_each_fano_point"] == 3, "order-2 plane, q+1"
    assert report["fano_is_uniform"] is True
    assert report["routes_agree"] is True
    assert report["n_generations"] == 3


def test_the_generation_report_does_not_claim_to_explain_three():
    """It fixes n_gen relative to b3 and G2; it does not derive 3 itself."""
    note = generation_count_report()["note"]
    assert "does not explain why 3" in note
