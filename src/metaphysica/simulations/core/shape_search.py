"""Generate geometric candidate formulas -- and report the trials factor.

THE HAZARD THIS MODULE EXISTS TO CONTROL
========================================
Searching expressions built from a few integers until one matches a target is
numerology, and it is very easy to do by accident. If you test N expressions
against a target at relative tolerance p, you expect roughly

    E[false matches] = N * 2p

purely by chance, under a flat prior over the log of the target. Find one match
after searching 50,000 expressions at 1e-3 and you expect ~100 matches from
noise alone: the match means nothing.

So every result here carries `n_searched`, `expected_by_chance` and a verdict
that is SIGNIFICANT only when expected_by_chance << 1. A match without that
number is not a finding, and this module refuses to present one.

WHAT COUNTS AS A GEOMETRIC PRIMITIVE
====================================
Only quantities the framework DERIVES or registers as structural -- not fitted
values, and no free-floating integers. Each carries its provenance so a formula
can be read back to its geometric content. Feeding fitted parameters in as
primitives would let the search rediscover them and call it a derivation.

WHAT A MATCH IS AND IS NOT
==========================
A surviving candidate is a HYPOTHESIS with a stated trials factor. It is not a
derivation: a derivation exhibits the mechanism, and an expression that lands on
a number exhibits nothing. The A4 bar from the register applies unchanged --
reproducing a value is not the same as producing the object.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
import math
from typing import Any, Dict, Iterable, List, Optional, Tuple

__all__ = [
    "primitives",
    "generate",
    "search_target",
    "search_free_set",
]

#: Relative tolerance for calling an expression a match. Deliberately tight:
#: loosening it multiplies the trials factor proportionally.
DEFAULT_TOL = 1e-4


def primitives() -> Dict[str, Tuple[float, str]]:
    """symbol -> (value, provenance). Derived or structural quantities only."""
    from metaphysica.simulations.core.arithma_formula import (
        arithma_constant,
        registry_value,
    )

    out: Dict[str, Tuple[float, str]] = {}

    def add(symbol: str, value: Optional[float], provenance: str) -> None:
        if value is not None and value > 0:
            out[symbol] = (float(value), provenance)

    add("b3", registry_value("topology.elder_kads"), "topology.elder_kads (INPUT)")
    add("D_bulk", registry_value("dimensions.D_bulk"), "dimensions.D_bulk")
    add("chi", registry_value("topology.mephorash_chi"), "topology.mephorash_chi")
    add("pi", arithma_constant("pi"), "arithma constant table")
    # Structural counts the framework derives in joyce_orbifold / the Fano work.
    add("n_fano", 7.0, "the 7 Fano points = 7 involutions (R2, derived)")
    add("n_face", 4.0, "the 4 moved coordinates of an involution (R2, derived)")
    add("n_block", 3.0, "the 3 fixed coordinates = a Fano line (R2, derived)")
    add("dim_O", 8.0, "dim of the octonions")
    add("dim_g2", 14.0, "dim g2, verified as the annihilator of a G2 form")
    add("dim_J3O", 27.0, "dim J_3(O), the exceptional Jordan algebra")
    add("aut_fano", 168.0, "|PSL(3,2)| = |Aut(Fano)|, computed")
    add("arc_stab", 24.0, "|S_4|, the arc stabiliser order, computed")
    add("phi_golden", (1.0 + math.sqrt(5.0)) / 2.0, "the golden ratio")
    return out


def generate(prims: Dict[str, Tuple[float, str]],
             max_terms: int = 2) -> List[Tuple[str, float]]:
    """Candidate expressions over the primitives. Small, closed grammar.

    Kept deliberately small: every extra operator multiplies the trials factor,
    and a bigger grammar makes matches cheaper rather than better.
    """
    names = sorted(prims)
    vals = {k: v for k, (v, _p) in prims.items()}
    out: List[Tuple[str, float]] = []

    for a in names:
        va = vals[a]
        out.append((a, va))
        out.append(("sqrt(%s)" % a, math.sqrt(va)))
        if va > 1:
            out.append(("ln(%s)" % a, math.log(va)))

    for a, b in itertools.permutations(names, 2):
        va, vb = vals[a], vals[b]
        out.append(("%s/%s" % (a, b), va / vb))
        out.append(("%s*%s" % (a, b), va * vb))
        if vb < 12:                      # keep exponents sane
            out.append(("%s^%s" % (a, b), va ** vb))

    if max_terms >= 3:
        for a, b, c in itertools.permutations(names, 3):
            va, vb, vc = vals[a], vals[b], vals[c]
            if vc:
                out.append(("%s*%s/%s" % (a, b, c), va * vb / vc))
                out.append(("%s/(%s*%s)" % (a, b, c), va / (vb * vc)))

    seen = set()
    unique: List[Tuple[str, float]] = []
    for expr, value in out:
        if not math.isfinite(value) or value <= 0:
            continue
        key = round(math.log(value), 12)
        if key in seen:
            continue
        seen.add(key)
        unique.append((expr, value))
    return unique


def search_target(target: float, name: str = "",
                  tol: float = DEFAULT_TOL,
                  max_terms: int = 3) -> Dict[str, Any]:
    """Search for expressions matching a target, with the trials factor.

    The verdict is the point. SIGNIFICANT requires expected_by_chance well
    below 1; anything else is reported as NUMEROLOGICAL no matter how pretty
    the expression looks.
    """
    prims = primitives()
    candidates = generate(prims, max_terms=max_terms)
    matches = [
        {"expression": expr, "value": value,
         "rel_error": abs(value - target) / abs(target)}
        for expr, value in candidates
        if target and abs(value - target) / abs(target) < tol
    ]
    matches.sort(key=lambda m: m["expression"])       # by name, never by error

    n = len(candidates)
    expected = n * 2.0 * tol
    if not matches:
        verdict = "NO_MATCH"
    elif expected < 0.05:
        verdict = "SIGNIFICANT"
    elif expected < 1.0:
        verdict = "WEAK"
    else:
        verdict = "NUMEROLOGICAL"

    return {
        "target_name": name,
        "target": target,
        "tolerance": tol,
        "n_searched": n,
        "expected_by_chance": expected,
        "n_matches": len(matches),
        "matches": matches,
        "verdict": verdict,
        "how_to_read_this": (
            "expected_by_chance = n_searched * 2 * tolerance. A match is only "
            "informative when that number is far below 1. Even then it is a "
            "HYPOTHESIS, not a derivation: reproducing a value is not "
            "producing the object (the A4 bar)."
        ),
    }


def search_free_set(tol: float = DEFAULT_TOL,
                    max_terms: int = 3) -> Dict[str, Any]:
    """Run the search across every numeric free-set parameter.

    Experimental anchors are searched too, but flagged: a formula matching a
    MEASURED value would be a PREDICTION of that measurement, which is a much
    stronger and much rarer thing than matching a fitted parameter -- and
    correspondingly more suspect if the trials factor is large.
    """
    import glob
    import json
    from pathlib import Path

    from metaphysica.simulations.core.free_set import build_free_set

    params: Dict[str, Any] = {}
    for candidate in [Path("AutoGenerated/parameters.json"),
                      Path("H:/Github/PrincipiaMetaphysica/AutoGenerated/parameters.json")]:
        try:
            if candidate.is_file():
                params = json.loads(
                    candidate.read_text(encoding="utf-8"))["parameters"]
                break
        except (OSError, ValueError):
            continue

    results = []
    for path in sorted(build_free_set()["free_set"]):
        row = params.get(path) or {}
        value = row.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        if value == 0:
            continue
        found = search_target(float(value), name=path, tol=tol,
                              max_terms=max_terms)
        found["status"] = row.get("status")
        found["is_experimental_anchor"] = row.get("status") == "MEASURED"
        results.append(found)

    significant = [r for r in results if r["verdict"] == "SIGNIFICANT"]
    return {
        "n_targets": len(results),
        "tolerance": tol,
        "results": results,
        "n_significant": len(significant),
        "significant": significant,
        "ordering": "parameter path; never by residual",
        "verdict": "NO_SELECTION_MADE",
        "caveat": (
            "A SIGNIFICANT verdict means the match is unlikely to be chance "
            "at this grammar size. It does NOT mean the formula is the "
            "physics. Each survivor needs a mechanism before it is anything "
            "more than a coincidence with good odds."
        ),
    }
