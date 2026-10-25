"""Data-driven SVG figures for the closed G2 geometry beginner topics."""
from typing import Any, Dict, List

from .betti import betti_figure
from .data import figure_data
from .eh_profile import eh_profile_figure
from .fold import fold_figure
from .proof_flow import proof_flow_figure, status

__all__ = ["betti_figure", "figure_data", "eh_profile_figure", "fold_figure",
           "proof_flow_figure", "status", "geometry_figures", "proof_figures",
           "proof_steps"]


def _fig(fid, title, caption, svg, source) -> Dict[str, str]:
    return {"id": fid, "title": title, "caption": caption, "svg": svg,
            "data_source": source}


def geometry_figures(data=None) -> List[Dict[str, str]]:
    data = data or figure_data()
    res_src = "joyce_resolution.resolution_report"
    return [
        _fig("fold", "The fold", "Flat T^7 folded by three Z/2 generators; each crease "
             "is resolved by an Eguchi-Hanson patch.", fold_figure(data), res_src),
        _fig("eh-profile", "The smooth patch", "The Eguchi-Hanson neck profile "
             "f(r) = sqrt(1 - a^4/r^4), sampled from the formula.", eh_profile_figure(),
             "eguchi_hanson (formula)"),
        _fig("betti", "Counting holes", "b3 = 7 + 3 x b2, read from the engine.",
             betti_figure(data), res_src),
    ]


def proof_figures(data=None) -> List[Dict[str, str]]:
    data = data or figure_data()
    return [_fig("proof-flow", "How the proof fits together", "Each hypothesis is "
                 "measured by the engine; the theorems then give Ric = 0 and Hol = G2.",
                 proof_flow_figure(data), "g2_closure.closure_report")]


def proof_steps(data: Dict[str, Any]) -> List[str]:
    """Plain-language ordered steps from closure_report, each naming its source."""
    report = data["closure"]
    steps = []
    for row in report["hypotheses"]:
        st = status(row)
        tail = " (%s)" % row["reason"] if row.get("reason") else ""
        steps.append("Check %s: %s. Result: %s%s. Source: %s." % (
            row["id"], row["hypothesis"], st, tail, row.get("source", "the engine")))
    for c in report["conclusions"]:
        state = "follows" if c["established"] else "is not yet reached"
        steps.append("Then %s %s. Source: %s." % (c["claim"], state, c["by"]))
    return steps
