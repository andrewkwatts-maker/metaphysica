"""128 conical assignments exist in the shift family; none is admissible.

The flavour dock's wall moved: not "the family has no codimension-7 points"
but "it has 128 conical assignments (measured, 2^21 scanned) whose
resolution physics is open, all off the A1-admissible branch". This file
pins the count, the criterion's honesty in both directions, and the
boundary statement's caveats.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.conical_point_search import (
    compose_all_elements,
    conical_report,
    full_group_fixed_points,
)


@pytest.fixture(scope="module")
def report():
    return conical_report()


def test_the_scan_covers_the_whole_derived_shift_space(report):
    assert report["n_assignments_scanned"] == 2 ** 21


def test_the_measured_count_is_128(report):
    """MEASURED 2026-09-22. If this moves, the criterion or the group
    action changed -- either is register-worthy, not absorbable."""
    assert report["n_conical_assignments"] == 128


def test_the_zero_shift_orbifold_is_conical(report):
    """The maximally singular T^7/Gamma fixes the origin -- the sanity
    anchor for the criterion."""
    assert report["zero_shift_is_one_of_them"] is True
    assert full_group_fixed_points(((0,) * 7,) * 3) == 2 ** 7


def test_the_criterion_can_say_no():
    """The canonical point's own shifts are NOT conical -- three singular
    elements only, and disjoint fixed sets. A criterion that fires
    everywhere would be a defect, not a discovery."""
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        canonical_point,
    )

    shifts = canonical_point()["shifts"]
    assert full_group_fixed_points(shifts) == 0


def test_composite_shifts_are_derived_not_chosen():
    """The cocycle: shifting one generator moves its composites."""
    base = compose_all_elements(((0,) * 7,) * 3)
    moved = compose_all_elements((((1,) + (0,) * 6), (0,) * 7, (0,) * 7))
    changed = [bits for bits in base
               if base[bits][1] != moved[bits][1]]
    assert changed, "no composite shift responded to a generator shift"
    assert (1, 1, 0) in changed or (1, 0, 1) in changed or \
        (1, 1, 1) in changed or (1, 0, 0) in changed


def test_the_report_refuses_the_three_overclaims(report):
    """The A4 bar: existence of the cone is not chirality, not
    resolvability, and not reachability from (12, 43)."""
    open_q = report["what_remains_open"]
    assert "chiral" in open_q
    assert "resolution" in open_q or "smoothing" in open_q
    assert "deformation" in open_q or "connects" in open_q
    assert "NONE" in report["on_the_admissible_branch"]


def test_the_boundary_statement_carries_the_measured_number(report):
    assert "128" in report["the_boundary_moved"]
