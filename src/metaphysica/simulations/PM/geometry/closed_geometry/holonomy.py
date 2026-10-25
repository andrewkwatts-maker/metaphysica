"""CG.13: the holonomy-G2 metric exists on Y_7, by theorem (D-023).

No explicit metric is known for any compact G2 manifold. Joyce's existence
theorem gives one when its hypotheses hold, and g2_closure measures each of
them on the active path with a control that fails. This theorem publishes that
report: it holds only if every hypothesis is measured and holds, and otherwise
names the first one that does not.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from metaphysica.simulations.PM.geometry.closed_geometry.references import (
    REF_BRYANT_1987,
    REF_EGUCHI_HANSON_1978,
    REF_JOYCE_1996,
    REF_JOYCE_1996_II,
    REF_JOYCE_2000,
    REF_WANG_1989,
)
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import (
    Spec,
    Theorem,
    _active,
    _off_family,
)


def _hol_evidence() -> Dict[str, Any]:
    """The closure report on the active path, plus the parallel-spinor count."""
    from metaphysica.simulations.PM.geometry.g2_closure import closure_report

    report = closure_report()
    rows = report["hypotheses"]
    path, profile, point = _active()
    spinors = next(r for r in rows if r["id"] == "H7").get("count")
    return dict(report, derived=all(r["measured"] for r in rows),
                n_hypotheses=len(rows),
                n_held=sum(1 for r in rows if r["measured"] and r["holds"]),
                spinors=spinors, path=path, on_family=point is not None,
                declared=(profile["b2"], profile["b3"]))


def _hol_holds(ev: Dict[str, Any]) -> bool:
    return ev["verdict"] == "CLOSED_BY_THEOREM"


def _row(ev: Dict[str, Any], hid: str) -> Dict[str, Any]:
    return next(r for r in ev["hypotheses"] if r["id"] == hid)


def _hol_statement(ev: Dict[str, Any]) -> str:
    if _hol_holds(ev):
        return (
            "Y_7, the resolution of T^7/(Z/2)^3 with (b_2, b_3) = (12, 43), "
            "carries a torsion-free G2 structure whose metric is Ricci-flat "
            "with holonomy exactly G2. All %d hypotheses of Joyce's existence "
            "theorem are measured on the active path and hold; the conclusions "
            "follow by citation. No explicit metric is claimed: none is known "
            "for any compact G2 manifold." % ev["n_hypotheses"])
    first = _row(ev, ev["first_failure"])
    why = first.get("reason") or (
        "measured and fails" if first["measured"] else "not measured")
    prefix = "" if ev["on_family"] else _off_family(ev) + " "
    return prefix + (
        "NOT established on this path (%s, %s): hypothesis %s, '%s', %s. "
        "%d of %d hypotheses hold, so Joyce's theorem does not apply here."
        % (ev["seed"], ev["convention"], first["id"], first["hypothesis"],
           why, ev["n_held"], ev["n_hypotheses"]))


def _hol_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    count = ev["spinors"] if isinstance(ev["spinors"], int) else 0
    return float(count), count


def _hol_latex(ev: Dict[str, Any]) -> str:
    return (r"d\tilde\varphi = d{*}\tilde\varphi = 0 \;\Rightarrow\; "
            r"\mathrm{Ric}(g_{\tilde\varphi}) = 0,\quad "
            r"\pi_1(Y_7)\ \text{finite} \;\Rightarrow\; "
            r"\mathrm{Hol}(g_{\tilde\varphi}) = G_2,\quad "
            r"N_{\text{parallel spinors}} = %s" % ev["spinors"])


def _hol_steps(ev: Dict[str, Any]) -> List[str]:
    steps = [
        "Joyce 2000, Thm 11.6.1: a closed G2 structure on a compact 7-manifold "
        "whose torsion is small in the theorem's norms can be deformed to a "
        "torsion-free one. Joyce's resolution of T^7/Gamma meets those bounds "
        "when the hypotheses below hold (Joyce 1996a; Joyce 2000, Ch. 11)."]
    for r in ev["hypotheses"]:
        verdict = ("holds" if r["measured"] and r["holds"] else
                   "FAILS" if r["measured"] else "NOT MEASURED")
        steps.append("%s, %s: %s (%s)." % (
            r["id"], r["hypothesis"], verdict,
            r.get("source") or r.get("reason", "no source")))
    for c in ev["conclusions"]:
        steps.append("Conclusion, %s: %s (%s)%s." % (
            c["id"], c["claim"], c["by"], "" if c["established"] else
            " -- NOT established on this path"))
    return steps


_HOL_TERMS = {
    r"\tilde\varphi": {"symbol": "phi~", "description": (
        "the torsion-free G2 3-form Joyce's theorem produces near the glued "
        "closed form")},
    r"g_{\tilde\varphi}": {"symbol": "g", "description": (
        "the Riemannian metric that phi~ induces")},
    r"\pi_1(Y_7)": {"symbol": "pi_1", "description": (
        "the fundamental group of the resolved manifold")},
    r"N_{\text{parallel spinors}}": {"symbol": "N", "description": (
        "the number of Gamma-invariant constant spinors on T^7, from Cl(7) "
        "built out of phi (H7)")},
}


HOLONOMY_THEOREMS: Tuple[Theorem, ...] = (
    Theorem(
        id="y7-holonomy-g2-metric", label="(CG.13)",
        title="The holonomy-G2 metric exists, by theorem",
        counts=("hypotheses of Joyce's existence theorem, each measured with a "
                "failing control; N counts Gamma-invariant constant spinors"),
        proof=("Measure H1-H8 (g2_closure.closure_report); apply Joyce 2000 "
               "Thm 11.6.1 for existence, Bonan (proof in Bryant 1987) for Ricci-flatness and Joyce "
               "1996b Prop. 1.1.1 for Hol = G2. The Betti numbers are those of "
               "Joyce's first example (Joyce 1996a)."),
        test="tests/test_g2_closure.py::"
             "test_closure_verdict_on_the_active_path_and_on_the_split_form",
        falsifier=("any hypothesis failing on the active path: an indefinite "
                   "phi0, a singular component that is not A1, a closed "
                   "Eguchi-Hanson triple in the wrong orientation, infinite "
                   "pi_1, or a spinor count other than 1"),
        evidence=_hol_evidence, holds=_hol_holds,
        statement=_hol_statement, track=_hol_track, latex=_hol_latex,
        steps=_hol_steps, terms=_HOL_TERMS,
        references=(REF_JOYCE_2000, REF_JOYCE_1996, REF_JOYCE_1996_II,
                    REF_BRYANT_1987, REF_EGUCHI_HANSON_1978, REF_WANG_1989),
        scope=("existence by theorem on the compact real form (D-015), not an "
               "explicit metric; the split form and unreachable seeds report "
               "the failing hypothesis instead")),
)
