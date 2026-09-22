"""The transverse Kummer structure, and chi(K3) = 24 as an enumeration ENTRY.

MEASURED 2026-09-22: each singular involution carries 16 / 16 / 16 fixed T^3 on
the COVER (4 families x orbit size 4), matching the 16 A_1 points of the
transverse T^4/Z_2 exactly. chi(K3) = 24 follows from the construction:
(chi(T^4) - 16)/2 + 16 chi(P^1) = (0 - 16)/2 + 32 = 24.

THE A4 BAR IS THE POINT OF THIS FILE
====================================
Two different sixteens live on different spaces and are not the same object:

    16 fixed T^3 on the COVER      components of the fixed locus upstairs
    16 A_1 points on the QUOTIENT  singular points of T^4/Z_2

They are equal in number because they are the same index set on the two sides
of the quotient map -- T^3 x (A_1 point), family by family -- not because two
independent counts agreed. Every test below states which side it is counting.

AND THE chi_eff ENTRY CAME BACK NEGATIVE, WHICH IS THE USEFUL PART
==================================================================
`chi_eff_routes.kummer_defect_entry` costs the defect-count pool against 144:
4 of 120 expressions hit it, and **none involves chi_K3**. The hits run through
n_families^2 = 12^2 and n_singular x total_tori = 3 x 48, both already on the
books. So the Kummer measurement gives chi_eff a real geometric entry point at
24 and supplies **no route from it to 144**. The ruling stays the author's.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry import kummer_transverse as kt
from metaphysica.simulations.PM.geometry.chi_eff_routes import (
    kummer_defect_entry,
)


# ------------------------------------------------ the sixteen on the quotient

def test_the_sixteen_a1_points_are_enumerated_not_asserted():
    """-1 on T^4 fixes the half-lattice points: 2^4 of them, listed."""
    report = kt.kummer_fixed_points()
    assert report["n_fixed_points"] == 16
    assert report["matches_two_to_the_dim"] is True
    assert len(set(report["points"])) == 16
    assert all(all(c in (0.0, 0.5) for c in p) for p in report["points"]), (
        "a fixed point of -1 on R^4/Z^4 must have every coordinate 0 or 1/2"
    )
    assert "POINTS" in report["counts_what"]
    assert "quotient" in report["counts_what"].lower(), (
        "the count must name which side of the quotient map it lives on"
    )


def test_the_fixed_point_count_tracks_the_dimension():
    """2^d, not a constant 16 -- or the derivation is a coincidence."""
    assert kt.kummer_fixed_points(2)["n_fixed_points"] == 4
    assert kt.kummer_fixed_points(3)["n_fixed_points"] == 8
    assert kt.kummer_fixed_points(4)["n_fixed_points"] == 16
    assert kt.kummer_fixed_points(5)["n_fixed_points"] == 32


# --------------------------------------------------- the sixteen on the cover

def test_each_singular_involution_carries_sixteen_fixed_tori():
    """Measured from the live enumeration: 16 / 16 / 16."""
    per = kt.fixed_tori_per_involution()
    assert len(per) == 3, (
        "there are no longer 3 singular involutions at the canonical point"
    )
    assert [rec["n_fixed_tori_on_cover"] for rec in per] == [16, 16, 16]
    assert all(rec["matches_kummer_16"] for rec in per)


def test_the_sixteen_is_four_orbits_of_size_four_not_four_families():
    """The count is a sum of ORBIT SIZES, not a count of orbits.

    Conflating them would give 4 and would still look like a plausible
    geometric number, which is exactly why the distinction gets a test.
    """
    per = kt.fixed_tori_per_involution()
    for rec in per:
        assert rec["n_families"] == 4, "orbits per involution"
        assert rec["orbit_sizes"] == [4, 4, 4, 4], "size of each orbit"
        assert sum(rec["orbit_sizes"]) == rec["n_fixed_tori_on_cover"] == 16
        assert rec["n_families"] != rec["n_fixed_tori_on_cover"], (
            "orbits and components have collapsed to the same number; the A4 "
            "bar cannot be checked"
        )


def test_the_two_sixteens_are_named_as_different_objects():
    report = kt.transverse_report()
    bar = report["a4_bar"]
    assert "COVER" in bar and "QUOTIENT" in bar
    assert "correspondence of index sets" in bar.lower()
    assert report["fixed_tori_on_cover_per_involution"] == [16, 16, 16]
    assert report["a1_points_on_quotient"] == 16


# ----------------------------------------------------------------- chi(K3)

def test_chi_k3_is_computed_from_the_construction():
    report = kt.chi_k3_from_kummer()
    assert report["chi_T4"] == 0
    assert report["n_fixed_points"] == 16
    assert report["chi_P1"] == 2
    assert report["chi_K3"] == 24
    assert report["is_24"] is True


def test_chi_k3_would_move_if_the_construction_did():
    """The formula must respond to its inputs, or 24 is a literal in disguise."""
    assert kt.chi_k3_from_kummer(2)["chi_K3"] == (0 - 4) // 2 + 4 * 2 == 6
    assert kt.chi_k3_from_kummer(3)["chi_K3"] == (0 - 8) // 2 + 8 * 2 == 12
    assert kt.chi_k3_from_kummer(4)["chi_K3"] == 24


def test_the_scope_excludes_a_tcs_reading():
    """The register excludes TCS independently; this must not re-open it."""
    report = kt.transverse_report()
    assert "not a global k3 fibration" in report["scope"].lower()
    assert "does not license a tcs reading" in report["scope"].lower()
    assert "71-155" in report["scope"]


# ----------------------------------------------- the chi_eff enumeration entry

def test_the_kummer_entry_is_an_entry_and_not_a_derivation():
    entry = kummer_defect_entry()
    assert entry["status"] == "ENTRY_IN_THE_ENUMERATION"
    assert entry["ruling_stays_with_the_author"] is True
    assert "nothing is selected" in entry["verdict"].lower()


def test_the_defect_pool_is_read_from_the_live_enumeration():
    entry = kummer_defect_entry()
    pool = entry["defect_pool"]
    assert pool["chi_K3"] == 24
    assert pool["n_singular"] == 3
    assert pool["n_families"] == 12
    assert pool["orbit_size"] == 4
    assert pool["tori_per_involution"] == 16
    assert pool["total_tori"] == 48
    assert pool["n_singular"] * pool["tori_per_involution"] == pool["total_tori"]


def test_no_expression_through_chi_k3_reaches_144():
    """The measured negative, and it is the useful half of the entry."""
    entry = kummer_defect_entry()
    assert entry["chi_K3_reaches_144"] is False, (
        "an expression through chi_K3 now reaches 144: %s. That is a finding "
        "for the chi_eff ruling, not a test to adjust."
        % entry["hits_through_chi_K3"]
    )
    assert entry["hits_through_chi_K3"] == []


def test_the_hits_that_do_occur_are_the_ones_already_on_the_books():
    entry = kummer_defect_entry()
    assert entry["n_hits_at_144"] == 4
    assert all("n_families" in h or "total_tori" in h
               for h in entry["hits_at_144"]), (
        "a new route to 144 appeared outside the known 12^2 and 3 x 48"
    )


def test_the_trials_factor_is_reported_with_the_hit():
    """A hit without its search size is not a measurement."""
    entry = kummer_defect_entry()
    assert entry["n_expressions_searched"] == 120
    assert entry["hit_rate"] == pytest.approx(4 / 120.0)
    assert "%" in entry["verdict"]
