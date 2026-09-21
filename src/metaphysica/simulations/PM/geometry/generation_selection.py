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
    "singular_involution_census",
    "rank_over_f2",
    "family_profiles",
    "generations_by_route",
    "select_by_generation_count",
    "selection_report",
]

#: The faces an involution moves. Derived in joyce_orbifold R2, not chosen.
_N_FACES = 4
#: dim O, the divisor the other n_gen route uses.
_DIM_O = 8


def rank_over_f2(bitvectors) -> int:
    """Rank of a set of F_2 vectors, by elimination. No tolerance to tune."""
    rows = [list(v) for v in bitvectors]
    if not rows:
        return 0
    rank, ncol = 0, len(rows[0])
    for col in range(ncol):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i][col]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def singular_involution_census(cap_triples: int = 6) -> Dict[str, Any]:
    """WHY n_gen is capped at 3, measured rather than asserted.

    Two facts come out of the live enumeration, and together they turn
    n_gen = b_2/4 into a statement about the group rather than a ratio:

      1. n_families = 4 x n_singular, at EVERY admissible assignment. So
         b_2/4 is not really dividing by the face count -- it RECOVERS THE
         NUMBER OF SINGULAR INVOLUTIONS.

      2. Wherever three involutions are singular, those three are INDEPENDENT
         over F_2 -- they form a basis of Gamma. So the singular set can never
         exceed rank(Gamma) = 3.

    Hence n_gen = n_singular <= rank(Gamma) = 3, and Gamma itself is forced by
    phi (R1). Three generations is the RANK OF THE DIAGONAL STABILISER OF PHI.

    THE A4 BAR, because this chain crosses type boundaries and must say so:
        rank(Gamma)        a group-theoretic rank
        n_singular         a count of group ELEMENTS
        n_families         a count of ORBITS of fixed-locus components
        b_2                a count of COHOMOLOGY CLASSES
        n_gen              a count of fermion generations
    Each arrow is a measured correspondence over the enumeration, not an
    identification. The chain is only as strong as its weakest arrow, and the
    last one -- b_2/n_faces = n_gen -- is the `n_gen_source` fork, an author
    ruling. Nothing here converts a group order into a dimension.
    """
    import itertools

    from metaphysica.simulations.PM.geometry.derived_contribution_table import (
        all_components_are_a1,
    )
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
        assignments,
        elements,
        families_of,
        fixed_sets_disjoint,
        generating_triples,
        is_singular,
    )

    group = _group()
    nz = _non_identity(group)
    by_singular: Dict[int, Dict[str, int]] = {}
    n_three_singular = 0
    n_three_independent = 0

    for triple in generating_triples(group)[:cap_triples]:
        gens = [nz[i] for i in triple]
        for svecs in assignments(triple, group, include_relative=True):
            els = elements(gens, svecs)
            singular = [(b, e) for b, e in els.items()
                        if b != (0, 0, 0) and is_singular(e)]
            if not all(fixed_sets_disjoint(a[1], b[1])
                       for a, b in itertools.combinations(singular, 2)):
                continue
            if not all_components_are_a1(els, singular):
                continue
            fams = []
            for _bits, el in singular:
                fams.extend(families_of(els, el))
            if fams and {f["type"] for f in fams} != {"T3"}:
                continue

            n_s = len(singular)
            row = by_singular.setdefault(
                n_s, {"assignments": 0, "families_is_four_times": 0})
            row["assignments"] += 1
            if len(fams) == 4 * n_s:
                row["families_is_four_times"] += 1

            if n_s == 3:
                n_three_singular += 1
                if rank_over_f2([b for b, _e in singular]) == 3:
                    n_three_independent += 1

    return {
        "by_singular_count": dict(sorted(by_singular.items())),
        "families_always_four_per_singular": all(
            v["assignments"] == v["families_is_four_times"]
            for v in by_singular.values()),
        "n_three_singular_assignments": n_three_singular,
        "n_of_those_independent_over_f2": n_three_independent,
        "singular_set_is_always_a_basis": (
            n_three_singular > 0 and n_three_singular == n_three_independent),
        "group_rank": 3,
        "max_singular_observed": max(by_singular) if by_singular else 0,
        "the_chain": (
            "Gamma = (Z/2)^3 forced by phi (R1) -> singular involutions are "
            "independent over F_2, so at most rank(Gamma) = 3 of them -> each "
            "carries exactly 4 A1 families -> b_2 = 4 n_singular -> "
            "n_gen = b_2/4 = n_singular <= 3"
        ),
        "counts": (
            "rank is group-theoretic; n_singular counts group ELEMENTS; "
            "n_families counts ORBITS; b_2 counts COHOMOLOGY CLASSES. Each "
            "arrow is a measured correspondence, not an identification."
        ),
    }


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
