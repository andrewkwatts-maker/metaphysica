"""The free-parameter count may not rest on an artifact of unknown seed.

WHY
===
`free_set.build_free_set` is where the framework's headline claim lives: how
many independent knobs it has. Every b_3-arithmetic removal in it is verified
against the ARTIFACT's b_3, not the live fork's, so the count is only the
adopted path's count if the artifact was built on the adopted path.

Two defects made that unenforceable, both found 2026-09-26.

1. `removals_resting_on_stale_b3` fired only when provenance was
   `consistent is False`. An artifact carrying NO seed at all -- which is what
   the bundled snapshot does, having no `particle.b3` row -- gives
   `consistent is None`, and took the same path as one verified to MATCH. So
   unknown provenance was reported exactly like agreement, and the module's own
   note already said an unknown read is "a reportable state, not a pass".

2. The removal of `cosmology.wa_thawing` sat INSIDE an `except ImportError:`
   branch, after its bare `pass` (from f289f94 until 2026-09-26). It therefore
   ran only when the b3_path import failed. On every ordinary run the row
   stayed in the free set, so the framework counted the RETIRED
   -4/sqrt(b_3) artefact as one of its own free parameters -- while the
   module's docstring listed that removal as one of its three verified
   reductions. It also left the stale-b_3 guard with almost nothing to guard,
   since this is one of only two removals marked `uses_b3`.

Each test here is written to fail on a perturbation, and the counts are pinned
so they cannot move silently in either direction.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import copy
import json
import math
import pathlib

import pytest

from metaphysica.simulations.core.free_set import build_free_set

_BUNDLED = (
    pathlib.Path(__file__).resolve().parents[1]
    / "src" / "metaphysica" / "data" / "parameters.json"
)


@pytest.fixture(scope="module")
def bundled():
    return json.loads(_BUNDLED.read_text(encoding="utf-8"))["parameters"]


def _seeded(params, b3):
    """The same snapshot, given a seed and a consistent retired-wa value."""
    out = copy.deepcopy(params)
    out["particle.b3"] = {"value": b3}
    out["cosmology.wa_thawing"] = {"value": -4.0 / math.sqrt(b3)}
    return out


# ------------------------------------------------- unknown seed is not a pass


def test_a_seedless_artifact_may_not_claim_the_live_forks_count(bundled):
    fs = build_free_set(params=bundled)
    assert fs["artifact_seed_provenance"]["artifact_b3"] is None, (
        "the bundled snapshot gained a particle.b3 row -- if it is now built "
        "on the adopted path, update this test and the caveat it checks"
    )
    assert fs["count_is_the_live_forks"] is False
    assert "no seed" in fs["count_caveat"]


def test_an_off_path_artifact_may_not_claim_the_live_forks_count(bundled):
    fs = build_free_set(params=_seeded(bundled, 24))
    assert fs["count_is_the_live_forks"] is False
    assert "24" in fs["count_caveat"] and "43" in fs["count_caveat"]


def test_an_adopted_seed_artifact_may_claim_it(bundled):
    """The other direction: the flag must be able to come out True, or it is
    a refusal dressed as a check."""
    fs = build_free_set(params=_seeded(bundled, 43))
    assert fs["count_is_the_live_forks"] is True
    assert fs["count_caveat"] == ""


# ------------------------------------------ the stale-b_3 guard actually fires


def test_the_stale_b3_guard_names_the_b3_dependent_removals(bundled):
    """It reported nothing at all before both fixes -- the condition excluded
    unknown provenance, and one of the two uses_b3 removals was dead code."""
    fs = build_free_set(params=_seeded(bundled, 24))
    resting = set(fs["removals_resting_on_stale_b3"])
    assert resting == {"algebra.freudenthal_quartic", "cosmology.wa_thawing"}, (
        "the b_3-dependent removals on an off-path artifact changed: %s"
        % sorted(resting)
    )


def test_nothing_rests_on_a_stale_b3_when_the_seed_is_the_adopted_one(bundled):
    fs = build_free_set(params=_seeded(bundled, 43))
    assert fs["removals_resting_on_stale_b3"] == []


# ------------------------------------------------ the retired row is removed


def test_the_retired_wa_formula_is_removed_on_an_ordinary_run(bundled):
    """The dead-code defect. -4/sqrt(b_3) is RETIRED on the register, and
    removing the row records that a legacy artefact of a falsified derivation
    carries no independent content. It is not a revival."""
    fs = build_free_set(params=_seeded(bundled, 43))
    assert "cosmology.wa_thawing" in fs["removed"], (
        "the retired -4/sqrt(b_3) row is being counted as a free parameter"
    )
    record = fs["removed"]["cosmology.wa_thawing"]
    assert record["reason"] == "DERIVED_ARITHMETIC"
    assert "RETIRED" in record["detail"]


def test_a_seedless_artifact_declines_the_removal_rather_than_crashing(bundled):
    """b3 is None there, and math.sqrt(None) raises. Declining to remove is
    the correct outcome; an exception would take the whole report down."""
    fs = build_free_set(params=bundled)
    assert "cosmology.wa_thawing" not in fs["removed"]
    assert "cosmology.wa_thawing" in fs["free_set"]


# --------------------------------------------------------- the counts, pinned


def test_the_free_parameter_counts_are_pinned_in_both_directions(bundled):
    """67 ledger rows, and what a reseeded probe can and cannot establish.

    IMPORTANT, and the reason this test does not pin an "adopted-path free
    parameter count": `_seeded` sets `particle.b3` on a snapshot whose OTHER
    rows were computed at b_3 = 24. That artifact is internally INCONSISTENT
    by construction -- exactly the shared-artifact trap `free_set` documents --
    and `algebra.freudenthal_quartic` duly goes CLAIMED_UNVERIFIED under it,
    because 16 (43/27)^2 does not reproduce a value computed from 16 (24/27)^2.

    That is the module behaving correctly, and it is why the honest adopted
    count needs a genuine build at the adopted seed rather than a reseeded
    probe. What the probe DOES establish is the provenance plumbing and the
    b_3-guarded removals, pinned above and below.
    """
    seedless = build_free_set(params=bundled)
    adopted = build_free_set(params=_seeded(bundled, 43))
    off_path = build_free_set(params=_seeded(bundled, 24))

    assert seedless["ledger_rows"] == 67
    assert seedless["free_set_size"] == 39, (
        "the seedless reduction moved; this is the number a bare process "
        "reports, and it is NOT the adopted path's count"
    )

    # The reseeded probes: the retired-wa removal lands in both, so the
    # dead-code fix is what these numbers demonstrate.
    assert (adopted["free_set_size"], adopted["removed_count"]) == (38, 29)
    assert off_path["free_set_size"] == 37

    # And the probe's own inconsistency is asserted rather than hidden, so
    # nobody reads 38 as a verified adopted-path count.
    assert "algebra.freudenthal_quartic" in adopted["unverified_claims"], (
        "the reseeded probe stopped being internally inconsistent -- if the "
        "bundled snapshot is now built at the adopted seed, this test and the "
        "count it refuses to pin should be rewritten against the real build"
    )
    assert adopted["unverified_claims"]["algebra.freudenthal_quartic"][
        "reason"] == "CLAIMED_UNVERIFIED"
    # A CLAIMED removal must still count against the total: it stays in.
    assert "algebra.freudenthal_quartic" in adopted["free_set"]


def test_an_unverified_reduction_still_counts_against_the_total(bundled):
    """The module's central rule: nothing leaves the free set on assertion."""
    adopted = build_free_set(params=_seeded(bundled, 43))
    for name in adopted["unverified_claims"]:
        assert name in adopted["free_set"], (
            "%s was recorded as an unverified claim AND removed from the free "
            "set; a reduction with no check may not reduce the count" % name
        )
