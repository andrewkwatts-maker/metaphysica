"""The reachable Joyce family, member by member: cohomology, chi, pi_1, holonomy.

Pre-registered as D-001 and D-002 in the site repo's docs/DECISION_LOG.md
(2026-09-30) before any of this was run.

THE TABLE
=========
For each member of the family b_3 = 7 + 3 b_2 (b3_path.PATHS), a
representative admissible assignment is found by search and its resolution
computed (joyce_resolution): the full Betti sequence, Poincare duality, the
Euler characteristic, and the singular components' own cohomology. Then
pi_1 is decided (fundamental_group.pi1_finiteness).

THE SELECTION IT EXPOSES (D-002)
================================
n singular involutions are linearly independent over F_2 -- if sigma and
tau are singular with disjoint fixed sets, sigma.tau is not singular -- so
their span has rank n = b_2/4. When the span is a proper subgroup, some
coordinate is fixed by all of them and pi_1 is infinite; when it is all of
Gamma, pi_1 = 1. So on the family, pi_1 is finite at n = 3 only.

Cited, not computed: for a compact torsion-free G_2-structure,
Hol = G_2 iff pi_1 is finite (D. D. Joyce, Compact Manifolds with Special
Holonomy, OUP 2000). With infinite pi_1 the universal cover splits as
R^k x N (Cheeger-Gromoll), and the restricted holonomy is that of N: trivial,
SU(2) (N = K3) or SU(3) (N a Calabi-Yau threefold) for k = 7, 3, 1. The
family is therefore the tower of special holonomies in seven dimensions, and
holonomy exactly G_2 -- the construction's own defining property -- holds
exactly when n = 3.

SCOPE OF "THE FAMILY" (red-team finding, 2026-09-30, D-006)
===========================================================
The four members here are the ALL-PLAIN subfamily that the A1 filter
(derived_contribution_table.all_components_are_a1) leaves. That filter tests
a component's setwise stabiliser, not the isotropy at its points; under
pairwise disjointness every singular point is already A1, and a free extra
stabiliser is exactly Joyce's JDG II setting (Example 4: b_2 = 8 + l,
b_3 = 47 - l, l = 0..8, all simply connected with holonomy G_2). In the full
family "finite pi_1 iff n = 3" still holds, but n = 3 is the whole line
b_2 + b_3 = 55, so holonomy selects that line and (12, 43) is unique only
inside the all-plain subfamily.

WHAT DOES NOT DISCRIMINATE (recorded so the wrong argument is not made):
supersymmetry. Under G_2 the spinor is 1 + 7, and extra parallel spinors are
parallel 1-forms, which on a compact Ricci-flat manifold are the harmonic
ones (Bochner). b_1 = 0 on every member, so every member gives N = 1.

SCOPE: holonomy is a Riemannian statement and applies on the compact real
form. On the split form only the topological half holds (pi_1 = 1 exactly at
n = 3). Which real form is adopted is the G3 ruling.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional

__all__ = [
    "RESTRICTED_HOLONOMY_BY_FLAT_RANK",
    "family_table",
    "independence_sweep",
    "holonomy_selection",
]

#: The restricted holonomy implied by k flat directions of the universal
#: cover, for a compact torsion-free G_2-structure. CITED consequences of
#: Cheeger-Gromoll and the classification of compact simply connected
#: Ricci-flat 4- and 6-manifolds with holonomy in SU(2), SU(3) -- not computed
#: here. k = 0 needs pi_1 finite, and then Hol = G_2 (Joyce).
RESTRICTED_HOLONOMY_BY_FLAT_RANK = {
    7: "trivial (flat)",
    3: "SU(2): universal cover R^3 x K3",
    1: "SU(3): universal cover R x (Calabi-Yau threefold)",
    0: "G2",
}

#: Surviving directions each n must leave: the coordinates whose character
#: vanishes on an n-dimensional span of Gamma = F_2^3, i.e. 2^(3-n) - 1.
EXPECTED_FLAT_RANK = {0: 7, 1: 3, 2: 1, 3: 0}


def _declared_betti(b2: int, b3: int) -> Dict[int, int]:
    return {0: 1, 1: 0, 2: b2, 3: b3, 4: b3, 5: b2, 6: 0, 7: 1}


def _member_row(name: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.fundamental_group import (
        pi1_finiteness,
    )
    from metaphysica.simulations.PM.geometry.joyce_resolution import (
        representative_point,
        resolution_report,
    )

    n = profile["n_t3"] // 4
    point = representative_point(n)
    res = resolution_report(point)
    pi1 = pi1_finiteness(point)
    k = pi1["flat_rank_k"]
    return {
        "path": name,
        "derived": True,
        "n_singular": n,
        "declared": (profile["b2"], profile["b3"]),
        "derived_pair": (res["b2"], res["b3"]),
        "matches_declared": (res["b2"], res["b3"]) == (profile["b2"],
                                                        profile["b3"]),
        "betti": res["betti"],
        "poincare_duality_holds": res["poincare_duality_holds"],
        "euler_characteristic": res["euler_characteristic"],
        "n_components": res["n_components"],
        "every_component_is_flat_T3": res["every_component_is_flat_T3"],
        "flat_rank_k": k,
        "pi1_finite": pi1["pi1_finite"],
        "pi1_sides_agree": pi1["sides_agree"],
        "restricted_holonomy": RESTRICTED_HOLONOMY_BY_FLAT_RANK.get(
            k, "UNCLASSIFIED (k = %d)" % k),
        "full_g2_holonomy": pi1["pi1_finite"],
    }


def _off_family_row(name: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    betti = _declared_betti(profile["b2"], profile["b3"])
    return {
        "path": name,
        "derived": False,
        "declared": (profile["b2"], profile["b3"]),
        "betti": betti,
        "poincare_duality_holds": True,
        "euler_characteristic": sum((-1) ** k * b for k, b in betti.items()),
        "label": (
            "OFF-FAMILY: no admissible assignment reaches this pair, so the "
            "sequence is DECLARED from (b_2, b_3) with b_1 = 0, not derived. "
            "chi = 0 here is Poincare duality alone."
        ),
    }


def family_table() -> List[Dict[str, Any]]:
    """Every profile in b3_path.PATHS, derived where the construction reaches
    it and labelled where it does not."""
    from metaphysica.simulations.PM.geometry.b3_path import PATHS

    rows = []
    for name, profile in sorted(PATHS.items(),
                                key=lambda kv: (not kv[1].get(
                                    "reachable_by_joyce"), kv[1]["b3"])):
        if profile.get("reachable_by_joyce"):
            rows.append(_member_row(name, profile))
        else:
            rows.append(_off_family_row(name, profile))
    return rows


def _span_rank(labels) -> int:
    span = {(0, 0, 0)}
    for lab in labels:
        span |= {tuple((x + y) % 2 for x, y in zip(lab, s)) for s in span}
    return len(span).bit_length() - 1


def independence_sweep(max_assignments: Optional[int] = None
                       ) -> Dict[str, Any]:
    """Every admissible assignment (or the first `max_assignments` of the
    search space): singular involutions independent, surviving directions as
    predicted, and pi_1 finite exactly when none survive.

    The whole space is 458,752 assignments; the full sweep is a slow test.
    """
    from metaphysica.simulations.PM.geometry.fundamental_group import (
        pi1_finiteness,
    )
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        elements,
    )
    from metaphysica.simulations.PM.geometry.joyce_resolution import (
        _admissible,
        _search_space,
        _singular_of,
    )

    visited = admissible = 0
    by_n: Dict[int, int] = {}
    violations: List[Dict[str, Any]] = []
    space = _search_space()
    if max_assignments is not None:
        space = itertools.islice(space, max_assignments)
    for triple, gens, svecs in space:
        visited += 1
        els = elements(gens, svecs)
        singular = _singular_of(els)
        if not _admissible(els, singular):
            continue
        admissible += 1
        n = len(singular)
        by_n[n] = by_n.get(n, 0) + 1
        point = {"elements": els, "singular": singular}
        pi1 = pi1_finiteness(point)
        rank = _span_rank([lab for lab, _e in singular])
        ok = (rank == n
              and pi1["flat_rank_k"] == EXPECTED_FLAT_RANK.get(n)
              and pi1["sides_agree"]
              and pi1["pi1_finite"] == (n == 3))
        if not ok and len(violations) < 10:
            violations.append({"triple": triple, "shifts": svecs, "n": n,
                               "rank": rank, "k": pi1["flat_rank_k"],
                               "sides_agree": pi1["sides_agree"]})
    return {
        "visited": visited,
        "admissible": admissible,
        "admissible_by_n_singular": dict(sorted(by_n.items())),
        "violations": violations,
        "holds": not violations and admissible > 0,
    }


def holonomy_selection() -> Dict[str, Any]:
    """D-002's verdict: which family members carry holonomy exactly G_2."""
    rows = [r for r in family_table() if r["derived"]]
    full = [r for r in rows if r["full_g2_holonomy"]]
    return {
        "members": [(r["path"], r["declared"], r["restricted_holonomy"])
                    for r in rows],
        "full_holonomy_members": [r["path"] for r in full],
        "unique": len(full) == 1,
        "selected": full[0]["declared"] if len(full) == 1 else None,
        "n_gen_at_selection": (full[0]["declared"][0] // 4
                               if len(full) == 1 else None),
        "uniqueness_scope": (
            "unique only inside the all-plain (A1-filtered) subfamily; in "
            "Joyce's full family every n = 3 member (the line "
            "b_2 + b_3 = 55, JDG II Example 4) has finite pi_1 -- D-006"),
        "scope": (
            "Riemannian holonomy: applies on the compact real form "
            "(g2_form_convention = octonion_derived). On the split form only "
            "the topological statement holds: pi_1 = 1 exactly at n = 3."
        ),
        "not_a_discriminator": (
            "supersymmetry: b_1 = 0 on every member, so each has exactly one "
            "parallel spinor and gives N = 1"
        ),
    }
