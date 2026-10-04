"""Lane 2B: standing failures (amendment (c)) and criterion grouping.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.testground.assessment.standing import (by_criterion,
                                                        effective_count,
                                                        failing_checks,
                                                        live_failures,
                                                        standing_failures)
from metaphysica.testground.signals.model import Measurement, Signal


def _m(signal, count=0, failures=None, status="MEASURED"):
    detail = {"failures": failures} if failures is not None else {}
    return Measurement(signal, status=status, count=count, detail=detail)


def test_an_itemized_check_failing_everywhere_is_standing():
    ms = {
        "c1": {"validity": [_m("kinds", 2, ["re_t", "vac"])]},
        "c2": {"validity": [_m("kinds", 1, ["re_t"])]},
    }
    assert standing_failures(ms) == frozenset({"kinds:re_t"})


def test_a_whole_signal_stands_only_with_the_same_count_everywhere():
    same = {"c1": {"consistency": [_m("omega", 1)]},
            "c2": {"consistency": [_m("omega", 1)]}}
    differ = {"c1": {"consistency": [_m("omega", 1)]},
              "c2": {"consistency": [_m("omega", 2)]}}
    assert standing_failures(same) == frozenset({"omega"})
    assert standing_failures(differ) == frozenset()


def test_measures_never_stand():
    """Closure and elegance are sizes, not checks."""
    ms = {"c1": {"closure": [_m("free", 3)], "elegance": [_m("leaves", 2)]},
          "c2": {"closure": [_m("free", 3)], "elegance": [_m("leaves", 2)]}}
    assert standing_failures(ms) == frozenset()


def test_an_unmeasured_reading_is_not_a_failure():
    ms = {"c1": {"validity": [_m("kinds", 1, ["re_t"])]},
          "c2": {"validity": [_m("kinds", None, status="UNMEASURED")]}}
    assert standing_failures(ms) == frozenset()


def test_unrun_configurations_take_no_part_and_one_is_not_enough():
    ms = {"c1": {"validity": [_m("kinds", 1, ["re_t"])]},
          "c2": {"validity": [_m("kinds", 1, ["re_t"])]},
          "never_run": {}}
    assert standing_failures(ms) == frozenset({"kinds:re_t"})
    single = {"c1": {"validity": [_m("kinds", 1, ["re_t"])]}}
    assert standing_failures(single) == frozenset()
    assert standing_failures(single, min_configurations=1) == frozenset(
        {"kinds:re_t"})


def test_effective_counts_exclude_only_standing_failures():
    standing = frozenset({"kinds:re_t", "omega"})
    assert effective_count(_m("kinds", 2, ["re_t", "vac"]), standing) == 1
    assert effective_count(_m("kinds", 0, ["re_t"]), standing) == 0
    assert effective_count(_m("omega", 4), standing) == 0
    assert effective_count(_m("beacons", 4), standing) == 4
    assert effective_count(_m("x", None), standing) is None
    assert live_failures(_m("kinds", 2, ["re_t", "vac"]), standing) == [
        "kinds:vac"]
    assert failing_checks(_m("kinds", 0)) == frozenset()


def test_by_criterion_accepts_every_documented_form():
    sig = Signal("omega", "consistency", "live", "screen", lambda c: None)
    m = _m("omega", 1)
    assert by_criterion({"consistency": [m]})["consistency"] == [m]
    assert by_criterion([(sig, m)])["consistency"] == [m]
    assert by_criterion([m], [sig])["consistency"] == [m]
    assert by_criterion([m], {"omega": "consistency"})["consistency"] == [m]
    assert by_criterion([m], {"omega": "consistency"})["closure"] == []


def test_by_criterion_refuses_what_it_cannot_place():
    with pytest.raises(ValueError, match="unknown criteria"):
        by_criterion({"beauty": []})
    with pytest.raises(ValueError, match="no criterion known"):
        by_criterion([_m("omega", 1)])
