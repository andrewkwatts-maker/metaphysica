"""The D-019 comparator is lexicographic -- checked exhaustively on small grids.

Properties (stated from the decision rule, not from the implementation):

P1  first difference decides: the winner is the configuration lower on the
    first criterion (in CRITERIA order) where the keys differ, and that
    criterion is the deciding one; equal everywhere is a TIE.
P2  later criteria are irrelevant: changing any criterion after the deciding
    one never changes the outcome.
P3  antisymmetry: swapping the arguments swaps the winner.
P4  transitivity of the strict order.
P5  amendment (f): an UNMEASURED value on criteria 1-4 reached before any
    difference makes the comparison UNDECIDED -- it never falls through.
P6  rank(): groups are exactly the classes of equal keys on criteria 1-4,
    ordered by the comparator, with data deciding nothing between groups.

Falsifiability: the same property checks are run against a deliberately
DATA-FIRST comparator and a FALL-THROUGH comparator (skips unmeasured
criteria) and must FAIL on both.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Callable, List, Optional, Sequence, Tuple

from metaphysica.testground.assessment.comparator import (A, B, TIE,
                                                          UNDECIDED,
                                                          Comparison,
                                                          compare, rank)
from metaphysica.testground.assessment.criteria import verdict_of
from metaphysica.testground.assessment.score import (CRITERIA, DATA,
                                                     DECIDING_CRITERIA,
                                                     UNMEASURED,
                                                     CriterionScore,
                                                     ScoreVector)

Key = Optional[Tuple[int, ...]]
Compare = Callable[[ScoreVector, ScoreVector], Comparison]

_FLIP = {A: B, B: A, TIE: TIE, UNDECIDED: UNDECIDED}


def vec(keys: Sequence[Key], tag: str = "") -> ScoreVector:
    """A vector over all five criteria (validity first); None = UNMEASURED."""
    scores = tuple(CriterionScore(c, k) if k is not None
                   else CriterionScore(c, None, UNMEASURED)
                   for c, k in zip(CRITERIA, keys))
    verdict, reasons = verdict_of(scores)
    digest = (tag or "-".join(str(k) for k in keys)).ljust(16, "_")
    return ScoreVector(digest, scores, verdict, reasons)


def grid(values: Sequence[Key], n_free: int = 4) -> List[ScoreVector]:
    """Validity (0,) and every combination of ``values`` on the next
    ``n_free`` criteria; any remaining criteria are (0,)."""
    rest = ((0,),) * (4 - n_free)
    return [vec(((0,),) + combo + rest)
            for combo in itertools.product(values, repeat=n_free)]


def _first_difference(a: ScoreVector, b: ScoreVector) -> Optional[str]:
    for c in CRITERIA:
        if a.score(c).key != b.score(c).key:
            return c
    return None


# -- the property checkers (return violations; [] means the property holds) --

def p1_violations(cmp: Compare, vectors: Sequence[ScoreVector]) -> List[str]:
    out = []
    for a, b in itertools.product(vectors, repeat=2):
        c = _first_difference(a, b)
        res = cmp(a, b)
        if c is None:
            expect = (TIE, None)
        else:
            expect = (A if a.score(c).key < b.score(c).key else B, c)
        if (res.winner, res.deciding_criterion) != expect:
            out.append("%s vs %s: got %s/%s, expected %s/%s" % (
                a.digest, b.digest, res.winner, res.deciding_criterion,
                *expect))
    return out


def p2_violations(cmp: Compare, vectors: Sequence[ScoreVector],
                  values: Sequence[Key]) -> List[str]:
    out = []
    for a, b in itertools.product(vectors, repeat=2):
        res = cmp(a, b)
        if res.deciding_criterion is None:
            continue
        later = CRITERIA[CRITERIA.index(res.deciding_criterion) + 1:]
        for new_a, new_b in itertools.product(values, repeat=2):
            for c in later:
                a2 = _with(a, c, new_a)
                b2 = _with(b, c, new_b)
                res2 = cmp(a2, b2)
                if (res2.winner, res2.deciding_criterion) != (
                        res.winner, res.deciding_criterion):
                    out.append("%s vs %s changed by %s" % (a.digest,
                                                           b.digest, c))
    return out


def p3_violations(cmp: Compare, vectors: Sequence[ScoreVector]) -> List[str]:
    return ["%s vs %s" % (a.digest, b.digest)
            for a, b in itertools.product(vectors, repeat=2)
            if cmp(b, a).winner != _FLIP[cmp(a, b).winner]]


def p4_violations(cmp: Compare, vectors: Sequence[ScoreVector]) -> List[str]:
    out = []
    for a, b, c in itertools.product(vectors, repeat=3):
        if cmp(a, b).winner == A and cmp(b, c).winner == A:
            if cmp(a, c).winner != A:
                out.append("%s > %s > %s" % (a.digest, b.digest, c.digest))
    return out


def p5_violations(cmp: Compare, vectors: Sequence[ScoreVector]) -> List[str]:
    out = []
    for a, b in itertools.product(vectors, repeat=2):
        for c in DECIDING_CRITERIA:
            sa, sb = a.score(c), b.score(c)
            if not (sa.measured and sb.measured):
                if cmp(a, b).winner != UNDECIDED:
                    out.append("%s vs %s fell through %s" % (
                        a.digest, b.digest, c))
                break
            if sa.key != sb.key:
                break
    return out


def _with(v: ScoreVector, criterion: str, key: Key) -> ScoreVector:
    keys = [v.score(c).key for c in CRITERIA]
    keys[CRITERIA.index(criterion)] = key
    return vec(keys)


# -- fixtures that MUST fail the properties ----------------------------------

def data_first_compare(a: ScoreVector, b: ScoreVector) -> Comparison:
    """A WRONG comparator: data consulted first, then criteria 1-4."""
    for c in (DATA,) + DECIDING_CRITERIA:
        ka, kb = a.score(c).key, b.score(c).key
        if ka != kb:
            return Comparison(A if ka < kb else B, c)
    return Comparison(TIE, None)


def fall_through_compare(a: ScoreVector, b: ScoreVector) -> Comparison:
    """A WRONG comparator: skips a criterion that is not measured."""
    for c in CRITERIA:
        sa, sb = a.score(c), b.score(c)
        if not (sa.measured and sb.measured):
            continue
        if sa.key != sb.key:
            return Comparison(A if sa.key < sb.key else B, c)
    return Comparison(TIE, None)


_SMALL = [(0,), (1,), (2,)]
_TINY = [(0,), (1,)]


def test_p1_first_difference_decides_on_the_full_grid():
    assert p1_violations(compare, grid(_SMALL)) == []


def test_p1_is_lexicographic_inside_a_multi_position_key():
    pairs = [(x, y) for x in (0, 1) for y in (0, 1)]
    vectors = [vec(((0,), p, (0,), e, d)) for p in pairs
               for e in _TINY for d in _TINY]
    assert p1_violations(compare, vectors) == []


def test_p2_later_criteria_never_change_the_outcome():
    assert p2_violations(compare, grid(_TINY), _TINY) == []


def test_p3_swapping_the_arguments_swaps_the_winner():
    assert p3_violations(compare, grid(_SMALL)) == []


def test_p4_the_strict_order_is_transitive():
    assert p4_violations(compare, grid(_TINY)) == []


def test_p5_unmeasured_never_falls_through():
    vectors = grid([(0,), (1,), None], n_free=3)
    vectors = [_with(v, DATA, (0,)) for v in vectors]
    assert p5_violations(compare, vectors) == []


def test_p6_rank_groups_are_the_classes_of_criteria_one_to_four():
    vectors = grid(_TINY)
    groups = rank(vectors)
    by = {v.digest: v for v in vectors}
    flat = [d for g in groups for d in g]
    assert sorted(flat) == sorted(by)
    for g in groups:
        keys = {tuple(by[d].score(c).key for c in DECIDING_CRITERIA)
                for d in g}
        assert len(keys) == 1
    for i, j in itertools.combinations(range(len(groups)), 2):
        res = compare(by[groups[i][0]], by[groups[j][0]])
        assert res.winner == A and res.deciding_criterion in DECIDING_CRITERIA


def test_the_data_first_fixture_fails_the_property():
    """Falsifiability: a data-first comparator is caught by P1 and P2."""
    assert p1_violations(data_first_compare, grid(_TINY))
    assert p2_violations(data_first_compare, grid(_TINY), _TINY)


def test_the_fall_through_fixture_fails_the_unmeasured_property():
    """Falsifiability: skipping an unmeasured criterion is caught by P5."""
    vectors = grid([(0,), (1,), None], n_free=3)
    vectors = [_with(v, DATA, (0,)) for v in vectors]
    assert p5_violations(fall_through_compare, vectors)
