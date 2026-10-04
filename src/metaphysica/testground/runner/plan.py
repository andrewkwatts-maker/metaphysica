"""Run plan: which configurations run, at which stage, in which process group.

A fork whose option is read when a module is imported (binding
``import_time``) cannot be flipped faithfully inside a process that has
already imported it. The plan therefore groups configurations by the options
of their import-time-bound forks: every group runs in its own fresh process,
and only call-time forks are flipped in-process within a group.

Order is deterministic: configurations keep the order they were given in (the
enumerator puts the active selection first), duplicates by digest are dropped,
and groups appear in the order of their first configuration.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Tuple

from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.signals.model import FULL, SCREEN
from metaphysica.testground.theory import Theory

__all__ = [
    "STAGES",
    "IMPORT_TIME",
    "UNKNOWN",
    "PlanEntry",
    "RunGroup",
    "RunPlan",
    "import_time_forks",
    "group_key",
    "build_plan",
]

STAGES = (SCREEN, FULL)
IMPORT_TIME = "import_time"
UNKNOWN = "unknown"

Pairs = Tuple[Tuple[str, str], ...]


@dataclass(frozen=True)
class PlanEntry:
    """One configuration in the plan, with its stage and process group."""

    index: int
    configuration: Configuration
    stage: str
    group: int

    @property
    def digest(self) -> str:
        return self.configuration.digest


@dataclass(frozen=True)
class RunGroup:
    """Configurations sharing every import-time fork option (one process)."""

    index: int
    #: The (fork, option) pairs of the import-time forks the group shares.
    key: Pairs
    configurations: Tuple[Configuration, ...]

    def env(self, theory: Theory) -> Dict[str, str]:
        """Environment to set BEFORE the group's process imports the theory."""
        return theory.env_for(dict(self.key))

    def digests(self) -> List[str]:
        return [cfg.digest for cfg in self.configurations]


@dataclass(frozen=True)
class RunPlan:
    """An ordered list of configurations, a stage, and process grouping."""

    theory: str
    stage: str
    import_time_forks: Tuple[str, ...]
    groups: Tuple[RunGroup, ...]
    entries: Tuple[PlanEntry, ...]

    @property
    def configurations(self) -> Tuple[Configuration, ...]:
        return tuple(entry.configuration for entry in self.entries)

    def digests(self) -> List[str]:
        return [entry.digest for entry in self.entries]

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self) -> Iterator[PlanEntry]:
        return iter(self.entries)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theory": self.theory,
            "stage": self.stage,
            "import_time_forks": list(self.import_time_forks),
            "groups": [{"index": g.index, "key": dict(g.key),
                        "digests": g.digests()} for g in self.groups],
            "entries": [{"index": e.index, "digest": e.digest,
                         "group": e.group} for e in self.entries],
        }


def import_time_forks(theory: Theory,
                      unknown_as_import_time: bool = False
                      ) -> Tuple[str, ...]:
    """Fork ids bound at import (optionally also those not yet calibrated)."""
    bound = {IMPORT_TIME, UNKNOWN} if unknown_as_import_time else {IMPORT_TIME}
    return tuple(fork_id for fork_id, fork in theory.switches.forks().items()
                 if fork.binding in bound)


def group_key(cfg: Configuration, forks: Iterable[str]) -> Pairs:
    """The (fork, option) pairs of ``forks`` in ``cfg`` (absent forks skipped)."""
    mapping = cfg.mapping
    return tuple((f, mapping[f]) for f in sorted(forks) if f in mapping)


def _unique(configurations: Iterable[Configuration]) -> List[Configuration]:
    seen, kept = set(), []
    for cfg in configurations:
        if cfg.digest not in seen:
            seen.add(cfg.digest)
            kept.append(cfg)
    return kept


def _check(theory: Theory, configurations: List[Configuration],
           stage: str) -> None:
    if stage not in STAGES:
        raise ValueError("stage %r is not one of %s" % (stage, STAGES))
    foreign = [c.digest for c in configurations if c.theory != theory.id]
    if foreign:
        raise ValueError("configurations %s do not belong to theory %r"
                         % (foreign, theory.id))


def build_plan(theory: Theory, configurations: Iterable[Configuration],
               stage: str = SCREEN, *,
               unknown_as_import_time: bool = False) -> RunPlan:
    """Order, de-duplicate and group ``configurations`` for one stage."""
    cfgs = _unique(configurations)
    _check(theory, cfgs, stage)
    forks = import_time_forks(theory, unknown_as_import_time)
    members: Dict[Pairs, List[Configuration]] = {}
    for cfg in cfgs:
        members.setdefault(group_key(cfg, forks), []).append(cfg)
    index_of = {key: i for i, key in enumerate(members)}
    groups = tuple(RunGroup(index_of[key], key, tuple(group))
                   for key, group in members.items())
    entries = tuple(PlanEntry(i, cfg, stage, index_of[group_key(cfg, forks)])
                    for i, cfg in enumerate(cfgs))
    return RunPlan(theory.id, stage, forks, groups, entries)
