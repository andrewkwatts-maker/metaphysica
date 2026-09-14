"""Derive the resolution contribution table, rather than transcribe it.

THE (15, 24) VERDICT IS WITHDRAWN. READ THIS FIRST.
===================================================
An earlier version of this module concluded that b_3 = 24 is reachable uniquely
at (b_2, b_3) = (15, 24), via the (0,16) profile. That conclusion is WITHDRAWN,
and the flaw was found by following the author's observation that one face sits
lop-sided.

The Kunneth derivation below models the transverse singularity as C^2/{+-1} --
the A1 case, transverse group of order 2. That is correct only when a
component's stabiliser is exactly <sigma>. Measured over the enumeration, the
stabilisers are NOT all of that form:

    |stabiliser|   transverse group   orbit size   count    type
             2                    2            4   43664    A1, C^2/{+-1}
             4                    4            2    4688    WORSE THAN A1
             8                    8            1      16    WORSE THAN A1

The 16 families of the (0,16) profile -- the ONLY profile that reached
b_3 = 24 -- are exactly the orbit-size-1 rows: each component is stabilised by
the WHOLE group, so its transverse quotient is C^2 by a group of order 8, not
order 2. Eguchi-Hanson resolves C^2/{+-1}; it does not resolve C^2/(order 8),
whose resolution has a different and larger exceptional divisor.

So (15, 24) rested on applying an A1 model outside its domain, to the one
profile where the singularity is worst. It is retracted rather than adjusted:
b_3 = 24 for this construction returns to UNDETERMINED.

WHAT SURVIVES
=============
The A1 rows are genuine. For components whose stabiliser is exactly <sigma>
(43,664 of them, orbit size 4), the derivation below holds as written, and the
corroborations it produced -- the canonical (12, 43) and the b_2 + b_3 = 55
series -- come from profiles built of plain and single-reflection families, not
from the order-8 rows. Those are unaffected.

WHAT IS NOW NEEDED, AND IT IS SMALLER THAN A BOOK
=================================================
The resolution data for C^2/G with |G| = 4 and 8 acting as a subgroup of the
diagonal sign group. These are A_k / D_k type quotient singularities whose
resolutions are classical (McKay correspondence: the exceptional divisor's
second cohomology has one class per non-trivial conjugacy class of G). That is
derivable in the same style as the A1 case and is the next mechanism to build
-- NOT an invented constant, and not a citation either.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.


ORIGINAL MODULE DOCUMENTATION FOLLOWS, VALID FOR THE A1 ROWS ONLY
================================================================

THE MECHANISM, WHICH IS THE POINT
=================================
The Joyce gate has been waiting on a CITED contribution table (ch. 12). But the
table is not physics data -- it is computable mathematics, and this module
computes it, from three ingredients:

1.  EGUCHI-HANSON COHOMOLOGY. Resolving C^2/{+-1} replaces it with T*S^2 (the
    Eguchi-Hanson space), which deformation-retracts onto the exceptional S^2.
    Hence H^0 = Z, H^2 = Z, everything else 0. Textbook topology, not a cited
    constant.

2.  KUNNETH ON T^3 x EH. A plain T^3 family resolves to T^3 x EH locally. The
    NEW classes relative to the orbifold are the products with the exceptional
    H^2(EH):
        Delta b_2 = dim H^0(T^3) * dim H^2(EH) = 1
        Delta b_3 = dim H^1(T^3) * dim H^2(EH) = 3
    (The T^3 fundamental class itself is NOT new -- the three fixed coordinates
    of sigma form a Fano line, whose 3-form is already one of the 7 flat
    invariants. Verified in joyce_orbifold R3.)

3.  INVARIANTS FOR REFLECTED FAMILIES. When a component's stabiliser contains a
    reflection delta, the contribution is the delta-INVARIANT part. Two facts
    decide it:

    k = dim H^1(T^3)^delta = 1, ALWAYS. Derivation: delta's linear part fixes
    its own Fano line L_delta, and two distinct lines of PG(2,2) meet in
    exactly one point, so delta flips exactly 2 of sigma's 3 fixed coordinates.
    Verified computationally over 35,712 reflection stabilisers in admissible
    assignments: k = 1 in every case, no exceptions.

    epsilon = delta's action on H^2(EH) is +1 or -1 according to the choice of
    resolution (delta acts on the transverse C^2 by a det=+1 diagonal map --
    it flips exactly 2 of sigma's 4 moved coordinates, arcs meeting in 2
    points -- which is holomorphic for one compatible complex structure and
    anti-holomorphic for the other; the two resolutions realise both). Hence
    per reflected family the TWO available contributions are

        epsilon = +1:  (Delta b_2, Delta b_3) = (1, k)     = (1, 1)
        epsilon = -1:  (Delta b_2, Delta b_3) = (0, 3 - k) = (0, 2)

THE ASSUMPTION, STATED
======================
Ingredients 1 and 2 are solid topology. Ingredient 3 carries one assumption:
that both resolution choices are available independently at every reflected
family (the epsilon-dichotomy). It is the same freedom Joyce's tables use --
one orbifold, several (b_2, b_3) -- and it is corroborated below by the
b_2 + b_3 = 55 series falling out, but it is an assumption and every verdict
downstream is CONDITIONAL_ON_DERIVED_TABLE until checked against the book.
This module does not touch the cited-table gate: a book table, when supplied,
CHECKS this derivation rather than being replaced by it.

WHAT FALLS OUT (computed in reachable_set, pinned by tests)
===========================================================
With flat (b_2, b_3) = (0, 7) [both derived] and the admissible profiles from
the corrected survey -- (n_T3, n_reflected) in {(0,0), (4,0), (8,0), (12,0),
(4,8), (8,8), (0,8), (0,16)} -- the reachable pairs include:

    (12, 43) from (12, 0)   -- the canonical Joyce structure's value, derived
                               here from pure Kunneth arithmetic
    b_2 + b_3 = 55 series from (8,8) and (12,0) -- (8,47) ... (16,39)
    b_3 = 24 REACHABLE, and ONLY via the (0,16) profile with exactly one
    family taking the epsilon = -1 resolution:  (b_2, b_3) = (15, 24)

    (4, 24) and (7, 24): UNREACHABLE. No profile and no choice of resolutions
    produces either.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Set, Tuple

__all__ = [
    "transverse_group_census",
    "eguchi_hanson_betti",
    "derived_table",
    "verify_k_equals_one",
    "profile_reachable",
    "reachable_set",
    "b3_verdict",
]

#: Flat contributions of T^7/Gamma itself, both DERIVED in joyce_orbifold:
#: b_2 flat = 0 (each 2-form carries a non-trivial character product) and
#: b_3 flat = 7 (exactly phi's triples survive).
FLAT_B2 = 0
FLAT_B3 = 7


def eguchi_hanson_betti() -> Dict[int, int]:
    """H^*(Eguchi-Hanson): retracts to the exceptional S^2."""
    return {0: 1, 1: 0, 2: 1, 3: 0}


def derived_table() -> Dict[str, Any]:
    """The contribution table, with its derivation and its one assumption."""
    eh = eguchi_hanson_betti()
    plain = (eh[0] * 1, eh[2] * 3)          # Kunneth: (1, 3)
    k = 1                                    # verified: verify_k_equals_one()
    return {
        "T3": {"options": [{"b2": plain[0] * eh[2], "b3": plain[1]}],
               "derivation": "Kunneth on T^3 x EH; new classes are products "
                             "with the exceptional H^2"},
        "T3_reflected": {
            "options": [
                {"b2": 1, "b3": k, "resolution": "epsilon=+1"},
                {"b2": 0, "b3": 3 - k, "resolution": "epsilon=-1"},
            ],
            "derivation": "delta-invariants of the Kunneth classes; k = 1 "
                          "because two Fano lines meet in one point",
        },
        "status": "DERIVED_KUNNETH",
        "assumption": (
            "epsilon-dichotomy: both resolutions available independently at "
            "every reflected family. Every downstream verdict is "
            "CONDITIONAL_ON_DERIVED_TABLE until checked against Joyce ch. 12."
        ),
        "checks_against_literature": (
            "reproduces (12, 43) for the canonical 12-family structure and "
            "the b_2 + b_3 = 55 series from the (8,8) profile"
        ),
    }


def verify_k_equals_one(n_triples: int = 4, stride: int = 7,
                        cap: int = 5000) -> Dict[str, Any]:
    """Recompute k over admissible assignments. The derivation, not a constant.

    k is claimed to be 1 because two distinct Fano lines meet in exactly one
    point, so a stabilising reflection flips exactly 2 of sigma's 3 fixed
    coordinates. This function measures it from the live enumeration so the
    claim fails loudly if the group data ever changes.
    """
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        act_on_component,
        assignments,
        elements,
        fixed_coords,
        generating_triples,
        is_singular,
        moved_coords,
    )
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
    )

    group = _group()
    nz = _non_identity(group)
    seen: Dict[int, int] = {}
    checked = 0
    for tri in generating_triples(group)[:n_triples]:
        gens = [nz[i] for i in tri]
        for svecs in itertools.islice(
                assignments(tri, group, include_relative=True),
                0, None, stride):
            els = elements(gens, svecs)
            singular = [(b, e) for b, e in els.items()
                        if b != (0, 0, 0) and is_singular(e)]
            admissible = all(
                any(x[1][0][c] < 0 and y[1][0][c] < 0
                    and x[1][1][c] != y[1][1][c] for c in range(7))
                for x, y in itertools.combinations(singular, 2))
            if not admissible:
                continue
            for _bits, (eps, s) in singular:
                moved = moved_coords(eps)
                fixed = fixed_coords(eps)
                comps = [dict(zip(moved, c))
                         for c in itertools.product((0, 1), repeat=len(moved))]
                for comp in comps:
                    key = tuple(sorted(comp.items()))
                    for delta in els.values():
                        de, _ds = delta
                        if act_on_component(delta, (eps, s), comp) != key:
                            continue
                        if all(de[b] > 0 for b in fixed):
                            continue          # trivial or translation, not a reflection
                        k = sum(1 for b in fixed if de[b] > 0)
                        seen[k] = seen.get(k, 0) + 1
                        checked += 1
                        if checked >= cap:
                            return {"checked": checked, "k_values": seen,
                                    "always_one": set(seen) == {1}}
    return {"checked": checked, "k_values": seen,
            "always_one": set(seen) == {1} if seen else None}


def profile_reachable(n_t3: int, n_reflected: int
                      ) -> Set[Tuple[int, int]]:
    """Every (b_2, b_3) one profile reaches over its resolution choices."""
    table = derived_table()
    t3 = table["T3"]["options"][0]
    ra, rb = table["T3_reflected"]["options"]
    out: Set[Tuple[int, int]] = set()
    for n_b in range(n_reflected + 1):        # families taking epsilon = -1
        n_a = n_reflected - n_b
        b2 = FLAT_B2 + n_t3 * t3["b2"] + n_a * ra["b2"] + n_b * rb["b2"]
        b3 = FLAT_B3 + n_t3 * t3["b3"] + n_a * ra["b3"] + n_b * rb["b3"]
        out.add((b2, b3))
    return out


def _admissible_profiles(full_survey: Optional[Dict[str, Any]] = None
                         ) -> List[Tuple[int, int]]:
    """(n_T3, n_reflected) per admissible assignment class, from the survey."""
    if full_survey is None:
        from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
            survey,
        )

        full_survey = survey(include_relative=True)
    profiles: Set[Tuple[int, int]] = set()
    for key in full_survey["admissible_type_profiles"]:
        names = eval(key) if key.startswith("(") else ()
        profiles.add((sum(1 for n in names if n == "T3"),
                      sum(1 for n in names if n == "T3_reflected")))
    return sorted(profiles)


def reachable_set(full_survey: Optional[Dict[str, Any]] = None
                  ) -> Dict[str, Any]:
    """All (b_2, b_3) the construction reaches under the derived table."""
    profiles = _admissible_profiles(full_survey)
    pairs: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
    for n_t3, n_refl in profiles:
        for pair in profile_reachable(n_t3, n_refl):
            pairs.setdefault(pair, []).append((n_t3, n_refl))
    return {
        "status": "CONDITIONAL_ON_DERIVED_TABLE",
        "profiles": profiles,
        "n_pairs": len(pairs),
        "pairs": {str(k): v for k, v in sorted(pairs.items())},
        "b3_values": sorted({b3 for _b2, b3 in pairs}),
    }


def transverse_group_census() -> Dict[str, Any]:
    """Measure the transverse group order per family. The check that withdrew
    the (15, 24) verdict, kept live so it cannot be forgotten.

    A1 -- the case the Kunneth derivation models -- requires transverse order 2.
    Anything larger is a worse quotient singularity that Eguchi-Hanson does not
    resolve.
    """
    import collections

    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        act_on_component,
        assignments,
        elements,
        fixed_sets_disjoint,
        generating_triples,
        is_singular,
        moved_coords,
    )
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
    )

    group = _group()
    nz = _non_identity(group)
    census: Dict[int, int] = collections.Counter()
    for tri in generating_triples(group)[:3]:
        gens = [nz[i] for i in tri]
        for svecs in itertools.islice(
                assignments(tri, group, include_relative=True), 0, None, 13):
            els = elements(gens, svecs)
            sing = [(b, e) for b, e in els.items()
                    if b != (0, 0, 0) and is_singular(e)]
            if not all(fixed_sets_disjoint(a[1], b[1])
                       for a, b in itertools.combinations(sing, 2)):
                continue
            for _b, (eps, s) in sing:
                mv = moved_coords(eps)
                for c in itertools.product((0, 1), repeat=len(mv)):
                    comp = dict(zip(mv, c))
                    key = tuple(sorted(comp.items()))
                    stab = [d for d in els.values()
                            if act_on_component(d, (eps, s), comp) == key]
                    transverse = {tuple(d[0][a] for a in mv) for d in stab}
                    census[len(transverse)] += 1
    return {
        "transverse_group_orders": dict(sorted(census.items())),
        "a1_count": census.get(2, 0),
        "worse_than_a1_count": sum(n for k, n in census.items() if k > 2),
        "kunneth_applies_only_to": "transverse order 2 (A1, C^2/{+-1})",
        "why_this_matters": (
            "the (0,16) profile that reached b_3 = 24 consists entirely of "
            "transverse-order-8 components, so the A1 model does not apply "
            "there and the (15, 24) verdict was withdrawn"
        ),
    }


def b3_verdict(full_survey: Optional[Dict[str, Any]] = None
               ) -> Dict[str, Any]:
    """WITHDRAWN. b_3 = 24 is UNDETERMINED for this construction.

    The reachability arithmetic is retained for the A1 rows, but the only
    profile that reached b_3 = 24 was built from transverse-order-8 components
    where the Kunneth/Eguchi-Hanson model does not apply. See the module
    docstring; transverse_group_census() measures it live.
    """
    reach = reachable_set(full_survey)
    hits = [(eval(k), v) for k, v in reach["pairs"].items()
            if eval(k)[1] == 24]
    return {
        "status": "WITHDRAWN_A1_MODEL_MISAPPLIED",
        "b3_24_status": "UNDETERMINED",
        "withdrawn_verdict": "(15, 24) reachable uniquely via the (0,16) profile",
        "why_withdrawn": (
            "the (0,16) profile's components have transverse group order 8, "
            "not 2, so they are not A1 and Eguchi-Hanson does not resolve "
            "them. The A1 contribution table was applied outside its domain."
        ),
        "still_valid": (
            "the A1 rows (43,664 components of transverse order 2) and the "
            "corroborations built from them: (12, 43) and the b_2 + b_3 = 55 "
            "series"
        ),
        "next_mechanism": (
            "resolution data for C^2/G with |G| = 4 and 8 in the diagonal sign "
            "group -- classical quotient singularities, derivable by McKay "
            "(one exceptional 2-class per non-trivial conjugacy class), not an "
            "invented constant and not a citation"
        ),
        "pairs_with_b3_24_under_the_misapplied_model": [k for k, _v in hits],
        "profiles_reaching_it": sorted({p for _k, v in hits for p in v}),
        "pair_4_24_reachable": (4, 24) in [k for k, _ in hits],
        "pair_7_24_reachable": (7, 24) in [k for k, _ in hits],
        "canonical_12_43_reachable": "(12, 43)" in reach["pairs"],
        "assumption": derived_table()["assumption"],
        "what_would_confirm_or_destroy": (
            "Joyce ch. 12's table. If its per-type contributions match the "
            "derived (1,3) / {(1,1),(0,2)}, every verdict here becomes "
            "unconditional; if they differ, the epsilon-dichotomy assumption "
            "was wrong and the derivation is corrected, not the book."
        ),
    }
