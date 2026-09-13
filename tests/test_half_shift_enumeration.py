"""The half-shift enumeration and the parity theorem refuting b_3 = 24.

The load-bearing tests here are the NON-VACUITY ones. A search that reports
"17 is unachievable" is worthless unless the same search finds achievable
targets, and a count of 14336 is worthless unless it moves when its inputs do.
Both are checked.
"""

from __future__ import annotations

import itertools

import numpy as np
import pytest

from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
    achievable_twisted,
    enumerate_all,
    fixed_coords,
    generating_triples,
    moved_coords,
    refutation_report,
    singular_profile,
    twisted_is_always_even,
)

_TRIPLES = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5),
            (1, 4, 6), (2, 3, 6), (2, 4, 5)]


@pytest.fixture(scope="module")
def report():
    return refutation_report()


@pytest.fixture(scope="module")
def enum():
    return enumerate_all()


class _FakePhi:
    def __init__(self, phi):
        self.phi = phi


def _perturbed():
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    phi = G2DifferentialGeometry().phi.copy()
    for perm, sign in (((0, 1, 3), 1), ((1, 3, 0), 1), ((3, 0, 1), 1),
                       ((1, 0, 3), -1), ((0, 3, 1), -1), ((3, 1, 0), -1)):
        phi[perm] = sign
    return _FakePhi(phi)


# ------------------------------------------------------------- the reduction


def test_there_are_28_generating_triples():
    """Non-collinear triples in F_2^3: 28 of the 35."""
    assert len(generating_triples()) == 28


def test_moved_and_fixed_split_is_four_and_three():
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
    )

    for g in diagonal_stabiliser():
        if not any(s < 0 for s in g):
            continue
        assert len(moved_coords(g)) == 4
        assert len(fixed_coords(g)) == 3


def test_the_enumeration_size_is_eight_cubed_times_28(enum):
    assert enum["n_assignments"] == 8 ** 3 * 28 == 14336


# ---------------------------------------------------------------- the theorem


def test_every_profile_entry_is_even(enum):
    """The whole refutation rests on this, so it is asserted directly."""
    assert twisted_is_always_even(list(enum["profiles"]))
    for profile in enum["profiles"]:
        for n in profile:
            assert n % 2 == 0, "odd family-class count %s" % (profile,)


def test_family_counts_are_all_even(enum):
    for n in enum["family_counts"]:
        assert n % 2 == 0
    assert 17 not in enum["family_counts"]


def test_there_are_22_distinct_profiles(enum):
    assert len(enum["profiles"]) == 22


def test_twisted_17_is_unachievable(report):
    assert report["twisted_needed_for_b3_24"] == 17
    assert report["twisted_24_is_achievable"] is False


def test_b3_is_always_odd_so_24_is_refuted(report):
    assert report["flat_contribution"] == 7
    assert report["b3_parity"] == "odd"
    assert "REFUTED" in report["verdict"]
    assert report["model_independent"] is True


# ------------------------------------------------- NON-VACUITY: the search works


def test_the_search_finds_achievable_targets(enum):
    """If achievable_twisted always returned False the theorem would be empty."""
    profiles = list(enum["profiles"])
    assert achievable_twisted(profiles, 0) is True
    # an even target reachable from a profile containing a 2
    assert achievable_twisted(profiles, 2) is True
    assert achievable_twisted(profiles, 4) is True
    assert achievable_twisted(profiles, 16) is True


def test_every_odd_target_is_unachievable(enum):
    """The parity claim, checked directly rather than argued."""
    profiles = list(enum["profiles"])
    for odd in (1, 3, 5, 7, 9, 15, 17, 19):
        assert achievable_twisted(profiles, odd) is False, (
            "odd twisted contribution %d became achievable" % odd
        )


def test_even_targets_are_broadly_achievable(enum):
    """Complementing the above, so the result is parity and not blanket denial."""
    profiles = list(enum["profiles"])
    reachable = [t for t in range(0, 33, 2) if achievable_twisted(profiles, t)]
    assert len(reachable) >= 10, "only %s even targets reachable" % reachable


# ------------------------------------------- NON-VACUITY: it reads its inputs


def test_a_perturbed_phi_changes_the_enumeration():
    """The counts must come from the group, not from constants in this file."""
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
    )

    fake = _perturbed()
    group = diagonal_stabiliser(fake)
    assert len(group) != 8, "perturbation did not move the group order"
    assert len(generating_triples(group)) != 28, (
        "the triple count did not respond to a perturbed phi, so the "
        "enumeration is not reading the group it was handed"
    )


def test_a_shift_on_a_fixed_direction_removes_the_fixed_points():
    """The mechanism the whole enumeration turns on."""
    triple = generating_triples()[0]
    no_shift = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
    with_shift = ((1, 0, 0), (0, 0, 0), (0, 0, 0))
    a = singular_profile(triple, no_shift)
    b = singular_profile(triple, with_shift)
    assert a is not None and b is not None
    assert a["freely_acting_involutions"] == 0
    assert b["freely_acting_involutions"] > 0, (
        "a half-shift along a fixed direction must make some element act freely"
    )
    assert b["n_families"] < a["n_families"]


def test_the_unshifted_case_reproduces_112_components():
    """Cross-check against arc_flag_structure's independent count."""
    from metaphysica.simulations.PM.geometry.arc_flag_structure import (
        fixed_locus_components,
    )

    triple = generating_triples()[0]
    rec = singular_profile(triple, ((0, 0, 0), (0, 0, 0), (0, 0, 0)))
    assert rec["n_families"] == 112
    assert fixed_locus_components()["total_three_torus_components"] == 112


# ------------------------------------------------------------ honest scoping


def test_the_report_states_its_assumptions_and_limits(report):
    assert len(report["assumptions"]) >= 4
    joined = " ".join(report["assumptions"]).lower()
    assert "flat contribution is exactly 7" in joined
    assert "additively" in joined
    assert "fano_tcs" in report["does_not_refute"]
    assert "ODD" in report["falsifiable_prediction"]


def test_no_published_betti_number_is_asserted():
    """The calibration gate is discharged by a prediction, not by a quoted table."""
    from metaphysica.simulations.PM.geometry import half_shift_enumeration

    doc = half_shift_enumeration.__doc__ or ""
    assert "No number from them is" in doc or "no number from them is" in doc.lower()
    blob = str(refutation_report())
    for suspicious in ("43", "215", "155"):
        assert ("b_3 = " + suspicious) not in blob
