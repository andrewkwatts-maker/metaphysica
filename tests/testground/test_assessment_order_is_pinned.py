"""The assessment order is pinned (D-019 governance test).

Changing the criteria order, the role of data, the verdict vocabularies or
the data-key components is a governance act: it needs a new decision, and
this test must be edited in the same commit, visibly.

Pinned here:
* CRITERIA = validity, closure, consistency, elegance, data -- and the schema
  and every report carry exactly that order;
* DECIDING_CRITERIA is the first four; data comes last and only breaks ties;
* behaviourally, for every pair of criteria i < j, a win on i beats a loss on
  j (the comparator follows the pinned order, whatever its internals);
* no assessment module restates the order with its own string literals;
* the verdict vocabularies match the report schema;
* the data key is (n_FAIL, n_TENSION, chi2_milli).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import ast
import itertools
import json
from pathlib import Path

from metaphysica.testground.assessment import report as report_mod
from metaphysica.testground.assessment.comparator import A, compare
from metaphysica.testground.assessment.recommend import (
    RECOMMENDATION_VERDICTS)
from metaphysica.testground.assessment.score import (CRITERIA, DATA,
                                                     DECIDING_CRITERIA,
                                                     VERDICTS,
                                                     CriterionScore,
                                                     ScoreVector)
from metaphysica.testground.assessment.tiebreak import DATA_KEY_COMPONENTS
from metaphysica.testground.configurations.model import Configuration

_PKG = Path(__file__).resolve().parents[2] / "src" / "metaphysica" / "testground"
_SCHEMA = json.loads((_PKG / "schemas" / "path_assessment.schema.json")
                     .read_text(encoding="utf-8"))

PINNED = ("validity", "closure", "consistency", "elegance", "data")


def _vec(digest: str, keys) -> ScoreVector:
    scores = tuple(CriterionScore(c, k) for c, k in zip(CRITERIA, keys))
    return ScoreVector(digest.ljust(16, "0"), scores, "ADOPTABLE")


def test_the_criteria_order_is_pinned():
    assert CRITERIA == PINNED
    assert DECIDING_CRITERIA == PINNED[:4]
    assert CRITERIA[-1] == DATA


def test_the_schema_carries_the_pinned_order():
    assert _SCHEMA["properties"]["criteria_order"]["const"] == list(PINNED)


def test_a_report_carries_the_pinned_order():
    cfg = Configuration.of("t", {"f": "x"})
    v = _vec(cfg.digest, [(0,)] * 5)
    rep = report_mod.build_report(theory="t", mode="assess",
                                  configurations=[cfg], vectors=[v],
                                  active_digest=cfg.digest)
    assert rep["criteria_order"] == list(PINNED)


def test_an_earlier_criterion_always_outweighs_a_later_one():
    """For every i < j: a better on i, worse on j -> a wins, on i."""
    for i, j in itertools.combinations(range(len(PINNED)), 2):
        a_keys = [(0,)] * 5
        b_keys = [(0,)] * 5
        a_keys[i], b_keys[i] = (0,), (1,)
        a_keys[j], b_keys[j] = (9,), (0,)
        res = compare(_vec("a", a_keys), _vec("b", b_keys))
        assert (res.winner, res.deciding_criterion) == (A, PINNED[i]), (i, j)


def test_no_assessment_module_restates_the_order():
    """Modules import the order from score.py; none spells it out again."""
    names = set(PINNED)
    offenders = []
    for path in sorted((_PKG / "assessment").glob("*.py")):
        if path.name == "score.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        offenders += ["%s:%d %r" % (path.name, n.lineno, n.value)
                      for n in ast.walk(tree)
                      if isinstance(n, ast.Constant) and n.value in names]
    assert not offenders, offenders


def test_the_verdict_vocabularies_match_the_schema():
    props = _SCHEMA["properties"]
    assert list(RECOMMENDATION_VERDICTS) == props["verdict"]["enum"]
    item = props["configurations"]["items"]["properties"]
    assert list(VERDICTS) == item["verdict"]["enum"]


def test_the_data_key_components_are_pinned():
    assert DATA_KEY_COMPONENTS == ("n_FAIL", "n_TENSION", "chi2_milli")
