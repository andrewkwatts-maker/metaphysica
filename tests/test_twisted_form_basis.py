"""b_3 = 43 must be a list of objects, not an integer.

The framework has carried 7 + 3 n_T3 as arithmetic for several passes without
ever exhibiting one of the twisted classes. These tests hold the basis module to
producing 43 closed 3-forms, each labelled with the family and chart that
supports it, and to doing so PARAMETRICALLY -- so the count tracks the profile
instead of being a constant that happens to read 43.

THE PERTURBATIONS THAT MAKE THESE TESTS REAL
============================================
  * the dimension is swept over every admissible profile, and each is compared
    against 7 + 3 n_T3 computed independently of the construction;
  * the family list is truncated by hand, and the twisted count must follow it;
  * `neck_chart` is fed a broken partition and must raise rather than paper over
    the missing coordinate;
  * closedness runs through the symbolic exterior derivative, which refuses
    floats -- so it cannot be passed by a stub returning zeros.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

sp = pytest.importorskip("sympy")

from metaphysica.simulations.PM.geometry import twisted_form_basis as tfb
from metaphysica.simulations.PM.geometry.intersection_tensor import (
    sector_families,
)
from metaphysica.simulations.PM.geometry.joyce_orbifold import (
    invariant_three_forms,
)


@pytest.fixture(scope="module")
def full():
    return tfb.build_basis()


# ------------------------------------------------- the parametric count

@pytest.mark.parametrize("n_sectors, n_t3", [(0, 0), (1, 4), (2, 8), (3, 12)])
def test_the_dimension_is_seven_plus_three_n_t3_at_every_profile(
        n_sectors, n_t3):
    """THE CENTRAL PARAMETRIC CHECK. At n_T3 = 8 this demands 7 + 12 + 12."""
    basis = tfb.build_basis(n_sectors=n_sectors)
    assert basis["n_t3"] == n_t3
    assert basis["dimension"] == tfb.basis_dimension(n_t3)
    assert basis["dimension"] == len(invariant_three_forms()) + 3 * n_t3
    assert basis["blocks"] == [7] + [12] * n_sectors


def test_the_profiles_are_exactly_the_admissible_n_t3_values():
    """The sweep must land on {0, 4, 8, 12} and nothing else."""
    reported = tuple(p["n_t3"] for p in tfb.basis_report()["profiles"])
    assert reported == tfb.ADMISSIBLE_N_T3


def test_the_full_basis_has_forty_three_elements(full):
    assert full["dimension"] == 43
    assert full["n_flat"] == 7
    assert full["n_twisted"] == 36
    assert full["blocks"] == [7, 12, 12, 12]


def test_a_smaller_profile_is_not_forty_three():
    """Guards the sweep against a constant that happens to read 43."""
    assert tfb.build_basis(n_sectors=2)["dimension"] == 31
    assert tfb.build_basis(n_sectors=0)["dimension"] == 7


def test_the_families_are_read_live_and_the_count_follows_them():
    """Truncating the family list must move the twisted count.

    If the 36 were tabulated rather than built per family, this would not move.
    """
    families = sector_families()
    assert len(families) == 12
    for keep in (1, 5, 11):
        reps = tfb.twisted_representatives(families[:keep])
        assert len(reps) == tfb.LEGS_PER_FAMILY * keep


def test_an_out_of_range_profile_is_refused():
    with pytest.raises(ValueError, match="n_sectors"):
        tfb.build_basis(n_sectors=99)


# ------------------------------------------------------ the objects

def test_every_representative_is_a_closed_three_form(full):
    report = tfb.basis_is_closed(full)
    assert report["n_checked"] == 43
    assert report["all_closed"] is True, report["failures"]
    for rep in list(full["flat"]) + list(full["twisted"]):
        assert rep["form"].degree == 3
        assert rep["form"].dim == tfb.N_COORDS
        assert not rep["form"].is_zero()


def test_the_flat_representatives_are_exactly_phis_triples(full):
    triples = sorted(rep["triple"] for rep in full["flat"])
    assert triples == sorted(tuple(sorted(t)) for t in invariant_three_forms())


def test_each_twisted_leg_lies_in_its_familys_fixed_line(full):
    """The 3 legs are the involution's FIXED coordinates (R2), not a choice."""
    for rep in full["twisted"]:
        assert rep["leg"] in rep["fixed_line"]
        assert len(rep["fixed_line"]) == tfb.LEGS_PER_FAMILY
        assert len(rep["moved_arc"]) == 4
        assert not set(rep["fixed_line"]) & set(rep["moved_arc"])


def test_each_family_contributes_exactly_three_legs(full):
    seen = {}
    for rep in full["twisted"]:
        seen.setdefault(rep["family"], set()).add(rep["leg"])
    assert len(seen) == 12
    assert all(len(legs) == tfb.LEGS_PER_FAMILY for legs in seen.values())


def test_the_representatives_are_distinct(full):
    """43 labels must be 43 different objects."""
    signatures = set()
    for rep in list(full["flat"]) + list(full["twisted"]):
        signatures.add((rep["kind"], rep["chart"], rep["leg"],
                        tuple(sorted(rep["form"].components))))
    assert len(signatures) == 43


def test_the_twisted_forms_carry_the_eguchi_hanson_bolt_parameter(full):
    """A twisted form built from a constant 2-form would not be the EH class."""
    a = sp.Symbol("a", positive=True)
    for rep in full["twisted"]:
        assert any(a in sp.sympify(v).free_symbols
                   for v in rep["form"].components.values())


# --------------------------------------------------------- the chart

def test_the_neck_chart_partitions_all_seven_coordinates():
    coords, slots = tfb.neck_chart((1, 3, 5), (0, 2, 4, 6))
    assert len(coords) == 7
    assert all(c is not None for c in coords)
    assert sorted(slots) == [0, 1, 2, 3]
    assert sorted(slots.values()) == [0, 2, 4, 6]


def test_a_broken_partition_raises_rather_than_being_papered_over():
    """If R2 ever stops holding, this must fail loudly."""
    with pytest.raises(RuntimeError, match="partition|R2"):
        tfb.neck_chart((1, 3), (0, 2, 4))


# --------------------------------------------------------- the honesty

def test_the_report_states_its_order_in_t():
    """Exact-vs-asymptotic must never be conflated at any consumer."""
    rep = tfb.basis_report()
    assert "LEADING ORDER" in rep["order_in_t"]
    assert "O(t)" in rep["order_in_t"]
    assert rep["all_closed"] is True
    assert rep["full_dimension"] == 43
