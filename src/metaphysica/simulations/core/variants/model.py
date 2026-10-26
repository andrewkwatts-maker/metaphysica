"""Fork model: environment constants, status vocabulary, VariantOption, Fork.

Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

#: Environment prefix: METAPHYSICA_VARIANT_<FORK_ID_UPPER>=<option id>
_ENV_PREFIX = "METAPHYSICA_VARIANT_"
#: Path to a JSON {fork: option} map honoured by resolve() (Track G1).
_SELECTION_ENV = "METAPHYSICA_SELECTION"

# ---------------------------------------------------------------------------
# OPTION STATUS VOCABULARY
# ---------------------------------------------------------------------------
# Three words, because the registry previously had only two states that a
# reader could distinguish -- adopted, and everything else -- while the
# "everything else" pile mixed two completely different things: a rival
# nobody has ruled out yet, and a candidate the framework has already
# refuted and keeps only because a falsified claim stays on the books.
#
# Collapsing those loses the fact that matters most about an option, so the
# distinction is now declared rather than inferred from a priority integer.

#: The adopted option. Exactly one per fork, and it is what runs by default.
ACTIVE = "active"

#: A live rival: runnable, not refuted, and a real candidate for adoption.
#: A sweep should cost these, because one of them might replace the ACTIVE
#: option tomorrow.
CONSIDERED = "considered"

#: Refuted -- falsified against data, or structurally impossible -- and
#: RETAINED ANYWAY, runnable and labelled, because this project never
#: deletes a failed candidate: a candidate that fails is a result.
#:
#: DISABLED means "not on the table", NOT "not executable". A disabled
#: option still runs end to end under an explicit override, which is the
#: only way its refutation stays checkable rather than becoming folklore.
DISABLED = "disabled"

#: Declaration order, which is also sweep order: adopted, then rivals, then
#: the refuted candidates kept for completeness.
OPTION_STATUSES = (ACTIVE, CONSIDERED, DISABLED)


class SourceUnmeasurable(RuntimeError):
    """A fork's source could not be read, so no option may be claimed.

    Raised instead of returning an option id. The distinction is the whole
    point: a reader that returns the declared default when it cannot see
    reports "the declaration is correct" on exactly the runs where it knows
    nothing, and `describe()` then publishes that as a verified state.
    """

#: status -> default sweep priority. One mapping, so "is this refuted" has a
#: single answer and the ordering cannot disagree with the label.
_STATUS_PRIORITY = {ACTIVE: 0, CONSIDERED: 1, DISABLED: 2}


@dataclass(frozen=True)
class VariantOption:
    """One branch of a fork, with what choosing it costs and buys."""

    id: str
    summary: str
    consequence: str
    #: True only for the option currently adopted at the fork's source.
    adopted: bool = False
    #: SEARCH PRIORITY, lower sweeps first. The adopted option always leads
    #: regardless of this number; among the rest it declares what is worth
    #: testing NEXT versus what is kept only so it stays runnable.
    #:
    #:   0  the live alternative -- a real contender, cost it early
    #:   1  plausible / under investigation
    #:   2  retained for completeness: already refuted, kept because a
    #:      falsified candidate stays on the books runnable and labelled
    #:
    #: This exists because a capped sweep must spend its budget on the
    #: combinations someone would actually adopt. Before it, enumeration was
    #: declaration order, and growing `b3_seed` from two options to five
    #: pushed the ADOPTED state out of a cap=3 search entirely.
    #:
    #: Left unset it is DERIVED from ``status`` via ``_STATUS_PRIORITY``, so
    #: the label and the sweep order cannot drift apart. Set it explicitly
    #: only to rank within a status -- e.g. priority 0 on a CONSIDERED
    #: option marks the rival worth costing before the other rivals.
    priority: Optional[int] = None
    #: ACTIVE / CONSIDERED / DISABLED -- see the vocabulary above. Left unset
    #: it is DERIVED from ``adopted``, which keeps every pre-existing
    #: declaration valid and means the only way to get DISABLED is to say so.
    status: Optional[str] = None
    #: Declared compatibility (Track G3), each a tuple of (fork, option).
    #: ``requires``: for every fork named, the selection must pick one of the
    #: listed options. ``excludes``: it must pick none of them. Only
    #: constraints the code or docs already state; each cites its source.
    requires: Tuple[Tuple[str, str], ...] = ()
    excludes: Tuple[Tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        """Derive the unset fields, then refuse an inconsistent declaration.

        A frozen dataclass, so the derived values go in via object.__setattr__.
        The checks here are the single place the three fields are reconciled:
        without them ``adopted``, ``status`` and ``priority`` are three
        independent ways to say the same thing, and the registry would be
        able to publish an option that is adopted and refuted at once.
        """
        status = self.status
        if status is None:
            status = ACTIVE if self.adopted else CONSIDERED
            object.__setattr__(self, "status", status)
        if status not in OPTION_STATUSES:
            raise ValueError(
                f"option {self.id!r}: status {status!r} is not one of "
                f"{list(OPTION_STATUSES)}"
            )
        # ACTIVE and adopted are the same statement, so they must agree.
        if (status == ACTIVE) != self.adopted:
            raise ValueError(
                f"option {self.id!r}: status {status!r} contradicts "
                f"adopted={self.adopted} -- ACTIVE means adopted and "
                f"adopted means ACTIVE"
            )
        if self.priority is None:
            object.__setattr__(self, "priority", _STATUS_PRIORITY[status])
        # A refuted option must sweep last; otherwise a capped search spends
        # its budget re-running candidates the framework already rejected.
        if status == DISABLED and self.priority != _STATUS_PRIORITY[DISABLED]:
            raise ValueError(
                f"option {self.id!r}: DISABLED must carry priority "
                f"{_STATUS_PRIORITY[DISABLED]}, not {self.priority}"
            )
        if status == CONSIDERED and self.priority not in (0, 1):
            raise ValueError(
                f"option {self.id!r}: CONSIDERED ranks 0 (cost it early) or "
                f"1 (plausible), not {self.priority}"
            )

    @property
    def refuted(self) -> bool:
        """Kept on the books and off the table."""
        return self.status == DISABLED


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
    #: Reads the currently-adopted option id from ``source``. Kept as a
    #: callable so the check is against live state, not a copy.
    read_adopted: Optional[Callable[[], str]] = None
    notes: str = ""

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
        """What a default sweep covers: the adopted option and its live rivals.

        DISABLED options are excluded HERE and nowhere else -- they stay fully
        runnable through ``resolve(fork, override)`` and through the
        environment, which is what keeps a refutation reproducible. What they
        do not do is consume sweep budget by default.
        """
        return [o.id for o in self.options if o.status != DISABLED]
