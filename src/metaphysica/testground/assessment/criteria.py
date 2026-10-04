"""Criteria: turn one configuration's measurements into its D-019 score vector.

Each criterion's key is a tuple of integers, lower is better (score.py). This
module only SCORES one configuration; it never compares two (that is the
comparator's job, and only the comparator's).

Rules embodied here
===================
* Validity is a hard gate. Any live validity failure -- a failing validity
  signal, a target fact not reproduced, a declared constraint violated --
  makes the verdict REJECTED, with the failures as reasons.
* Amendment (f): an UNMEASURED or UNEVALUABLE value on criteria 1-4 leaves the
  criterion without a key (None) and the verdict UNDECIDED. Nothing falls
  through to a later criterion.
* Amendment (c): standing failures are excluded from the counts (and
  disclosed by the report, not here).
* NOT_RUNNABLE configurations pass straight through, unscored.
* Data (criterion 5) is optional per configuration: the tie-break normally
  scores it per tied group on common rows. Its absence never changes the
  verdict.

Key layout: the assessment config may pre-register, per criterion, which
signals sum into which key position (e.g. closure = (free_set_size +
discrete_inputs, n_calibrated)). A measured signal missing from a
pre-registered layout, or a layout signal never measured, leaves the
criterion UNMEASURED -- the pre-registration has to be amended first (K5).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import (Any, Dict, FrozenSet, List, Mapping, Optional, Sequence,
                    Tuple)

from metaphysica.testground.assessment.config import (AssessmentConfig,
                                                      TargetFact)
from metaphysica.testground.assessment.score import (ADOPTABLE, CLOSURE,
                                                     CRITERIA, DATA,
                                                     DECIDING_CRITERIA,
                                                     NOT_RUNNABLE, REJECTED,
                                                     UNDECIDED, UNMEASURED,
                                                     VALIDITY, CriterionScore,
                                                     ScoreVector)
from metaphysica.testground.assessment.standing import (SignalLookup,
                                                        by_criterion,
                                                        effective_count,
                                                        live_failures)
from metaphysica.testground.configurations.model import INVALID, Configuration
from metaphysica.testground.signals.model import UNEVALUABLE, Measurement
from metaphysica.testground.switches.model import Fork

__all__ = [
    "DISCRETE_INPUTS_SIGNAL",
    "DISCRETE_INPUTS_CRITERION",
    "DATA_DEFERRED",
    "by_criterion",
    "score_criterion",
    "validity_score",
    "score_configuration",
    "verdict_of",
    "discrete_inputs",
]

#: Signal id of the closure component "discrete inputs declared by options".
DISCRETE_INPUTS_SIGNAL = "discrete_inputs"
DISCRETE_INPUTS_CRITERION = CLOSURE
DATA_DEFERRED = ("data is scored per tied group on common rows "
                 "(tie-break only)")


def _not_measured(ms: Sequence[Measurement]) -> List[str]:
    return ["%s %s: %s" % (m.signal, m.status, "; ".join(m.reasons) or "-")
            for m in ms if not m.measured]


def _status_for(ms: Sequence[Measurement], problems: List[str]) -> str:
    """UNEVALUABLE only when every gap is an UNEVALUABLE reading."""
    gaps = [m for m in ms if not m.measured]
    if gaps and len(gaps) == len(problems) and all(
            m.status == UNEVALUABLE for m in gaps):
        return UNEVALUABLE
    return UNMEASURED


def _components(ms: Sequence[Measurement], standing: FrozenSet[str],
                readings: FrozenSet[str]) -> Tuple[Dict[str, int], List[str]]:
    """signal -> effective count, and the problems found on the way."""
    components: Dict[str, int] = {}
    problems: List[str] = []
    for m in ms:
        if not m.measured:
            continue
        if m.signal in components:
            problems.append("%s measured twice" % m.signal)
            continue
        count = effective_count(m, standing)
        if count is None:
            if m.signal not in readings:
                problems.append("%s measured without a count" % m.signal)
            continue
        components[m.signal] = count
    return components, problems


def _key(criterion: str, components: Dict[str, int],
         layout: Optional[Tuple[Tuple[str, ...], ...]],
         seen: FrozenSet[str]) -> Tuple[Optional[Tuple[int, ...]], List[str]]:
    """The criterion key from its components and pre-registered layout."""
    if layout is None:
        if not seen:
            return None, ["no signal measured for %s (pre-register an empty "
                          "layout to declare none)" % criterion]
        return (sum(components.values()),), []
    declared = {s for position in layout for s in position}
    problems = ["%s is not in the pre-registered %s layout" % (s, criterion)
                for s in sorted(set(components) - declared)]
    problems += ["%s pre-registered for %s was not measured" % (s, criterion)
                 for s in sorted(declared - seen)]
    if problems:
        return None, problems
    return tuple(sum(components.get(s, 0) for s in position)
                 for position in layout), []


def score_criterion(criterion: str, ms: Sequence[Measurement],
                    layout: Optional[Tuple[Tuple[str, ...], ...]] = None,
                    standing: FrozenSet[str] = frozenset(),
                    readings: FrozenSet[str] = frozenset()) -> CriterionScore:
    """Score one non-validity criterion from its measurements."""
    problems = _not_measured(ms)
    components, extra = _components(ms, standing, readings)
    seen = frozenset(m.signal for m in ms
                     if not (m.measured and m.count is None
                             and m.signal in readings))
    key, layout_problems = _key(criterion, components, layout, seen)
    problems += extra + layout_problems
    failures = tuple(sorted({f for m in ms for f in live_failures(m, standing)}))
    if problems:
        return CriterionScore(criterion, None, _status_for(ms, problems),
                              components, failures, tuple(problems))
    return CriterionScore(criterion, key, components=components,
                          failures=failures)


def _target_results(facts: Sequence[TargetFact],
                     index: Mapping[str, Measurement]
                     ) -> Tuple[List[str], List[str]]:
    """(failures, unmeasured) of the pre-registered target facts."""
    failures: List[str] = []
    unmeasured: List[str] = []
    for fact in facts:
        m = index.get(fact.signal)
        if m is None or not m.measured:
            why = "not measured" if m is None else m.status
            unmeasured.append("%s: signal %s %s" % (fact.check_id(),
                                                    fact.signal, why))
        elif fact.field not in m.detail:
            unmeasured.append("%s: signal %s reports no %r"
                              % (fact.check_id(), fact.signal, fact.field))
        elif m.detail[fact.field] != fact.expected:
            failures.append("%s: expected %r, got %r%s" % (
                fact.check_id(), fact.expected, m.detail[fact.field],
                " (%s)" % fact.source if fact.source else ""))
    return failures, unmeasured


def _validity_failures(ms: Sequence[Measurement],
                       standing: FrozenSet[str]) -> Tuple[List[str], int]:
    """Live failure ids (with each failing signal's reasons) and their count."""
    failures: List[str] = []
    total = 0
    for m in ms:
        if not m.measured:
            continue
        count = effective_count(m, standing) or 0
        live = live_failures(m, standing)
        total += count
        if count and not live:
            live = ["%s (count %d)" % (m.signal, count)]
        if live:
            failures += live + ["%s: %s" % (m.signal, r) for r in m.reasons]
    return failures, total


def validity_score(cfg: Configuration, ms: Sequence[Measurement],
                   index: Mapping[str, Measurement],
                   assess_cfg: AssessmentConfig,
                   standing: FrozenSet[str] = frozenset()) -> CriterionScore:
    """The validity gate: signals, target facts and declared constraints."""
    failures, total = _validity_failures(ms, standing)
    fact_failures, unmeasured = _target_results(assess_cfg.target_facts, index)
    failures += fact_failures
    total += len(fact_failures)
    if cfg.lifecycle == INVALID:
        failures += ["constraint: %s" % r for r in cfg.reasons] or [
            "constraint: violates a declared constraint"]
        total += 1
    readings = assess_cfg.target_signals()
    unmeasured = _not_measured(ms) + unmeasured
    unmeasured += ["%s measured without a count" % m.signal for m in ms
                   if m.measured and m.count is None
                   and m.signal not in readings]
    if not ms and not assess_cfg.target_facts and cfg.lifecycle != INVALID:
        unmeasured.append("no validity check measured")
    components = {m.signal: effective_count(m, standing) or 0
                  for m in ms if m.measured}
    if unmeasured:
        return CriterionScore(VALIDITY, None, _status_for(ms, unmeasured),
                              components, tuple(failures), tuple(unmeasured))
    return CriterionScore(VALIDITY, (total,), components=components,
                          failures=tuple(failures))


def _data_score(ms: Sequence[Measurement], assess_cfg: AssessmentConfig,
                standing: FrozenSet[str]) -> CriterionScore:
    if not ms:
        return CriterionScore(DATA, None, UNMEASURED,
                              unmeasured=(DATA_DEFERRED,))
    return score_criterion(DATA, ms, assess_cfg.layout(DATA), standing)


def verdict_of(scores: Sequence[CriterionScore]) -> Tuple[str, Tuple[str, ...]]:
    """REJECTED on a validity failure, UNDECIDED on a gap in 1-4, else
    ADOPTABLE -- with the reasons."""
    validity = scores[CRITERIA.index(VALIDITY)]
    if validity.failures:
        return REJECTED, tuple(validity.failures)
    gaps = [s for s in scores if s.criterion in DECIDING_CRITERIA
            and not s.measured]
    if gaps:
        return UNDECIDED, tuple("%s: %s" % (s.criterion, u) for s in gaps
                                for u in (s.unmeasured or (s.status,)))
    return ADOPTABLE, ()


def _not_runnable(cfg: Configuration, stage_reached: str) -> ScoreVector:
    why = tuple(cfg.reasons) or ("not runnable",)
    scores = tuple(CriterionScore(c, None, UNMEASURED, unmeasured=why)
                   for c in CRITERIA)
    return ScoreVector(cfg.digest, scores, NOT_RUNNABLE, why, stage_reached)


def _index(grouped: Mapping[str, List[Measurement]]) -> Dict[str, Measurement]:
    return {m.signal: m for ms in grouped.values() for m in ms}


def score_configuration(cfg: Configuration, measurements: Any,
                        assess_cfg: Optional[AssessmentConfig] = None,
                        standing: FrozenSet[str] = frozenset(),
                        signals: SignalLookup = None,
                        stage_reached: str = "screen") -> ScoreVector:
    """The score vector of one configuration.

    ``measurements``: any form `by_criterion` accepts (a criterion-keyed
    mapping, ``(Signal, Measurement)`` pairs, or bare Measurements with
    ``signals`` for the lookup).
    """
    if cfg.not_runnable:
        return _not_runnable(cfg, stage_reached)
    assess_cfg = assess_cfg or AssessmentConfig.empty()
    grouped = by_criterion(measurements, signals)
    index = _index(grouped)
    readings = assess_cfg.target_signals()
    scores: List[CriterionScore] = []
    for criterion in CRITERIA:
        ms = grouped[criterion]
        if criterion == VALIDITY:
            scores.append(validity_score(cfg, ms, index, assess_cfg, standing))
        elif criterion == DATA:
            scores.append(_data_score(ms, assess_cfg, standing))
        else:
            scores.append(score_criterion(criterion, ms,
                                          assess_cfg.layout(criterion),
                                          standing, readings))
    verdict, reasons = verdict_of(scores)
    return ScoreVector(cfg.digest, tuple(scores), verdict, reasons,
                       stage_reached)


def discrete_inputs(forks: Mapping[str, Fork],
                    cfg: Configuration) -> Measurement:
    """The closure component: discrete inputs the chosen options declare.

    Counts options with ``adds_discrete_input=True``. Add the result to the
    closure measurements (signal id ``discrete_inputs``; criterion
    `DISCRETE_INPUTS_CRITERION`).
    """
    inputs = ["%s=%s" % (f, o) for f, o in cfg.selection
              if f in forks and forks[f].option(o).adds_discrete_input]
    return Measurement(DISCRETE_INPUTS_SIGNAL, count=len(inputs),
                       detail={"inputs": inputs})
