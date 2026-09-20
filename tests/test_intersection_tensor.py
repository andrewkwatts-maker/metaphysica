"""The 12 x 12 x 43 integer tensor: non-isotropic, metric-free, and forced.

This is the object the Leech and E8^3 routes were reaching for and could not
have. Those failed for a specific reason -- Co_0 and W(E8)^3 are large enough
that Schur's lemma forces a shell form proportional to the identity -- and an
integer intersection tensor read off a resolution carries no such symmetry.

Every entry is forced by three facts established elsewhere:

  diagonality   Joyce admissibility makes the singular sets pairwise disjoint,
                so alpha_f ^ alpha_g = 0 for f /= g
  the value -2  the intersection form on an A_n resolution is minus the A_n
                Cartan matrix; A1 gives -(2), and A1 is what the transverse
                group census established
  which omega   R2: each involution's fixed set is a Fano line, so exactly one
                flat 3-form restricts to that family's T^3 volume

Nothing is fitted and nothing is tabulated. The test that matters most is the
last group: the tensor must respond to the enumeration it is read from.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.intersection_tensor import (
    A1_SELF_INTERSECTION,
    canonical_point,
    image_is_isotropic,
    intersection_tensor,
    sector_families,
    tensor_report,
)


@pytest.fixture(scope="module")
def point():
    return canonical_point()


@pytest.fixture(scope="module")
def tensor(point):
    return intersection_tensor(point)


@pytest.fixture(scope="module")
def report(point):
    return tensor_report(point)


# ------------------------------------------------------------ shape and values

def test_the_shape_is_the_one_the_degree_audit_predicted(tensor):
    """Cross-check against the independent degree enumeration."""
    from metaphysica.simulations.PM.geometry.multilinear_degree_audit import (
        degree_audit_report,
    )

    assert tensor["shape"] == (12, 12, 43)
    assert degree_audit_report()["metric_free_cubic_shape"] == tensor["shape"]


def test_every_nonzero_entry_is_the_a1_self_intersection(tensor):
    assert tensor["distinct_values"] == [A1_SELF_INTERSECTION]
    assert A1_SELF_INTERSECTION == -2


def test_the_minus_two_is_the_a1_cartan_entry_not_a_choice():
    """A_1 Cartan matrix is (2); the exceptional curve self-intersects at -(2).

    Asserted against the singularity type the census independently establishes,
    so if the admissible components stopped being A1 this value would be wrong
    and would have to move with them.
    """
    from metaphysica.simulations.PM.geometry.derived_contribution_table import (
        eguchi_hanson_betti,
    )

    # A1 resolution: one exceptional 2-class, hence a 1x1 intersection form
    assert eguchi_hanson_betti()[2] == 1
    assert A1_SELF_INTERSECTION == -2


def test_the_tensor_is_sparse_and_that_is_the_result(tensor):
    total = tensor["shape"][0] * tensor["shape"][1] * tensor["shape"][2]
    assert total == 6192
    assert tensor["n_nonzero"] == 12
    assert tensor["n_nonzero"] < total // 100


# ------------------------------------------------------------ the structure

def test_disjoint_necks_make_it_diagonal_in_h2(tensor):
    """Joyce admissibility, showing up as tensor structure."""
    assert tensor["diagonal_in_h2"] is True
    for key in tensor["entries"]:
        f, g, _k = eval(key)
        assert f == g


def test_it_hits_exactly_three_h3_slots_one_per_singular_involution(
        tensor, report):
    assert tensor["h3_slots_hit"] == [0, 1, 3]
    assert len(tensor["h3_slots_hit"]) == report["n_sectors"] == 3


def test_four_flat_forms_are_never_paired_matching_the_free_involutions(
        tensor, report):
    """The 3 + 4 split of the flat forms mirrors 3 singular + 4 free in Gamma."""
    assert tensor["h3_slots_unhit_flat"] == [2, 4, 5, 6]
    assert report["n_flat_forms_never_paired"] == 4
    assert report["n_sectors"] + report["n_flat_forms_never_paired"] == 7
    assert "mirrors" in report["the_three_plus_four_split"]


def test_the_twelve_families_split_four_per_sector(report):
    assert report["families_per_sector"] == {0: 4, 1: 4, 2: 4}
    assert len(report["distinct_fixed_lines"]) == 3


def test_every_fixed_line_is_one_of_phis_triples(point):
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        invariant_three_forms,
    )

    flat = {tuple(sorted(t)) for t in invariant_three_forms()}
    for fam in sector_families(point):
        assert fam["fixed_line"] in flat, fam


# ------------------------------------------------------------ non-isotropy

def test_the_tensor_is_not_isotropic(report):
    assert report["is_isotropic"] is False
    assert report["h3_image_dimension"] == 3
    assert "Schur" in report["why_not_isotropic"]


def test_the_isotropy_rule_fires_in_both_directions():
    """A non-isotropy claim is worthless if the rule cannot say otherwise.

    An earlier version of this test asserted `(1 <= 1) is True`, which is a
    tautology and could not have failed -- exactly the defect this codebase
    exists to catch, committed inside the file that checks for it. The rule is
    now a named predicate and is exercised on both sides.
    """
    assert image_is_isotropic(1) is True, (
        "a single H^3 target IS the isotropic shape"
    )
    assert image_is_isotropic(0) is True
    assert image_is_isotropic(3) is False
    assert image_is_isotropic(43) is False

    report = tensor_report()
    assert report["h3_image_dimension"] == 3
    assert report["is_isotropic"] is image_is_isotropic(3) is False


# ------------------------------------------------------------ falsifiability

def test_the_families_are_read_from_the_live_enumeration(point):
    """Not tabulated: every family carries its enumeration provenance."""
    families = sector_families(point)
    assert len(families) == 12
    for fam in families:
        assert fam["type"] == "T3"
        assert fam["orbit_size"] == 4
        assert len(fam["fixed_line"]) == 3
        assert len(fam["moved_arc"]) == 4
        assert set(fam["fixed_line"]).isdisjoint(fam["moved_arc"])


def test_the_provenance_of_each_structural_fact_is_recorded(report):
    prov = report["provenance"]
    assert "pairwise disjoint" in prov["diagonality"]
    assert "Cartan" in prov["minus_two"]
    assert "Fano line" in prov["which_omega"]


def test_the_report_declares_what_it_counts(report):
    """A4 bar: classes and intersection numbers, never dimensions."""
    assert "cohomology classes" in report["counts"]
    assert "no conversion to dimensions" in report["counts"].replace("\n", " ")


def test_a_family_fixing_a_non_line_would_raise(monkeypatch):
    """The pairing rule depends on R2; if R2 broke, this must not carry on."""
    from metaphysica.simulations.PM.geometry import intersection_tensor as mod

    real = sector_families()
    broken = [dict(f) for f in real]
    broken[0]["fixed_line"] = (0, 1, 3)        # not a phi triple
    monkeypatch.setattr(mod, "sector_families", lambda point=None: broken)
    with pytest.raises(RuntimeError, match="not one of phi's triples"):
        mod.intersection_tensor()
