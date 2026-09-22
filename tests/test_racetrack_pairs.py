"""The racetrack pair enumeration is costed, ordered by name, and adopts nothing.

WHY THIS EXISTS
---------------
`racetrack_pairs` runs the declared racetrack solver over every ordered pair
from the derived integer menu. That is the shape of computation that turns
into a parameter fit if nobody watches it: 28 pairs, each producing a Re(T),
against a quantity with six incumbent values already in the codebase. Finding
a pair whose minimum lands near an incumbent would be unsurprising and would
mean nothing.

So the properties asserted here are mostly about what the module must REFUSE
to do -- rank, select, or let its trials factor go unpublished -- and two
cross-checks that establish it is solving the right equations at all.

THE TWO CROSS-CHECKS, AND WHY THEY MATTER MOST
----------------------------------------------
The enumeration substitutes exponents into `racetrack_vacuum`'s own solver.
If the substitution were wrong, every row would be plausible and all of them
false. Two rows have independently recorded answers:

    (24, 26)  Re(T) = 37.852731  the seed_24 branch's recorded minimum
    (26, 43)  Re(T) = 10.2085    the ordering-restored control that proved
                                 the solver innocent when the adopted path's
                                 vacuum vanished

Both were measured elsewhere, before this module existed. Reproducing them is
what makes the other 26 pairs worth reading.
"""
from __future__ import annotations

import math

import pytest

from metaphysica.simulations.PM.cosmology.racetrack_pairs import (
    DERIVED_INTEGER_MENU,
    KAHLER_SLOPES,
    enumerate_pairs,
    ordered_pairs,
    solve_pair,
)


# The enumeration is 28 solves per slope at roughly 0.8s each, and five tests
# below need it. Built ONCE per module rather than per test: re-running it
# five times added about four minutes to every full-suite run, which is a real
# cost paid on every CI invocation for no additional coverage.
@pytest.fixture(scope="module")
def single_slope():
    return enumerate_pairs(slopes=(3,))


# ── the cross-checks ────────────────────────────────────────────────────────


def test_the_pair_24_26_reproduces_the_seed_24_recorded_minimum():
    """(24, 26) IS the seed_24 racetrack, so it must give its recorded value."""
    result = solve_pair(24, 26, 3)
    assert result["re_t_minimum"] == pytest.approx(37.852731, abs=1e-3), result
    assert result["vacuum_energy_sign"] == "AdS"
    assert result["n_susy_roots"] >= 1


def test_the_pair_26_43_reproduces_the_ordering_restored_control():
    """(26, 43) is the a<->b swap that proved the solver innocent.

    When the adopted path's vacuum vanished, swapping the exponents brought a
    SUSY AdS minimum back at Re(T) = 10.2085 with a dS saddle at 15.6529. That
    control was recorded on the register before this module existed.
    """
    result = solve_pair(26, 43, 3)
    assert result["re_t_minimum"] == pytest.approx(10.2085, abs=1e-3), result
    assert result["n_minima"] == 1


def test_the_adopted_exponents_are_not_in_the_enumeration():
    """The adopted path has a < b, so it is not an ordered pair here.

    Stated as a test because the absence is easy to misread as an omission.
    b_3 = 43 against D_bulk = 26 means a = 2pi/43 < b = 2pi/26: the ordering
    is LOST, which is the finding this enumeration exists downstream of.
    """
    assert (43, 26) not in ordered_pairs()
    assert (26, 43) in ordered_pairs()
    assert 2.0 * math.pi / 43 < 2.0 * math.pi / 26


# ── the enumeration's own discipline ────────────────────────────────────────


def test_every_ordered_pair_restores_the_ordering_by_construction():
    for n1, n2 in ordered_pairs():
        assert n1 < n2
        assert 2.0 * math.pi / n1 > 2.0 * math.pi / n2


def test_the_pair_list_is_complete_and_deterministic():
    menu = sorted(n for n, _why in DERIVED_INTEGER_MENU)
    pairs = ordered_pairs()
    assert len(pairs) == len(menu) * (len(menu) - 1) // 2 == 28
    assert pairs == sorted(pairs)


def test_every_menu_integer_says_what_it_counts():
    """The A4 bar, applied to the menu itself.

    An integer on this menu without a stated referent is an unearned
    coincidence waiting to be found, and widening the menu silently is how a
    trials factor gets understated.
    """
    for n, why in DERIVED_INTEGER_MENU:
        assert isinstance(n, int) and n > 0
        assert why and len(why) > 15, (n, why)


def test_the_trials_factor_is_published_as_a_field(single_slope):
    """An enumeration whose cost is not stated is a fit wearing a table."""
    payload = single_slope
    assert payload["trials_factor"] == len(ordered_pairs()) * 1
    assert "trials_factor" in payload
    assert "means nothing" in payload["trials_note"]


def test_the_prefactors_are_held_fixed_across_pairs(single_slope):
    """B/A is the one continuous knob; letting it float makes this a fit."""
    payload = single_slope
    assert payload["held_fixed"]["A"] == 1.0
    assert payload["held_fixed"]["B"] == -0.5


def test_the_enumeration_adopts_nothing_and_ranks_nothing(single_slope):
    payload = single_slope
    assert payload["verdict"] == "NO_SELECTION_MADE"
    assert payload["adopted"] is None
    assert "never by agreement" in payload["ordering"]
    names = [row["pair"] for row in payload["rows"]]
    assert names == [r["pair"] for r in sorted(
        payload["rows"], key=lambda r: (r["N1"], r["N2"]))]


def test_no_row_carries_a_comparison_to_an_experimental_anchor(single_slope):
    """The rows describe structure; they never score it against anything."""
    payload = single_slope
    banned = ("sigma", "agreement", "best", "preferred", "matches", "closest")
    for row in payload["rows"]:
        blob = str(row).lower()
        for word in banned:
            assert word not in blob, (row["pair"], word)


# ── the structural reading ──────────────────────────────────────────────────


def test_no_pair_on_the_derived_menu_gives_a_de_sitter_minimum(single_slope):
    """A structural result, measured across all 28 pairs at n = 3.

    Every pair that restores the ordering produces an AdS minimum. Nothing on
    the derived menu uplifts the vacuum to dS, so the cosmological-constant
    problem is not solved by a different exponent choice -- which is worth
    recording because "try other exponents" is the obvious next thought after
    the adopted vacuum vanished.
    """
    payload = single_slope
    signs = {row["by_slope"]["n_3"].get("vacuum_energy_sign")
             for row in payload["rows"]}
    assert "dS" not in signs, signs
    assert "AdS" in signs


def test_the_slopes_run_are_the_declared_ones():
    assert KAHLER_SLOPES == (3, 7)


# ── the generator actually generates ────────────────────────────────────────


def test_main_writes_the_artifact_not_just_the_table(tmp_path, monkeypatch):
    """A build step whose evidence is on stdout has not produced anything.

    Wired into the build, `main()` called `enumerate_pairs()` rather than
    `write_report()`. It printed all 56 rows, the build reported OK in 31.2s,
    and no file was written. Nothing in the build summary could show that:
    the step exited 0 and said a lot. Only looking for the artifact found it.
    """
    import json

    from metaphysica.simulations.PM.cosmology import racetrack_pairs

    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    assert racetrack_pairs.main() == 0

    written = tmp_path / "AutoGenerated" / "racetrack_pairs.json"
    assert written.is_file(), (
        "racetrack_pairs.main() produced no artifact; a generator wired into "
        "the build must write, not print"
    )
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["n_pairs"] == 28
    assert payload["trials_factor"] == 56
    assert payload["verdict"] == "NO_SELECTION_MADE"
