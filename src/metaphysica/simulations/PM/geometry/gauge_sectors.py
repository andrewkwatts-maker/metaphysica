"""Which gauge theories live on the singular loci, across phi's Joyce family (C2).

Pre-registered as D-010 (site repo docs/DECISION_LOG.md, 2026-09-30).

Acharya (hep-th/9812205): C^2/{+-1} fibred over a 3-manifold Q carries pure
N = (1 + b_1(Q)) super Yang-Mills. Only b_1(Q) = 0 gives pure N = 1, the
theory that confines and forms a gaugino condensate -- the ingredient of every
non-perturbative moduli-stabilisation mechanism of the racetrack kind. A locus
here is Q = T^3 / Stab, and b_1(Q) is the number of the torus's constant
1-forms that every stabilising element leaves invariant (translations act
trivially on constant forms; the lift character of D-006 plays no role, since
it concerns the exceptional sphere, not Q).

A4: b_1 counts 1-cohomology classes of Q; N counts supersymmetries; n counts
singular involutions. None is converted into another.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict

__all__ = ["locus_b1", "confinement_sweep"]


def locus_b1(els, sigma, comp) -> int:
    """b_1 of the locus T^3/Stab carrying the fixed torus `comp` of sigma."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        act_on_component,
        fixed_coords,
    )

    here = tuple(sorted(comp.items()))
    stab = [d for d in els.values() if act_on_component(d, sigma, comp) == here]
    return sum(1 for b in fixed_coords(sigma[0])
               if all(d[0][b] > 0 for d in stab))


def confinement_sweep() -> Dict[str, Any]:
    """For every pairwise-disjoint class of the first generating triple: the
    smallest b_1 among its loci, collected by n."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
        assignments,
        elements,
        fixed_sets_disjoint,
        generating_triples,
        is_singular,
        moved_coords,
    )

    group = _group()
    nz = _non_identity(group)
    triple = generating_triples(group)[0]
    gens = [nz[i] for i in triple]
    by_n: Dict[int, Dict[int, int]] = {}
    for svecs in assignments(triple, group, include_relative=True):
        els = elements(gens, svecs)
        singular = [(b, e) for b, e in els.items()
                    if b != (0, 0, 0) and is_singular(e)]
        if not singular or not all(
                fixed_sets_disjoint(a[1], b[1])
                for a, b in itertools.combinations(singular, 2)):
            continue
        smallest = min(
            locus_b1(els, sigma, dict(zip(moved_coords(sigma[0]), bits)))
            for _label, sigma in singular
            for bits in itertools.product((0, 1), repeat=4))
        counts = by_n.setdefault(len(singular), {})
        counts[smallest] = counts.get(smallest, 0) + 1
    confining_n = sorted(n for n, c in by_n.items() if 0 in c)
    return {
        "min_b1_by_n": {n: dict(sorted(c.items()))
                        for n, c in sorted(by_n.items())},
        "n_with_a_confining_locus": confining_n,
        "full_holonomy_can_confine": 3 in confining_n,
        "counts": "classes by the smallest b_1(Q) among their loci",
    }
