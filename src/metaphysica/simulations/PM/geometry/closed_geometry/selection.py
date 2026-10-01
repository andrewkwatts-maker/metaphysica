"""Certificate theorem CG.12: what selects (b_2, b_3) = (12, 43).

RULED 2026-10-01 by the author (decision D-015): adopt WA-1 -- each bridge is
one resolved A1 component, one U(1) -- and the compact real form of phi, with
the alternatives kept switchable. The selection then runs without data:

1. phi's diagonal stabiliser Gamma = (Z/2)^3 and Joyce's construction give the
   reachable family (CG.7);
2. pi_1 is finite exactly on the n = 3 line (CG.4) -- on the compact form this
   is the statement that the holonomy is exactly G2 there (Joyce, JDG II,
   Prop. 1.1.1); on the split form only the topological statement survives;
3. on that line the 12 bridges match the 12 A1 components as one 3 x 4
   structure only on the all-plain classes (CG.8), and WA-1 makes that match
   the selection: (12, 43).

The statement is generated from the live switches -- `g2_form_convention`
decides whether step 2 may speak of holonomy, `seed_selection` whether step 3
selects or is reported as a finding beside the 2026-09-22 ruling.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from metaphysica.simulations.PM.geometry.closed_geometry.references import (
    REF_ARMSTRONG,
    REF_JOYCE_1996_II,
    REF_LUKAS_MORRIS,
)
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import (
    Spec,
    Theorem,
    _active,
    _off_family,
)

__all__ = ["SELECTION_ROUTE", "selection_route", "selection_report",
           "SELECTION_THEOREMS"]

#: The `seed_selection` fork's source. RULED 2026-10-01 (D-015): WA-1.
SELECTION_ROUTE = "wa1_correspondence"


def selection_route() -> str:
    """The selection route in force (the `seed_selection` switch)."""
    try:
        from metaphysica.simulations.core.variants import resolve
    except ImportError:                  # import cycle: the one real case
        return SELECTION_ROUTE
    return resolve("seed_selection")


def selection_report() -> Dict[str, Any]:
    """Each step of the selection, computed, on the switches in force."""
    from metaphysica.simulations.PM.geometry.closed_geometry.findings import (
        _n3_selection,
    )
    from metaphysica.simulations.PM.geometry.family_topology import (
        holonomy_selection,
    )
    from metaphysica.simulations.PM.geometry.geometry_narration import (
        holonomy_claim,
    )

    hol = holonomy_claim()
    pi1 = holonomy_selection()
    corr = _n3_selection()
    route = selection_route()
    return {
        "route": route,
        "real_form": hol["real_form"],
        "riemannian": hol["may_claim_g2_holonomy"],
        "pi1_finite_members": pi1["full_holonomy_members"],
        "pi1_line": pi1["selected"],
        "correspondence": corr,
        "selects": corr["selects"] if route == SELECTION_ROUTE else None,
    }


def _sel_evidence() -> Dict[str, Any]:
    path, profile, point = _active()
    ev = {"path": path, "declared": (profile["b2"], profile["b3"]),
          "derived": point is not None}
    if point is not None:
        ev.update(selection_report())
    return ev


def _sel_holds(ev: Dict[str, Any]) -> bool:
    if not ev["derived"] or not ev["correspondence"]["holds"]:
        return False
    if ev["route"] == SELECTION_ROUTE:
        return tuple(ev["selects"]) == tuple(ev["declared"])
    return True        # ruling_only: the correspondence is a finding only


def _sel_statement(ev: Dict[str, Any]) -> str:
    if not ev["derived"]:
        return _off_family(ev)
    t = ev["correspondence"]["tally"]
    step2 = (
        "pi_1 is finite exactly on the n = 3 line, so on the compact form "
        "the holonomy is exactly G2 there and nowhere else in the family"
        if ev["riemannian"] else
        "pi_1 is finite exactly on the n = 3 line; on the split form (this "
        "switch setting) no Riemannian holonomy statement is available, so "
        "the line is singled out topologically")
    if ev["route"] == SELECTION_ROUTE:
        lands = tuple(ev["selects"]) == tuple(ev["declared"])
        step3 = (
            "On that line the 12 bridges match the 12 A1 components as one "
            "3 x 4 structure on %d all-plain classes and on none of the %d "
            "Example-4 classes; with WA-1 (one bridge = one resolved A1 "
            "component, adopted 2026-10-01) this selects %s without using "
            "data%s."
            % (t.get("all_plain/bijection", 0),
               t.get("not_all_plain/none", 0), tuple(ev["selects"]),
               ", the seed in force" if lands else
               " -- NOT the seed in force, %s" % (tuple(ev["declared"]),)))
    else:
        step3 = (
            "On this switch setting (seed_selection = %s) the bridge match "
            "is reported as a finding (CG.8), and %s stands by the "
            "2026-09-22 ruling." % (ev["route"], tuple(ev["declared"])))
    return ("Joyce's construction from phi's (Z/2)^3 reaches the family of "
            "CG.7; %s (CG.4). %s" % (step2, step3))


def _sel_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    return float(ev["declared"][1]), ("add", 7, ("mul", 3, ("mul", 4, 3)))


def _sel_latex(ev: Dict[str, Any]) -> str:
    return (r"n = 3 \;\wedge\; 12_{\mathrm{bridges}} \leftrightarrow "
            r"12_{A_1} \;\Rightarrow\; (b_2, b_3) = (4n,\, 7 + 12n) = "
            r"(12, 43)")


def _sel_steps(ev: Dict[str, Any]) -> List[str]:
    if not ev["derived"]:
        return [_sel_statement(ev)]
    return [
        "phi fixes Gamma = (Z/2)^3; Joyce's construction from Gamma reaches "
        "the family of CG.7 (b_3 = 24 is not in it).",
        "pi_1 is finite exactly at n = 3 singular involutions (CG.4); on the "
        "compact form Joyce's Prop. 1.1.1 makes that holonomy exactly G2.",
        "On the n = 3 line the bridge <-> component 3 x 4 match exists only "
        "on the all-plain classes (CG.8).",
        _sel_statement(ev),
    ]


_SEL_TERMS = {
    "n": {"symbol": "n", "description": "the number of singular involutions"},
    "12_{\\mathrm{bridges}}": {"symbol": "12 bridges", "description": (
        "the directed edges of K4 on the Fano arc of four faces")},
    "12_{A_1}": {"symbol": "12 A1 components", "description": (
        "the connected fixed three-tori of the singular involutions")},
}


SELECTION_THEOREMS: Tuple[Theorem, ...] = (
    Theorem(
        id="y7-selection", label="(CG.12)",
        title="What selects (b2, b3) = (12, 43)",
        counts=("n counts singular involutions; bridges count directed edges "
                "of K4; components count connected fixed 3-tori"),
        proof=("Compose CG.7 (the reachable family), CG.4 (pi_1 finite only "
               "at n = 3; holonomy exactly G2 there on the compact form, by "
               "Joyce's Prop. 1.1.1) and CG.8 (the 3 x 4 match only on the "
               "all-plain n = 3 classes), read through WA-1."),
        test="tests/test_selection.py::"
             "test_the_selection_lands_on_the_adopted_seed",
        falsifier=("an all-plain n = 3 class other than (12, 43), a "
                   "bijection on an Example-4 class, or finite pi_1 off the "
                   "n = 3 line"),
        evidence=_sel_evidence, holds=_sel_holds,
        statement=_sel_statement, track=_sel_track, latex=_sel_latex,
        steps=_sel_steps, terms=_SEL_TERMS,
        references=(REF_JOYCE_1996_II, REF_ARMSTRONG, REF_LUKAS_MORRIS),
        scope=("WA-1 and the compact real form adopted 2026-10-01 (D-015); "
               "both are switches, so the split form and the ruling-only "
               "selection stay runnable")),
)
