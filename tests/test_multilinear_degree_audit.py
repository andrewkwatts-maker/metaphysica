"""The triple intersection form on H^3 does not exist, and the audit says which
invariants do.

The register carries d_ijk as BLOCKED -- "needs a harmonic basis on an actual
Y_7". It is not blocked. The proposed object

    N_IJK = int_M omega_I ^ omega_J ^ omega_K,  omega in H^3

has total degree 3 + 3 + 3 = 9 on a 7-manifold, so it is identically zero for
every input. No metric, no harmonic representative, no resolution changes that.
The item closes by REFUTATION, which is a closure.

The positive half is the useful one, and it is equally cheap: degree arithmetic
enumerates every multilinear invariant that DOES exist. For the 43 path the list
is exactly three long, and only one of them is not Poincare duality.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools

import pytest

from metaphysica.simulations.PM.geometry.multilinear_degree_audit import (
    admissible_pairings,
    audit_pairing,
    degree_audit_report,
    is_top_form,
    refuted_pairings,
    wedge_degree,
)


@pytest.fixture(scope="module")
def report():
    return degree_audit_report()


# ------------------------------------------------------------ the refutation

def test_a_cubic_form_on_h3_is_not_defined_on_a_seven_manifold():
    row = audit_pairing((3, 3, 3))
    assert row["total_degree"] == 9
    assert row["verdict"] == "NOT_DEFINED"
    assert "identically zero" in row["why"]


def test_there_is_no_topological_bilinear_on_h3_alone():
    """So the intrinsic route does NOT escape the metric."""
    row = audit_pairing((3, 3))
    assert row["total_degree"] == 6
    assert row["verdict"] == "NOT_DEFINED"


def test_the_refuted_routes_stay_on_the_books_with_their_reason(report):
    refuted = {r["degrees"]: r for r in report["refuted"]}
    assert (3, 3, 3) in refuted and (3, 3) in refuted
    for row in refuted.values():
        assert row["status"] == "REFUTED_BY_DEGREE"
        assert row["consequence"]
    assert "closes by refutation" in refuted[(3, 3, 3)]["consequence"]
    assert "METRIC-DEPENDENT" in refuted[(3, 3)]["consequence"]
    assert report["no_cubic_form_on_h3"] is True


# ------------------------------------------------------- what does exist

def test_the_admissible_list_is_exactly_three_for_the_43_path(report):
    assert report["betti"][2] == 12
    assert report["betti"][3] == 43
    degrees = [r["degrees"] for r in report["admissible"]]
    assert degrees == [(2, 5), (3, 4), (2, 2, 3)], degrees


def test_the_metric_free_cubic_is_a_12_by_12_by_43_integer_tensor(report):
    assert report["metric_free_cubic_available"] is True
    assert report["metric_free_cubic_shape"] == (12, 12, 43)


def test_the_cubic_is_the_only_non_poincare_pairing(report):
    """Why it is THE replacement for the lattice Gram matrix, not one of many."""
    non_poincare = [r["degrees"] for r in report["admissible"]
                    if len(r["degrees"]) > 2]
    assert non_poincare == [(2, 2, 3)], non_poincare


def test_the_two_factor_pairings_are_poincare_duality(report):
    for row in report["admissible"]:
        if len(row["degrees"]) == 2:
            p, q = row["degrees"]
            assert p + q == 7
            assert report["betti"][p] == report["betti"][q]


# ------------------------------------------------------- completeness

def test_the_enumeration_is_complete_against_brute_force(report):
    """Independent recount, so the list cannot be short by construction."""
    betti = report["betti"]
    live = [d for d in range(1, 8) if betti.get(d, 0) > 0]
    expected = set()
    for k in range(2, 5):
        for combo in itertools.combinations_with_replacement(live, k):
            if sum(combo) == 7:
                expected.add(combo)
    got = {r["degrees"] for r in report["admissible"]}
    assert got == expected, "missing %s / extra %s" % (
        sorted(expected - got), sorted(got - expected))


def test_ordering_is_canonical_not_iteration_dependent(report):
    rows = report["admissible"]
    keys = [(len(r["degrees"]), r["degrees"]) for r in rows]
    assert keys == sorted(keys)


# ------------------------------------------------------- falsifiability

def test_a_vanishing_betti_number_makes_the_pairing_vanish_not_disappear():
    """The distinction the verdict vocabulary exists for."""
    row = audit_pairing((2, 2, 3), betti={2: 0, 3: 43})
    assert row["verdict"] == "VANISHES"
    assert "identically zero rather than unavailable" in row["why"]


def test_the_audit_responds_to_its_betti_input():
    """An audit that ignored the topology would pass everything above."""
    with_b2 = admissible_pairings({0: 1, 2: 12, 3: 43, 4: 43, 5: 12, 7: 1})
    without_b2 = admissible_pairings({0: 1, 2: 0, 3: 43, 4: 43, 5: 0, 7: 1})
    assert (2, 2, 3) in {r["degrees"] for r in with_b2}
    assert (2, 2, 3) not in {r["degrees"] for r in without_b2}, (
        "the cubic survived b_2 = 0, so the enumeration is not reading Betti "
        "numbers at all"
    )


def test_b1_zero_removes_every_pairing_that_would_use_it(report):
    """On a G2 manifold b_1 = 0, so no admissible pairing may contain a 1."""
    assert report["betti"][1] == 0
    for row in report["admissible"]:
        assert 1 not in row["degrees"]


# ------------------------------------------------------- the A4 bar

def test_every_row_declares_that_it_counts_degrees(report):
    """Degrees are not dimensions, not group orders, not cycle counts."""
    assert "degrees" in report["counts"]
    for row in report["admissible"] + report["refuted"]:
        assert row["counts"] == "degrees of differential forms"


def test_the_primitives_are_trivial_and_therefore_checkable():
    assert wedge_degree((2, 2, 3)) == 7
    assert is_top_form((2, 2, 3)) is True
    assert is_top_form((3, 3, 3)) is False
    assert is_top_form((2, 2, 2)) is False
    # dimension is a parameter, not a hardcoded 7
    assert is_top_form((3, 3), dim=6) is True
