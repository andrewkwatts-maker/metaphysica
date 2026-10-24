"""The theory seam: what any physics theory provides to the test ground.

The test ground is theory-agnostic. A theory plugs in by supplying a few small
providers -- one per concern (interface segregation) -- bundled in a frozen
`Theory`. The PM theory (`metaphysica.theories.pm`) and a toy theory
(`metaphysica.theories.toy`) both implement it; one contract test suite runs
against every registered theory, so the seam cannot quietly become PM-shaped.

Dependency rule: this package imports nothing from `metaphysica.simulations`,
`metaphysica.generators` or `metaphysica.website`; theories depend on the test
ground, never the reverse (an AST test enforces it).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import (Any, Callable, Dict, Iterable, List, Mapping, Optional,
                    Protocol, Sequence, Tuple, runtime_checkable)

from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.constraints import Constraint
from metaphysica.testground.signals.model import Signal
from metaphysica.testground.switches.model import Fork

__all__ = [
    "SwitchProvider",
    "SelectionStore",
    "Stage",
    "Pipeline",
    "SignalProvider",
    "ScoredRow",
    "AnchorProvider",
    "Claim",
    "CertificateProvider",
    "DecisionLogProvider",
    "Theory",
]


@runtime_checkable
class SwitchProvider(Protocol):
    """The theory's forks and the constraints between their options."""

    def forks(self) -> Mapping[str, Fork]: ...

    def constraints(self) -> Sequence[Constraint]: ...


@runtime_checkable
class SelectionStore(Protocol):
    """Where the adopted selection (and named configurations) live."""

    def active(self) -> Configuration: ...

    def named(self) -> Mapping[str, Configuration]: ...

    def write_active(self, cfg: Configuration, decision_id: str,
                     note: str = "") -> None: ...


@dataclass(frozen=True)
class Stage:
    """One step of a full run, executed in a fresh process."""

    id: str
    kind: str                        # "compute" or "generate"
    command: Tuple[str, ...]         # argv, run with cwd = the run root
    tolerated_exit_codes: Tuple[int, ...] = (0,)
    timeout_s: Optional[float] = None


@runtime_checkable
class Pipeline(Protocol):
    """The ordered stages of a full run."""

    def stages(self) -> Sequence[Stage]: ...


@runtime_checkable
class SignalProvider(Protocol):
    """Every measurement the comparator reads, with binding and cost."""

    def signals(self) -> Sequence[Signal]: ...


@dataclass(frozen=True)
class ScoredRow:
    """One comparison with data, for criterion 5 (tie-break only)."""

    id: str
    verdict: str                     # PASS / MARGINAL / TENSION / FAIL / ...
    sigma: Optional[float] = None


@runtime_checkable
class AnchorProvider(Protocol):
    """Rows comparing a configuration's outputs with experiment."""

    def scored_rows(self, root: Path) -> Sequence[ScoredRow]: ...


@dataclass(frozen=True)
class Claim:
    """A certificate statement: what holds, its proof route and falsifier."""

    id: str
    holds: bool
    statement: str
    falsifier: str = ""
    scope: str = ""
    references: Tuple[str, ...] = ()


@runtime_checkable
class CertificateProvider(Protocol):
    """The theory's proved claims, evaluated on the configuration in force."""

    def claims(self) -> Sequence[Claim]: ...


@runtime_checkable
class DecisionLogProvider(Protocol):
    """Where the theory's decisions are recorded."""

    def decision_log_path(self) -> Optional[Path]: ...


@dataclass(frozen=True)
class Theory:
    """A theory plugged into the test ground."""

    id: str
    title: str
    #: Environment prefix of per-fork overrides, e.g. "METAPHYSICA_VARIANT_".
    env_prefix: str
    switches: SwitchProvider
    selections: SelectionStore
    pipeline: Pipeline
    signals: SignalProvider
    anchors: Optional[AnchorProvider] = None
    certificate: Optional[CertificateProvider] = None
    decisions: Optional[DecisionLogProvider] = None
    #: Path of the pre-registered assessment configuration (YAML).
    assessment_config: Optional[Path] = None
    #: Called after an in-process switch flip, so call-time caches re-read.
    invalidate_caches: Callable[[], None] = lambda: None
    #: Narrative (non-executable) decisions drawn in the graph.
    narrative: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    #: Lineage catalogue (YAML, `metaphysica.lineage/1`); None = no lineage.
    lineage: Optional[Path] = None

    def fork_ids(self) -> List[str]:
        return list(self.switches.forks())

    def env_var(self, fork_id: str) -> str:
        return self.env_prefix + fork_id.upper()

    def env_for(self, selection: Mapping[str, str]) -> Dict[str, str]:
        """Environment that forces ``selection`` in a fresh process."""
        return {self.env_var(f): o for f, o in sorted(selection.items())}

    def describe_forks(self) -> Iterable[Fork]:
        return self.switches.forks().values()
