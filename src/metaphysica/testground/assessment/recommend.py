"""The recommendation: is the active configuration still in the top group?

Reads the comparator's groups and returns one of five verdicts. It RECOMMENDS
and never adopts -- adoption is one explicit accept (D-019, the author's
ruling of 2026-10-02).

ACTIVE_CONFIRMED            the active is in the top group and data does not
                            put another member strictly ahead of it. A
                            complete tie keeps the active (amendment (e)).
RECOMMEND_CHANGE            the top group beats the active on a deciding
                            criterion (1-4); the recommendation names the
                            criterion and the margins.
DATA_TIEBREAK_SUGGESTS      the active ties the top group on 1-4 and data (on
                            common rows) puts another member ahead. Disclosed
                            with its trials factor k; accepting on it adds one
                            fitted degree of freedom.
NO_ADOPTABLE_CONFIGURATION  every configuration is REJECTED or NOT_RUNNABLE.
UNDECIDED                   the answer rests on an UNMEASURED value (K4): the
                            active is unmeasured or not runnable, or an
                            UNDECIDED configuration is not beaten by the top
                            group on a measured criterion.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (Any, Dict, List, Mapping, Optional, Sequence, Tuple)

from metaphysica.testground.assessment.comparator import (A, Comparison,
                                                          compare, groups_of)
from metaphysica.testground.assessment.score import (DATA, NOT_RUNNABLE,
                                                     UNDECIDED as
                                                     CFG_UNDECIDED,
                                                     ScoreVector)
from metaphysica.testground.assessment.tiebreak import (FITTED_DOF_ON_ACCEPT,
                                                        TieBreak, tiebreak)
from metaphysica.testground.theory import ScoredRow

__all__ = [
    "ACTIVE_CONFIRMED",
    "RECOMMEND_CHANGE",
    "DATA_TIEBREAK_SUGGESTS",
    "NO_ADOPTABLE_CONFIGURATION",
    "UNDECIDED",
    "RECOMMENDATION_VERDICTS",
    "Recommendation",
    "recommend",
]

ACTIVE_CONFIRMED = "ACTIVE_CONFIRMED"
RECOMMEND_CHANGE = "RECOMMEND_CHANGE"
DATA_TIEBREAK_SUGGESTS = "DATA_TIEBREAK_SUGGESTS"
NO_ADOPTABLE_CONFIGURATION = "NO_ADOPTABLE_CONFIGURATION"
UNDECIDED = "UNDECIDED"
RECOMMENDATION_VERDICTS = (ACTIVE_CONFIRMED, RECOMMEND_CHANGE,
                           DATA_TIEBREAK_SUGGESTS, NO_ADOPTABLE_CONFIGURATION,
                           UNDECIDED)

Rows = Optional[Mapping[str, Sequence[ScoredRow]]]


@dataclass(frozen=True)
class Recommendation:
    """What the assessment suggests, why, and what accepting it would cost."""

    active: str
    #: The single suggested configuration, or None when several are equal.
    target: Optional[str] = None
    #: Every configuration the suggestion is drawn from (or still open).
    candidates: Tuple[str, ...] = ()
    deciding_criterion: Optional[str] = None
    margins: Dict[str, Tuple[int, ...]] = field(default_factory=dict)
    pareto_note: Optional[str] = None
    fragile: bool = False
    tiebreak: Optional[TieBreak] = None
    uses_data_tiebreak: bool = False
    reasons: Tuple[str, ...] = ()

    @property
    def fitted_dof_on_accept(self) -> int:
        return FITTED_DOF_ON_ACCEPT if self.uses_data_tiebreak else 0

    @property
    def trials_factor(self) -> Optional[int]:
        return self.tiebreak.k if self.uses_data_tiebreak else None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "target": self.target,
            "candidates": list(self.candidates),
            "deciding_criterion": self.deciding_criterion,
            "margins": {c: list(m) for c, m in self.margins.items()},
            "pareto_note": self.pareto_note,
            "fragile": self.fragile,
            "uses_data_tiebreak": self.uses_data_tiebreak,
            "trials_factor_k": self.trials_factor,
            "fitted_dof_on_accept": self.fitted_dof_on_accept,
            "tiebreak": self.tiebreak.as_dict() if self.tiebreak else None,
            "reasons": list(self.reasons),
        }


def _open_contenders(top: ScoreVector, vectors: Sequence[ScoreVector]
                     ) -> List[Tuple[str, Comparison]]:
    """UNDECIDED configurations the top group does not beat on a measured
    criterion -- each could still outrank or tie it."""
    out = []
    for v in vectors:
        if v.verdict == CFG_UNDECIDED:
            c = compare(top, v)
            if c.winner != A:
                out.append((v.digest, c))
    return out


def _undecided(active: str, open_: List[Tuple[str, Comparison]]
               ) -> Tuple[str, Recommendation]:
    reasons = tuple("%s: %s" % (d, "; ".join(c.reasons)) for d, c in open_)
    return UNDECIDED, Recommendation(
        active, candidates=tuple(d for d, _ in open_), reasons=(
            "K4: the answer would rest on an UNMEASURED value",) + reasons)


def _within_top(active: ScoreVector, top: List[ScoreVector],
                rows: Rows) -> Tuple[str, Optional[Recommendation]]:
    """The active ties the top group on 1-4: data may only suggest."""
    if len(top) == 1:
        return ACTIVE_CONFIRMED, None
    tb = tiebreak(top, rows)
    if active.digest in tb.order[0]:
        return ACTIVE_CONFIRMED, None
    by = {v.digest: v for v in top}
    target = tb.leader
    margins = compare(by[target or tb.order[0][0]], active).margins
    return DATA_TIEBREAK_SUGGESTS, Recommendation(
        active.digest, target, tb.order[0], DATA, margins, tiebreak=tb,
        uses_data_tiebreak=True, reasons=(
            "the active ties the top group on criteria 1-4; data (%s) puts "
            "%s ahead" % (tb.basis, ", ".join(tb.order[0])),
            "trials factor k=%d; accepting on it adds %d fitted degree of "
            "freedom" % (tb.k, FITTED_DOF_ON_ACCEPT)))


def _change(active: ScoreVector, top: List[ScoreVector],
            rows: Rows) -> Tuple[str, Recommendation]:
    """The top group beats the active on a deciding criterion."""
    digests = tuple(v.digest for v in top)
    tb = tiebreak(top, rows) if len(top) > 1 else None
    target = digests[0] if tb is None else tb.leader
    picked_by_data = tb is not None and target is not None
    by = {v.digest: v for v in top}
    c = compare(by[target or digests[0]], active)
    reasons = ["the top group beats the active on %s"
               % c.deciding_criterion] + list(c.reasons)
    if tb is not None:
        reasons.append(
            "the top group has %d equal members; data (%s) %s; trials factor "
            "k=%d" % (tb.k, tb.basis,
                      "picks %s" % target if target else "does not separate "
                      "them -- choose explicitly", tb.k))
    return RECOMMEND_CHANGE, Recommendation(
        active.digest, target, digests, c.deciding_criterion, c.margins,
        c.pareto_note, c.fragile, tb, uses_data_tiebreak=picked_by_data,
        reasons=tuple(reasons))


def recommend(active_digest: str, vectors: Sequence[ScoreVector],
              rows: Rows = None) -> Tuple[str, Optional[Recommendation]]:
    """(verdict, recommendation) for the active configuration.

    ``rows`` (digest -> scored rows) lets the data tie-break use the rows
    common to a tied group; without it each vector's own data key is used.
    """
    by = {v.digest: v for v in vectors}
    active = by.get(active_digest)
    if active is None or active.verdict == NOT_RUNNABLE:
        why = ("the active configuration was not assessed" if active is None
               else "the active configuration is NOT_RUNNABLE: %s"
               % "; ".join(active.reasons))
        return UNDECIDED, Recommendation(active_digest, reasons=(why,))
    groups = groups_of(vectors)
    if not groups:
        undecided = tuple(v.digest for v in vectors
                          if v.verdict == CFG_UNDECIDED)
        if undecided:
            return UNDECIDED, Recommendation(
                active_digest, candidates=undecided,
                reasons=("no configuration is fully measured on criteria "
                         "1-4",))
        return NO_ADOPTABLE_CONFIGURATION, None
    top = groups[0]
    open_ = _open_contenders(top[0], vectors)
    if open_:
        return _undecided(active_digest, open_)
    if active_digest in {v.digest for v in top}:
        return _within_top(active, top, rows)
    return _change(active, top, rows)
