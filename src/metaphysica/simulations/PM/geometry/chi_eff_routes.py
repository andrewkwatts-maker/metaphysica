"""chi_eff = 144 has three claimed derivations. They cannot all be right, and
their agreement is not evidence.

WHY THIS EXISTS
===============
`topology.mephorash_chi` = 144 is load-bearing: n_gen is taken as chi_eff/48,
alpha_leak as 1/sqrt(chi_eff/b_3), and the EML/Arithma track encodes it too.
Three different derivations are claimed for it across the codebase, and all
three return 144 at b_3 = 24:

    A  2 (h11 - h21 + h31)   TCS Hodge numbers        g2_geometry
    B  b_3^2 / 4             FormulasRegistry         registry comment
    C  6 b_3                 EML operator trees       eml_integration

Three independent routes converging on one number reads as strong corroboration.
It is not, and this module shows why in three separate ways.

FINDING 1 -- B AND C INTERSECT AT EXACTLY ONE POINT, AND IT IS 24
==================================================================
    6 b = b^2 / 4   <=>   b^2 - 24 b = 0   <=>   b = 24   (positive root)

So routes B and C agree at exactly one value of b_3, and that value is the one
the framework adopted. Their agreement at 144 is not corroboration: it is the
DEFINITION of their unique crossing point. Off 24 they diverge immediately --
at b_3 = 43 they give 258 and 462.25.

This is the "matching values are not evidence of the same statement" trap with a
proof attached: the match is structural, not evidential.

FINDING 2 -- 144 IS CHEAP
=========================
Enumerating simple expressions in (b_2, b_3) and the small integers the
framework already uses, 144 is hit by roughly 8 of 320 at either seed point --
about 2.7%, not a rare target. Two expressions landing on it is weak.

FINDING 3 -- ROUTE A IS A TYPE ERROR ON THE JOYCE PATH
=======================================================
2(h11 - h21 + h31) is the Euler characteristic of a Calabi-Yau THREEFOLD,
written in its Hodge numbers. The Joyce orbifold T^7/Gamma is not a CY3 and has
no h21 and no h31; the only reason the expression evaluates at all is that
g2_geometry carries TCS #187's Hodge numbers as attributes. On the Joyce path
those numbers describe a different manifold. This is the A4 bar in a new place:
the arithmetic runs, the object it refers to is not there.

THE CONSEQUENCE, AND IT IS A DICHOTOMY
======================================
No expression in b_2 or b_3 gives 144 on BOTH seed paths -- only constants do,
and a constant is not a derivation. So chi_eff is exactly one of:

    * a CONSTANT, independent of the seed, in which case routes B and C are
      wrong and n_gen = chi_eff/48 carries no topological content; or
    * SEED-DEPENDENT, in which case it is not 144 on the 43 path and every
      consumer of the literal 144 must move.

The framework currently wants both. Which it is is an AUTHOR RULING; this module
computes the alternatives and decides nothing.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "ROUTES",
    "evaluate_routes",
    "unique_intersection",
    "reachable_family",
    "how_cheap_is",
    "chi_eff_report",
]

#: The three claimed derivations, as callables on (b_2, b_3, hodge).
#: Each carries where it lives, so none of them is restated from memory.
ROUTES: Dict[str, Dict[str, Any]] = {
    "tcs_hodge": {
        "expression": "2 (h11 - h21 + h31)",
        "site": "PM/geometry/g2_geometry.py",
        "depends_on_b3": False,
        "fn": lambda b2, b3, h: 2 * (h["h11"] - h["h21"] + h["h31"]),
        "type_note": (
            "the Euler characteristic of a Calabi-Yau THREEFOLD in its Hodge "
            "numbers. A Joyce orbifold T^7/Gamma is not a CY3 and has no h21 "
            "or h31; the expression evaluates only because TCS #187's numbers "
            "are carried as attributes."
        ),
    },
    "b3_squared_over_4": {
        "expression": "b_3^2 / 4",
        "site": "core/FormulasRegistry.py",
        "depends_on_b3": True,
        "fn": lambda b2, b3, h: b3 ** 2 / 4.0,
        "type_note": "dimensionally a square of a Betti number; no stated origin",
    },
    "six_b3": {
        "expression": "6 b_3",
        "site": "EML operator trees (eml_integration.b3_leaf)",
        "depends_on_b3": True,
        "fn": lambda b2, b3, h: 6.0 * b3,
        "type_note": "no stated origin for the 6",
    },
}

#: TCS #187's Hodge numbers, carried only so route A can be EVALUATED and shown
#: to be type-incorrect on the Joyce path. Not asserted as Joyce data.
_TCS_HODGE = {"h11": 4, "h21": 0, "h31": 68}


def reachable_family() -> List[Dict[str, int]]:
    """The Joyce-reachable (b_2, b_3), and the relation between them.

    Read from the derived contribution table rather than tabulated. Every
    admissible profile has b_2 = n_T3 and b_3 = 7 + 3 n_T3, so across the whole
    family

        b_3 = 7 + 3 b_2

    which means b_2 and b_3 are NOT independent: there is one topological input,
    not two. The adopted pair (24, 4) violates it -- 7 + 3*4 = 19 -- which is an
    independent way to see that it is off the family.
    """
    from metaphysica.simulations.PM.geometry.derived_contribution_table import (
        FLAT_B2,
        FLAT_B3,
    )

    out = []
    for n_t3 in (0, 4, 8, 12):
        b2 = FLAT_B2 + n_t3
        b3 = FLAT_B3 + 3 * n_t3
        out.append({
            "n_T3": n_t3,
            "b2": b2,
            "b3": b3,
            "satisfies_b3_eq_7_plus_3b2": b3 == 7 + 3 * b2,
        })
    return out


def evaluate_routes(b2: int, b3: int,
                    hodge: Optional[Dict[str, int]] = None) -> Dict[str, float]:
    """Each claimed route at one (b_2, b_3)."""
    hodge = hodge or _TCS_HODGE
    return {name: float(spec["fn"](b2, b3, hodge))
            for name, spec in ROUTES.items()}


def unique_intersection() -> Dict[str, Any]:
    """Where 6 b_3 and b_3^2/4 agree. Solved, not sampled.

    6b = b^2/4  <=>  b^2 - 24b = 0  <=>  b in {0, 24}. The positive root is 24,
    so the two routes cross exactly once and the crossing is the adopted seed.
    """
    import sympy as sp

    b = sp.Symbol("b", positive=True)
    roots = sp.solve(sp.Eq(6 * b, b ** 2 / 4), b)
    positive = [int(r) for r in roots if r.is_number and r > 0]
    value = [float(6 * r) for r in positive]
    return {
        "equation": "6 b_3 = b_3^2 / 4",
        "positive_roots": positive,
        "value_at_roots": value,
        "is_unique": len(positive) == 1,
        "why_this_matters": (
            "routes B and C agree at exactly one b_3, and it is the adopted "
            "one. Their agreement at 144 is the definition of their crossing "
            "point, not independent corroboration of it."
        ),
    }


def how_cheap_is(target: float, b2: int, b3: int) -> Dict[str, Any]:
    """How many simple expressions in the framework's own integers hit `target`.

    The trials-factor question `shape_search` exists to ask: a match is only
    informative if the search that found it was small.
    """
    pool = {"b2": b2, "b3": b3, "7": 7, "2": 2, "3": 3,
            "4": 4, "6": 6, "8": 8, "12": 12, "24": 24}
    built: Dict[str, float] = {}
    for (na, a), (nb, bb) in itertools.product(pool.items(), repeat=2):
        built["%s*%s" % (na, nb)] = a * bb
        built["%s+%s" % (na, nb)] = a + bb
        built["%s-%s" % (na, nb)] = a - bb
    for na, a in pool.items():
        built["%s^2" % na] = a * a
        built["%s^2/4" % na] = a * a / 4.0

    hits = sorted(k for k, v in built.items() if abs(v - target) < 1e-9)
    return {
        "target": target,
        "n_expressions_searched": len(built),
        "n_hits": len(hits),
        "hit_rate": len(hits) / float(len(built)),
        "hits": hits,
    }


def chi_eff_report() -> Dict[str, Any]:
    """The three routes, evaluated across the reachable family, with the verdict."""
    family = reachable_family()
    adopted = {"b2": 4, "b3": 24, "label": "adopted (off the Joyce family)"}
    canonical = {"b2": 12, "b3": 43, "label": "canonical Joyce point"}

    table = []
    for point in [adopted] + [{"b2": f["b2"], "b3": f["b3"],
                               "label": "reachable n_T3=%d" % f["n_T3"]}
                              for f in family]:
        values = evaluate_routes(point["b2"], point["b3"])
        table.append({
            **point,
            **values,
            "all_agree": len({round(v, 9) for v in values.values()}) == 1,
        })

    crossing = unique_intersection()
    cheap_at_24 = how_cheap_is(144.0, 4, 24)
    cheap_at_43 = how_cheap_is(144.0, 12, 43)

    # Which expressions give 144 at BOTH points? Only ones with no b dependence.
    both = sorted(set(cheap_at_24["hits"]) & set(cheap_at_43["hits"]))
    b_dependent_both = [h for h in both if "b2" in h or "b3" in h]

    return {
        "routes": {k: {"expression": v["expression"], "site": v["site"],
                       "depends_on_b3": v["depends_on_b3"],
                       "type_note": v["type_note"]}
                   for k, v in ROUTES.items()},
        "table": table,
        "family_relation": "b_3 = 7 + 3 b_2 across every reachable profile",
        "family_relation_holds": all(f["satisfies_b3_eq_7_plus_3b2"]
                                     for f in family),
        "adopted_pair_on_family": (7 + 3 * 4) == 24,
        "unique_intersection": crossing,
        "trials_factor_at_24": cheap_at_24,
        "trials_factor_at_43": cheap_at_43,
        "expressions_giving_144_at_both_points": both,
        "b_dependent_expressions_giving_144_at_both": b_dependent_both,
        "the_dichotomy": (
            "No expression in b_2 or b_3 gives 144 at both seed points -- only "
            "constants do, and a constant is not a derivation. So chi_eff is "
            "either a CONSTANT independent of the seed, in which case "
            "n_gen = chi_eff/48 carries no topological content; or it is "
            "SEED-DEPENDENT, in which case it is not 144 on the 43 path and "
            "every consumer of the literal must move. The framework currently "
            "wants both."
        ),
        "ruling_required": (
            "which chi_eff route is meant. This module computes the "
            "alternatives and selects none."
        ),
        "counts": (
            "Betti numbers are counts of cohomology classes; the Hodge numbers "
            "in route A describe a Calabi-Yau threefold, not this manifold."
        ),
    }
