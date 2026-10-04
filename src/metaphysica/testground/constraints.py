"""Constraints: which option combinations are configurations of the theory at all.

Only DEFINITIONAL presuppositions belong here -- a combination that is not a
path of the theory (an origin story for b_3 = 24 on a seed where b_3 = 43). A
combination that is a path but fails a test is not a constraint violation: it is
run and REJECTED by a measured check, so the failure stays visible and the
check stays falsifiable. Every constraint carries the quote it rests on and its
source, and is pre-registered (D-019 annex) before an assessment uses it.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, List, Mapping, Sequence, Tuple, Union

__all__ = ["Requires", "Excludes", "Constraint", "violations", "is_valid"]


@dataclass(frozen=True)
class Requires:
    """Choosing ``(fork, option)`` requires ``needs_fork`` to be one of
    ``needs_options``."""

    fork: str
    option: str
    needs_fork: str
    needs_options: FrozenSet[str]
    rationale: str
    source: str

    def violated_by(self, selection: Mapping[str, str]) -> bool:
        return (selection.get(self.fork) == self.option
                and selection.get(self.needs_fork) not in self.needs_options)

    def describe(self) -> str:
        return "%s=%s requires %s in {%s}" % (
            self.fork, self.option, self.needs_fork,
            ", ".join(sorted(self.needs_options)))


@dataclass(frozen=True)
class Excludes:
    """``(fork_a, option_a)`` and ``(fork_b, option_b)`` cannot co-occur."""

    fork_a: str
    option_a: str
    fork_b: str
    option_b: str
    rationale: str
    source: str

    def violated_by(self, selection: Mapping[str, str]) -> bool:
        return (selection.get(self.fork_a) == self.option_a
                and selection.get(self.fork_b) == self.option_b)

    def describe(self) -> str:
        return "%s=%s excludes %s=%s" % (self.fork_a, self.option_a,
                                         self.fork_b, self.option_b)


Constraint = Union[Requires, Excludes]


def violations(selection: Mapping[str, str],
               constraints: Sequence[Constraint]) -> List[Tuple[str, str]]:
    """(description, rationale) for every constraint the selection breaks."""
    return [(c.describe(), c.rationale) for c in constraints
            if c.violated_by(selection)]


def is_valid(selection: Mapping[str, str],
             constraints: Sequence[Constraint]) -> bool:
    return not any(c.violated_by(selection) for c in constraints)
