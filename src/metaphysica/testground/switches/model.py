"""Switches: forks and their options -- the theory-agnostic model.

Moved here from `simulations/core/variants.py` (which re-exports these names, so
no import anywhere changes). The status vocabulary and the reconciliation
rules are unchanged; the new fields at the end of each class are optional and
default to the behaviour the registry already had, so every existing
declaration stays valid.

OPTION STATUS VOCABULARY
========================
ACTIVE      the adopted option; exactly one per fork; what runs by default.
CONSIDERED  a live rival: runnable, not refuted, a real candidate.
DISABLED    refuted and RETAINED ANYWAY, runnable and labelled -- a candidate
            that fails is a result, so it is never deleted. "Not on the
            table", not "not executable".

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

__all__ = [
    "ACTIVE",
    "CONSIDERED",
    "DISABLED",
    "OPTION_STATUSES",
    "STATUS_PRIORITY",
    "CERTAIN",
    "REASSESSABLE",
    "FORK_KINDS",
    "FORK_STAGES",
    "BINDINGS",
    "SourceUnmeasurable",
    "VariantOption",
    "Fork",
]

ACTIVE = "active"
CONSIDERED = "considered"
DISABLED = "disabled"
OPTION_STATUSES = (ACTIVE, CONSIDERED, DISABLED)

#: status -> default sweep priority. One mapping, so "is this refuted" has a
#: single answer and the ordering cannot disagree with the label.
STATUS_PRIORITY = {ACTIVE: 0, CONSIDERED: 1, DISABLED: 2}

#: How sure the refutation of a DISABLED option is. A certain one leaves the
#: default assessment configurations (mode `archaeology` still runs it); a
#: reassessable one is swept by mode `reassess`.
CERTAIN = "certain"
REASSESSABLE = "reassessable"
_CERTAINTIES = (CERTAIN, REASSESSABLE)

#: physics forks are assessed; policy forks are held at their active value in
#: every comparison; narrative forks change what a result MEANS, not what the
#: code computes, and are drawn but never run.
FORK_KINDS = ("physics", "policy", "narrative")
FORK_STAGES = ("simulation", "generation")
#: Whether flipping the fork in-process is faithful (call_time) or needs a
#: fresh process because a singleton froze it at import (import_time).
#: `unknown` until the binding calibration measures it.
BINDINGS = ("call_time", "import_time", "unknown")


class SourceUnmeasurable(RuntimeError):
    """A fork's source could not be read, so no option may be claimed.

    Raised instead of returning an option id: a reader that returns the
    declared default when it cannot see reports "the declaration is correct"
    on exactly the runs where it knows nothing.
    """


@dataclass(frozen=True)
class VariantOption:
    """One branch of a fork, with what choosing it costs and buys."""

    id: str
    summary: str
    consequence: str
    #: True only for the option currently adopted.
    adopted: bool = False
    #: Search priority, lower sweeps first (0 live rival, 1 plausible, 2
    #: refuted). Derived from ``status`` when unset.
    priority: Optional[int] = None
    #: ACTIVE / CONSIDERED / DISABLED. Derived from ``adopted`` when unset.
    status: Optional[str] = None
    # -- optional fields added 2026-10-02 (D-019); defaults keep old meaning --
    #: For DISABLED options: CERTAIN or REASSESSABLE (default reassessable).
    certainty: Optional[str] = None
    #: False when no code implements the option yet; configurations using it
    #: are NOT_RUNNABLE rather than failing.
    implemented: bool = True
    #: True when choosing the option adds a discrete input the theory does
    #: not derive (counted under closure).
    adds_discrete_input: bool = False
    #: ``repo@ref:path`` for a model restored from history.
    restored_from: str = ""
    #: Pre-registered condition under which the option is demoted.
    kill_condition: str = ""
    #: Decision ids that ruled on this option, e.g. ("D-015",).
    decision_refs: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Derive the unset fields, then refuse an inconsistent declaration."""
        status = self.status
        if status is None:
            status = ACTIVE if self.adopted else CONSIDERED
            object.__setattr__(self, "status", status)
        if status not in OPTION_STATUSES:
            raise ValueError(
                f"option {self.id!r}: status {status!r} is not one of "
                f"{list(OPTION_STATUSES)}"
            )
        if (status == ACTIVE) != self.adopted:
            raise ValueError(
                f"option {self.id!r}: status {status!r} contradicts "
                f"adopted={self.adopted} -- ACTIVE means adopted and "
                f"adopted means ACTIVE"
            )
        if self.priority is None:
            object.__setattr__(self, "priority", STATUS_PRIORITY[status])
        if status == DISABLED and self.priority != STATUS_PRIORITY[DISABLED]:
            raise ValueError(
                f"option {self.id!r}: DISABLED must carry priority "
                f"{STATUS_PRIORITY[DISABLED]}, not {self.priority}"
            )
        if status == CONSIDERED and self.priority not in (0, 1):
            raise ValueError(
                f"option {self.id!r}: CONSIDERED ranks 0 (cost it early) or "
                f"1 (plausible), not {self.priority}"
            )
        if self.certainty is not None:
            if self.certainty not in _CERTAINTIES:
                raise ValueError(
                    f"option {self.id!r}: certainty {self.certainty!r} is not "
                    f"one of {list(_CERTAINTIES)}")
            if status != DISABLED:
                raise ValueError(
                    f"option {self.id!r}: only a DISABLED option carries a "
                    f"certainty")
        if isinstance(self.decision_refs, list):
            object.__setattr__(self, "decision_refs", tuple(self.decision_refs))

    @property
    def refuted(self) -> bool:
        """Kept on the books and off the table."""
        return self.status == DISABLED

    @property
    def retired_certain(self) -> bool:
        return self.status == DISABLED and self.certainty == CERTAIN


@dataclass(frozen=True)
class Fork:
    """An open decision that can be executed either way.

    ``source`` names where the adopted value actually lives, so the default
    can be checked against it rather than restated here.
    """

    id: str
    question: str
    source: str
    options: List[VariantOption]
    status: str
    #: Reads the currently-adopted option id from ``source``.
    read_adopted: Optional[Callable[[], str]] = None
    notes: str = ""
    # -- optional fields added 2026-10-02 (D-019) --
    kind: str = "physics"
    stage: str = "simulation"
    binding: str = "unknown"
    #: The option that reproduces behaviour from before the fork existed, so
    #: an old selection can be extended deterministically.
    legacy_option: Optional[str] = None
    #: Module paths that read this fork (empty = inert).
    consumers: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.kind not in FORK_KINDS:
            raise ValueError(f"fork {self.id!r}: kind {self.kind!r} not in "
                             f"{list(FORK_KINDS)}")
        if self.stage not in FORK_STAGES:
            raise ValueError(f"fork {self.id!r}: stage {self.stage!r} not in "
                             f"{list(FORK_STAGES)}")
        if self.binding not in BINDINGS:
            raise ValueError(f"fork {self.id!r}: binding {self.binding!r} not "
                             f"in {list(BINDINGS)}")
        if (self.legacy_option is not None
                and self.legacy_option not in self.option_ids()):
            raise ValueError(f"fork {self.id!r}: legacy_option "
                             f"{self.legacy_option!r} is not an option")

    def option_ids(self) -> List[str]:
        return [o.id for o in self.options]

    def default(self) -> str:
        active = [o.id for o in self.options if o.status == ACTIVE]
        if not active:
            raise ValueError(f"fork {self.id!r} declares no adopted option")
        if len(active) > 1:
            raise ValueError(
                f"fork {self.id!r} declares {len(active)} ACTIVE options "
                f"({active}); exactly one runs by default"
            )
        return active[0]

    def option(self, option_id: str) -> VariantOption:
        for option in self.options:
            if option.id == option_id:
                return option
        raise ValueError(
            f"fork {self.id!r} has no option {option_id!r}; "
            f"available: {self.option_ids()}"
        )

    def options_by_status(self, status: str) -> List[str]:
        """Option ids carrying *status*, in declaration order."""
        if status not in OPTION_STATUSES:
            raise ValueError(
                f"unknown status {status!r}; expected one of "
                f"{list(OPTION_STATUSES)}"
            )
        return [o.id for o in self.options if o.status == status]

    def sweepable_ids(self) -> List[str]:
        """The adopted option and its live rivals (DISABLED excluded here,
        and only here -- they stay runnable by explicit override)."""
        return [o.id for o in self.options if o.status != DISABLED]
