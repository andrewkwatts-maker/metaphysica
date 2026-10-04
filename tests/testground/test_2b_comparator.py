"""Lane 2B: the comparator -- gate, margins, Pareto note, groups.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.testground.assessment.comparator import (A, B, TIE,
                                                          UNDECIDED,
                                                          Comparison,
                                                          compare, groups_of,
                                                          margins_of, rank,
                                                          unranked)
from metaphysica.testground.assessment.criteria import verdict_of
from metaphysica.testground.assessment.score import (CRITERIA, UNMEASURED,
                                                     CriterionScore,
                                                     ScoreVector)
from metaphysica.testground.theory import ScoredRow


def vec(digest, closure=(0,), consistency=(0,), elegance=(0,), data=(0,),
        validity=(0,), failures=(), components=None, verdict=None):
    keys = (validity, closure, consistency, elegance, data)
    scores = []
    for c, k in zip(CRITERIA, keys):
        comp = (components or {}) if c == "consistency" else {}
        fails = failures if c == "validity" else ()
        scores.append(CriterionScore(c, k, components=comp, failures=fails)
                      if k is not None else
                      CriterionScore(c, None, UNMEASURED, failures=fails))
    v, reasons = verdict_of(tuple(scores))
    return ScoreVector(digest.ljust(16, "0"), tuple(scores), verdict or v,
                       reasons)


def test_the_first_differing_criterion_decides_with_margins():
    a = vec("a", closure=(1,), consistency=(5,))
    b = vec("b", closure=(2,), consistency=(0,))
    res = compare(a, b)
    assert (res.winner, res.deciding_criterion) == (A, "closure")
    assert res.margins["closure"] == (1,)
    assert res.margins["consistency"] == (-5,)
    assert compare(b, a).winner == B


def test_a_consistency_win_carries_a_pareto_note():
    robust = compare(vec("a", consistency=(1,), components={"x": 1, "y": 0}),
                     vec("b", consistency=(2,), components={"x": 1, "y": 1}))
    assert robust.winner == A and not robust.fragile
    assert robust.pareto_note.startswith("Pareto-robust")
    fragile = compare(vec("a", consistency=(1,), components={"x": 1, "y": 0}),
                      vec("b", consistency=(2,), components={"x": 0, "y": 2}))
    assert fragile.winner == A and fragile.fragile
    assert "better on x" in fragile.pareto_note
    other = compare(vec("a", closure=(0,)), vec("b", closure=(1,)))
    assert other.pareto_note is None and not other.fragile


def test_validity_is_a_gate_and_rejections_are_not_ranked():
    good = vec("good", closure=(9,))
    bad = vec("bad", validity=(1,), failures=("kinds:x",))
    worse = vec("worse", validity=(3,), failures=("kinds:y",))
    assert compare(good, bad).winner == A
    assert compare(bad, good).winner == B
    assert compare(good, bad).deciding_criterion == "validity"
    both = compare(bad, worse)
    assert both.winner == UNDECIDED and both.deciding_criterion is None
    open_ = vec("open", validity=None)
    assert compare(bad, open_).winner == UNDECIDED
    not_runnable = vec("nr", verdict="NOT_RUNNABLE")
    assert compare(bad, not_runnable).winner == UNDECIDED


def test_an_unmeasured_criterion_stops_the_comparison():
    a = vec("a", consistency=None, elegance=(0,))
    b = vec("b", consistency=(0,), elegance=(5,))
    res = compare(a, b)
    assert res.winner == UNDECIDED and res.deciding_criterion == "consistency"
    assert "K4" in res.reasons[0]
    early = compare(vec("a", closure=(0,), consistency=None),
                    vec("b", closure=(1,)))
    assert early.winner == A and early.deciding_criterion == "closure"


def test_data_only_breaks_a_tie_on_criteria_one_to_four():
    a, b = vec("a", data=(0, 1, 5)), vec("b", data=(0, 2, 0))
    res = compare(a, b)
    assert res.winner == A and res.deciding_criterion == "data"
    assert res.data_tiebreak and "trials factor" in res.reasons[0]
    assert compare(a, b, use_data=False).winner == TIE
    assert compare(a, vec("c", data=(0, 1, 5))).winner == TIE
    assert compare(a, vec("d", data=None)).winner == TIE


def test_keys_of_different_length_cannot_be_compared():
    with pytest.raises(ValueError):
        compare(vec("a", closure=(0, 1)), vec("b", closure=(0,)))
    assert "closure" not in margins_of(vec("a", closure=(0, 1)),
                                       vec("b", closure=(0,)))


def test_a_comparison_refuses_an_unknown_winner_and_serializes():
    with pytest.raises(ValueError):
        Comparison("c", None)
    d = compare(vec("a", closure=(0,)), vec("b", closure=(1,))).as_dict()
    assert d["winner"] == "a" and d["margins"]["closure"] == [1]


def test_groups_hold_equals_on_criteria_one_to_four_lowest_first():
    v1 = vec("v1", closure=(1,), data=(3,))
    v2 = vec("v2", closure=(0,), data=(9,))
    v3 = vec("v3", closure=(1,), data=(1,))
    rejected = vec("r", validity=(1,), failures=("x",))
    undecided = vec("u", elegance=None)
    groups = groups_of([v1, v2, v3, rejected, undecided])
    assert [[v.digest[:2] for v in g] for g in groups] == [["v2"],
                                                           ["v1", "v3"]]
    assert [[d[:2] for d in g] for g in rank([v1, v2, v3])] == [
        ["v2"], ["v3", "v1"]]
    left = unranked([v1, rejected, undecided])
    assert left == {"REJECTED": [rejected.digest],
                    "UNDECIDED": [undecided.digest]}


def test_rank_uses_common_rows_inside_a_group():
    v1, v3 = vec("v1", data=None), vec("v3", data=None)
    rows = {v1.digest: [ScoredRow("r1", "FAIL")],
            v3.digest: [ScoredRow("r1", "PASS")]}
    assert rank([v1, v3], rows) == [[v3.digest, v1.digest]]
    assert rank([v1, v3]) == [[v1.digest, v3.digest]]


def test_mixed_key_layouts_cannot_be_grouped():
    with pytest.raises(ValueError):
        groups_of([vec("a", closure=(0, 1)), vec("b", closure=(0,))])
