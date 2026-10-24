"""The lineage catalogue types (contracts section 1), frozen.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple

__all__ = [
    "SCHEMA",
    "VERSION_STATUSES",
    "OPTION_STATUSES",
    "TRUNK",
    "BRANCH",
    "DEAD_END",
    "ACTIVE",
    "KeyResult",
    "Version",
    "DeclaredFork",
    "DeclaredOption",
    "Lineage",
]

SCHEMA = "metaphysica.lineage/1"
TRUNK, BRANCH, DEAD_END, ACTIVE = "trunk", "branch", "dead_end", "active"
VERSION_STATUSES = (TRUNK, BRANCH, DEAD_END, ACTIVE)
OPTION_STATUSES = ("considered", "disabled", "rejected")


@dataclass(frozen=True)
class KeyResult:
    quantity: str
    value: str
    source: str


@dataclass(frozen=True)
class Version:
    """One version of the theory."""

    id: str
    label: str
    era: str
    status: str
    parent: Optional[str] = None
    superseded_by: Optional[str] = None
    framing: str = ""
    why: str = ""
    worked: Tuple[str, ...] = ()
    failed: Tuple[str, ...] = ()
    key_results: Tuple[KeyResult, ...] = ()
    evidence: Tuple[str, ...] = ()
    maps_to: Tuple[str, ...] = ()
    #: {title, answer, status, why, source} entries, passed through.
    branches_considered: Tuple[Mapping[str, Any], ...] = ()


@dataclass(frozen=True)
class DeclaredFork:
    """A fork the engine has no switch for yet."""

    id: str
    question: str
    source: str = ""
    notes: str = ""


@dataclass(frozen=True)
class DeclaredOption:
    """An answer to a fork question that no code implements yet."""

    fork: str
    id: str
    summary: str
    consequence: str = ""
    status: str = "considered"
    restored_from: str = ""
    source: str = ""
    kill_condition: str = ""
    decision_refs: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Lineage:
    """A loaded, validated catalogue; versions are oldest first."""

    versions: Tuple[Version, ...]
    forks: Tuple[DeclaredFork, ...] = ()
    options: Tuple[DeclaredOption, ...] = ()
    sources: str = ""

    def version(self, version_id: str) -> Version:
        for v in self.versions:
            if v.id == version_id:
                return v
        raise KeyError(version_id)

    @property
    def active(self) -> Version:
        return next(v for v in self.versions if v.status == ACTIVE)
