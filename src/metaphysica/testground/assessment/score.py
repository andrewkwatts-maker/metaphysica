"""The score vector: what the D-019 comparator compares.

Five criteria in a FIXED order (pinned by a test). Each criterion's key is a
tuple of integers, lower is better. The comparator (assessment/comparator.py,
the only module allowed to rank) compares keys lexicographically: the first
criterion where two configurations differ decides, whatever later criteria say.
Data (criterion 5) is consulted only between configurations equal on 1-4.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

__all__ = [
    "VALIDITY",
    "CLOSURE",
    "CONSISTENCY",
    "ELEGANCE",
    "DATA",
    "CRITERIA",
    "DECIDING_CRITERIA",
    "MEASURED",
    "UNMEASURED",
    "CriterionScore",
    "ScoreVector",
    "ADOPTABLE",
    "REJECTED",
    "UNDECIDED",
    "NOT_RUNNABLE",
    "VERDICTS",
]

VALIDITY = "validity"
CLOSURE = "closure"
CONSISTENCY = "consistency"
ELEGANCE = "elegance"
DATA = "data"

#: THE ORDER. Changing it is a governance act (D-019) and a test pins it.
CRITERIA = (VALIDITY, CLOSURE, CONSISTENCY, ELEGANCE, DATA)
#: Criteria that may decide a recommendation outright; DATA only breaks ties.
DECIDING_CRITERIA = (VALIDITY, CLOSURE, CONSISTENCY, ELEGANCE)

MEASURED = "MEASURED"
UNMEASURED = "UNMEASURED"

# per-configuration verdicts
ADOPTABLE = "ADOPTABLE"          # passed the validity gate, fully measured
REJECTED = "REJECTED"            # failed the validity gate (reasons given)
UNDECIDED = "UNDECIDED"          # something on criteria 1-4 not measured
NOT_RUNNABLE = "NOT_RUNNABLE"    # unimplemented option or the run crashed
VERDICTS = (ADOPTABLE, REJECTED, UNDECIDED, NOT_RUNNABLE)


@dataclass(frozen=True)
class CriterionScore:
    """One criterion's key and how it was obtained."""

    criterion: str
    key: Optional[Tuple[int, ...]]
    status: str = MEASURED
    components: Dict[str, int] = field(default_factory=dict)
    failures: Tuple[str, ...] = ()
    unmeasured: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.criterion not in CRITERIA:
            raise ValueError("unknown criterion %r" % self.criterion)
        if self.status == MEASURED and self.key is None:
            raise ValueError("a MEASURED criterion needs a key")
        if self.key is not None and not all(
                isinstance(k, int) and not isinstance(k, bool)
                for k in self.key):
            raise ValueError("criterion keys are tuples of integers; got %r"
                             % (self.key,))

    @property
    def measured(self) -> bool:
        return self.status == MEASURED


@dataclass(frozen=True)
class ScoreVector:
    """All five criterion scores for one configuration."""

    digest: str
    scores: Tuple[CriterionScore, ...]
    verdict: str
    reasons: Tuple[str, ...] = ()
    stage_reached: str = "screen"

    def __post_init__(self) -> None:
        names = tuple(s.criterion for s in self.scores)
        if names != CRITERIA[:len(names)] or len(names) != len(CRITERIA):
            raise ValueError("scores must cover %s in order; got %s"
                             % (CRITERIA, names))
        if self.verdict not in VERDICTS:
            raise ValueError("verdict %r not in %s" % (self.verdict, VERDICTS))

    def score(self, criterion: str) -> CriterionScore:
        return self.scores[CRITERIA.index(criterion)]

    def keys(self) -> Tuple[Optional[Tuple[int, ...]], ...]:
        return tuple(s.key for s in self.scores)

    def decided(self) -> bool:
        """True when every deciding criterion (1-4) is measured."""
        return all(self.score(c).measured for c in DECIDING_CRITERIA)
