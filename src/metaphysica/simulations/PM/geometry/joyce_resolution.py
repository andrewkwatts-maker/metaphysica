"""The full Betti sequence of the resolved Joyce manifold, and chi(Y_7) = 0.

WHAT THIS MODULE DERIVES
========================
Every Betti number of the resolution Y of T^7/Gamma, for any admissible
assignment, from the live enumeration. Nothing here is tabulated:

    H^k(Y) = H^k(T^7/Gamma)  (+)  (+)_j  H^{k-2}(L_j)            (Joyce)

  * the flat sector H^*(T^7/Gamma) is the Gamma-invariant constant forms
    (joyce_orbifold.flat_betti_report: 1, 0, 0, 7, 7, 0, 0, 1);
  * each L_j is one singular component of the QUOTIENT: a Gamma-orbit of fixed
    3-tori of a singular involution, i.e. T^3 / Stab_j. Its cohomology is the
    part of H^*(T^3) invariant under the stabiliser's linear parts on the
    fixed coordinates (translations act trivially on constant forms);
  * the shift by 2 is the exceptional 2-class of the Eguchi-Hanson space that
    replaces each transverse C^2/{+-1}: H^*(T^3 x EH) - H^*(T^3) =
    H^*(T^3) (x) H^2(EH).

The stabiliser must also preserve that exceptional class. On an A1 component
every stabilising element acts on the transverse C^2 as +1 or -1, a scalar,
so it preserves the class; a component where that fails is not A1 and the
Eguchi-Hanson model does not apply there at all
(derived_contribution_table.all_components_are_a1). Both conditions are
checked per component, not assumed.

WHAT CHI(Y_7) = 0 SAYS, AND WHAT IT DOES NOT
============================================
chi = sum (-1)^k b_k vanishes for every closed odd-dimensional manifold, by
Poincare duality. So the value is not the news. What the computation adds is
that the DERIVED sequence has the duality it must have: the flat sector is
self-dual, and each component contributes chi(L_j) = 0 because every L_j is a
closed orientable 3-manifold. A component with the wrong stabiliser action
would break the duality visibly -- that is the falsifier.

The number published as `euler-characteristic` (chi_eff, 144 on the seed_24
model) is NOT this invariant. It is an effective index whose definition is an
open ruling; the Euler characteristic of Y_7 is 0 on every profile.

A4 BAR
======
b_k counts cohomology classes (real dimensions). chi is their alternating sum,
an Euler characteristic. Stabiliser orders and orbit sizes count GROUP
ELEMENTS and COMPONENTS respectively. None is converted into another.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import functools
import itertools
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "representative_point",
    "component_cohomology",
    "singular_components",
    "resolved_betti",
    "poincare_duality_holds",
    "euler_characteristic",
    "resolution_report",
]

_DIM = 7


def _search_space():
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
        assignments,
        generating_triples,
    )

    group = _group()
    nz = _non_identity(group)
    for triple in generating_triples(group):
        for svecs in assignments(triple, group, include_relative=True):
            yield triple, [nz[i] for i in triple], svecs


def _singular_of(els) -> List[Tuple[Tuple[int, ...], Any]]:
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        is_singular,
    )

    return [(b, e) for b, e in els.items()
            if b != (0, 0, 0) and is_singular(e)]


def _admissible(els, singular) -> bool:
    """Joyce admissibility: pairwise-disjoint singular sets, every one A1."""
    from metaphysica.simulations.PM.geometry.derived_contribution_table import (
        all_components_are_a1,
    )
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        fixed_sets_disjoint,
    )

    return (all(fixed_sets_disjoint(a[1], b[1])
                for a, b in itertools.combinations(singular, 2))
            and all_components_are_a1(els, singular))


@functools.lru_cache(maxsize=None)
def _first_admissible(n_singular: int):
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        elements,
    )

    for triple, gens, svecs in _search_space():
        els = elements(gens, svecs)
        singular = _singular_of(els)
        if len(singular) == n_singular and _admissible(els, singular):
            return triple, svecs
    return None


def representative_point(n_singular: int) -> Dict[str, Any]:
    """The first admissible assignment with exactly `n_singular` singular
    involutions, in enumeration order. Found by search, never tabulated.

    n_singular = 3 is the adopted point, and must coincide with
    intersection_tensor.canonical_point(). The search result is cached as
    the (triple, shifts) pair only; the returned dict is rebuilt on every
    call, so a caller that mutates it cannot corrupt the next one.
    """
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
        elements,
    )

    found = _first_admissible(int(n_singular))
    if found is None:
        raise LookupError(
            "no admissible assignment has %d singular involutions; the "
            "reachable family is n in {0, 1, 2, 3}" % n_singular)
    triple, svecs = found
    nz = _non_identity(_group())
    els = elements([nz[i] for i in triple], svecs)
    return {
        "triple": triple,
        "shifts": svecs,
        "elements": els,
        "singular": _singular_of(els),
        "n_singular": int(n_singular),
    }


def _key(comp: Dict[int, int]) -> Tuple[Tuple[int, int], ...]:
    return tuple(sorted(comp.items()))


def component_cohomology(els, sigma, comp: Dict[int, int]) -> Dict[str, Any]:
    """H^*(T^3 / Stab) for one fixed 3-torus of `sigma`, and whether the
    stabiliser preserves the exceptional Eguchi-Hanson class.

    The Betti numbers are the invariant constant forms on sigma's fixed
    coordinates: a p-form dx_I survives iff every stabilising element has an
    even number of sign flips on I.
    """
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        act_on_component,
        fixed_coords,
        moved_coords,
    )

    eps, _shift = sigma
    fixed = fixed_coords(eps)
    moved = moved_coords(eps)
    here = _key(comp)
    stab = [d for d in els.values() if act_on_component(d, sigma, comp) == here]

    betti = tuple(
        sum(1 for idx in itertools.combinations(fixed, p)
            if all(_even_flips(d[0], idx) for d in stab))
        for p in range(len(fixed) + 1))

    scalar = {tuple([1] * len(moved)), tuple([-1] * len(moved))}
    transverse = {tuple(d[0][a] for a in moved) for d in stab}
    return {
        "betti": betti,
        "stabiliser_order": len(stab),
        "transverse_is_scalar": transverse <= scalar,
        "a1": transverse == scalar,
    }


def _even_flips(signs, idx) -> bool:
    return sum(1 for b in idx if signs[b] < 0) % 2 == 0


def singular_components(point: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One row per singular component of T^7/Gamma: a Gamma-orbit of fixed
    3-tori of one singular involution, with its cohomology."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        act_on_component,
        fixed_coords,
        moved_coords,
    )

    els = point["elements"]
    rows: List[Dict[str, Any]] = []
    for label, sigma in point["singular"]:
        moved = moved_coords(sigma[0])
        seen = set()
        for bits in itertools.product((0, 1), repeat=len(moved)):
            comp = dict(zip(moved, bits))
            if _key(comp) in seen:
                continue
            orbit = {act_on_component(d, sigma, comp) for d in els.values()}
            seen |= orbit
            coh = component_cohomology(els, sigma, comp)
            rows.append({
                "involution": tuple(label),
                "fixed_coordinates": fixed_coords(sigma[0]),
                "orbit_size": len(orbit),
                **coh,
            })
    return rows


def resolved_betti(point: Dict[str, Any]) -> Dict[int, int]:
    """b_0 .. b_7 of the resolution, from the resolution formula."""
    from metaphysica.simulations.PM.geometry.derived_contribution_table import (
        eguchi_hanson_betti,
    )
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        flat_betti_report,
    )

    betti = dict(flat_betti_report()["flat_betti"])
    exceptional = eguchi_hanson_betti()[2]
    for row in singular_components(point):
        if not (row["a1"] and row["transverse_is_scalar"]):
            raise ValueError(
                "component of involution %s is not A1: the Eguchi-Hanson "
                "resolution does not apply and no Betti number is defined by "
                "this formula" % (row["involution"],))
        for p, bp in enumerate(row["betti"]):
            betti[p + 2] += bp * exceptional
    return betti


def poincare_duality_holds(betti: Dict[int, int]) -> bool:
    return all(betti[k] == betti[_DIM - k] for k in range(_DIM + 1))


def euler_characteristic(betti: Dict[int, int]) -> int:
    """sum (-1)^k b_k -- an Euler characteristic, nothing else."""
    return sum((-1) ** k * betti[k] for k in range(_DIM + 1))


def resolution_report(point: Optional[Dict[str, Any]] = None
                      ) -> Dict[str, Any]:
    """The resolved cohomology of one assignment, with its two self-checks."""
    if point is None:
        point = representative_point(3)
    comps = singular_components(point)
    betti = resolved_betti(point)
    component_b1 = sorted({row["betti"][1] for row in comps})
    return {
        "betti": betti,
        "b2": betti[2],
        "b3": betti[3],
        "poincare_duality_holds": poincare_duality_holds(betti),
        "euler_characteristic": euler_characteristic(betti),
        "n_singular_involutions": len(point["singular"]),
        "n_components": len(comps),
        "component_betti": sorted({row["betti"] for row in comps}),
        "component_b1_values": component_b1,
        "every_component_is_flat_T3": all(
            row["betti"] == (1, 3, 3, 1) for row in comps),
        "orbit_sizes": sorted({row["orbit_size"] for row in comps}),
        "counts": (
            "betti: cohomology classes; euler_characteristic: their "
            "alternating sum; components: singular 3-tori of T^7/Gamma"
        ),
    }
