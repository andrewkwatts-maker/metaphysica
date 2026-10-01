"""Both chi_eff branches, costed. This file adopts nothing and must not.

MEASURED 2026-09-22, and both are NEW costs the dichotomy did not name:

1. **6 b_3 / 48 = b_3 / 8 identically.** So "chi_eff = 6 b_3" plus the standard
   n_gen = chi_eff/48 is not an independent route to the generation count -- it
   IS n_gen_source = b3_over_dim_O, and inherits that route's refutation (b_3
   is odd at every Joyce profile; 8 divides no odd number).

2. **n_gen = chi_eff/48 fails on BOTH branches across the Joyce family.**
   Seed-dependent gives a non-integer at all 8 rows; the constant branch gives
   n_gen = 3 even at n_T3 = 0, where the manifold carries no A_1 families and
   the count should be 0.

So ruling chi_eff also rules on n_gen_source: the two forks are not
independent. WHICH WAY TO RULE IS THE AUTHOR'S and nothing here selects.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry import chi_eff_branches as cb


# ------------------------------------------------------------ both branches run

def test_both_branches_are_executable():
    """A fork whose branches cannot be run is prose with a switch on it."""
    for branch_id in cb.BRANCHES:
        assert isinstance(cb.chi_eff_on_branch(branch_id, 24), float)
        assert isinstance(cb.chi_eff_on_branch(branch_id, 43), float)


def test_an_unknown_branch_is_refused_not_defaulted():
    with pytest.raises(ValueError, match="unknown chi_eff branch"):
        cb.chi_eff_on_branch("whichever_is_convenient", 24)


def test_all_three_routes_agree_only_at_the_adopted_seed():
    """The crossing is the whole reason the agreement is not evidence."""
    at_24 = {cb.chi_eff_on_branch(b, 24) for b in cb.BRANCHES}
    at_43 = {cb.chi_eff_on_branch(b, 43) for b in cb.BRANCHES}
    assert at_24 == {144.0}, "the three routes no longer agree at b_3 = 24"
    assert len(at_43) == 3, (
        "the routes agree somewhere off b_3 = 24, which the unique-crossing "
        "result forbids: %s" % sorted(at_43)
    )


# ---------------------------------------------------------- the route C identity

def test_route_c_is_the_b3_over_8_route_identically():
    """Symbolic, not sampled: a sampled identity could be a coincidence."""
    report = cb.route_c_is_the_b3_over_8_route()
    assert report["holds_identically"] is True
    assert report["difference"] == "0"


def test_the_identity_is_not_shared_by_the_other_routes():
    """Or the finding would be about the divisor rather than about route C."""
    import sympy as sp

    b = sp.Symbol("b", positive=True)
    other = cb.BRANCHES["b3_squared_over_4"]["fn"](b) / cb.N_GEN_DIVISOR
    assert sp.simplify(other - b / 8) != 0


# --------------------------------------------------------- the two branch costs

def test_the_constant_branch_gives_three_generations_on_an_empty_manifold():
    """Branch A's cost, demonstrated rather than interpreted.

    At n_T3 = 0 there are no A_1 families, so b_2 = 0 and there is nothing for
    a generation to come from. A constant chi_eff still reports 3.
    """
    values = cb.downstream_values("constant_144", 7)
    assert values["n_gen"] == 3.0
    assert values["n_gen_equals_three"] is True, (
        "the constant branch no longer returns 3 at the empty profile, so the "
        "demonstration of its vacuity has changed"
    )


def test_the_seed_dependent_branch_gives_a_non_integer_everywhere_on_the_family():
    """Branch B's cost. A generation count is a number of things."""
    table = cb.branch_cost_table()
    on_family = [r for r in table
                 if r["on_joyce_family"] and r["branch_kind"] == "SEED_DEPENDENT"]
    assert len(on_family) == 8
    assert all(not r["n_gen_is_integer"] for r in on_family), (
        "a seed-dependent route now gives an integer n_gen somewhere on the "
        "Joyce family; that is a finding for the ruling, not a test to adjust"
    )


def test_the_dangerous_near_miss_is_not_an_integer():
    """b_3 = 31 via b_3^2/4 gives 5.00521, which rounds to 5 and is not 5."""
    values = cb.downstream_values("b3_squared_over_4", 31)
    assert values["n_gen"] == pytest.approx(961 / 192.0)
    assert round(values["n_gen"]) == 5
    assert values["n_gen_is_integer"] is False, (
        "5.00521 is being read as an integer; that is exactly the rounding "
        "this test exists to forbid"
    )


def test_every_route_agrees_at_the_off_family_seed_and_only_there():
    table = cb.branch_cost_table()
    off_family = [r for r in table if not r["on_joyce_family"]]
    assert off_family, "the adopted seed must be in the table, labelled"
    assert all(r["b3"] == 24 for r in off_family)
    assert all(r["n_gen_equals_three"] for r in off_family)


# ------------------------------------------------------------- the consumers

def test_the_consumers_are_traced_not_recalled():
    report = cb.consumers()
    assert report["n_modules"] > 0
    assert report["n_mentions"] >= report["n_modules"]
    for instrument in report["excluded_as_instruments"]:
        assert instrument not in report["by_module"], (
            "a module that DISCUSSES chi_eff is being counted as one that "
            "consumes it: %s" % instrument
        )


# ------------------------------------------------------------- nothing adopted

def test_the_fork_defaults_to_the_ruled_k3_reading(monkeypatch):
    """D-015 (2026-10-01): the author adopted the K3 reading; the old routes
    stay switchable, the refuted seed_dependent route demoted."""
    from metaphysica.simulations.core.variants import FORKS, resolve

    monkeypatch.delenv("METAPHYSICA_VARIANT_CHI_EFF_ROUTE", raising=False)
    assert resolve("chi_eff_route") == "k3_reading"
    fork = FORKS["chi_eff_route"]
    assert fork.status == "RULED"
    assert set(fork.option_ids()) == {"k3_reading", "unruled",
                                      "constant_144", "seed_dependent"}
    assert fork.option("seed_dependent").refuted
    assert not fork.option("unruled").refuted


def test_the_narration_still_returns_the_dichotomy_when_switched_back(
        monkeypatch):
    from metaphysica.simulations.PM.geometry.geometry_narration import (
        chi_eff_claim,
    )

    monkeypatch.setenv("METAPHYSICA_VARIANT_CHI_EFF_ROUTE", "unruled")
    claim = chi_eff_claim()
    assert claim["may_claim_a_derivation"] is False
    assert claim["ruling_required"] is True
    assert claim["branch"] == "UNRULED"


def test_the_report_states_the_live_ruling(monkeypatch):
    monkeypatch.delenv("METAPHYSICA_VARIANT_CHI_EFF_ROUTE", raising=False)
    report = cb.branches_report()
    assert report["ruling"].startswith("RULED 2026-10-01")
    assert "chi_eff" not in report["still_the_authors"]
    assert "n_gen_source" in report["still_the_authors"]
    assert report["the_k3_resolution"]
    monkeypatch.setenv("METAPHYSICA_VARIANT_CHI_EFF_ROUTE", "unruled")
    assert cb.branches_report()["ruling"].startswith("OPEN")
    assert report["the_coupled_cost"], (
        "the coupling between chi_eff and n_gen_source must be stated, or the "
        "author rules one fork believing the other is independent"
    )


def test_the_fork_drift_guard_fires_if_the_narration_disagrees():
    """The guard must be capable of failing, or it is decoration: a narration
    that refuses a derivation on the ruled K3 branch contradicts the fork."""
    from metaphysica.simulations.core import variants
    from metaphysica.simulations.PM.geometry import geometry_narration

    original = geometry_narration.chi_eff_claim
    try:
        geometry_narration.chi_eff_claim = lambda branch=None: {
            "may_claim_a_derivation": False, "branch": "k3_reading"}
        with pytest.raises(RuntimeError, match="diverged"):
            variants._chi_eff_route_adopted()
    finally:
        geometry_narration.chi_eff_claim = original
    assert variants._chi_eff_route_adopted() == "k3_reading"
