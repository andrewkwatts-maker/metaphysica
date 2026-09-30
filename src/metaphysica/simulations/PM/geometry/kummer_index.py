"""The K3 reading of chi_eff: one Kummer surface per singular involution (G1).

Pre-registered as D-009 (site repo docs/DECISION_LOG.md, 2026-09-30) before
this was run, after a neutral inventory of chi_eff's 946 consumers.

THE OBJECT
==========
A singular involution sigma acts on its four flipped coordinates as
x -> -x + s: a copy of the Kummer involution on a transverse T^4. Its fixed
points are counted here, not assumed, and the resolved quotient's Euler
characteristic is computed two ways:

  * from the quotient:  chi(T^4/{+-1}) = (chi(T^4) - F)/2 + F, then +1 for each
    A1 point replaced by a CP^1;
  * from Betti numbers: b_0 = b_4 = 1, b_1 = b_3 = 0 (odd forms are
    anti-invariant under -1), b_2 = (invariant 2-forms) + F.

For F = 16 both give 24, and b_2 = 6 + 16 = 22: the Kummer K3.

THE READING
===========
    chi_eff := 2 * sum_{sigma singular} chi(K3_sigma) = 48 n

-- 72 per shadow and 144 in total at n = 3, which is exactly the registry's
existing mephorash_chi / chi_eff_total, now with an object behind them. Then
n_gen = chi_eff / 48 = n: THE SAME STATEMENT as counting singular involutions,
not a second derivation. Its merit over b_2 / 4 is that it holds on Joyce's
whole corrected family (D-006); b_2 / 4 equals n only on the all-plain members.

A4: F counts points, chi counts an alternating sum of Betti numbers of a real
4-manifold, n counts group elements, and the factor 2 counts shadows.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Any, Dict, List

__all__ = [
    "transverse_fixed_points",
    "kummer_euler",
    "kummer_betti",
    "k3_reading",
    "family_sweep",
]

_QUARTERS = (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))


def transverse_fixed_points(sigma) -> int:
    """Points of sigma's transverse torus it fixes, counted on the quarter
    lattice (every fixed point of x -> -x + s/2 lies on it)."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        moved_coords,
    )

    eps, shift = sigma
    moved = moved_coords(eps)
    count = 0
    for x in itertools.product(_QUARTERS, repeat=len(moved)):
        if all(((-xa + Fraction(shift[a], 2)) - xa) % 1 == 0
               for xa, a in zip(x, moved)):
            count += 1
    return count


def kummer_euler(n_fixed: int) -> int:
    """chi of T^4/{+-1} with each fixed point resolved by a CP^1."""
    quotient = Fraction(0 - n_fixed, 2) + n_fixed
    return int(quotient + n_fixed * (2 - 1))


def kummer_betti(n_fixed: int) -> Dict[int, int]:
    """Betti numbers of the resolved quotient, from invariant forms."""
    invariant_two_forms = sum(1 for _ in itertools.combinations(range(4), 2))
    return {0: 1, 1: 0, 2: invariant_two_forms + n_fixed, 3: 0, 4: 1}


def k3_reading(point: Dict[str, Any]) -> Dict[str, Any]:
    """chi_eff under the K3 reading, for one assignment."""
    rows = []
    for label, sigma in point["singular"]:
        fixed = transverse_fixed_points(sigma)
        betti = kummer_betti(fixed)
        rows.append({
            "involution": tuple(label),
            "fixed_points": fixed,
            "chi": kummer_euler(fixed),
            "chi_from_betti": sum((-1) ** k * b for k, b in betti.items()),
            "b2": betti[2],
        })
    per_shadow = sum(r["chi"] for r in rows)
    chi_eff = 2 * per_shadow
    return {
        "n_singular": len(rows),
        "kummer": rows,
        "per_shadow": per_shadow,
        "chi_eff": chi_eff,
        "n_gen": Fraction(chi_eff, 48),
        "consistent": all(r["chi"] == r["chi_from_betti"] == 24
                          for r in rows),
    }


def family_sweep() -> Dict[str, Any]:
    """Every pairwise-disjoint class of the first generating triple: does
    chi_eff / 48 equal n, and where does b_2 / 4 fail to?"""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
        assignments,
        elements,
        fixed_sets_disjoint,
        generating_triples,
        is_singular,
    )
    from metaphysica.simulations.PM.geometry.joyce_reachability import (
        class_options,
    )

    group = _group()
    nz = _non_identity(group)
    triple = generating_triples(group)[0]
    gens = [nz[i] for i in triple]
    classes = k3_holds = 0
    b2_pairs_total = b2_pairs_matching_n = 0
    failures: List[Dict[str, Any]] = []
    for svecs in assignments(triple, group, include_relative=True):
        els = elements(gens, svecs)
        singular = [(b, e) for b, e in els.items()
                    if b != (0, 0, 0) and is_singular(e)]
        if not all(fixed_sets_disjoint(a[1], b[1])
                   for a, b in itertools.combinations(singular, 2)):
            continue
        classes += 1
        reading = k3_reading({"singular": singular})
        n = len(singular)
        if reading["consistent"] and reading["n_gen"] == n:
            k3_holds += 1
        elif len(failures) < 5:
            failures.append({"shifts": svecs, "reading": reading})
        _profile, pairs = class_options(els, singular)
        for b2, _b3 in pairs:
            b2_pairs_total += 1
            b2_pairs_matching_n += int(Fraction(b2, 4) == n)
    return {
        "classes": classes,
        "k3_reading_equals_n": k3_holds,
        "k3_failures": failures,
        "b2_over_4_equals_n": b2_pairs_matching_n,
        "reachable_pairs_checked": b2_pairs_total,
        "holds": classes > 0 and k3_holds == classes,
    }
