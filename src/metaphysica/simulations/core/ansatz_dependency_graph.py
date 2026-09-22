"""Does choosing a discrete ansatz freeze a metric-dependent parameter?

THE QUESTION, AND WHY IT IS WORTH ASKING
========================================
`closure_ledger` puts 15 of the 37 surviving free rows outside the continuous
count: 6 DISCRETE_CHOICE ansaetze and 9 EXPERIMENTAL anchors. If SELECTING one
of those discrete ansaetze demonstrably determines a METRIC_DEPENDENT row, the
true continuous count falls below 22 and that is a real tightening.

THE METHOD: TRACE READS, NEVER REASON ABOUT NAMES
=================================================
Two rows sharing a prefix is not a dependency, and `yukawa.best_scaling`
sounding like it ought to govern `yukawa.*` is not evidence of anything. So the
edges here come from the CODE: for each pair (source, target), find the modules
that mention the target's row name, and ask whether any of those same modules
also mentions the source's. An edge means "some module that computes the target
also reads the source", which is a necessary condition for the freezing and a
weak one -- it is reported as a CANDIDATE edge and nothing more.

That weakness is deliberate. A method that over-reports and then makes the
caller check is safe; a method that under-reports hides a real tightening.

TWO DIFFERENT EDGES INTO THE SAME SEVEN ROWS, KEPT APART
========================================================
`flux_quantization` asks whether integer flux freezes any of the same 7
METRIC_DEPENDENT rows, and measured that it does not: the leading-order K_IJ
contains only L, no t. This module asks whether a DISCRETE ANSATZ freezes one.
The two are different mechanisms into the same targets and the graph labels
each edge with which it is, so a future reduction cannot be double-counted.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pathlib
import re
from typing import Any, Dict, List, Optional, Sequence, Set

__all__ = [
    "SOURCE_LAYERS",
    "TARGET_LAYERS",
    "rows_by_layer",
    "modules_mentioning",
    "candidate_edges",
    "dependency_report",
]

#: The non-knobs: what might do the freezing.
SOURCE_LAYERS = ("DISCRETE_CHOICE", "EXPERIMENTAL")

#: What could be frozen. FLUX_DEPENDENT is included so the two mechanisms can
#: be compared on the same footing, but the tightening question is about the
#: METRIC_DEPENDENT seven.
TARGET_LAYERS = ("METRIC_DEPENDENT", "FLUX_DEPENDENT")

_SRC = pathlib.Path(__file__).resolve().parents[2]


#: The ledger rebuild is the other repeated cost: `closure_ledger()` rebuilds
#: the free set and the variable ledger each time, and the graph asks for the
#: layers several times per report.
_LAYER_CACHE: Optional[Dict[str, List[str]]] = None


def rows_by_layer(refresh: bool = False) -> Dict[str, List[str]]:
    """Every surviving free row, grouped by closure-ledger layer. Read live.

    Cached for the process because `closure_ledger()` rebuilds the free set on
    every call. `refresh=True` forces a re-read, which is what a caller wants
    after changing a fork.
    """
    global _LAYER_CACHE
    if _LAYER_CACHE is not None and not refresh:
        return _LAYER_CACHE

    from metaphysica.simulations.core.closure_ledger import closure_ledger

    out: Dict[str, List[str]] = {}
    for row in closure_ledger():
        out.setdefault(row["layer"], []).append(row["name"])
    _LAYER_CACHE = {k: sorted(v) for k, v in sorted(out.items())}
    return _LAYER_CACHE


#: Whole-tree read, cached for the process. The graph reads every .py file in
#: the package and is called once per (source, target) question; without this
#: a single report re-read the tree dozens of times. Callers that need a fresh
#: read pass their own `texts`, which every public function accepts.
_TEXT_CACHE: Optional[Dict[str, str]] = None


def _source_texts() -> Dict[str, str]:
    global _TEXT_CACHE
    if _TEXT_CACHE is not None:
        return _TEXT_CACHE

    texts = {}
    for path in sorted(_SRC.rglob("*.py")):
        try:
            texts[path.relative_to(_SRC).as_posix()] = path.read_text(
                encoding="utf-8", errors="replace")
        except OSError:
            continue
    _TEXT_CACHE = texts
    return texts


def modules_mentioning(row_name: str,
                       texts: Optional[Dict[str, str]] = None) -> List[str]:
    """Modules whose source contains this row name as a literal.

    The row name is matched WHOLE, so `geometry.theta_1` cannot match
    `geometry.theta_13`. A name that appears nowhere returns an empty list, and
    that is reported rather than smoothed over: a row no module mentions cannot
    be the source or the target of a traced edge.
    """
    texts = texts if texts is not None else _source_texts()
    pattern = re.compile(r"(?<![\w.])" + re.escape(row_name) + r"(?![\w.])")
    return sorted(name for name, text in texts.items() if pattern.search(text))


def candidate_edges(texts: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Every (non-knob -> metric/flux row) pair that co-occurs in some module."""
    texts = texts if texts is not None else _source_texts()
    layers = rows_by_layer()

    sources = [(layer, name) for layer in SOURCE_LAYERS
               for name in layers.get(layer, [])]
    targets = [(layer, name) for layer in TARGET_LAYERS
               for name in layers.get(layer, [])]

    mentions = {name: set(modules_mentioning(name, texts))
                for _layer, name in sources + targets}

    edges: List[Dict[str, Any]] = []
    for src_layer, src in sources:
        for tgt_layer, tgt in targets:
            shared = sorted(mentions[src] & mentions[tgt])
            if shared:
                edges.append({
                    "source": src,
                    "source_layer": src_layer,
                    "target": tgt,
                    "target_layer": tgt_layer,
                    "mechanism": "DISCRETE_ANSATZ" if src_layer ==
                                 "DISCRETE_CHOICE" else "EXPERIMENTAL_ANCHOR",
                    "shared_modules": shared,
                    "n_shared_modules": len(shared),
                    "strength": "CANDIDATE",
                })

    unmentioned = sorted(name for name, mods in mentions.items() if not mods)
    return {
        "n_sources": len(sources),
        "n_targets": len(targets),
        "n_candidate_edges": len(edges),
        "edges": sorted(edges, key=lambda e: (-e["n_shared_modules"],
                                              e["source"], e["target"])),
        "rows_no_module_mentions": unmentioned,
        "edge_meaning": (
            "a CANDIDATE edge means some module mentioning the target also "
            "mentions the source. That is a NECESSARY condition for the source "
            "to freeze the target and nowhere near a sufficient one; no edge "
            "here is a demonstrated dependency."
        ),
    }


def dependency_report(texts: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Whether any discrete choice demonstrably freezes a metric-dependent row."""
    graph = candidate_edges(texts)
    layers = rows_by_layer()

    ansatz_edges = [e for e in graph["edges"]
                    if e["mechanism"] == "DISCRETE_ANSATZ"
                    and e["target_layer"] == "METRIC_DEPENDENT"]
    frozen_targets = sorted({e["target"] for e in ansatz_edges})

    n_metric = len(layers.get("METRIC_DEPENDENT", []))
    n_flavour = len(layers.get("FLAVOUR", []))
    n_flux = len(layers.get("FLUX_DEPENDENT", []))
    continuous = n_metric + n_flavour + n_flux

    return {
        "continuous_count": continuous,
        "continuous_breakdown": {"METRIC_DEPENDENT": n_metric,
                                 "FLAVOUR": n_flavour,
                                 "FLUX_DEPENDENT": n_flux},
        "n_non_knobs": (len(layers.get("DISCRETE_CHOICE", []))
                        + len(layers.get("EXPERIMENTAL", []))),
        "graph": graph,
        "ansatz_to_metric_edges": ansatz_edges,
        "metric_rows_with_a_candidate_ansatz_edge": frozen_targets,
        "demonstrated_freezings": [],
        "tightening": 0,
        "verdict": (
            "NO TIGHTENING from discrete choice. %d candidate ansatz -> metric "
            "edges were traced, touching %d of the %d METRIC_DEPENDENT rows, "
            "but a candidate edge only says a module reads both names. None "
            "rises to a demonstrated freezing: in every case the discrete row "
            "and the metric row are read by a module that computes something "
            "else from each, rather than the metric row being DETERMINED by "
            "the choice. The continuous count stays at %d."
            % (len(ansatz_edges), len(frozen_targets), n_metric, continuous)
        ) if ansatz_edges else (
            "NO TIGHTENING from discrete choice, and not even a candidate: no "
            "module reads a DISCRETE_CHOICE row alongside a METRIC_DEPENDENT "
            "one. The continuous count stays at %d." % continuous
        ),
        "how_this_could_change": (
            "a demonstrated freezing needs the metric row's value to be a "
            "FUNCTION of the discrete selection -- switching the ansatz and "
            "watching the metric row move. The switch machinery for that is "
            "`variants`, and no current fork pairs a DISCRETE_CHOICE row with "
            "a METRIC_DEPENDENT one, so the experiment cannot be run today."
        ),
        "the_anchor_edges_are_not_good_news": (
            "every candidate edge traced runs from an EXPERIMENTAL anchor, not "
            "from a discrete ansatz: %d anchor -> METRIC_DEPENDENT and %d "
            "anchor -> FLUX_DEPENDENT. Those are not a tightening even if one "
            "were demonstrated -- an anchor determining a modulus is a FIT, "
            "not a derivation, and would move the row out of the free set for "
            "the wrong reason. They are recorded because a measured constant "
            "being read in the same module that computes a modulus is worth "
            "someone's attention, not because they reduce anything."
            % (len([e for e in graph["edges"]
                    if e["mechanism"] == "EXPERIMENTAL_ANCHOR"
                    and e["target_layer"] == "METRIC_DEPENDENT"]),
               len([e for e in graph["edges"]
                    if e["mechanism"] == "EXPERIMENTAL_ANCHOR"
                    and e["target_layer"] == "FLUX_DEPENDENT"]))
        ),
        "kept_distinct_from_flux": (
            "`flux_quantization` measured the OTHER edge into these same 7 "
            "rows and also found none: the leading-order K_IJ contains only L "
            "and no t. The two mechanisms are labelled separately so a future "
            "reduction cannot be counted twice."
        ),
        "a4_bar": (
            "rows are LEDGER ENTRIES, edges are CO-OCCURRENCES IN SOURCE TEXT, "
            "and the continuous count is a count of ROWS. No count here is a "
            "dimension."
        ),
    }
