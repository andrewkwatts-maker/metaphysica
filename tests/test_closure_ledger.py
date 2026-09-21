"""Can geometry close the model? No -- and the reason is structural.

Of the 37 surviving free-set rows, ZERO are reachable from topology. That is not
a shortfall of effort. The topological layer was already closed this campaign --
b_2 and b_3 stopped being inputs when n_gen = rank(Gamma) = 3 selected (12, 43)
out of four enumerated candidates -- and those rows are absent from the free set
precisely BECAUSE they closed. What remains sits in layers a G2 compactification
structurally cannot supply from topology: flux quanta, zero-mode overlaps,
moduli VEVs, and measured anchors that were never model outputs.

This file pins the boundary so "close the model geometrically" is answered with
a classification rather than an aspiration.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.core.closure_ledger import (
    LAYERS,
    classify_row,
    closure_ledger,
    closure_report,
)


@pytest.fixture(scope="module")
def report():
    return closure_report()


def test_every_free_row_is_classified(report):
    assert report["n_free"] == len(report["ledger"])
    assert report["n_free"] > 0
    for row in report["ledger"]:
        assert row["layer"] in LAYERS or row["layer"] == "UNCLASSIFIED"


def test_nothing_is_left_unclassified(report):
    stragglers = [r["name"] for r in report["ledger"]
                  if r["layer"] == "UNCLASSIFIED"]
    assert not stragglers, (
        "unclassified rows need a reading, not a default: %s" % stragglers
    )


def test_no_free_row_is_reachable_from_topology_today(report):
    """The headline. If this ever becomes non-zero, something real closed."""
    assert report["closable_by_topology_today"] == 0, (
        "a free row is now topologically reachable, which would be a genuine "
        "closure and must be recorded rather than absorbed: %s"
        % [r["name"] for r in report["ledger"] if r["layer"] == "TOPOLOGICAL"]
    )


def test_the_layers_partition_the_free_set(report):
    total = sum(report["by_layer"].values())
    assert total == report["n_free"]
    assert (report["closable_by_topology_today"]
            + report["partially_open_via_the_glued_metric"]
            + report["blocked_on_objects_the_framework_lacks"]
            + report["not_continuous_knobs_at_all"]) == report["n_free"]


def test_gauge_couplings_are_not_claimed_as_topological(report):
    """A G2 compactification does not fix a coupling from Betti numbers."""
    rows = {r["name"]: r for r in report["ledger"]}
    for name in ("geometry.alpha_inverse",):
        if name in rows:
            assert rows[name]["layer"] == "FLUX_DEPENDENT", rows[name]


def test_mixing_angles_are_flavour_not_topology(report):
    rows = {r["name"]: r for r in report["ledger"]}
    for name in ("geometry.J_CKM", "ckm.rho_wolfenstein"):
        if name in rows:
            assert rows[name]["layer"] == "FLAVOUR", rows[name]


def test_moduli_vevs_sit_behind_the_metric(report):
    rows = {r["name"]: r for r in report["ledger"]}
    if "cosmology.racetrack_Re_T" in rows:
        assert rows["cosmology.racetrack_Re_T"]["layer"] == "METRIC_DEPENDENT"


def test_the_metric_layer_is_marked_only_partially_available():
    """K_IJ has values, but leading-order-in-t only."""
    layer = LAYERS["METRIC_DEPENDENT"]
    assert layer["available"] == "PARTIAL"
    assert "asymptotic" in layer["note"]


def test_flux_is_marked_as_not_supplied_by_geometry():
    layer = LAYERS["FLUX_DEPENDENT"]
    assert layer["available"] is False
    assert "no geometry on Y_7 supplies them" in layer["note"]


def test_the_rules_are_auditable_not_opinions(report):
    """Every classification carries the rule that produced it."""
    for row in report["ledger"]:
        assert row["why"], row
        assert len(row["why"]) > 15, row


def test_classification_responds_to_the_row():
    """A classifier ignoring its input would put everything in one layer."""
    a = classify_row("geometry.alpha_inverse", {"status": "CALIBRATED",
                                                "role": "LOAD_BEARING_INPUT"})
    b = classify_row("cosmology.racetrack_Re_T", {"status": "CALIBRATED",
                                                  "role": "UNRESOLVED"})
    c = classify_row("yukawa.best_scaling", {"status": "ANSATZ",
                                             "role": "UNRESOLVED"})
    assert len({a["layer"], b["layer"], c["layer"]}) == 3


def test_what_geometry_did_close_is_recorded(report):
    """The reduction that DID happen must not be lost in the negative result."""
    text = report["what_geometry_DID_close"]
    assert "rank(Gamma)" in text
    assert "(12, 43)" in text
    assert "real reduction" in text


def test_the_answer_states_the_structural_reason(report):
    answer = report["the_answer"]
    assert "cannot be closed by geometry alone" in answer
    assert "structural rather than incomplete work" in answer
    assert "flux quanta" in answer


def test_the_report_declares_what_it_counts(report):
    assert "Not a claim that any row is closable" in report["counts"]
