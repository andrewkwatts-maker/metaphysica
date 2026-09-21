"""Three generations SELECTS the topology, rather than being matched by it.

THE RESULT
==========
Given three things the framework already derives, and nothing else:

  R1  Gamma = (Z/2)^3 is the diagonal stabiliser of the framework's own phi --
      forced by phi, not chosen (joyce_orbifold).
  A1  every admissible component is A1: transverse group exactly of order 2.
      Orders 4 and 8 flip exactly two of the four transverse coordinates, so
      they sit OUTSIDE SU(2), the quotient is not a complex orbifold, and no
      hyperkahler ALE resolution applies (derived_contribution_table).
  R2  n_faces = 4 is the number of coordinates an involution MOVES, and the
      moved set is a Fano arc (joyce_orbifold).

the reachable profiles are n_T3 in {0, 4, 8, 12}, giving

      n_T3     b_2     b_3     n_gen = b_2 / 4
        0       0       7            0
        4       4      19            1
        8       8      31            2
       12      12      43            3

so across the whole family **b_3 = 7 + 3 b_2** -- b_2 and b_3 are NOT
independent, and the construction carries ONE topological input, not two.

And then:

  * n_gen <= 3 ALWAYS. There are 3 singular involutions carrying 4 families
    each, so n_T3 <= 12, so b_2 <= 12. **Three generations is the maximum this
    construction admits.**
  * n_gen = 3 is attained by exactly ONE profile. So the observed generation
    count FORCES (b_2, b_3) = (12, 43).

Three generations stops being an output the model must reproduce and becomes a
SELECTOR that picks the topology out of four candidates. Nothing is fitted: the
four candidates were enumerated before the count was applied.

THE OTHER ROUTE IS NOT MERELY WORSE, IT IS EMPTY
=================================================
The `n_gen_source` fork's other branch takes n_gen = b_3 / 8, the 8 being dim O.
On this family it yields an integer NOWHERE:

    b_3 = 7 + 3 n_T3 with n_T3 even  =>  b_3 is odd at every profile,
    and 8 divides no odd number.

    b_3/8  =  0.875,  2.375,  3.875,  5.375

So `b3_over_dim_O` does not give a wrong generation count on the Joyce family --
it gives no generation count at all, at any reachable profile. That is a
stronger statement than "43/8 is not an integer", which is about one point.

SCOPE, STATED
=============
This is a selection WITHIN the declared construction, not a proof that the
universe is a Joyce orbifold. It says: IF the manifold is a Joyce (Z/2)^3
resolution of T^7/Gamma with Gamma the stabiliser of this phi, and IF n_gen =
b_2/n_faces, THEN three generations forces b_3 = 43. Both premises are the
author's to rule on; the fork `n_gen_source` carries the second.

It also does not rescue b_3 = 24: 7 + 3*4 = 19, so the adopted (24, 4) pair does
not satisfy the family relation and is not one of the four candidates. That is a
third independent route to the same exclusion, alongside b_3 = 7 (mod 12) and
the TCS range 71-155.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

__all__ = [
    "family_profiles",
    "generations_by_route",
    "select_by_generation_count",
    "selection_report",
]

#: The faces an involution moves. Derived in joyce_orbifold R2, not chosen.
_N_FACES = 4
#: dim O, the divisor the other n_gen route uses.
_DIM_O = 8


def family_profiles() -> List[Dict[str, int]]:
    """The reachable (n_T3, b_2, b_3), read from the contribution table."""
    from metaphysica.simulations.PM.geometry.derived_contribution_table import (
        FLAT_B2,
        FLAT_B3,
    )

    return [{"n_T3": n, "b2": FLAT_B2 + n, "b3": FLAT_B3 + 3 * n}
            for n in (0, 4, 8, 12)]


def generations_by_route(b2: int, b3: int) -> Dict[str, Dict[str, Any]]:
    """Both n_gen routes at one profile, with integrality reported per route."""
    def entry(value: float, formula: str) -> Dict[str, Any]:
        integral = abs(value - round(value)) < 1e-12
        return {"value": value, "is_integer": integral,
                "as_count": int(round(value)) if integral else None,
                "formula": formula}

    return {
        "b2_over_faces": entry(b2 / float(_N_FACES),
                               "b_2 / %d, the %d being the moved coordinates "
                               "of an involution (R2)" % (_N_FACES, _N_FACES)),
        "b3_over_dim_O": entry(b3 / float(_DIM_O),
                               "b_3 / %d, the %d being dim O" % (_DIM_O, _DIM_O)),
    }


def select_by_generation_count(n_gen: int = 3,
                               route: str = "b2_over_faces"
                               ) -> Dict[str, Any]:
    """Which reachable profiles give exactly `n_gen` generations by `route`.

    The candidates are enumerated BEFORE the count is applied, so a unique
    survivor is a selection and not a fit.
    """
    profiles = family_profiles()
    matches = []
    for prof in profiles:
        routes = generations_by_route(prof["b2"], prof["b3"])
        entry = routes[route]
        if entry["is_integer"] and entry["as_count"] == n_gen:
            matches.append(prof)

    return {
        "n_gen_requested": n_gen,
        "route": route,
        "n_candidates_before": len(profiles),
        "n_matching": len(matches),
        "matches": matches,
        "is_unique": len(matches) == 1,
        "selected": matches[0] if len(matches) == 1 else None,
    }


def selection_report() -> Dict[str, Any]:
    """The full statement, with both routes and the scope."""
    profiles = family_profiles()
    table = []
    for prof in profiles:
        routes = generations_by_route(prof["b2"], prof["b3"])
        table.append({
            **prof,
            "b3_eq_7_plus_3b2": prof["b3"] == 7 + 3 * prof["b2"],
            "n_gen_b2_over_faces": routes["b2_over_faces"]["as_count"],
            "n_gen_b3_over_dim_O": routes["b3_over_dim_O"]["value"],
            "b3_over_dim_O_is_integer": routes["b3_over_dim_O"]["is_integer"],
        })

    by_b2 = select_by_generation_count(3, "b2_over_faces")
    by_b3 = select_by_generation_count(3, "b3_over_dim_O")

    reachable_counts = sorted({row["n_gen_b2_over_faces"] for row in table})
    max_reachable = max(reachable_counts)

    return {
        "premises": {
            "R1": "Gamma = (Z/2)^3 is the diagonal stabiliser of phi, forced",
            "A1": ("every admissible component is A1; orders 4 and 8 flip two "
                   "of four transverse coordinates, sit outside SU(2), and "
                   "admit no hyperkahler ALE resolution"),
            "R2": "n_faces = 4 is the moved-coordinate count of an involution",
        },
        "table": table,
        "family_relation": "b_3 = 7 + 3 b_2",
        "family_relation_holds": all(r["b3_eq_7_plus_3b2"] for r in table),
        "one_input_not_two": (
            "b_2 and b_3 are both functions of n_T3, so the construction "
            "carries ONE topological input"
        ),
        "reachable_generation_counts": reachable_counts,
        "max_generations": max_reachable,
        "three_is_the_maximum": max_reachable == 3,
        "why_three_is_maximal": (
            "3 singular involutions carry 4 families each, so n_T3 <= 12 and "
            "b_2 <= 12; n_gen = b_2/4 <= 3"
        ),
        "selection_by_b2_route": by_b2,
        "selection_by_b3_route": by_b3,
        "b3_route_is_empty_on_this_family": by_b3["n_matching"] == 0,
        "why_the_b3_route_is_empty": (
            "b_3 = 7 + 3 n_T3 with n_T3 even is ODD at every profile, and 8 "
            "divides no odd number, so b_3/8 yields an integer NOWHERE on the "
            "family -- not merely a wrong value at one point"
        ),
        "adopted_pair_is_on_the_family": (7 + 3 * 4) == 24,
        "scope": (
            "a selection WITHIN the declared construction, not a proof of it. "
            "IF the manifold is a Joyce (Z/2)^3 resolution of T^7/Gamma for "
            "this phi, AND n_gen = b_2/n_faces, THEN three generations forces "
            "b_3 = 43. Both premises are author rulings; n_gen_source carries "
            "the second."
        ),
        "counts": (
            "b_2 and b_3 count cohomology classes; n_T3 counts A1 families; "
            "n_faces counts moved coordinates of a group element. n_gen is a "
            "ratio of a class count to a coordinate count and is asserted to "
            "be a number of things only because it must be an integer."
        ),
    }
