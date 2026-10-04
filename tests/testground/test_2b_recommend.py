"""Lane 2B: recommend -- the five verdicts, and the active kept on a tie.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.testground.assessment.criteria import verdict_of
from metaphysica.testground.assessment.recommend import (
    ACTIVE_CONFIRMED, DATA_TIEBREAK_SUGGESTS, NO_ADOPTABLE_CONFIGURATION,
    RECOMMEND_CHANGE, UNDECIDED, recommend)
from metaphysica.testground.assessment.score import (CRITERIA, UNMEASURED,
                                                     CriterionScore,
                                                     ScoreVector)
from metaphysica.testground.theory import ScoredRow


def vec(digest, closure=(0,), consistency=(0,), elegance=(0,), data=None,
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
                       reasons or ("r",))


ACTIVE = vec("active")


def test_a_sole_top_active_is_confirmed():
    verdict, rec = recommend(ACTIVE.digest, [ACTIVE, vec("x", closure=(1,))])
    assert (verdict, rec) == (ACTIVE_CONFIRMED, None)


def test_a_complete_tie_keeps_the_active():
    """Amendment (e)."""
    other = vec("other")
    assert recommend(ACTIVE.digest, [other, ACTIVE]) == (ACTIVE_CONFIRMED,
                                                         None)
    same = {ACTIVE.digest: [ScoredRow("r", "PASS", 1.0)],
            other.digest: [ScoredRow("r", "PASS", 1.0)]}
    assert recommend(ACTIVE.digest, [other, ACTIVE], same)[0] == (
        ACTIVE_CONFIRMED)


def test_a_better_fitting_configuration_with_an_extra_input_loses():
    """The toy's known answer (i), in unit form: closure decides first."""
    fits = vec("fits", closure=(1,), data=(0, 0, 0))
    active = vec("active", closure=(0,), data=(3, 2, 900))
    assert recommend(active.digest, [active, fits]) == (ACTIVE_CONFIRMED,
                                                        None)


def test_data_ahead_of_the_active_inside_its_group_only_suggests():
    other = vec("other")
    rows = {ACTIVE.digest: [ScoredRow("r", "FAIL")],
            other.digest: [ScoredRow("r", "PASS")]}
    verdict, rec = recommend(ACTIVE.digest, [ACTIVE, other], rows)
    assert verdict == DATA_TIEBREAK_SUGGESTS
    assert rec.target == other.digest and rec.deciding_criterion == "data"
    assert rec.uses_data_tiebreak and rec.trials_factor == 2
    assert rec.fitted_dof_on_accept == 1
    assert "trials factor k=2" in rec.reasons[1]


def test_data_ahead_of_the_active_never_moves_it_when_it_leads():
    other = vec("other")
    rows = {ACTIVE.digest: [ScoredRow("r", "PASS")],
            other.digest: [ScoredRow("r", "FAIL")]}
    assert recommend(ACTIVE.digest, [ACTIVE, other], rows)[0] == (
        ACTIVE_CONFIRMED)


def test_several_data_leaders_are_named_without_a_target():
    o1, o2 = vec("o1"), vec("o2")
    rows = {ACTIVE.digest: [ScoredRow("r", "FAIL")],
            o1.digest: [ScoredRow("r", "PASS")],
            o2.digest: [ScoredRow("r", "PASS")]}
    verdict, rec = recommend(ACTIVE.digest, [ACTIVE, o1, o2], rows)
    assert verdict == DATA_TIEBREAK_SUGGESTS and rec.target is None
    assert set(rec.candidates) == {o1.digest, o2.digest}


def test_a_top_group_beating_the_active_recommends_a_change():
    active = vec("active", closure=(1,))
    top = vec("top", closure=(0,), consistency=(4,))
    verdict, rec = recommend(active.digest, [active, top])
    assert verdict == RECOMMEND_CHANGE
    assert rec.target == top.digest and rec.deciding_criterion == "closure"
    assert rec.margins["closure"] == (1,)
    assert not rec.uses_data_tiebreak and rec.fitted_dof_on_accept == 0
    assert rec.trials_factor is None
    d = rec.as_dict()
    assert d["target"] == top.digest and d["tiebreak"] is None


def test_a_change_inside_a_tied_top_group_discloses_the_data_pick():
    active = vec("active", closure=(1,))
    t1, t2 = vec("t1"), vec("t2")
    rows = {t1.digest: [ScoredRow("r", "TENSION")],
            t2.digest: [ScoredRow("r", "PASS")]}
    verdict, rec = recommend(active.digest, [active, t1, t2], rows)
    assert verdict == RECOMMEND_CHANGE and rec.target == t2.digest
    assert rec.uses_data_tiebreak and rec.trials_factor == 2
    assert rec.as_dict()["tiebreak"]["leader"] == t2.digest
    verdict, rec = recommend(active.digest, [active, t1, t2])
    assert verdict == RECOMMEND_CHANGE and rec.target is None
    assert set(rec.candidates) == {t1.digest, t2.digest}
    assert "choose explicitly" in rec.reasons[-1]


def test_a_fragile_consistency_win_is_flagged():
    active = vec("active", consistency=(2,), components={"x": 0, "y": 2})
    top = vec("top", consistency=(1,), components={"x": 1, "y": 0})
    verdict, rec = recommend(active.digest, [active, top])
    assert verdict == RECOMMEND_CHANGE and rec.fragile
    assert "better on x" in rec.pareto_note


def test_a_rejected_active_is_replaced_on_validity():
    active = vec("active", validity=(1,), failures=("kinds:x",))
    verdict, rec = recommend(active.digest, [active, vec("ok")])
    assert verdict == RECOMMEND_CHANGE
    assert rec.deciding_criterion == "validity"


def test_nothing_adoptable():
    active = vec("active", validity=(1,), failures=("kinds:x",))
    nr = vec("nr", verdict="NOT_RUNNABLE")
    assert recommend(active.digest, [active, nr]) == (
        NO_ADOPTABLE_CONFIGURATION, None)


def test_only_undecided_configurations_leave_the_answer_open():
    active = vec("active", elegance=None)
    verdict, rec = recommend(active.digest, [active])
    assert verdict == UNDECIDED and rec.candidates == (active.digest,)


def test_an_undecided_contender_not_beaten_keeps_the_answer_open():
    """K4: the top group would rest on an UNMEASURED value."""
    open_ = vec("open", consistency=None)
    verdict, rec = recommend(ACTIVE.digest, [ACTIVE, open_])
    assert verdict == UNDECIDED and rec.candidates == (open_.digest,)
    assert rec.reasons[0].startswith("K4")
    beaten = vec("beaten", closure=(1,), consistency=None)
    assert recommend(ACTIVE.digest, [ACTIVE, beaten])[0] == ACTIVE_CONFIRMED


def test_an_undecided_active_beaten_on_a_measured_criterion_is_replaced():
    active = vec("active", closure=(2,), elegance=None)
    verdict, rec = recommend(active.digest, [active, vec("top")])
    assert verdict == RECOMMEND_CHANGE and rec.deciding_criterion == "closure"


def test_an_unassessed_or_unrunnable_active_is_undecided():
    verdict, rec = recommend("missing", [ACTIVE])
    assert verdict == UNDECIDED and "not assessed" in rec.reasons[0]
    nr = vec("active", verdict="NOT_RUNNABLE")
    verdict, rec = recommend(nr.digest, [nr, vec("ok")])
    assert verdict == UNDECIDED and "NOT_RUNNABLE" in rec.reasons[0]
