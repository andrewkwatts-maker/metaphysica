"""The option status vocabulary: active, considered, disabled.

WHY THIS EXISTS
===============
The registry used to have two states a reader could tell apart -- adopted,
and everything else -- while "everything else" mixed two different things:
a rival nobody has ruled out, and a candidate the framework has already
refuted and keeps only because a falsified claim stays on the books. The
distinction lived in a `priority` integer whose meaning was documented in a
comment, so nothing checked that an option labelled "retained because
refuted" was actually being treated as refuted.

Every test here is written to fail on a perturbation. A guard on the status
vocabulary that could not fire would be worse than none, because the
published artifact now carries the statuses and a reader would cite them.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import os

import pytest

from metaphysica.simulations.core.variants import (
    ACTIVE,
    CONSIDERED,
    DISABLED,
    FORKS,
    OPTION_STATUSES,
    VariantOption,
    describe,
    off_table_selections,
    resolve,
    selected_status,
)

_ENV_PREFIX = "METAPHYSICA_VARIANT_"


# ------------------------------------------------ the declaration is coherent


def test_every_option_carries_a_known_status():
    for fid, fork in FORKS.items():
        for option in fork.options:
            assert option.status in OPTION_STATUSES, (
                f"{fid}.{option.id}: status {option.status!r} is not one of "
                f"{list(OPTION_STATUSES)}"
            )


def test_exactly_one_active_option_per_fork():
    """ACTIVE is what runs, so two of them is an unresolvable default."""
    for fid, fork in FORKS.items():
        active = fork.options_by_status(ACTIVE)
        assert len(active) == 1, f"{fid}: {len(active)} ACTIVE options {active}"
        assert fork.default() == active[0]


def test_active_and_adopted_say_the_same_thing():
    """Two fields, one fact -- so they must never disagree."""
    for fid, fork in FORKS.items():
        for option in fork.options:
            assert (option.status == ACTIVE) == option.adopted, (
                f"{fid}.{option.id}: status={option.status!r} but "
                f"adopted={option.adopted}"
            )


def test_a_disabled_option_is_never_the_default():
    """The framework cannot run a candidate it has refuted by default."""
    for fid, fork in FORKS.items():
        assert fork.option(fork.default()).status != DISABLED, (
            f"{fid}: default {fork.default()!r} is DISABLED"
        )


def test_refuted_property_matches_the_status():
    for fork in FORKS.values():
        for option in fork.options:
            assert option.refuted == (option.status == DISABLED)


# ------------------------------------------- the declaration refuses nonsense


def test_adopted_option_cannot_be_declared_disabled():
    with pytest.raises(ValueError) as exc:
        VariantOption(
            id="x", summary="s", consequence="c",
            adopted=True, status=DISABLED,
        )
    assert "contradicts" in str(exc.value)


def test_disabled_option_cannot_claim_a_sweep_slot_ahead_of_a_rival():
    """DISABLED sweeps last; letting it declare priority 0 would put a
    refuted candidate ahead of a live one in a capped search, which is the
    defect the priority field was added to fix."""
    with pytest.raises(ValueError) as exc:
        VariantOption(
            id="x", summary="s", consequence="c",
            status=DISABLED, priority=0,
        )
    assert "DISABLED" in str(exc.value)


def test_unknown_status_is_rejected():
    with pytest.raises(ValueError) as exc:
        VariantOption(id="x", summary="s", consequence="c", status="retired")
    assert "retired" in str(exc.value)


def test_status_defaults_from_adopted_so_old_declarations_stay_valid():
    plain = VariantOption(id="x", summary="s", consequence="c")
    assert plain.status == CONSIDERED and plain.priority == 1
    chosen = VariantOption(id="y", summary="s", consequence="c", adopted=True)
    assert chosen.status == ACTIVE and chosen.priority == 0


def test_priority_is_derived_from_status_when_unset():
    refuted = VariantOption(
        id="x", summary="s", consequence="c", status=DISABLED,
    )
    assert refuted.priority == 2, "a refuted option must sweep last"


# ------------------------------------------ disabled means off-table, not gone


def test_disabled_options_stay_runnable_through_an_override():
    """A refutation nobody can re-run is folklore. The three structurally
    refuted Joyce profiles must still resolve, or the selection argument
    stops being checkable."""
    refuted = FORKS["b3_seed"].options_by_status(DISABLED)
    assert refuted, "b3_seed should retain its structurally refuted profiles"
    for option_id in refuted:
        assert resolve("b3_seed", option_id) == option_id
        assert selected_status("b3_seed", option_id) == DISABLED


def test_sweepable_excludes_only_the_disabled():
    for fid, fork in FORKS.items():
        expected = [
            o.id for o in fork.options if o.status != DISABLED
        ]
        assert fork.sweepable_ids() == expected, fid
        for option_id in fork.options_by_status(DISABLED):
            assert option_id not in fork.sweepable_ids()


def test_a_default_run_is_never_off_table():
    """Nothing refuted is selected unless someone says so explicitly."""
    assert off_table_selections() == {}


def test_off_table_detects_a_refuted_override(monkeypatch):
    """The other direction: it must actually fire, or it is decoration."""
    monkeypatch.setenv(_ENV_PREFIX + "B3_SEED", "seed_19_joyce")
    assert off_table_selections() == {"b3_seed": "seed_19_joyce"}


# ------------------------------------------------------ the published artifact


def test_describe_publishes_the_status_of_every_option():
    payload = describe()
    assert payload["schema_version"] == 2
    assert set(payload["option_statuses"]) == set(OPTION_STATUSES)
    for fid, fork in payload["forks"].items():
        for option in fork["options"]:
            assert option["status"] in OPTION_STATUSES, fid
            assert isinstance(option["priority"], int), fid
        counts = fork["status_counts"]
        assert sum(counts.values()) == len(fork["options"]), fid
        assert counts[ACTIVE] == 1, fid


def test_the_refuted_seeds_are_labelled_refuted_not_merely_deprioritised():
    """Reading the framework's own words: seed_7/19/31 fail STRUCTURALLY at
    0, 1 and 2 generations, which is a different kind of refutation from
    disagreeing with data. Whatever else changes, those three must not drift
    back to CONSIDERED, and seed_43_joyce must not drift out of ACTIVE."""
    fork = FORKS["b3_seed"]
    assert fork.options_by_status(ACTIVE) == ["seed_43_joyce"]
    assert set(fork.options_by_status(DISABLED)) == {
        "seed_7_joyce", "seed_19_joyce", "seed_31_joyce",
    }
    for option_id in fork.options_by_status(DISABLED):
        consequence = fork.option(option_id).consequence
        assert "refut" in consequence.lower() or "STRUCTURAL" in consequence, (
            f"{option_id}: DISABLED without saying what refuted it"
        )


def test_the_status_population_is_pinned_in_both_directions():
    """A count is not a check unless something can move it either way.

    This asserts the measured population exactly, so a NEW refuted option
    fails it (the inventory grew) and so does promoting one back to
    CONSIDERED (the inventory shrank). Update the numbers deliberately when
    a ruling moves an option -- that edit is the point.
    """
    measured = {s: 0 for s in OPTION_STATUSES}
    for fork in FORKS.values():
        for option in fork.options:
            measured[option.status] += 1
    assert measured == {ACTIVE: 18, CONSIDERED: 30, DISABLED: 3}, measured
    assert len(FORKS) == 18
