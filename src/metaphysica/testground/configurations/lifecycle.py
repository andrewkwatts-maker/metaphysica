"""Lifecycle: what a selection IS, derived from the declarations -- never typed.

Precedence, first match wins:

    ACTIVE                the selection equals the store's active selection
    INVALID               it violates a declared constraint (not a path of the
                          theory at all, so it cannot be a retired path either)
    RETIRED_CERTAIN       it uses a DISABLED option whose certainty is CERTAIN
    RETIRED_REASSESSABLE  it uses any other DISABLED option
    CONSIDERED            otherwise

NOT_RUNNABLE is a separate flag: the selection uses an option declared
``implemented=False``. Every reason behind the label (each violated constraint
with its rationale, each DISABLED option, each unimplemented option) is carried
in ``reasons`` so nothing a lower-precedence rule would have said is lost --
an ACTIVE selection that breaks a constraint says so there.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import (TYPE_CHECKING, Dict, List, Mapping, Optional, Tuple,
                    Union)

from metaphysica.testground.configurations.model import (
    ACTIVE,
    CONSIDERED,
    INVALID,
    RETIRED_CERTAIN,
    RETIRED_REASSESSABLE,
    Configuration,
)
from metaphysica.testground.constraints import violations
from metaphysica.testground.switches.model import CERTAIN, DISABLED, Fork
from metaphysica.testground.switches.resolve import extend_selection

if TYPE_CHECKING:  # pragma: no cover - typing only
    from metaphysica.testground.theory import Theory

__all__ = [
    "Standing",
    "Classifier",
    "lifecycle_of",
    "standing_of",
    "configuration_for",
]

Selection = Union[Mapping[str, str], Configuration]
_Key = Tuple[Tuple[str, str], ...]


@dataclass(frozen=True)
class Standing:
    """A selection's lifecycle, runnability and the reasons for both."""

    lifecycle: str
    not_runnable: bool
    reasons: Tuple[str, ...]


def _as_mapping(selection: Selection) -> Dict[str, str]:
    if isinstance(selection, Configuration):
        return selection.mapping
    return dict(selection)


def _key(selection: Mapping[str, str]) -> _Key:
    return tuple(sorted(selection.items()))


@dataclass(frozen=True)
class _OptionFacts:
    implemented: bool
    #: None, CERTAIN or "reassessable" (any DISABLED option not certain).
    retired: Optional[str]


class Classifier:
    """Labels selections of one theory; reads the store once on construction."""

    def __init__(self, theory: "Theory") -> None:
        self.theory_id = theory.id
        self.forks: Mapping[str, Fork] = theory.switches.forks()
        self.constraints = list(theory.switches.constraints())
        active = theory.selections.active()
        self.active = extend_selection(self.forks, active.mapping)
        self.active_name = active.name
        self._active_key = _key(self.active)
        self._decided_by = dict(active.decided_by)
        self._names = self._names_by_key(theory)
        self._facts: Dict[Tuple[str, str], _OptionFacts] = {}

    @staticmethod
    def _names_by_key(theory: "Theory") -> Dict[_Key, str]:
        named = theory.selections.named()
        names: Dict[_Key, str] = {}
        for name in sorted(named, reverse=True):   # first name wins
            names[named[name].selection] = name
        return names

    def _option(self, fork_id: str, option_id: str) -> _OptionFacts:
        cached = self._facts.get((fork_id, option_id))
        if cached is not None:
            return cached
        if fork_id not in self.forks:
            raise KeyError("theory %r has no fork %r"
                           % (self.theory_id, fork_id))
        option = self.forks[fork_id].option(option_id)
        retired = None
        if option.status == DISABLED:
            retired = CERTAIN if option.certainty == CERTAIN else "reassessable"
        facts = _OptionFacts(option.implemented, retired)
        self._facts[(fork_id, option_id)] = facts
        return facts

    def is_active(self, selection: Mapping[str, str]) -> bool:
        return _key(selection) == self._active_key

    def standing(self, selection: Selection) -> Standing:
        """Lifecycle, NOT_RUNNABLE flag and reasons for ``selection``."""
        sel = _as_mapping(selection)
        broken = violations(sel, self.constraints)
        reasons: List[str] = ["violates %s -- %s" % pair for pair in broken]
        retired: List[str] = []
        unimplemented: List[str] = []
        for fork_id, option_id in sorted(sel.items()):
            facts = self._option(fork_id, option_id)
            if facts.retired is not None:
                retired.append(facts.retired)
                reasons.append("uses DISABLED %s=%s (%s)"
                               % (fork_id, option_id, facts.retired))
            if not facts.implemented:
                unimplemented.append(fork_id)
                reasons.append("%s=%s is not implemented"
                               % (fork_id, option_id))
        lifecycle = self._lifecycle(sel, bool(broken), retired)
        return Standing(lifecycle, bool(unimplemented), tuple(reasons))

    def _lifecycle(self, sel: Mapping[str, str], invalid: bool,
                   retired: List[str]) -> str:
        if self.is_active(sel):
            return ACTIVE
        if invalid:
            return INVALID
        if CERTAIN in retired:
            return RETIRED_CERTAIN
        if retired:
            return RETIRED_REASSESSABLE
        return CONSIDERED

    def decided_by(self, selection: Mapping[str, str],
                   ) -> Tuple[Tuple[str, Tuple[str, ...]], ...]:
        """The store's decisions for every fork still at its active option."""
        return tuple(sorted(
            (fork_id, tuple(ids)) for fork_id, ids in self._decided_by.items()
            if fork_id in selection
            and selection[fork_id] == self.active.get(fork_id)))

    def name_of(self, selection: Mapping[str, str]) -> Optional[str]:
        """The active name, else a stored configuration's name, else None."""
        if self.is_active(selection):
            return self.active_name
        return self._names.get(_key(selection))

    def configuration(self, selection: Selection, name: Optional[str] = None,
                      extra_reasons: Tuple[str, ...] = (),
                      ) -> Configuration:
        """A fully labelled Configuration for ``selection``."""
        sel = _as_mapping(selection)
        standing = self.standing(sel)
        return Configuration.of(
            self.theory_id, sel,
            lifecycle=standing.lifecycle,
            name=name if name is not None else self.name_of(sel),
            not_runnable=standing.not_runnable,
            decided_by=self.decided_by(sel),
            reasons=tuple(extra_reasons) + standing.reasons)


def lifecycle_of(theory: "Theory", selection: Selection) -> str:
    """The derived lifecycle of ``selection`` (see the module docstring)."""
    return Classifier(theory).standing(selection).lifecycle


def standing_of(theory: "Theory", selection: Selection) -> Standing:
    """Lifecycle, NOT_RUNNABLE flag and reasons of ``selection``."""
    return Classifier(theory).standing(selection)


def configuration_for(theory: "Theory", selection: Selection,
                      name: Optional[str] = None) -> Configuration:
    """``selection`` as a labelled Configuration of ``theory``."""
    return Classifier(theory).configuration(selection, name=name)
