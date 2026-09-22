"""The fork implication matrix covers every fork, and its control is null.

WHY THIS EXISTS
---------------
`core/fork_implications.py` publishes what ONE fork deviation from the
adopted state changes. Two things have to be true for that table to mean
anything, and both are asserted here:

COVERAGE     every declared fork appears, with every one of its options. A
             matrix missing a fork is worse than no matrix, because its
             silence reads as "this fork changes nothing".

THE CONTROL  each fork's ADOPTED option gets a row too, and it must show
             zero changes -- deviating to the option already in force is a
             no-op. If it shows movement, the harness is measuring noise (a
             surviving module cache, a nondeterministic observable, an
             artifact rewritten mid-run) and every other row is suspect.

Building the whole matrix runs one process-wide evaluation per deviation, so
the expensive tests here read the EMITTED ARTIFACT when one is available and
fall back to computing a small slice directly. The slice is not a shortcut
around the check: the control is computed live, because it is the one row
whose correctness the artifact cannot vouch for.
"""
from __future__ import annotations

import json

import pytest

from metaphysica.simulations.core.fork_implications import (
    ARTIFACT_BOUND_OBSERVABLES,
    _run_under,
    build_matrix,
    implications_for,
    one_fork_deviations,
)
from metaphysica.simulations.core.preferred_path import preferred_selection
from metaphysica.simulations.core.variants import FORKS

from tests._artifact_search import artifact


def _emitted():
    path = artifact("fork_implications.json")
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ── coverage ────────────────────────────────────────────────────────────────


def test_every_fork_and_every_option_is_enumerated():
    """Coverage, computed from the fork registry rather than a frozen list."""
    rows = one_fork_deviations()
    seen = {(fork, option) for fork, option, _adopted in rows}
    expected = {(fid, o.id) for fid, fork in FORKS.items() for o in fork.options}
    assert seen == expected, (
        "matrix coverage and the fork registry disagree; missing=%s extra=%s"
        % (sorted(expected - seen), sorted(seen - expected))
    )
    assert len(FORKS) == 18, (
        "the fork count moved to %d; the register and switch_search both "
        "state it, so both need re-reading" % len(FORKS)
    )


def test_exactly_one_adopted_option_per_fork():
    """The control row must exist once per fork, not zero or twice."""
    adopted = preferred_selection()
    per_fork = {}
    for fork, option, is_adopted in one_fork_deviations():
        per_fork.setdefault(fork, []).append((option, is_adopted))
    for fork, options in per_fork.items():
        flagged = [o for o, a in options if a]
        assert len(flagged) == 1, (fork, options)
        assert flagged[0] == adopted[fork]


def test_the_ordering_is_deterministic_and_carries_no_preference():
    rows = one_fork_deviations()
    assert rows == sorted(rows, key=lambda r: (r[0], r[1]))


# ── the control ─────────────────────────────────────────────────────────────


def test_deviating_to_the_adopted_option_changes_nothing():
    """THE CONTROL, computed live for one fork with real consequences.

    `b3_seed` is chosen deliberately: it is the fork with the largest measured
    consequence (22 changes on a deviation to seed_24), so if the harness
    produced spurious movement anywhere it would show here first.
    """
    adopted = preferred_selection()
    result = implications_for("b3_seed", adopted["b3_seed"])
    assert result["n_changes"] == 0, result


def test_the_measurement_harness_restores_the_environment():
    """A deviation must not leak into the state measured after it."""
    before = _run_under(preferred_selection())
    implications_for("b3_seed", "seed_24")
    after = _run_under(preferred_selection())
    assert before["identities"] == after["identities"]
    assert before["gates"] == after["gates"]


# ── what the matrix must be able to see ─────────────────────────────────────


def test_the_seed_deviation_moves_the_identities_it_should():
    """The matrix sees the b3_seed consequence, which is its headline use."""
    result = implications_for("b3_seed", "seed_24")
    flipped = {f["identity"] for f in result["identities_flipped"]}
    # Deviating to the off-family seed HEALS the coincidences that the
    # adoption broke, and BREAKS the two relations the adoption rests on.
    assert "d_bulk_is_b3_plus_two" in flipped
    assert "reachability_b3_is_seven_plus_three_b2" in flipped
    assert "n_gen_from_b2_over_faces" in flipped
    assert len(flipped) >= 12, sorted(flipped)


def test_the_flavour_fork_shows_its_measured_cost():
    """A matrix that cannot see theta_13 move is not publishing the cost.

    Before the cost observables were added, `flavour_seed_coupling` reported
    zero changes while its headline consequence is theta_13 going from
    8.6686 to 4.8351 degrees. That silence read as "this fork is free".
    """
    result = implications_for("flavour_seed_coupling", "calibrated_24")
    moved = {m["observable"]: m for m in result["observables_moved"]}
    assert "theta_13_deg" in moved, sorted(moved)
    assert moved["theta_13_deg"]["adopted"] == pytest.approx(4.8351, abs=1e-3)
    assert moved["theta_13_deg"]["deviated"] == pytest.approx(8.6686, abs=1e-3)
    # And the axion window verdict flips with it, which is debt (a)'s cost.
    assert moved["axion_window_status"]["adopted"].startswith("ABOVE")
    assert moved["axion_window_status"]["deviated"].startswith("lies within")


def test_artifact_bound_rows_are_labelled_not_reported_as_movement():
    """"Did not move" and "could not move" are different facts.

    `free_set_size` is built from `parameters.json`, so flipping a fork in
    the environment re-reads the ADOPTED artifact under a different fork
    rather than measuring the deviated branch. It may appear to move; the
    row must say that it is not a measurement.
    """
    result = implications_for("b3_seed", "seed_24")
    for moved in result["observables_moved"]:
        if moved["observable"] in ARTIFACT_BOUND_OBSERVABLES:
            assert moved["artifact_bound"] is True
            assert "NOT A MEASUREMENT" in moved["reading"]
        else:
            assert moved["artifact_bound"] is False
            assert moved["reading"] == "live"


# ── the anti-tuning rule ────────────────────────────────────────────────────


def test_the_matrix_never_ranks_and_says_so():
    emitted = _emitted()
    payload = emitted if emitted is not None else build_matrix()
    assert payload["verdict"] == "NO_SELECTION_MADE"
    assert "never" in payload["ordering"]
    rows = [(r["fork"], r["option"]) for r in payload["rows"]]
    assert rows == sorted(rows), "rows are ordered by something other than name"


def test_the_emitted_artifact_matches_the_declared_coverage():
    """If a matrix has been published, it covers what it claims to."""
    emitted = _emitted()
    if emitted is None:
        pytest.skip("no fork_implications.json; run the generator first")
    assert emitted["n_deviations"] == len(one_fork_deviations())
    assert emitted["n_forks"] == len(FORKS)
    for row in emitted["rows"]:
        if row["is_adopted_option"]:
            assert row["n_changes"] == 0, (
                "the published matrix has a non-null adopted column for %s; "
                "every other row in it is suspect" % row["fork"]
            )
