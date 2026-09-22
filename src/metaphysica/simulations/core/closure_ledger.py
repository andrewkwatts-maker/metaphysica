"""Can the model be closed by geometry? Which parameters, and where the wall is.

THE QUESTION
============
"Give every free parameter a geometric definition." The honest answer is that
most of them CANNOT have one, and the useful output is not a closure but a
BOUNDARY: which parameters the geometry could in principle reach, which need an
object the framework does not have, and which are not model outputs at all.

This module classifies every surviving free-set row by the KIND of object that
would have to supply it. The classification is rule-based and the rules are
stated, so it can be audited rather than believed.

THE LAYERS, in increasing distance from what is derived today
=============================================================
TOPOLOGICAL       Betti numbers, group data, intersection numbers. The
                  framework HAS these: b_2 and b_3 are fixed by n_gen = rank(Gamma)
                  on the 43 path, the flat sector is derived (R5), and the
                  12x12x43 integer tensor is computed metric-free.

METRIC_DEPENDENT  Needs the G2 metric on Y_7 -- moduli VEVs, decay constants,
                  the racetrack vacuum. K_IJ now has leading-order-in-t VALUES,
                  so this layer is PARTIALLY open, and every result in it is
                  asymptotic and must be labelled so.

FLUX_DEPENDENT    Needs flux quanta. These are independent DISCRETE inputs to an
                  M-theory compactification; no amount of geometry on Y_7
                  supplies them. A closure claim here would be a category error.

FLAVOUR           Yukawa couplings and mixing angles need overlap integrals of
                  zero modes: metric AND singular locus AND the wavefunctions.
                  The locus now exists; the metric is leading-order; the
                  wavefunctions do not exist at all.

EXPERIMENTAL      A measured constant that the model is SCORED against, not one
                  it outputs. Calling this "free" inflates the count: an anchor
                  is not a knob, which is the rule free_set already applies to
                  error bars.

DISCRETE_CHOICE   An ansatz or a selection among options. Not a continuous knob,
                  so "derive it" is the wrong request; the right one is "exhibit
                  the argument that selects it".

WHAT THIS DOES NOT DO
=====================
It does not assert that any row IS closable, only which layer would have to
close it. Claiming alpha_inverse or H_0 follows from Betti numbers would be the
overreach this project exists to prevent: a G2 compactification does not fix a
gauge coupling from topology, it fixes it from topology PLUS flux PLUS threshold
data PLUS the metric.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

__all__ = ["LAYERS", "classify_row", "closure_ledger", "closure_report"]

#: Layer -> (what it needs, does the framework have it today).
LAYERS: Dict[str, Dict[str, Any]] = {
    "TOPOLOGICAL": {
        "needs": "Betti numbers, group data, intersection numbers",
        "available": True,
        "note": ("derived: b_2 and b_3 from n_gen = rank(Gamma), the flat "
                 "sector from R5, the 12x12x43 integer tensor metric-free"),
    },
    "METRIC_DEPENDENT": {
        "needs": "the G2 metric on Y_7 (moduli VEVs)",
        "available": "PARTIAL",
        "note": ("K_IJ has leading-order-in-t values from the glued metric; "
                 "every result here is asymptotic and must be labelled so. "
                 "Two freezing mechanisms MEASURED NULL 2026-09-22: integer "
                 "flux cannot freeze these rows at leading order because the "
                 "leading-order pairing is t-free (flux_quantization), and "
                 "no discrete ansatz reaches them either -- zero traced "
                 "edges (ansatz_dependency_graph). And the racetrack supplies "
                 "NO value on the adopted seed: a = 2*pi/43 < b = 2*pi/26 "
                 "deletes the vacuum entirely (0 stationary points, 0 SUSY "
                 "roots, measured 2026-09-22), so Re(T) is unbound-by-"
                 "racetrack until the re_t_adoption ruling"),
    },
    "FLAVOUR": {
        "needs": "zero-mode overlap integrals: metric, singular locus, wavefunctions",
        "available": False,
        "note": ("the locus exists and the metric is leading-order; the "
                 "wavefunctions do not exist at all"),
    },
    "FLUX_DEPENDENT": {
        "needs": "flux quanta",
        "available": False,
        "note": ("independent DISCRETE inputs to an M-theory compactification; "
                 "no geometry on Y_7 supplies them. MEASURED 2026-09-22: at "
                 "leading order the 43 flux integers collapse to 2 invariants "
                 "because the pairing is t-free, so flux fixes the overall "
                 "scale and nothing else (flux_quantization)"),
    },
    "EXPERIMENTAL": {
        "needs": "nothing -- it is a measured anchor, not a model output",
        "available": "NOT_APPLICABLE",
        "note": "an anchor is not a knob; counting it as free inflates the total",
    },
    "DISCRETE_CHOICE": {
        "needs": "an argument that selects among options, not a derivation",
        "available": "NOT_APPLICABLE",
        "note": "'derive it' is the wrong request for a discrete selection",
    },
}

#: Ordered rules. First match wins; each states WHY, so the result is auditable.
_RULES = [
    ("DISCRETE_CHOICE",
     lambda name, row: row.get("status") == "ANSATZ"
     or name.endswith("best_scaling") or "classification" in name,
     "declared ANSATZ or a named discrete selection"),

    ("EXPERIMENTAL",
     lambda name, row: row.get("status") == "MEASURED"
     and row.get("role") in ("COMPARISON_ONLY", "LOAD_BEARING_INPUT"),
     "declared MEASURED and consumed as an anchor"),

    ("FLAVOUR",
     lambda name, row: bool(re.search(
         r"theta_1[23]|theta_23|delta_cp|delta_CP|wolfenstein|jarlskog|J_CKM"
         r"|V_[a-z]{2}|yukawa|mass_ratio|dm2|dm21|dm31|mass_sum|lambda_0"
         r"|lambda_eff|m_higgs|phi_fit", name)),
     "a mixing angle, mass ratio or Yukawa-sector quantity"),

    ("METRIC_DEPENDENT",
     lambda name, row: bool(re.search(
         r"racetrack|Re_T|moduli|alpha_T|alpha_R|vev_coefficient|theta_i"
         r"|alpha_shadow|delta_b3", name)),
     "a modulus VEV or a quantity built from one"),

    ("FLUX_DEPENDENT",
     lambda name, row: bool(re.search(
         r"alpha_inverse|alpha_s|sin2_theta_W|su2_|su3_|M_GUT|as_weight", name)),
     "a gauge coupling or unification scale: needs flux and thresholds"),

    ("METRIC_DEPENDENT",
     lambda name, row: bool(re.search(
         r"H0_|Omega_|entropy_damping|wa_thawing", name)),
     "a cosmological observable downstream of the full reduction "
     "(wa_thawing returned to the free set when its -4/sqrt(b_3) removal "
     "stopped reproducing under the adopted seed, 2026-09-22 -- the "
     "removal was 24-arithmetic; it re-fires after a rebuild registers "
     "the seed-consistent value)"),
]


def classify_row(name: str, row: Dict[str, Any]) -> Dict[str, Any]:
    """Which layer would have to supply this parameter, and why."""
    for layer, predicate, why in _RULES:
        try:
            if predicate(name, row):
                return {"name": name, "layer": layer, "why": why,
                        "status": row.get("status"), "role": row.get("role")}
        except Exception:                  # a rule must never crash the ledger
            continue
    return {"name": name, "layer": "UNCLASSIFIED",
            "why": "no rule matched; needs a reading",
            "status": row.get("status"), "role": row.get("role")}


def closure_ledger() -> List[Dict[str, Any]]:
    """Every surviving free-set row, classified."""
    from metaphysica.simulations.core.free_set import build_free_set
    from metaphysica.simulations.core.free_variable_ledger import build_ledger

    removed = set(build_free_set()["removed"])
    rows = build_ledger()["rows"]
    rows = list(rows.values()) if isinstance(rows, dict) else rows
    survivors = [r for r in rows if r.get("name") not in removed]
    return [classify_row(r["name"], r) for r in sorted(
        survivors, key=lambda r: r.get("name", ""))]


def closure_report() -> Dict[str, Any]:
    """How far geometry can close the model, and where it stops."""
    import collections

    from metaphysica.simulations.core.free_set import artifact_seed_provenance

    ledger = closure_ledger()
    counts = collections.Counter(row["layer"] for row in ledger)
    provenance = artifact_seed_provenance()

    reachable_now = counts.get("TOPOLOGICAL", 0)
    partial = counts.get("METRIC_DEPENDENT", 0)
    not_a_knob = counts.get("EXPERIMENTAL", 0) + counts.get("DISCRETE_CHOICE", 0)
    blocked = counts.get("FLAVOUR", 0) + counts.get("FLUX_DEPENDENT", 0)

    return {
        "n_free": len(ledger),
        "by_layer": dict(sorted(counts.items())),
        "layers": LAYERS,
        "ledger": ledger,
        "free_set_artifact_provenance": provenance,
        "closable_by_topology_today": reachable_now,
        "partially_open_via_the_glued_metric": partial,
        "not_continuous_knobs_at_all": not_a_knob,
        "blocked_on_objects_the_framework_lacks": blocked,
        "the_answer": (
            "The model cannot be closed by geometry alone, and the reason is "
            "structural rather than incomplete work. A G2 compactification "
            "fixes TOPOLOGY; a gauge coupling additionally needs flux quanta "
            "and threshold data, a Yukawa needs zero-mode overlap integrals, "
            "and a modulus VEV needs the metric. Of %d free rows, %d are "
            "reachable from topology today, %d sit behind the glued metric "
            "(leading order only), %d are blocked on objects the framework "
            "does not have, and %d are not continuous knobs at all."
            % (len(ledger), reachable_now, partial, blocked, not_a_knob)
        ),
        "what_geometry_DID_close": (
            "b_2 and b_3 stop being inputs on the 43 path: n_gen = rank(Gamma) "
            "= 3 selects (12, 43) uniquely out of four enumerated candidates, "
            "and b_3 = 7 + 3 b_2 makes them one input rather than two. That is "
            "a real reduction, and it happened in the TOPOLOGICAL layer -- the "
            "only layer where a closure of this kind was ever available."
        ),
        "counts": (
            "rows of the free-variable ledger, classified by the KIND of "
            "object that would have to determine them. Not a claim that any "
            "row is closable."
        ),
    }
