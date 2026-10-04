"""Configurations: one option chosen for every fork -- a path through the theory.

A configuration is identified by its DIGEST, computed exactly as
`simulations/core/preferred_path.digest_of` always has (sha256 over the sorted
(fork, option) pairs, first 16 hex characters), so digests recorded before this
module existed stay valid.

LIFECYCLE (derived, never declared by hand)
===========================================
ACTIVE                the selection equals the adopted one (drawn gold)
CONSIDERED            valid, uses no refuted option
RETIRED_REASSESSABLE  uses a DISABLED option not marked certain
RETIRED_CERTAIN       uses a DISABLED option marked certain
INVALID               violates a declared constraint -- never run
NOT_RUNNABLE is a separate flag: an option is unimplemented, or the run crashed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping, Optional, Tuple

__all__ = [
    "ACTIVE",
    "CONSIDERED",
    "RETIRED_REASSESSABLE",
    "RETIRED_CERTAIN",
    "INVALID",
    "LIFECYCLES",
    "digest_of",
    "Configuration",
]

ACTIVE = "ACTIVE"
CONSIDERED = "CONSIDERED"
RETIRED_REASSESSABLE = "RETIRED_REASSESSABLE"
RETIRED_CERTAIN = "RETIRED_CERTAIN"
INVALID = "INVALID"
LIFECYCLES = (ACTIVE, CONSIDERED, RETIRED_REASSESSABLE, RETIRED_CERTAIN,
              INVALID)


def digest_of(selection: Mapping[str, str]) -> str:
    """A stable short digest over (fork, option) pairs.

    Byte-identical to `preferred_path.digest_of`, which delegates here.
    """
    payload = json.dumps(sorted(dict(selection).items()),
                         separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Configuration:
    """A full selection, its digest, and what it is."""

    theory: str
    selection: Tuple[Tuple[str, str], ...]
    lifecycle: str = CONSIDERED
    name: Optional[str] = None
    not_runnable: bool = False
    #: fork -> decision ids that chose its option (from the selection store).
    decided_by: Tuple[Tuple[str, Tuple[str, ...]], ...] = ()
    reasons: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.lifecycle not in LIFECYCLES:
            raise ValueError("lifecycle %r not in %s"
                             % (self.lifecycle, LIFECYCLES))
        ordered = tuple(sorted(tuple(p) for p in self.selection))
        object.__setattr__(self, "selection", ordered)

    @classmethod
    def of(cls, theory: str, selection: Mapping[str, str],
           **kwargs) -> "Configuration":
        return cls(theory=theory, selection=tuple(dict(selection).items()),
                   **kwargs)

    @property
    def mapping(self) -> Dict[str, str]:
        return dict(self.selection)

    @property
    def digest(self) -> str:
        return digest_of(self.mapping)

    def option(self, fork_id: str) -> str:
        return self.mapping[fork_id]

    def differs_from(self, other: "Configuration") -> Dict[str, Tuple[str, str]]:
        """fork -> (this option, other option) where they differ."""
        a, b = self.mapping, other.mapping
        return {f: (a.get(f), b.get(f))
                for f in sorted(set(a) | set(b)) if a.get(f) != b.get(f)}

    def with_overrides(self, overrides: Mapping[str, str],
                       **kwargs) -> "Configuration":
        merged = dict(self.mapping)
        merged.update(overrides)
        return Configuration.of(self.theory, merged, **kwargs)


def option_paths(cfg: Configuration) -> Iterable[str]:
    """Graph node ids of the options a configuration passes through."""
    for fork_id, option_id in cfg.selection:
        yield "option:%s.%s" % (fork_id, option_id)
