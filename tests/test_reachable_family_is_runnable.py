"""The selection argument, CHECKED across the whole family instead of restated.

"n_gen = rank(Gamma) = 3 selects (12, 43) uniquely out of four enumerated
candidates" was the load-bearing claim behind the b3_seed adoption -- and
until 2026-09-23 only TWO of those four candidates were runnable, because
b3_path.PATHS listed seed_24 and seed_43_joyce by hand. A selection
argument over a family the pipeline cannot execute is an assertion with a
citation, not a measurement.

PATHS is now GENERATED from the contribution table's own relation
(b_3 = 7 + 3 n_T3, n_T3 in {0, 4, 8, 12}, b_2 = n_T3), so all four profiles
run end to end and this file checks the selection by running it:

    b_3    b_2   n_gen = b_2/4
      7      0       0
     19      4       1
     31      8       2
     43     12       3   <- the only three

MEASURED 2026-09-23 with the registry resolving each seed in turn.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.b3_path import (
    PATHS,
    n_gen_report,
    seed_values,
)

#: The relation the family is generated from. Stated here independently so
#: the test is not checking the generator against itself.
_EXPECTED = {7: 0, 19: 4, 31: 8, 43: 12}


def _reachable():
    return {k: v for k, v in PATHS.items() if v.get("reachable_by_joyce")}


def test_every_reachable_profile_is_declared():
    """All four, not the two that happened to be written by hand."""
    got = {v["b3"]: v["b2"] for v in _reachable().values()}
    assert got == _EXPECTED, (
        "the reachable family is %s, not the four profiles the contribution "
        "table derives (b_3 = 7 + 3 n_T3 over n_T3 in {0,4,8,12}): %s"
        % (got, _EXPECTED)
    )


def test_the_family_satisfies_its_own_relation():
    for spec in _reachable().values():
        assert spec["b3"] == 7 + 3 * spec["b2"], (
            "profile b_3=%d b_2=%d violates b_3 = 7 + 3 b_2, so the "
            "generator and the relation have drifted apart"
            % (spec["b3"], spec["b2"])
        )


@pytest.mark.parametrize("seed", sorted(_reachable()))
def test_each_profile_runs_end_to_end(seed, monkeypatch):
    """Runnable means RUNNABLE: the registry resolves it without special
    casing, so a candidate can be costed rather than argued about."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", seed)
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    b3, b2 = seed_values(seed)
    assert FormulasRegistry().elder_kads == b3, (
        "%s does not reach the registry; the fork is declared but not live"
        % seed
    )
    assert b3 == 7 + 3 * b2


def test_only_the_adopted_profile_gives_three_generations(monkeypatch):
    """THE selection argument, measured over the family rather than cited."""
    three = []
    for seed, spec in sorted(_reachable().items()):
        monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", seed)
        report = n_gen_report(seed)
        if report["equals_three"]:
            three.append((seed, spec["b3"], spec["b2"]))

    assert three == [("seed_43_joyce", 43, 12)], (
        "three generations are no longer unique to (12, 43) on the "
        "reachable family; the selection argument behind the adoption "
        "would need re-deriving. Profiles giving three: %s" % three
    )


def test_the_other_profiles_fail_structurally_not_numerically(monkeypatch):
    """0, 1 and 2 generations are refutations of a different KIND from a
    disagreement with data -- a generation count is a number of things."""
    counts = {}
    for seed in sorted(_reachable()):
        monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", seed)
        counts[seed_values(seed)[0]] = n_gen_report(seed)["n_gen"]
    assert counts == {7: 0.0, 19: 1.0, 31: 2.0, 43: 3.0}, (
        "the generation counts across the family are %s, not the measured "
        "0/1/2/3 -- re-measure before trusting the selection" % counts
    )


def test_the_off_family_seed_is_labelled_as_such():
    """seed_24 stays runnable and stays marked unreachable; keeping it is
    the point, and so is not pretending it is on the family."""
    assert PATHS["seed_24"]["reachable_by_joyce"] is False
    assert PATHS["seed_24"]["b3"] != 7 + 3 * PATHS["seed_24"]["b2"], (
        "seed_24 now satisfies b_3 = 7 + 3 b_2, which would make it "
        "reachable and overturn one of the three exclusions"
    )
