"""Enumeration: the configurations a mode visits, lazily and constraint-pruned.

ORDER (deterministic, identical to switch_search.combinations_for)
=================================================================
Each fork's options are ordered: the active option first, then by declared
priority, then by declaration order. Configurations are the product of those
lists in fork declaration order (the first fork varies slowest), so the very
first configuration is always the active selection and a capped sweep drops
the most exotic combinations, never the baseline.

WHAT IS SWEPT
=============
Only physics forks are swept. Policy and narrative forks are held at their
active option in every mode; ``forks=`` narrows the sweep further (every other
fork is held at its active option). The mode decides which option statuses a
swept fork visits (see `modes`). An option declared ``implemented=False`` is
still yielded; its configuration carries ``not_runnable=True`` and a reason.

PRUNING
=======
The walk is a depth-first search that assigns forks in order and tests each
constraint as soon as the last of its swept forks is assigned (held forks are
assigned up front), so an excluded prefix is never expanded and the full
product is never built. INVALID configurations are never yielded, except in
mode `probe-constraint`, which does not prune and labels them INVALID.

COUNTING
========
`count_configurations` never materialises the product: forks that no
constraint touches contribute a plain factor, and each connected group of
constrained forks is counted by the same pruned walk. A group larger than
``limit`` valid assignments stops early and the count is flagged inexact (a
lower bound).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import (TYPE_CHECKING, Any, Dict, Iterable, Iterator, List,
                    Mapping, Optional, Sequence, Tuple)

from metaphysica.testground.configurations.lifecycle import Classifier
from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.configurations.modes import SINGLE, spec, sweeps
from metaphysica.testground.constraints import Constraint, violations
from metaphysica.testground.switches.model import Fork
from metaphysica.testground.switches.resolve import resolve_selection

if TYPE_CHECKING:  # pragma: no cover - typing only
    from metaphysica.testground.theory import Theory

__all__ = [
    "SWEPT_KIND",
    "DEFAULT_COUNT_LIMIT",
    "InvalidSelectionError",
    "EnumerationPlan",
    "ConfigurationCount",
    "ordered_options",
    "plan_enumeration",
    "enumerate_configurations",
    "count_configurations",
]

#: The only fork kind a sweep varies.
SWEPT_KIND = "physics"
#: Valid assignments counted per constrained group before giving up exactness.
DEFAULT_COUNT_LIMIT = 1_000_000


class InvalidSelectionError(ValueError):
    """Mode `single` was asked to yield a selection that breaks a constraint."""


@dataclass(frozen=True)
class EnumerationPlan:
    """The per-fork option lists a mode walks, before any walking."""

    theory: str
    mode: str
    #: Every declared fork, in declaration order.
    forks: Tuple[str, ...]
    #: Ordered option ids per fork (a held fork has exactly one).
    domains: Tuple[Tuple[str, ...], ...]
    swept: Tuple[str, ...]
    held: Tuple[str, ...]
    prunes: bool
    #: Disclosures about the plan (e.g. a policy fork held against the env).
    notes: Tuple[str, ...] = ()

    @property
    def raw(self) -> int:
        """Size of the unpruned product."""
        return math.prod(len(d) for d in self.domains)

    def domain(self, fork_id: str) -> Tuple[str, ...]:
        return self.domains[self.forks.index(fork_id)]


@dataclass(frozen=True)
class ConfigurationCount:
    """How many configurations a mode yields, counted without materialising."""

    theory: str
    mode: str
    swept: Tuple[str, ...]
    held: Tuple[str, ...]
    #: Size of the unpruned product over the per-fork option lists.
    raw: int
    #: Combinations satisfying every constraint.
    valid: int
    #: What the enumeration yields without a cap (probe-constraint: raw).
    total: int
    #: Of ``total``, configurations using an unimplemented option; None when
    #: the count is inexact.
    not_runnable: Optional[int]
    #: False when a constrained group exceeded the limit: valid and total are
    #: then lower bounds.
    exact: bool
    cap: Optional[int] = None

    @property
    def pruned(self) -> int:
        """Combinations a constraint excludes (raw - valid)."""
        return self.raw - self.valid

    @property
    def yielded(self) -> int:
        """What `enumerate_configurations` with the same cap yields."""
        return self.total if self.cap is None else min(self.total, self.cap)

    @property
    def capped(self) -> bool:
        """True when the cap may truncate the enumeration."""
        return self.cap is not None and (self.total > self.cap
                                         or not self.exact)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "theory": self.theory, "mode": self.mode,
            "swept": list(self.swept), "held": list(self.held),
            "raw": self.raw, "valid": self.valid, "pruned": self.pruned,
            "total": self.total, "not_runnable": self.not_runnable,
            "exact": self.exact, "cap": self.cap, "yielded": self.yielded,
            "capped": self.capped,
        }


# ------------------------------------------------------------------ planning


def ordered_options(fork: Fork, active_option: str, mode: str,
                    ) -> Tuple[str, ...]:
    """The options ``mode`` visits on ``fork``: active, priority, declaration."""
    in_order = sorted(enumerate(fork.options),
                      key=lambda pair: (pair[1].id != active_option,
                                        pair[1].priority, pair[0]))
    return tuple(opt.id for _, opt in in_order
                 if opt.id == active_option or sweeps(mode, opt))


def _requested(forks: Mapping[str, Fork],
               requested: Optional[Iterable[str]]) -> Optional[frozenset]:
    if requested is None:
        return None
    ids = [requested] if isinstance(requested, str) else list(requested)
    unknown = sorted(set(ids) - set(forks))
    if unknown:
        raise KeyError("unknown forks %s; declared: %s"
                       % (unknown, sorted(forks)))
    return frozenset(ids)


def _single_selection(theory: "Theory", forks: Mapping[str, Fork],
                      active: Mapping[str, str],
                      ) -> Tuple[Dict[str, str], Tuple[str, ...]]:
    """The selection in force, policy and narrative forks held at active."""
    in_force = resolve_selection(theory)
    notes: List[str] = []
    for fork_id, fork in forks.items():
        if fork.kind != SWEPT_KIND and in_force[fork_id] != active[fork_id]:
            notes.append("%s fork %s held at its active option %s "
                         "(in force: %s)" % (fork.kind, fork_id,
                                             active[fork_id],
                                             in_force[fork_id]))
            in_force[fork_id] = active[fork_id]
    return in_force, tuple(notes)


def _plan(theory: "Theory", mode: str, requested: Optional[Iterable[str]],
          classifier: Classifier) -> EnumerationPlan:
    mode_spec = spec(mode)
    forks = classifier.forks
    wanted = _requested(forks, requested)
    active = classifier.active
    if mode_spec.single:
        selection, notes = _single_selection(theory, forks, active)
        return EnumerationPlan(
            theory.id, mode_spec.name, tuple(forks),
            tuple((selection[f],) for f in forks), (), tuple(forks), True,
            notes)
    swept = [f for f, fork in forks.items() if fork.kind == SWEPT_KIND
             and (wanted is None or f in wanted)]
    notes = tuple("%s fork %s is held at its active option in every mode"
                  % (forks[f].kind, f) for f in sorted(wanted or ())
                  if forks[f].kind != SWEPT_KIND)
    domains = tuple(
        ordered_options(fork, active[f], mode_spec.name) if f in swept
        else (active[f],) for f, fork in forks.items())
    return EnumerationPlan(
        theory.id, mode_spec.name, tuple(forks), domains, tuple(swept),
        tuple(f for f in forks if f not in swept), mode_spec.prunes, notes)


def plan_enumeration(theory: "Theory", mode: str,
                     forks: Optional[Iterable[str]] = None,
                     ) -> EnumerationPlan:
    """The option lists ``mode`` walks (``forks`` narrows the sweep)."""
    return _plan(theory, mode, forks, Classifier(theory))


# ------------------------------------------------------------------- walking


def _constraint_forks(constraint: Constraint) -> Optional[Tuple[str, ...]]:
    """Forks a constraint reads; None for an unrecognised constraint type."""
    if hasattr(constraint, "needs_fork"):
        return (constraint.fork, constraint.needs_fork)
    if hasattr(constraint, "fork_b"):
        return (constraint.fork_a, constraint.fork_b)
    return None


def _checks_by_depth(names: Sequence[str],
                     domains: Sequence[Sequence[str]],
                     constraints: Sequence[Constraint],
                     ) -> Tuple[List[Constraint], List[List[Constraint]]]:
    """(up-front checks, checks per depth): each constraint is tested once,
    when the last of its varying forks is assigned."""
    index = {name: i for i, name in enumerate(names)}
    upfront: List[Constraint] = []
    by_depth: List[List[Constraint]] = [[] for _ in names]
    for constraint in constraints:
        read = _constraint_forks(constraint)
        positions = (range(len(names)) if read is None
                     else [index[f] for f in read if f in index])
        varying = [p for p in positions if len(domains[p]) > 1]
        if varying:
            by_depth[max(varying)].append(constraint)
        else:                       # same verdict for every assignment
            upfront.append(constraint)
    return upfront, by_depth


def _walk(names: Sequence[str], domains: Sequence[Sequence[str]],
          constraints: Sequence[Constraint]) -> Iterator[Dict[str, str]]:
    """Every assignment of ``domains`` (product order) that no constraint
    excludes, pruning a prefix as soon as it is excluded."""
    if any(not d for d in domains):
        return
    upfront, by_depth = _checks_by_depth(names, domains, constraints)
    sel = {name: domains[i][0] for i, name in enumerate(names)}
    if any(c.violated_by(sel) for c in upfront):
        return
    if not names:
        yield {}
        return
    last = len(names) - 1
    idx = [0] * len(names)
    depth = 0
    while depth >= 0:
        if idx[depth] == len(domains[depth]):
            idx[depth] = 0
            depth -= 1
            if depth >= 0:
                idx[depth] += 1
            continue
        sel[names[depth]] = domains[depth][idx[depth]]
        if any(c.violated_by(sel) for c in by_depth[depth]):
            idx[depth] += 1
        elif depth == last:
            yield dict(sel)
            idx[depth] += 1
        else:
            depth += 1


def _generate(plan: EnumerationPlan, classifier: Classifier,
              constraints: Sequence[Constraint], cap: Optional[int],
              ) -> Iterator[Configuration]:
    if cap == 0:
        return
    reasons = plan.notes if plan.mode == SINGLE else ()
    produced = 0
    for sel in _walk(plan.forks, plan.domains,
                     constraints if plan.prunes else ()):
        yield classifier.configuration(sel, extra_reasons=reasons)
        produced += 1
        if cap is not None and produced >= cap:
            return


def _check_cap(cap: Optional[int]) -> None:
    if cap is not None and (isinstance(cap, bool) or cap < 0):
        raise ValueError("cap must be a non-negative integer or None, not %r"
                         % (cap,))


def enumerate_configurations(theory: "Theory", mode: str,
                             forks: Optional[Iterable[str]] = None,
                             cap: Optional[int] = None,
                             ) -> Iterator[Configuration]:
    """Lazily yield the labelled configurations ``mode`` visits.

    Arguments are checked, and the store read, when this is CALLED; the
    configurations themselves are produced one at a time as iterated.
    """
    _check_cap(cap)
    classifier = Classifier(theory)
    plan = _plan(theory, mode, forks, classifier)
    if plan.mode == SINGLE:
        selection = {f: d[0] for f, d in zip(plan.forks, plan.domains)}
        broken = violations(selection, classifier.constraints)
        if broken:
            raise InvalidSelectionError(
                "the selection in force violates %s"
                % "; ".join("%s -- %s" % pair for pair in broken))
    return _generate(plan, classifier, classifier.constraints, cap)


# ------------------------------------------------------------------ counting


def _components(names: Sequence[str],
                constraints: Sequence[Constraint],
                ) -> List[Tuple[List[int], List[Constraint]]]:
    """Connected groups of fork positions joined by constraints."""
    parent = list(range(len(names)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    index = {name: i for i, name in enumerate(names)}
    touched: List[Tuple[Constraint, List[int]]] = []
    for constraint in constraints:
        read = _constraint_forks(constraint)
        positions = (list(range(len(names))) if read is None
                     else [index[f] for f in read if f in index])
        for p in positions[1:]:
            parent[find(p)] = find(positions[0])
        if positions:
            touched.append((constraint, positions))
    groups: Dict[int, Tuple[List[int], List[Constraint]]] = {}
    for constraint, positions in touched:
        root = find(positions[0])
        groups.setdefault(root, ([], []))[1].append(constraint)
    for i in range(len(names)):
        if find(i) in groups:
            groups[find(i)][0].append(i)
    return list(groups.values())


def _count(names: Sequence[str], domains: Sequence[Sequence[str]],
           constraints: Sequence[Constraint], limit: int,
           ) -> Tuple[int, bool]:
    """(number of valid assignments, exact?) without building the product."""
    if any(not d for d in domains):
        return 0, True
    groups = _components(names, constraints)
    in_group = {i for positions, _ in groups for i in positions}
    total = math.prod(len(domains[i]) for i in range(len(names))
                      if i not in in_group)
    exact = True
    for positions, group_constraints in groups:
        walk = _walk([names[i] for i in positions],
                     [domains[i] for i in positions], group_constraints)
        found = sum(1 for _ in itertools.islice(walk, limit + 1))
        if found > limit:
            exact = False
        total *= found
    return total, exact


def _runnable_domains(plan: EnumerationPlan, classifier: Classifier,
                      ) -> Tuple[Tuple[str, ...], ...]:
    return tuple(
        tuple(o for o in domain
              if classifier.forks[fork_id].option(o).implemented)
        for fork_id, domain in zip(plan.forks, plan.domains))


def count_configurations(theory: "Theory", mode: str,
                         forks: Optional[Iterable[str]] = None,
                         cap: Optional[int] = None, *,
                         limit: int = DEFAULT_COUNT_LIMIT,
                         ) -> ConfigurationCount:
    """How many configurations ``mode`` yields, and how many are runnable."""
    _check_cap(cap)
    classifier = Classifier(theory)
    plan = _plan(theory, mode, forks, classifier)
    constraints = classifier.constraints
    valid, exact = _count(plan.forks, plan.domains, constraints, limit)
    runnable_domains = _runnable_domains(plan, classifier)
    if plan.prunes:
        total = valid
        runnable, runnable_exact = _count(plan.forks, runnable_domains,
                                          constraints, limit)
    else:
        total = plan.raw
        runnable = math.prod(len(d) for d in runnable_domains)
        runnable_exact = True
    exact_all = exact and runnable_exact
    return ConfigurationCount(
        theory.id, plan.mode, plan.swept, plan.held, plan.raw, valid, total,
        total - runnable if exact_all else None, exact, cap)
