"""The pre-registered assessment configuration (D-019 annex), loaded and hashed.

An assessment is only meaningful against the configuration that was committed
BEFORE it ran: the target facts, the policy forks held fixed, the constraint
list, the run budget and the key layout of each criterion. This module reads
that YAML file and records the sha256 of its exact bytes, so a report can prove
which pre-registration it was scored under (D-019 kill condition K5: a run
against any other sha256 is void).

Unknown top-level fields are refused: a typo in a pre-registered file must not
silently drop a rule.

YAML FIELDS
===========
theory        theory id the file belongs to (optional)
decision      the decision that pre-registered it, e.g. "D-019" (optional)
target_facts  list of {id, signal, expected, field="value", source=""}: the
              signal's ``detail[field]`` must equal ``expected`` (validity)
policy_forks  forks held at their active option in every compared configuration
constraints   references to the declared constraints in force (descriptions)
budget        free-form run budget (timeouts, jobs, caps) -- recorded, not used
key_layout    {criterion: [[signal ids], ...]}: each inner list is one position
              of the criterion's integer key (the sum of those signals' counts);
              an empty list pre-registers a criterion with no components.
              Not allowed for validity (a gate: its key is the failure count).
              Without a layout a criterion's key is one position, the sum of
              all its signals' counts.
notes / description / schema   free text, recorded

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import yaml

from metaphysica.testground.assessment.score import CRITERIA, VALIDITY

__all__ = [
    "TargetFact",
    "AssessmentConfig",
    "sha256_of_file",
    "policy_drift",
    "KNOWN_FIELDS",
]

KNOWN_FIELDS = frozenset({
    "schema", "theory", "decision", "description", "notes", "target_facts",
    "policy_forks", "constraints", "budget", "key_layout",
})

Layout = Tuple[Tuple[str, ...], ...]


@dataclass(frozen=True)
class TargetFact:
    """A fact every valid configuration must reproduce, e.g. n_gen = 3."""

    id: str
    signal: str
    expected: Any
    field: str = "value"
    source: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "TargetFact":
        missing = [k for k in ("id", "signal", "expected") if k not in data]
        if missing:
            raise ValueError("target fact %r lacks %s"
                             % (data.get("id"), ", ".join(missing)))
        return cls(id=str(data["id"]), signal=str(data["signal"]),
                   expected=data["expected"],
                   field=str(data.get("field", "value")),
                   source=str(data.get("source", "")))

    def check_id(self) -> str:
        """The id this fact carries in failure lists and reports."""
        return "target:%s" % self.id

    def as_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "signal": self.signal,
                "expected": self.expected, "field": self.field,
                "source": self.source}


def sha256_of_file(path: Path) -> str:
    """Hex sha256 of the file's exact bytes."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _layout_from(raw: Any) -> Dict[str, Layout]:
    """Parse and check ``key_layout``: criterion -> tuple of signal-id tuples."""
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ValueError("key_layout must be a mapping of criterion -> list")
    layout: Dict[str, Layout] = {}
    for criterion, positions in raw.items():
        if criterion not in CRITERIA:
            raise ValueError("key_layout names unknown criterion %r"
                             % criterion)
        if criterion == VALIDITY:
            raise ValueError("validity is a gate: its key is the failure "
                             "count and takes no layout")
        if not isinstance(positions, (list, tuple)):
            raise ValueError("key_layout[%s] must be a list of lists"
                             % criterion)
        layout[criterion] = tuple(_position(criterion, p) for p in positions)
    return layout


def _position(criterion: str, position: Any) -> Tuple[str, ...]:
    if isinstance(position, str):
        return (position,)
    if not isinstance(position, (list, tuple)) or not position:
        raise ValueError("key_layout[%s]: each position is a non-empty list "
                         "of signal ids" % criterion)
    return tuple(str(s) for s in position)


def _string_tuple(raw: Any, name: str) -> Tuple[str, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, (list, tuple)):
        raise ValueError("%s must be a list" % name)
    return tuple(str(x) for x in raw)


@dataclass(frozen=True)
class AssessmentConfig:
    """What an assessment was pre-registered to use, and the hash proving it."""

    sha256: str
    path: Optional[Path] = None
    theory: Optional[str] = None
    decision: Optional[str] = None
    target_facts: Tuple[TargetFact, ...] = ()
    policy_forks: Tuple[str, ...] = ()
    constraints: Tuple[str, ...] = ()
    budget: Dict[str, Any] = field(default_factory=dict)
    key_layout: Dict[str, Layout] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "AssessmentConfig":
        """Read a YAML file; ``sha256`` is over its exact bytes."""
        path = Path(path)
        data = path.read_bytes()
        loaded = yaml.safe_load(data.decode("utf-8")) or {}
        return cls.from_mapping(loaded, sha256=hashlib.sha256(data).hexdigest(),
                                path=path)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any], sha256: str = "",
                     path: Optional[Path] = None) -> "AssessmentConfig":
        """Build from an already-parsed mapping (tests, in-memory theories)."""
        if not isinstance(data, Mapping):
            raise ValueError("an assessment configuration is a mapping")
        unknown = sorted(set(data) - KNOWN_FIELDS)
        if unknown:
            raise ValueError("unknown assessment-config field(s): %s"
                             % ", ".join(unknown))
        facts = tuple(TargetFact.from_mapping(f)
                      for f in data.get("target_facts") or ())
        budget = data.get("budget") or {}
        if not isinstance(budget, Mapping):
            raise ValueError("budget must be a mapping")
        return cls(sha256=sha256, path=path,
                   theory=data.get("theory"), decision=data.get("decision"),
                   target_facts=facts,
                   policy_forks=_string_tuple(data.get("policy_forks"),
                                              "policy_forks"),
                   constraints=_string_tuple(data.get("constraints"),
                                             "constraints"),
                   budget=dict(budget),
                   key_layout=_layout_from(data.get("key_layout")),
                   raw=dict(data))

    @classmethod
    def empty(cls) -> "AssessmentConfig":
        """No pre-registration: every criterion uses its default layout."""
        return cls(sha256="")

    def layout(self, criterion: str) -> Optional[Layout]:
        """The pre-registered key layout of ``criterion``, or None."""
        return self.key_layout.get(criterion)

    def matches(self, recorded_sha256: Optional[str]) -> bool:
        """True when ``recorded_sha256`` is this file's hash (K5)."""
        return bool(recorded_sha256) and recorded_sha256 == self.sha256

    def target_signals(self) -> frozenset:
        return frozenset(f.signal for f in self.target_facts)

    def summary(self) -> Dict[str, Any]:
        """The fields a report records about the pre-registration."""
        return {
            "assessment_config": str(self.path) if self.path else None,
            "sha256": self.sha256,
            "theory": self.theory,
            "decision": self.decision,
            "target_facts": [f.as_dict() for f in self.target_facts],
            "policy_forks": list(self.policy_forks),
            "constraints": list(self.constraints),
            "budget": dict(self.budget),
            "key_layout": {c: [list(p) for p in pos]
                           for c, pos in sorted(self.key_layout.items())},
        }


def policy_drift(selection: Mapping[str, str], active: Mapping[str, str],
                 policy_forks: Sequence[str]) -> List[str]:
    """Policy forks on which ``selection`` is NOT held at the active option.

    Amendment (d): policy forks are held at their active values in every
    compared configuration. A fork absent from either selection is skipped.
    """
    return [f for f in policy_forks
            if f in selection and f in active and selection[f] != active[f]]
