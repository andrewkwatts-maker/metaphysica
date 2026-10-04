"""The D-019 comparator -- the ONLY module of the test ground that ranks.

Lexicographic over the criteria in their pinned order (score.CRITERIA):

1. validity    a hard gate. A REJECTED configuration loses to one that passed;
               two REJECTED configurations are never ranked against each other.
2. closure
3. consistency (a Pareto note marks a win that is not Pareto-robust across
               the criterion's components: "fragile")
4. elegance
5. data        tie-break ONLY: consulted when 1-4 are all equal.

The first criterion where two configurations differ decides, whatever later
criteria say. An UNMEASURED or UNEVALUABLE value on criteria 1-4 never falls
through to a later criterion (amendment (f), kill condition K4): reaching one
makes the comparison UNDECIDED. Only ADOPTABLE configurations are ranked; the
rest are listed as unranked by verdict, never above a decided one.

This module ranks and never adopts: adoption is an explicit accept.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (Any, Dict, List, Mapping, Optional, Sequence, Tuple)

from metaphysica.testground.assessment.score import (ADOPTABLE, CONSISTENCY,
                                                     CRITERIA, DATA,
                                                     DECIDING_CRITERIA,
                                                     NOT_RUNNABLE, REJECTED,
                                                     VALIDITY, ScoreVector)
from metaphysica.testground.assessment.tiebreak import tiebreak
from metaphysica.testground.theory import ScoredRow

__all__ = [
    "A",
    "B",
    "TIE",
    "UNDECIDED",
    "WINNERS",
    "PARETO_CRITERIA",
    "Comparison",
    "margins_of",
    "pareto_note",
    "compare",
    "groups_of",
    "rank",
    "unranked",
]

A = "a"
B = "b"
TIE = "TIE"
UNDECIDED = "UNDECIDED"
WINNERS = (A, B, TIE, UNDECIDED)

#: Criteria whose wins carry a Pareto note across their components.
PARETO_CRITERIA = (CONSISTENCY,)

# validity gate states
_PASS, _FAIL, _OPEN = "pass", "fail", "open"


@dataclass(frozen=True)
class Comparison:
    """Who wins between two configurations, on which criterion, by how much.

    ``margins[c]`` is ``b_key - a_key`` per key position, for every criterion
    measured in both: positive entries favour ``a`` (lower is better).
    """

    winner: str
    deciding_criterion: Optional[str]
    margins: Dict[str, Tuple[int, ...]] = field(default_factory=dict)
    pareto_note: Optional[str] = None
    fragile: bool = False
    data_tiebreak: bool = False
    reasons: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.winner not in WINNERS:
            raise ValueError("winner %r not in %s" % (self.winner, WINNERS))

    def as_dict(self) -> Dict[str, Any]:
        return {
            "winner": self.winner,
            "deciding_criterion": self.deciding_criterion,
            "margins": {c: list(m) for c, m in self.margins.items()},
            "pareto_note": self.pareto_note,
            "fragile": self.fragile,
            "data_tiebreak": self.data_tiebreak,
            "reasons": list(self.reasons),
        }


def _gate(v: ScoreVector) -> str:
    if v.verdict == REJECTED:
        return _FAIL
    if v.verdict != NOT_RUNNABLE and v.score(VALIDITY).measured:
        return _PASS
    return _OPEN


def margins_of(a: ScoreVector, b: ScoreVector) -> Dict[str, Tuple[int, ...]]:
    """``b - a`` per key position, for criteria measured in both."""
    out: Dict[str, Tuple[int, ...]] = {}
    for c in CRITERIA:
        ka, kb = a.score(c).key, b.score(c).key
        if (a.score(c).measured and b.score(c).measured
                and ka is not None and kb is not None and len(ka) == len(kb)):
            out[c] = tuple(y - x for x, y in zip(ka, kb))
    return out


def pareto_note(winner: ScoreVector, loser: ScoreVector,
                criterion: str) -> Tuple[Optional[str], bool]:
    """(note, fragile) for a win on ``criterion``; (None, False) if n/a."""
    if criterion not in PARETO_CRITERIA:
        return None, False
    w = winner.score(criterion).components
    lo = loser.score(criterion).components
    worse = sorted(s for s in set(w) | set(lo) if lo.get(s, 0) < w.get(s, 0))
    if worse:
        return ("fragile: the %s win is not Pareto-robust -- the losing "
                "configuration is better on %s" % (criterion, ", ".join(worse)),
                True)
    return ("Pareto-robust: no worse on any %s component" % criterion, False)


def _gated(a: ScoreVector, b: ScoreVector,
           margins: Dict[str, Tuple[int, ...]]) -> Optional[Comparison]:
    """The validity-gate outcome, or None when both passed or are open."""
    ga, gb = _gate(a), _gate(b)
    if ga == _FAIL and gb == _FAIL:
        return Comparison(UNDECIDED, None, margins, reasons=(
            "both REJECTED: rejected configurations are not ranked against "
            "each other",))
    if _FAIL not in (ga, gb):
        return None
    other = gb if ga == _FAIL else ga
    if other == _PASS:
        return Comparison(B if ga == _FAIL else A, VALIDITY, margins,
                          reasons=("validity gate: the other configuration "
                                   "is REJECTED",))
    return Comparison(UNDECIDED, VALIDITY, margins, reasons=(
        "one configuration is REJECTED and the other's validity is not "
        "measured",))


def _on_criteria(a: ScoreVector, b: ScoreVector,
                 margins: Dict[str, Tuple[int, ...]]) -> Optional[Comparison]:
    """The first criterion of 1-4 that differs decides; a gap stops."""
    for c in DECIDING_CRITERIA:
        sa, sb = a.score(c), b.score(c)
        if not (sa.measured and sb.measured):
            gap = [x for x, s in ((A, sa), (B, sb)) if not s.measured]
            return Comparison(UNDECIDED, c, margins, reasons=(
                "%s not measured for %s: an UNMEASURED value never falls "
                "through to a later criterion (K4)" % (c, " and ".join(gap)),))
        if len(sa.key) != len(sb.key):
            raise ValueError("%s keys of different length: %r vs %r"
                             % (c, sa.key, sb.key))
        if sa.key != sb.key:
            first = A if sa.key < sb.key else B
            win, lose = (a, b) if first == A else (b, a)
            note, fragile = pareto_note(win, lose, c)
            return Comparison(first, c, margins, note, fragile)
    return None


def _on_data(a: ScoreVector, b: ScoreVector,
             margins: Dict[str, Tuple[int, ...]]) -> Comparison:
    sa, sb = a.score(DATA), b.score(DATA)
    if sa.measured and sb.measured and sa.key != sb.key:
        first = A if sa.key < sb.key else B
        return Comparison(first, DATA, margins, data_tiebreak=True, reasons=(
            "equal on criteria 1-4; data tie-break only (trials factor k=2; "
            "accepting on it adds 1 fitted degree of freedom)",))
    return Comparison(TIE, None, margins, reasons=(
        "equal on criteria 1-4 and not separated by data",))


def compare(a: ScoreVector, b: ScoreVector,
            use_data: bool = True) -> Comparison:
    """Compare two score vectors under the D-019 decision rule."""
    margins = margins_of(a, b)
    gated = _gated(a, b, margins)
    if gated is not None:
        return gated
    decided = _on_criteria(a, b, margins)
    if decided is not None:
        return decided
    if not use_data:
        return Comparison(TIE, None, margins, reasons=(
            "equal on criteria 1-4",))
    return _on_data(a, b, margins)


def _deciding_keys(v: ScoreVector) -> Tuple[Tuple[int, ...], ...]:
    return tuple(v.score(c).key for c in DECIDING_CRITERIA)


def groups_of(vectors: Sequence[ScoreVector]) -> List[List[ScoreVector]]:
    """ADOPTABLE vectors in groups of equals on criteria 1-4, lowest first.

    Input order is kept inside a group.
    """
    decided = [v for v in vectors if v.verdict == ADOPTABLE and v.decided()]
    shapes = {tuple(len(k) for k in _deciding_keys(v)) for v in decided}
    if len(shapes) > 1:
        raise ValueError("score vectors with different key layouts cannot "
                         "be ranked together: %s" % sorted(shapes))
    buckets: Dict[Tuple[Tuple[int, ...], ...], List[ScoreVector]] = {}
    for v in decided:
        buckets.setdefault(_deciding_keys(v), []).append(v)
    return [buckets[k] for k in sorted(buckets)]


def rank(vectors: Sequence[ScoreVector],
         rows: Optional[Mapping[str, Sequence[ScoredRow]]] = None
         ) -> List[List[str]]:
    """Digests in groups of equals on criteria 1-4, lowest keys first.

    Inside a group, data (tie-break only) orders the members; it never moves
    a configuration between groups.
    """
    out: List[List[str]] = []
    for group in groups_of(vectors):
        if len(group) == 1:
            out.append([group[0].digest])
            continue
        tb = tiebreak(group, rows)
        out.append([d for sub in tb.order for d in sub])
    return out


def unranked(vectors: Sequence[ScoreVector]) -> Dict[str, List[str]]:
    """verdict -> digests of every configuration left out of the ranking."""
    out: Dict[str, List[str]] = {}
    for v in vectors:
        if not (v.verdict == ADOPTABLE and v.decided()):
            out.setdefault(v.verdict, []).append(v.digest)
    return out
