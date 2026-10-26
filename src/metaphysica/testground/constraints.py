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
from typing import Dict, FrozenSet, List, Mapping, Sequence, Tuple, Union

__all__ = ["Requires", "Excludes", "Constraint", "violations", "is_valid",
           "constraints_from_options"]


@dataclass(frozen=True)
class Requires:
    """Choosing ``(fork, option)`` requires ``needs_fork`` to be one of
    ``needs_options``. Judged only when ``needs_fork`` is in the selection, so
    a partial selection is never refused for what it does not say."""

    fork: str
    option: str
    needs_fork: str
    needs_options: FrozenSet[str]
    rationale: str
    source: str

    def violated_by(self, selection: Mapping[str, str]) -> bool:
        return (selection.get(self.fork) == self.option
                and self.needs_fork in selection
                and selection[self.needs_fork] not in self.needs_options)

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


def constraints_from_options(forks) -> List[Constraint]:
    """The constraints that options declare on themselves (``requires`` and
    ``excludes``), as ``Requires`` and ``Excludes`` in declaration order.

    ``requires`` entries naming the same fork are one ``Requires`` (the listed
    options are OR'd); every ``excludes`` entry is one ``Excludes``. *forks* is
    a mapping of fork id to ``Fork`` or an iterable of ``Fork``.
    """
    items = forks.values() if isinstance(forks, Mapping) else forks
    out: List[Constraint] = []
    for fork in items:
        for opt in fork.options:
            rationale = "declared on %s.%s" % (fork.id, opt.id)
            needs: Dict[str, List[str]] = {}
            for need_fork, need_opt in opt.requires:
                needs.setdefault(need_fork, []).append(need_opt)
            for need_fork, need_opts in needs.items():
                out.append(Requires(fork.id, opt.id, need_fork,
                                    frozenset(need_opts), rationale,
                                    fork.source))
            for other_fork, other_opt in opt.excludes:
                out.append(Excludes(fork.id, opt.id, other_fork, other_opt,
                                    rationale, fork.source))
    return out
