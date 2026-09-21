"""Three derivations of chi_eff = 144 agree at one point, and that is not evidence.

chi_eff is load-bearing -- n_gen = chi_eff/48, alpha_leak = 1/sqrt(chi_eff/b_3),
and the EML trees encode it -- and three different derivations are claimed:

    A  2(h11 - h21 + h31)   TCS Hodge numbers     g2_geometry
    B  b_3^2 / 4            FormulasRegistry
    C  6 b_3                EML operator trees

All three return 144 at b_3 = 24, which reads as strong corroboration. This file
pins the three reasons it is not.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.chi_eff_routes import (
    ROUTES,
    chi_eff_report,
    evaluate_routes,
    how_cheap_is,
    reachable_family,
    unique_intersection,
)


@pytest.fixture(scope="module")
def report():
    return chi_eff_report()


# ----------------------------------------------- the family relation

def test_b3_is_determined_by_b2_across_the_whole_family():
    """b_3 = 7 + 3 b_2 everywhere reachable: ONE input, not two."""
    family = reachable_family()
    assert len(family) == 4
    for row in family:
        assert row["b3"] == 7 + 3 * row["b2"], row
        assert row["satisfies_b3_eq_7_plus_3b2"] is True


def test_the_adopted_pair_violates_the_family_relation(report):
    """A third independent way to see (24, 4) is off the Joyce family."""
    assert report["adopted_pair_on_family"] is False
    assert 7 + 3 * 4 == 19 != 24


def test_the_relation_is_not_vacuous():
    """If b_2 were constant across the family the relation would say nothing."""
    family = reachable_family()
    assert len({row["b2"] for row in family}) == 4
    assert len({row["b3"] for row in family}) == 4


# ----------------------------------------------- finding 1: the crossing

def test_the_two_b3_routes_cross_at_exactly_one_point_and_it_is_24():
    result = unique_intersection()
    assert result["positive_roots"] == [24]
    assert result["is_unique"] is True
    assert result["value_at_roots"] == [144.0]


def test_the_routes_diverge_at_every_other_reachable_b3():
    for row in reachable_family():
        values = evaluate_routes(row["b2"], row["b3"])
        if row["b3"] == 24:                      # not reachable, but guard anyway
            continue
        assert values["six_b3"] != values["b3_squared_over_4"], row


def test_all_three_agree_only_at_the_adopted_off_family_point(report):
    agreeing = [r for r in report["table"] if r["all_agree"]]
    assert len(agreeing) == 1
    assert (agreeing[0]["b2"], agreeing[0]["b3"]) == (4, 24)
    assert "off the Joyce family" in agreeing[0]["label"]


# ----------------------------------------------- finding 2: 144 is cheap

def test_144_is_not_a_rare_target(report):
    cheap = report["trials_factor_at_24"]
    assert cheap["n_hits"] >= 5
    assert cheap["hit_rate"] > 0.01, (
        "144 became rare in this expression pool, so the trials-factor "
        "argument needs restating rather than asserting"
    )


def test_the_claimed_routes_are_among_the_cheap_hits(report):
    hits = report["trials_factor_at_24"]["hits"]
    assert "6*b3" in hits or "b3*6" in hits
    assert "b3^2/4" in hits


def test_the_search_finds_nothing_when_the_target_is_absurd():
    """A counter that hit everything would make the trials factor meaningless."""
    result = how_cheap_is(1_000_003.0, 4, 24)
    assert result["n_hits"] == 0, result["hits"]


# ----------------------------------------------- finding 3: the dichotomy

def test_no_b_dependent_expression_gives_144_on_both_paths(report):
    """The heart of it: only constants survive both seeds."""
    assert report["b_dependent_expressions_giving_144_at_both"] == [], (
        "a b-dependent expression now gives 144 at both seeds, which would "
        "break the dichotomy this module rests on: %s"
        % report["b_dependent_expressions_giving_144_at_both"]
    )
    assert report["expressions_giving_144_at_both_points"], (
        "not even constants survive, so the comparison is broken"
    )


def test_the_tcs_route_does_not_depend_on_b3_at_all(report):
    """Which is why it is 144 everywhere -- it is a constant in disguise."""
    assert ROUTES["tcs_hodge"]["depends_on_b3"] is False
    values = {r["tcs_hodge"] for r in report["table"]}
    assert values == {144.0}


def test_the_tcs_route_is_flagged_as_a_type_error():
    note = ROUTES["tcs_hodge"]["type_note"]
    assert "Calabi-Yau" in note
    assert "h21" in note and "h31" in note


def test_the_dichotomy_is_stated_and_undecided(report):
    text = report["the_dichotomy"]
    assert "CONSTANT" in text and "SEED-DEPENDENT" in text
    assert "wants both" in text
    assert "selects none" in report["ruling_required"]


def test_the_report_declares_what_it_counts(report):
    assert "cohomology classes" in report["counts"]
    assert "Calabi-Yau threefold" in report["counts"]


# ----------------------------------------------- falsifiability

def test_the_routes_respond_to_their_inputs():
    """A route that ignored b_3 (other than A, which is declared to) is a bug."""
    low = evaluate_routes(12, 43)
    high = evaluate_routes(12, 44)
    assert low["six_b3"] != high["six_b3"]
    assert low["b3_squared_over_4"] != high["b3_squared_over_4"]
    assert low["tcs_hodge"] == high["tcs_hodge"]      # declared constant
