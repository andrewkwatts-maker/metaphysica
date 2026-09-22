"""Does a discrete ansatz freeze a metric-dependent parameter? Measured: no.

RE-MEASURED 2026-09-22 after the b3_seed adoption, because the ruling moved
the free set underneath this graph. ``cosmology.wa_thawing`` used to be
REMOVED by free_set's own check -- it matched -4/sqrt(b_3) exactly at
b_3 = 24 -- and at b_3 = 43 that formula is retired, so the row survives as a
39th free row and is classified METRIC_DEPENDENT. The continuous count is
therefore 23 (8 METRIC_DEPENDENT + 13 FLAVOUR + 2 FLUX_DEPENDENT), up from
22, and 29 candidate edges are traced where 20 were before.

The headline survives, but it is no longer a bare zero and must not be
reported as one. TWO candidate DISCRETE_CHOICE -> METRIC_DEPENDENT edges now
exist, ``algebra.freudenthal_quartic`` and ``yukawa.best_scaling``, both
pointing at ``cosmology.wa_thawing``, and the reading a candidate edge is
owed is this: the single module they share is
``simulations/core/free_set.py``, which is the free-set BOOKKEEPING module.
It names those rows in its removal checks -- the wa_thawing check against
-4/sqrt(b_3) sits a few lines from the ``yukawa.best_scaling == "phi"``
branch and the ``algebra.freudenthal_quartic`` check -- so the co-occurrence
is the ledger listing its own candidates, not a physics module computing a
modulus from a discrete choice. ``tightening`` is still 0 and
``demonstrated_freezings`` is still empty. The tests below pin the two edges
by name and by shared module, so a THIRD edge, or either of these appearing
in a module that actually computes something, fails this file.

The other 27 candidate edges run from EXPERIMENTAL anchors: 25 to
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


def test_the_continuous_count_is_twenty_three():
    """Measured 2026-09-22, b3_seed adoption: 22 -> 23.

    cosmology.wa_thawing stopped being removable when -4/sqrt(b_3) stopped
    matching at b_3 = 43, so it survives into the free set and lands in
    METRIC_DEPENDENT, taking that layer from 7 to 8. n_non_knobs moved
    15 -> 16 with the DISCRETE_CHOICE row that arrived alongside it.
    """
    report = adg.dependency_report()
    assert report["continuous_count"] == 23
    assert report["continuous_breakdown"] == {
        "METRIC_DEPENDENT": 8, "FLAVOUR": 13, "FLUX_DEPENDENT": 2}
    assert report["n_non_knobs"] == 16


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
    """The measured null, and the headline of this file.

    Measured 2026-09-22, b3_seed adoption: the null is no longer a bare zero.
    Exactly two candidate edges exist, both into cosmology.wa_thawing, both
    sharing only simulations/core/free_set.py -- the free-set bookkeeping
    module, whose removal checks name the discrete rows and the metric row a
    few lines apart. Each is pinned by name and by shared module, so a third
    edge, a different source, or a shared module that actually computes
    something fails here and gets the reading it is owed.
    """
    report = adg.dependency_report()
    edges = report["ansatz_to_metric_edges"]
    assert {(e["source"], e["target"]) for e in edges} == {
        ("algebra.freudenthal_quartic", "cosmology.wa_thawing"),
        ("yukawa.best_scaling", "cosmology.wa_thawing"),
    }, (
        "the DISCRETE_CHOICE -> METRIC_DEPENDENT candidate edges are no "
        "longer the two measured bookkeeping co-occurrences: %s. That is a "
        "candidate tightening and needs a reading, not a passing test."
        % edges
    )
    for edge in edges:
        assert edge["shared_modules"] == ["simulations/core/free_set.py"], (
            "%s -> %s is now co-read in %s, which is not the free-set "
            "ledger; a discrete ansatz sharing a COMPUTING module with a "
            "modulus is the candidate tightening this file exists to catch"
            % (edge["source"], edge["target"], edge["shared_modules"])
        )
        assert edge["strength"] == "CANDIDATE"
    assert report["metric_rows_with_a_candidate_ansatz_edge"] == [
        "cosmology.wa_thawing"
    ]
    assert report["demonstrated_freezings"] == []
    assert report["tightening"] == 0


def test_every_edge_but_the_two_bookkeeping_ones_comes_from_an_anchor():
    """Measured 2026-09-22, b3_seed adoption: 29 edges, 27 of them anchors.

    Before the ruling every traced edge was an EXPERIMENTAL_ANCHOR one. The
    two exceptions are the free_set.py co-occurrences read in
    test_no_discrete_ansatz_reaches_a_metric_dependent_row; they are excluded
    here by mechanism and pinned there by name, so neither test can absorb a
    new one silently.
    """
    graph = adg.candidate_edges()
    assert graph["n_candidate_edges"] > 0, (
        "no edge at all was traced, which means the tracer is broken rather "
        "than the graph being empty"
    )
    anchors = [e for e in graph["edges"]
               if e["mechanism"] == "EXPERIMENTAL_ANCHOR"]
    ansatz = [e for e in graph["edges"]
              if e["mechanism"] == "DISCRETE_ANSATZ"]
    assert len(anchors) + len(ansatz) == len(graph["edges"]), (
        "a third edge mechanism appeared: %s"
        % sorted({e["mechanism"] for e in graph["edges"]})
    )
    assert len(ansatz) == 2
    assert all(e["target"] == "cosmology.wa_thawing" for e in ansatz)
    assert len(anchors) == 27


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
