"""Does a discrete ansatz freeze a metric-dependent parameter? Measured: no.

MEASURED 2026-09-22: **zero** candidate edges from a DISCRETE_CHOICE row to a
METRIC_DEPENDENT one. Not "candidates that did not survive scrutiny" -- no
module in the tree reads a discrete-ansatz row's name alongside a
metric-dependent row's name at all. The continuous count stays at 22
(7 METRIC_DEPENDENT + 13 FLAVOUR + 2 FLUX_DEPENDENT).

All 20 candidate edges that DO exist run from EXPERIMENTAL anchors: 18 to
METRIC_DEPENDENT rows and 2 to FLUX_DEPENDENT ones. Those are not a tightening
even if one were demonstrated -- an anchor determining a modulus is a FIT, not
a derivation. They are recorded because a measured constant being read in the
same module that computes a modulus deserves someone's attention.

A measured null is worth as much as a reduction, and this one comes with the
condition that would change it.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.core import ansatz_dependency_graph as adg


def test_the_layers_are_read_live_not_tabulated():
    rows = adg.rows_by_layer()
    assert rows.get("METRIC_DEPENDENT")
    assert rows.get("DISCRETE_CHOICE")
    assert rows.get("EXPERIMENTAL")
    assert "UNCLASSIFIED" not in rows, (
        "an unclassified row has appeared, so the graph's source and target "
        "sets no longer cover the free set"
    )


def test_the_continuous_count_is_twenty_two():
    report = adg.dependency_report()
    assert report["continuous_count"] == 22
    assert report["continuous_breakdown"] == {
        "METRIC_DEPENDENT": 7, "FLAVOUR": 13, "FLUX_DEPENDENT": 2}
    assert report["n_non_knobs"] == 15


def test_row_names_are_matched_whole():
    """`geometry.theta_1` must not match `geometry.theta_13`.

    A prefix match would invent edges, and inventing edges in a module whose
    output is a null result would turn the null into a false positive.
    """
    texts = {"a.py": "geometry.theta_13 = 8.54",
             "b.py": "geometry.theta_1 = 1.0"}
    assert adg.modules_mentioning("geometry.theta_13", texts) == ["a.py"]
    assert adg.modules_mentioning("geometry.theta_1", texts) == ["b.py"]


def test_the_tracer_finds_co_occurrence_when_it_is_there():
    """The detector must be able to report an edge, or the null is empty."""
    texts = {"m.py": "yukawa.best_scaling and cosmology.racetrack_Re_T"}
    assert adg.modules_mentioning("yukawa.best_scaling", texts) == ["m.py"]
    assert adg.modules_mentioning("cosmology.racetrack_Re_T", texts) == ["m.py"]


def test_every_row_is_mentioned_somewhere_in_the_tree():
    """A row no module mentions cannot be traced, so it must be reported."""
    graph = adg.candidate_edges()
    assert graph["rows_no_module_mentions"] == [], (
        "these free-set rows appear in no module, so no edge involving them "
        "could ever be traced: %s" % graph["rows_no_module_mentions"]
    )


def test_no_discrete_ansatz_reaches_a_metric_dependent_row():
    """The measured null, and the headline of this file."""
    report = adg.dependency_report()
    assert report["ansatz_to_metric_edges"] == [], (
        "a DISCRETE_CHOICE row is now read alongside a METRIC_DEPENDENT one: "
        "%s. That is a candidate tightening and needs a reading, not a passing "
        "test." % report["ansatz_to_metric_edges"]
    )
    assert report["demonstrated_freezings"] == []
    assert report["tightening"] == 0


def test_the_edges_that_exist_all_come_from_anchors():
    graph = adg.candidate_edges()
    assert graph["n_candidate_edges"] > 0, (
        "no edge at all was traced, which means the tracer is broken rather "
        "than the graph being empty"
    )
    assert all(e["mechanism"] == "EXPERIMENTAL_ANCHOR" for e in graph["edges"])


def test_an_anchor_edge_is_not_counted_as_a_tightening():
    report = adg.dependency_report()
    assert "FIT" in report["the_anchor_edges_are_not_good_news"]
    assert report["tightening"] == 0


def test_the_two_mechanisms_are_kept_distinguishable():
    """Flux freezing and ansatz freezing are different edges into the same 7."""
    report = adg.dependency_report()
    assert "flux" in report["kept_distinct_from_flux"].lower()
    mechanisms = {e["mechanism"] for e in report["graph"]["edges"]}
    assert mechanisms <= {"DISCRETE_ANSATZ", "EXPERIMENTAL_ANCHOR"}


def test_the_null_states_what_would_overturn_it():
    report = adg.dependency_report()
    assert report["how_this_could_change"], (
        "a null without a falsification condition is not a result"
    )
    assert "variants" in report["how_this_could_change"]


def test_an_edge_is_labelled_a_candidate_and_never_a_dependency():
    graph = adg.candidate_edges()
    assert all(e["strength"] == "CANDIDATE" for e in graph["edges"])
    assert "NECESSARY condition" in graph["edge_meaning"]


def test_the_a4_bar_is_stated():
    report = adg.dependency_report()
    assert "LEDGER ENTRIES" in report["a4_bar"]
    assert "CO-OCCURRENCES" in report["a4_bar"]
