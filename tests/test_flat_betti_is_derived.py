"""b_2 flat = 0 was asserted with a false citation. Derived here, and it is
the same fact as b_3 flat = 7.

derived_contribution_table carried FLAT_B2 = 0 commented as "DERIVED in
joyce_orbifold". joyce_orbifold had no Lambda^2 computation. The value was
right; the provenance was not -- and that is the worse failure, because a wrong
number gets caught and a wrong citation gets trusted.

THE MECHANISM, WHICH SETTLES EVERY DEGREE AT ONCE
=================================================
(Z/2)^3 has 8 characters: trivial plus 7 non-trivial. Measured, the 7
coordinates of T^7 realise the 7 non-trivial ones BIJECTIVELY. So:

  b_1 = 0   no coordinate carries the trivial character
  b_2 = 0   chi_i chi_j trivial iff chi_i = chi_j iff i = j, and a 2-form
            needs i /= j -- so no invariant 2-form CAN exist
  b_3 = 7   zero-sum character triples are exactly the 7 lines of PG(2,2)

The index set is a Fano plane, and that single fact -- not phi, not the real
form -- fixes the whole flat sector.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools

import pytest

from metaphysica.simulations.PM.geometry.joyce_orbifold import (
    coordinate_characters,
    diagonal_stabiliser,
    flat_betti_report,
    group_fano_lines,
    invariant_p_forms,
    invariant_three_forms,
)


@pytest.fixture(scope="module")
def report():
    return flat_betti_report()


def test_the_seven_coordinates_realise_the_seven_nontrivial_characters(report):
    """The single fact everything else follows from."""
    assert report["group_order"] == 8
    assert report["n_distinct_coordinate_characters"] == 7
    assert report["any_coordinate_is_trivial"] is False
    assert report["characters_realise_all_nontrivial_bijectively"] is True


def test_b2_flat_is_zero_and_now_derived(report):
    assert report["b2_flat"] == 0
    assert report["invariant_two_forms"] == []
    assert "forced, not observed" in report["why_b2_is_zero"]


def test_b2_is_forced_by_distinctness_not_merely_absent():
    """The reason, re-derived independently of the module.

    If two coordinates shared a character, an invariant 2-form would exist. They
    do not, and this asserts the implication rather than the outcome.
    """
    chars = coordinate_characters()
    assert len(set(chars.values())) == 7
    for i, j in itertools.combinations(range(7), 2):
        assert chars[i] != chars[j]
    group = diagonal_stabiliser()
    for i, j in itertools.combinations(range(7), 2):
        assert any(eps[i] * eps[j] == -1 for eps in group), (
            "coordinates %d,%d are invariant as a pair, so b_2 flat > 0" % (i, j)
        )


def test_b3_flat_is_seven_and_equals_the_fano_lines(report):
    assert report["b3_flat"] == 7
    assert report["b3_flat_equals_fano_lines"] is True
    assert sorted(report["invariant_three_forms"]) == sorted(group_fano_lines())


def test_invariant_p_forms_agrees_with_the_older_r3(report):
    """Guards against the generalisation drifting from what it generalises."""
    assert sorted(invariant_p_forms(3)) == sorted(invariant_three_forms())


def test_poincare_duality_holds_on_the_flat_sector(report):
    """A real consequence, not a restatement: it can fail."""
    betti = {int(k): v for k, v in report["flat_betti"].items()}
    assert betti == {0: 1, 1: 0, 2: 0, 3: 7, 4: 7, 5: 0, 6: 0, 7: 1}
    assert report["poincare_duality_holds"] is True
    for p in range(8):
        assert betti[p] == betti[7 - p]


def test_the_euler_characteristic_vanishes_as_odd_dimension_requires(report):
    assert report["euler_characteristic"] == 0
    assert report["euler_is_zero_as_odd_dimension_requires"] is True


def test_the_provenance_correction_is_recorded(report):
    assert "was not" in report["provenance_correction"]
    assert "R5" in report["provenance_correction"]


def test_the_table_constant_matches_the_derivation():
    """FLAT_B2 must not drift from what joyce_orbifold now computes."""
    from metaphysica.simulations.PM.geometry import derived_contribution_table as d

    assert d.FLAT_B2 == flat_betti_report()["b2_flat"]
    assert d.FLAT_B3 == flat_betti_report()["b3_flat"]


def test_a_smaller_group_would_admit_invariant_two_forms():
    """Falsifiability: the argument must depend on the group, not be vacuous.

    Drop a generator and the characters stop being distinct, so invariant
    2-forms appear. If this produced 0 as well, the derivation above would be
    proving nothing about Gamma in particular.
    """
    group = diagonal_stabiliser()
    subgroup = sorted(set(group[:4]))
    assert len(subgroup) == 4, "expected a proper subgroup of order 4"
    n_inv2 = sum(
        1 for i, j in itertools.combinations(range(7), 2)
        if all(eps[i] * eps[j] == 1 for eps in subgroup)
    )
    assert n_inv2 > 0, (
        "a proper subgroup admitted no invariant 2-forms either, so the full "
        "group is not what is doing the work and the derivation is vacuous"
    )
