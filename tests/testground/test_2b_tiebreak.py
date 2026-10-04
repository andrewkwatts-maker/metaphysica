"""Lane 2B: the data tie-break -- common rows, trials factor, disclosure.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.testground.assessment.score import (CRITERIA, UNMEASURED,
                                                     CriterionScore,
                                                     ScoreVector)
from metaphysica.testground.assessment.tiebreak import (COMMON_ROWS, NO_DATA,
                                                        PER_CONFIGURATION,
                                                        common_row_ids,
                                                        data_key,
                                                        order_by_key,
                                                        tiebreak)
from metaphysica.testground.theory import ScoredRow


def vec(digest, data=(0,)):
    scores = tuple(CriterionScore(c, (0,)) for c in CRITERIA[:4]) + (
        CriterionScore("data", data) if data is not None
        else CriterionScore("data", None, UNMEASURED),)
    return ScoreVector(digest.ljust(16, "0"), scores, "ADOPTABLE")


A, B, C = vec("a"), vec("b"), vec("c")


def test_the_key_counts_fails_tensions_and_chi2_in_thousandths():
    rows = [ScoredRow("r1", "FAIL", 3.0), ScoredRow("r2", "tension", 2.0),
            ScoredRow("r3", "PASS", 0.5), ScoredRow("r4", "MARGINAL", None)]
    ids = frozenset({"r1", "r2", "r3", "r4"})
    assert data_key(rows, ids, frozenset({"r1", "r3"})) == (1, 1, 9250)


def test_only_rows_common_to_the_group_count():
    rows = {
        A.digest: [ScoredRow("r1", "PASS", 0.1), ScoredRow("only_a", "FAIL")],
        B.digest: [ScoredRow("r1", "FAIL", 4.0)],
    }
    assert common_row_ids(rows) == frozenset({"r1"})
    tb = tiebreak([A, B], rows)
    assert tb.basis == COMMON_ROWS and tb.common_rows == 1
    assert tb.keys[A.digest] == (0, 0, 10)
    assert tb.order == ((A.digest,), (B.digest,))
    assert tb.leader == A.digest and tb.separates
    assert tb.k == 2 and tb.fitted_dof_on_accept == 1


def test_chi2_uses_only_rows_with_a_sigma_in_every_member():
    rows = {A.digest: [ScoredRow("r1", "PASS", 1.0)],
            B.digest: [ScoredRow("r1", "PASS", None)]}
    tb = tiebreak([A, B], rows)
    assert tb.chi2_rows == 0 and not tb.separates and tb.leader is None


def test_a_member_without_rows_stops_the_tiebreak():
    tb = tiebreak([A, B], {A.digest: []})
    assert tb.basis == NO_DATA and tb.order == ((A.digest, B.digest),)
    assert "no scored rows" in tb.reasons[0]


def test_without_rows_the_vectors_own_data_keys_are_used_and_said_so():
    tb = tiebreak([vec("a", (2,)), vec("b", (1,)), vec("c", (1,))])
    assert tb.basis == PER_CONFIGURATION and "common rows" in tb.reasons[0]
    assert [len(s) for s in tb.order] == [2, 1] and tb.leader is None
    assert tb.k == 3
    gap = tiebreak([vec("a", (2,)), vec("b", None)])
    assert gap.basis == NO_DATA and not gap.separates


def test_order_by_key_keeps_input_order_inside_equal_keys():
    keys = {"x": (1,), "y": (0,), "z": (1,)}
    assert order_by_key(["x", "y", "z"], keys) == (("y",), ("x", "z"))
    assert common_row_ids({}) == frozenset()


def test_the_disclosure_serializes():
    d = tiebreak([vec("a", (2,)), vec("b", (1,))]).as_dict()
    assert d["trials_factor_k"] == 2 and d["fitted_dof_on_accept"] == 1
    assert d["key_components"] == ["n_FAIL", "n_TENSION", "chi2_milli"]
    assert d["leader"] == vec("b").digest
    assert tiebreak([vec("a", None)]).as_dict()["keys"] == {
        vec("a").digest: None}
