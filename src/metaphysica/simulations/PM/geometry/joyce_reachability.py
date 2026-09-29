"""Which (b_2, b_3) Joyce's construction reaches from phi's own (Z/2)^3: D-006.

Pre-registered 2026-09-30 (site repo docs/DECISION_LOG.md) before this was
run, after a blind red-team review found the A1 filter too strict.

ADMISSIBILITY, AS JOYCE STATES IT
=================================
Joyce's Condition 2.1.2 (JDG II) is pairwise disjointness of the singular
sets. Under it, every element that stabilises a fixed 3-torus of sigma,
other than sigma itself, acts FREELY on that torus -- a fixed point would lie
in two singular sets -- so the isotropy at every singular point is {1, sigma}
and every singular point is A1. A free extra stabiliser is not an obstruction
but Joyce's JDG II setting, (T^3 x C^2/{+-1})/F with F free, resolved by his
Theorems 2.2.2-2.2.3. `derived_contribution_table.all_components_are_a1`
tested the SETWISE stabiliser instead and so rejected Joyce's own Example 4.

A FAMILY'S CONTRIBUTION, COMPUTED RATHER THAN TABULATED
======================================================
A family is a Gamma-orbit of fixed 3-tori; its component in the quotient is
T^3/Stab. Resolving puts an Eguchi-Hanson space X over it, and each free
stabilising element g lifts to X in one of two ways: preserving the class of
the exceptional sphere or reversing it (Joyce, JDG II Example 4). That choice
is a character eps: Stab -> {+-1} with eps(sigma) = +1 (sigma is the deck
involution of C^2/{+-1}, trivial on X). The new cohomology is

    [ H^*(T^3) (x) H^2(X) ]^Stab  =  { forms w on T^3 : g.w = eps(g) w },

shifted up by two degrees. So a family contributes, for each admissible eps,
(b_2, b_3) += (# such 0-forms, # such 1-forms). For a plain family
(Stab = {1, sigma}) this is (1, 3). For Joyce's T^3/Z_2 families it gives
(1, 1) with eps = +1 and (0, 2) with eps = -1, which is exactly his
eq. (27) -- the check that the computation reads the geometry correctly.
Families with |Stab| = 8 are computed the same way; no literature example
covers them, and they are reported separately and labelled.

ONE TRIPLE SUFFICES
===================
Each of the 28 generating triples parametrises all 16,384 conjugacy classes
of actions (red-team finding, re-checked in the slow test), so the default
sweep uses the first triple only.

A4: pairs (b_2, b_3) count cohomology classes; stabiliser orders count group
elements; the character eps is a choice of lift, not a number.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

__all__ = [
    "family_options",
    "class_options",
    "reachable_set",
    "LITERATURE_CHECKED_STABILISER_ORDERS",
]

Pair = Tuple[int, int]

#: |Stab| of a family whose contribution a published example fixes:
#: 2 -- plain T^3 (Joyce JDG I); 4 -- T^3/Z_2 (Joyce JDG II, Example 4).
LITERATURE_CHECKED_STABILISER_ORDERS = frozenset({2, 4})

_FLAT = (0, 7)


def _key(comp):
    return tuple(sorted(comp.items()))


def _sign_on(signs, idx) -> int:
    out = 1
    for b in idx:
        out *= signs[b]
    return out


def _characters(stab, sigma) -> List[Dict[Tuple[int, ...], int]]:
    """Every homomorphism eps: Stab -> {+-1} with eps(sigma) = +1.

    Keyed by linear part, which is unique per element of Gamma. Stab is
    elementary abelian, so a character is fixed by its values on a basis of
    Stab/<sigma>, found greedily; each value choice is extended to all of
    Stab by multiplicativity.
    """
    identity = tuple([1] * len(sigma[0]))
    base = {identity: 1, tuple(sigma[0]): 1}
    basis: List[Tuple[int, ...]] = []
    span = set(base)
    for d in stab:
        v = tuple(d[0])
        if v not in span:
            basis.append(v)
            span |= {_product(v, s) for s in span}
    out = []
    for values in itertools.product((1, -1), repeat=len(basis)):
        eps = dict(base)
        for v, e in zip(basis, values):
            eps.update({_product(v, known): e * ke
                        for known, ke in list(eps.items())})
        out.append(eps)
    return out


def _product(u: Sequence[int], v: Sequence[int]) -> Tuple[int, ...]:
    return tuple(a * b for a, b in zip(u, v))


def family_options(els, sigma, comp) -> Tuple[int, FrozenSet[Pair]]:
    """(|Stab|, the (b_2, b_3) contributions over every admissible lift)."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        act_on_component,
        fixed_coords,
    )

    here = _key(comp)
    stab = [d for d in els.values() if act_on_component(d, sigma, comp) == here]
    fixed = fixed_coords(sigma[0])
    options: Set[Pair] = set()
    for eps in _characters(stab, sigma):
        counts = []
        for p in (0, 1):
            counts.append(sum(
                1 for idx in itertools.combinations(fixed, p)
                if all(_sign_on(d[0], idx) == eps[tuple(d[0])]
                       for d in stab)))
        options.add((counts[0], counts[1]))
    return len(stab), frozenset(options)


def class_options(els, singular) -> Tuple[Dict[int, int], Set[Pair]]:
    """Stabiliser-order profile and every reachable (b_2, b_3) of one class."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        act_on_component,
        moved_coords,
    )

    profile: Dict[int, int] = {}
    totals: Set[Pair] = {_FLAT}
    for _label, sigma in singular:
        moved = moved_coords(sigma[0])
        seen = set()
        for bits in itertools.product((0, 1), repeat=len(moved)):
            comp = dict(zip(moved, bits))
            if _key(comp) in seen:
                continue
            seen |= {act_on_component(d, sigma, comp) for d in els.values()}
            order, opts = family_options(els, sigma, comp)
            profile[order] = profile.get(order, 0) + 1
            totals = {(a + x, b + y) for (a, b) in totals for (x, y) in opts}
    return profile, totals


def reachable_set(triples: Optional[Sequence[int]] = (0,)) -> Dict[str, Any]:
    """The reachable set over every pairwise-disjoint class.

    `triples` indexes generating_triples(); the default first triple already
    covers every class. Pass None to sweep all 28 (the slow cross-check).
    """
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
        assignments,
        elements,
        fixed_sets_disjoint,
        generating_triples,
        is_singular,
    )

    group = _group()
    nz = _non_identity(group)
    all_triples = generating_triples(group)
    chosen = all_triples if triples is None else [all_triples[i]
                                                   for i in triples]
    by_n: Dict[int, Set[Pair]] = {}
    checked: Set[Pair] = set()
    unchecked_only: Set[Pair] = set()
    profiles: Dict[Tuple[int, Tuple[Tuple[int, int], ...]], int] = {}
    n_classes = 0
    for triple in chosen:
        gens = [nz[i] for i in triple]
        for svecs in assignments(triple, group, include_relative=True):
            els = elements(gens, svecs)
            singular = [(b, e) for b, e in els.items()
                        if b != (0, 0, 0) and is_singular(e)]
            if not all(fixed_sets_disjoint(a[1], b[1])
                       for a, b in itertools.combinations(singular, 2)):
                continue
            n_classes += 1
            profile, pairs = class_options(els, singular)
            key = (len(singular), tuple(sorted(profile.items())))
            profiles[key] = profiles.get(key, 0) + 1
            by_n.setdefault(len(singular), set()).update(pairs)
            if set(profile) <= LITERATURE_CHECKED_STABILISER_ORDERS:
                checked |= pairs
            else:
                unchecked_only |= pairs
    unchecked_only -= checked
    everything = sorted(set().union(*by_n.values())) if by_n else []
    return {
        "n_disjoint_classes_visited": n_classes,
        "triples": [tuple(t) for t in chosen],
        "reachable": everything,
        "by_n_singular": {n: sorted(v) for n, v in sorted(by_n.items())},
        "literature_checked": sorted(checked),
        "only_via_unchecked_stabilisers": sorted(unchecked_only),
        "stabiliser_profiles": {"n=%d %s" % (n, dict(p)): c
                                for (n, p), c in sorted(profiles.items())},
        "b3_24_reachable": any(b3 == 24 for _b2, b3 in everything),
        "b2_plus_b3_by_n": {n: sorted({a + b for a, b in v})
                            for n, v in sorted(by_n.items())},
        "counts": (
            "pairs count cohomology classes; profiles count families by "
            "stabiliser order (group elements)"),
    }
