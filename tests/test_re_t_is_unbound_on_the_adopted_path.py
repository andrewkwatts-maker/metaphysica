"""Re(T) supplies no derived value on the adopted seed, and nothing may
pretend otherwise.

The racetrack vacuum was DELETED by the b3_seed adoption (2026-09-22):
a = 2*pi/43 < b = 2*pi/26 breaks the ordering the mechanism is, and the
measured state is 0 stationary points, 0 SUSY roots, monotone V. So on this
path Re(T) is a free boundary input awaiting the re_t_adoption ruling, and
this file is the guard Gemini's review described before it existed: if any
part of the pipeline starts treating Re(T) as a DERIVED racetrack vacuum on
the adopted branch -- or if a vacuum quietly reappears without a documented
mechanism -- the build fails here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _adopted_branch(monkeypatch):
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)


def test_the_ledger_says_the_racetrack_supplies_nothing_here():
    from metaphysica.simulations.core.closure_ledger import LAYERS

    note = LAYERS["METRIC_DEPENDENT"]["note"]
    assert "racetrack supplies" in note and "NO value" in note
    assert "unbound-by-racetrack" in note
    assert "re_t_adoption" in note, (
        "the note must name the OPEN ruling that retires it"
    )


def test_re_t_stays_a_free_metric_dependent_row():
    from metaphysica.simulations.core.closure_ledger import closure_report

    rows = {r["name"]: r for r in closure_report()["ledger"]}
    if "cosmology.racetrack_Re_T" not in rows:
        pytest.skip("racetrack_Re_T not in the current free set snapshot")
    assert rows["cosmology.racetrack_Re_T"]["layer"] == "METRIC_DEPENDENT", (
        "Re(T) left the metric layer; if it became DERIVED on the adopted "
        "path, some module is harvesting a vacuum that does not exist"
    )


def test_no_vacuum_quietly_reappears_on_the_adopted_branch():
    """The defended absence: a returning minimum without a documented new
    mechanism is a regression of the record, not a discovery."""
    from metaphysica.simulations.PM.cosmology.racetrack_vacuum import (
        vacuum_report,
    )

    report = vacuum_report()
    assert report["declared"]["ordering_a_gt_b"] is False, (
        "a > b again: either the seed moved (a ruling) or a frozen exponent "
        "returned (a defect); both must be looked at, not absorbed"
    )
    for name, branch in report["branches"].items():
        assert not branch.get("minima"), (
            "branch %r reports a minimum on the adopted seed with a < b; a "
            "runaway potential has no interior minimum, so either a new "
            "stabilisation mechanism landed (document it on the register "
            "and retire this guard deliberately) or the solver changed"
            % name
        )


def test_the_artifact_does_not_carry_a_derived_racetrack_re_t():
    """The published parameters may carry Re(T) rows as inputs/incumbents,
    never as a racetrack-DERIVED value while the vacuum is absent."""
    import json
    from pathlib import Path

    from metaphysica.simulations.core.parameter_artifact import params_source

    src = params_source()
    params = src.get("params") or {}
    if not params:
        pytest.skip("no built parameters.json available to audit")
    offenders = []
    for name, row in params.items():
        if "racetrack" not in name.lower() and "re_t" not in name.lower():
            continue
        if not isinstance(row, dict):
            continue
        source = str(row.get("source", ""))
        status = str(row.get("status", ""))
        if status == "DERIVED" and "racetrack" in source.lower():
            offenders.append((name, source))
    assert not offenders, (
        "rows harvested as racetrack-DERIVED while the adopted path has no "
        "racetrack vacuum: %s -- the artifact was built before the guard or "
        "a module is publishing a vacuum that does not exist" % offenders
    )
