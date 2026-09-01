"""The 576-of-15400 claim, computed instead of asserted.

WHY THIS EXISTS
---------------
``four_face_structure``'s module header stated "15400 total 4x3 groupings of
12 bridges; 576 satisfy the cross-E8 property (each face spans all 3 E8
blocks)" and drew a conclusion from it -- that the standard grouping is "one
of 576, NOT unique". No code computed either number. The claim, and the
honest classification of the face grouping as FITTED that rested on it,
existed only in prose.

Both numbers now come out of an enumeration that agrees with a closed form:

    total    = 12! / ((3!)^4 * 4!) = 15400
    cross-E8 = (4!)^2              = 576

The closed form for 576 also explains it. Bridge b occupies Leech
coordinates (2b, 2b+1), so the 24 coordinates' three E8 blocks give three
blocks of four bridges. A grouping is cross-E8-valid exactly when each face
takes one bridge per block. Fixing block 0's four bridges as the face labels,
block 1 can be matched in 4! ways and block 2 independently in 4!.

THE OTHER THING THIS SETTLES
----------------------------
Two face conventions coexisted with nothing reconciling them: stride-4
{i, i+4, i+8} in ``leech_lattice`` and this module, contiguous {0,1,2},
{3,4,5}, ... in ``consciousness/four_dice_sampling``. They are not two
labellings of one object. Stride-4 spans all three blocks in every face;
the contiguous grouping's first face lies entirely inside block 0.
"""
from __future__ import annotations

import math

import pytest

from metaphysica.simulations.PM.geometry.four_face_structure import (
    canonical_grouping,
    contiguous_grouping,
    cross_e8_valid_groupings,
    e8_block_of,
    enumerate_face_groupings,
    face_grouping_report,
    is_cross_e8_valid,
    stride4_grouping,
)


def test_enumeration_matches_the_closed_form():
    report = face_grouping_report()
    assert report["n_groupings"] == 15400
    assert report["n_groupings_closed_form"] == 15400
    assert report["n_cross_e8_valid"] == 576
    assert report["n_cross_e8_valid_closed_form"] == 576
    assert report["closed_forms_agree"] is True


def test_the_closed_forms_are_the_stated_expressions():
    """Guards against a coincidence: check the formulas, not just the values."""
    assert math.factorial(12) // (math.factorial(3) ** 4 * math.factorial(4)) == 15400
    assert math.factorial(4) ** 2 == 576


def test_every_grouping_is_a_genuine_partition():
    groupings = enumerate_face_groupings()
    assert len(groupings) == 15400
    for grouping in groupings:
        bridges = [b for face in grouping for b in face]
        assert sorted(bridges) == list(range(12)), "not a partition of 12"
        assert all(len(face) == 3 for face in grouping)


def test_enumeration_has_no_duplicates():
    """Canonical form must be canonical, or the count is inflated."""
    groupings = enumerate_face_groupings()
    assert len(set(groupings)) == len(groupings)


def test_cross_e8_valid_is_a_strict_subset():
    valid = cross_e8_valid_groupings()
    assert 0 < len(valid) < 15400
    for grouping in valid:
        for face in grouping:
            assert len({e8_block_of(b) for b in face}) == 3


# -- the two rival conventions ----------------------------------------------


def test_stride4_spans_the_blocks_and_contiguous_does_not():
    assert is_cross_e8_valid(stride4_grouping()) is True
    assert is_cross_e8_valid(contiguous_grouping()) is False


def test_the_contiguous_first_face_sits_inside_one_block():
    """The specific reason they are different objects."""
    report = face_grouping_report()
    assert report["contiguous_first_face_blocks"] == [0]
    assert report["stride4_is_cross_e8_valid"] is True
    assert report["contiguous_is_cross_e8_valid"] is False


def test_the_two_conventions_are_not_the_same_grouping():
    assert canonical_grouping(stride4_grouping()) != canonical_grouping(
        contiguous_grouping())


# -- what the property does and does not select -----------------------------


def test_cross_e8_does_not_single_out_stride4():
    """576 admit it, so the convention is a choice inside an orbit."""
    valid = set(cross_e8_valid_groupings())
    assert stride4_grouping() in valid
    assert len(valid) > 1, (
        "the cross-E8 property now selects a unique grouping; if that is "
        "real the FITTED classification of the face grouping should be "
        "revisited, and if not, something has been assumed"
    )
    assert "not a derivation" in face_grouping_report()["selection"]


def test_a_bad_face_size_is_rejected_rather_than_silently_truncated():
    with pytest.raises(ValueError):
        enumerate_face_groupings(n_bridges=12, face_size=5)
