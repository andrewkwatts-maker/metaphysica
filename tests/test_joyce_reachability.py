"""Joyce's construction from phi's (Z/2)^3 reaches 28 literature-checked pairs,
and b_3 = 24 is not one of them (D-006).

Pre-registered 2026-09-30 in the site repo's docs/DECISION_LOG.md, after a
blind red-team review found the A1 filter tested the setwise stabiliser
instead of the isotropy. The contribution of each family is COMPUTED -- the
part of H^*(T^3) transforming by a lift character -- and the check that this
reads the geometry correctly is that it reproduces Joyce's own JDG II
Example 4, eq. (27): (1, 1) or (0, 2) per T^3/Z_2 family.

MEASURED 2026-09-30 (first generating triple, 15,963 pairwise-disjoint
classes): literature-checked set = (0, 7) plus b_2 + b_3 = 23 (b_2 = 0..8),
39 (4..12) and 55 (8..16), 28 pairs, identical to the verifier's independent
computation. Eight further pairs, (9, 14) .. (16, 7), arise only from the
trivial lift on order-8 stabilisers, a case no published example covers.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools

import pytest

from metaphysica.simulations.PM.geometry.joyce_reachability import (
    class_options,
    family_options,
    reachable_set,
)

_LINES = {1: (23, range(0, 9)), 2: (39, range(4, 13)), 3: (55, range(8, 17))}


def _expected_checked():
    pairs = {(0, 7)}
    for total, b2s in _LINES.values():
        pairs |= {(b2, total - b2) for b2 in b2s}
    return sorted(pairs)


@pytest.fixture(scope="module")
def result():
    return reachable_set()


def test_the_literature_checked_set_is_the_three_lines(result):
    assert result["literature_checked"] == _expected_checked()
    assert len(result["literature_checked"]) == 28


def test_b3_24_is_unreachable_in_every_variant(result):
    assert not result["b3_24_reachable"]
    assert all(b3 != 24 for _b2, b3 in result["reachable"])


def test_b2_plus_b3_is_7_plus_16n(result):
    assert result["b2_plus_b3_by_n"] == {0: [7], 1: [23], 2: [39], 3: [55]}


def test_the_adopted_pair_is_on_the_n3_line_twice_over(result):
    """(12, 43) is Joyce's Example 3 (all plain) and Example 4 with l = 4."""
    assert (12, 43) in result["by_n_singular"][3]
    plain = result["stabiliser_profiles"]["n=3 {2: 12}"]
    example_4 = result["stabiliser_profiles"]["n=3 {2: 8, 4: 8}"]
    assert plain > 0 and example_4 > 0


def test_unchecked_stabilisers_are_reported_separately(result):
    extra = result["only_via_unchecked_stabilisers"]
    assert extra == [(b2, 23 - b2) for b2 in range(9, 17)]
    assert not set(extra) & set(result["literature_checked"])


def _example_4_class():
    """The first pairwise-disjoint n = 3 class with T^3/Z_2 families."""
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
    triple = generating_triples(group)[0]
    gens = [nz[i] for i in triple]
    for svecs in assignments(triple, group, include_relative=True):
        els = elements(gens, svecs)
        singular = [(b, e) for b, e in els.items()
                    if b != (0, 0, 0) and is_singular(e)]
        if len(singular) != 3 or not all(
                fixed_sets_disjoint(a[1], b[1])
                for a, b in itertools.combinations(singular, 2)):
            continue
        profile, pairs = class_options(els, singular)
        if profile == {2: 8, 4: 8}:
            return els, singular, pairs
    pytest.fail("no Example-4 class found; the enumeration changed")


def test_the_computation_reproduces_joyce_example_4():
    """Joyce JDG II eq. (27): b_2 = 8 + l, b_3 = 47 - l, l = 0..8."""
    els, singular, pairs = _example_4_class()
    assert sorted(pairs) == [(8 + l, 47 - l) for l in range(9)]


def test_a_free_z2_family_contributes_one_one_or_zero_two():
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        moved_coords,
    )

    els, singular, _pairs = _example_4_class()
    seen = set()
    for _label, sigma in singular:
        for bits in itertools.product((0, 1), repeat=4):
            comp = dict(zip(moved_coords(sigma[0]), bits))
            order, opts = family_options(els, sigma, comp)
            seen.add((order, opts))
    assert (2, frozenset({(1, 3)})) in seen
    assert (4, frozenset({(1, 1), (0, 2)})) in seen


@pytest.mark.slow
def test_every_generating_triple_reaches_the_same_set(result):
    """Each triple parametrises all 16,384 classes (red-team finding)."""
    everything = reachable_set(triples=None)
    assert everything["reachable"] == result["reachable"]
    assert everything["literature_checked"] == result["literature_checked"]
