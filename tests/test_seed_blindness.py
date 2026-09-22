"""A conclusion drawn from a frozen value is a bug report, not a result.

Four seed-blind writers were found one at a time by four different
accidents. This pins the detector that searches for the CLASS, and the
re-assessment it forced: each headline cost of the b3_seed adoption was
put through it, and one did not survive (the axion ceiling breach is a
prediction about a pending fix, not a published reading).

The run is expensive -- two full pipeline executions in fresh subprocesses,
because the registry is a per-process singleton and in-process flipping
would make every row look frozen. Marked slow; the cheap structural tests
run always.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.core.seed_blindness import (
    classify_rows,
    seed_blindness_report,
)

#: MEASURED 2026-09-22: 786 rows compared, 135 FROZEN_CLAIM. A ceiling, not
#: a target -- many FROZEN_CLAIMs are correct (geometry.D_bulk and the other
#: disentangled bulk-24s are SUPPOSED to stay put). It may fall, never rise.
_FROZEN_CEILING = 135


def test_the_classifier_separates_the_three_cases():
    """Cheap and structural: it must not put everything in one bucket."""
    at_24 = {
        "moves": {"value": 24, "claims_b3": True},
        "frozen_but_claims": {"value": 7.0, "claims_b3": True},
        "static_and_silent": {"value": 1.0, "claims_b3": False},
    }
    at_43 = {
        "moves": {"value": 43, "claims_b3": True},
        "frozen_but_claims": {"value": 7.0, "claims_b3": True},
        "static_and_silent": {"value": 1.0, "claims_b3": False},
    }
    out = classify_rows(at_24, at_43)
    assert out["MOVED"] == ["moves"]
    assert out["FROZEN_CLAIM"] == ["frozen_but_claims"]
    assert out["STATIC"] == ["static_and_silent"]


def test_a_row_that_moves_is_never_called_frozen():
    """The detector's one-way guarantee."""
    out = classify_rows(
        {"x": {"value": 1.0, "claims_b3": True}},
        {"x": {"value": 2.0, "claims_b3": True}},
    )
    assert out["FROZEN_CLAIM"] == []
    assert out["MOVED"] == ["x"]


@pytest.mark.slow
def test_the_frozen_claim_count_does_not_rise():
    report = seed_blindness_report()
    if not report.get("available"):
        pytest.skip("harvest unavailable: %s" % str(report.get("reason"))[:120])
    assert report["n_frozen_claim"] <= _FROZEN_CEILING, (
        "rows claiming b_3 but not moving rose to %d, above the measured "
        "ceiling of %d. A new frozen claim is a seed-blind writer until "
        "someone reads it and says otherwise: %s"
        % (report["n_frozen_claim"], _FROZEN_CEILING,
           report["frozen_claims"][-8:])
    )


@pytest.mark.slow
def test_the_seed_actually_reaches_a_large_part_of_the_pipeline():
    """A detector over a pipeline that ignores the seed would be vacuous.

    MEASURED 2026-09-22: 182 of 786 rows move. If this collapses, the fork
    stopped propagating and every 'cost of the adoption' on the register
    needs re-deriving before it can be believed.
    """
    report = seed_blindness_report()
    if not report.get("available"):
        pytest.skip("harvest unavailable: %s" % str(report.get("reason"))[:120])
    assert report["n_moved"] >= 150, (
        "only %d rows move with the seed (was 182); the fork's reach "
        "shrank and the adoption's recorded costs must be re-measured"
        % report["n_moved"]
    )


@pytest.mark.slow
def test_the_confirmed_costs_really_move():
    """The re-assessment, pinned: eta_B and m_higgs_local are PHYSICS.

    Both were in doubt for the same reason the axion claim failed -- a
    value can look like a cost while being frozen. These two move; the
    axion status string does not, and that asymmetry is the finding.
    """
    from metaphysica.simulations.core.seed_blindness import rows_under_seed

    at_24 = rows_under_seed("seed_24")
    at_43 = rows_under_seed("seed_43_joyce")
    if "error" in at_24 or "error" in at_43:
        pytest.skip("harvest unavailable")

    for name in ("cosmology.eta_B", "higgs.m_higgs_local"):
        if name not in at_24 or name not in at_43:
            continue
        assert at_24[name]["value"] != at_43[name]["value"], (
            "%s no longer moves with the seed, so the cost recorded for it "
            "on the register is a frozen value wearing a result" % name
        )

    frozen_prose = "particle.axion_photon_coupling_status"
    if frozen_prose in at_24 and frozen_prose in at_43:
        assert at_24[frozen_prose]["value"] == at_43[frozen_prose]["value"], (
            "the axion status string now MOVES with the seed -- debt (a) "
            "closed, so the ceiling breach became a published cost and the "
            "register's correction should be updated to say so"
        )
