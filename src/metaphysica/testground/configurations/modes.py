"""Enumeration modes: which option statuses a sweep visits, and whether it prunes.

A mode answers one question per option -- "is this option swept?" -- plus
whether constraint-violating combinations are pruned. The modes nest:

    assess            the active option and its CONSIDERED rivals
    reassess          + DISABLED options whose refutation is reassessable
    archaeology       + DISABLED options whose refutation is certain
    single            nothing swept: the one configuration in force
    probe-constraint  the assess sweep WITHOUT pruning, so the combinations a
                      constraint excludes are yielded (labelled INVALID) and a
                      constraint can be tested for being truly definitional

A DISABLED option with no declared certainty counts as reassessable (the
switches model's default). Policy and narrative forks are never swept, in any
mode; that rule lives in the enumerator, not here, because it is about forks
rather than options.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from metaphysica.testground.switches.model import (
    ACTIVE,
    CERTAIN,
    CONSIDERED,
    DISABLED,
    VariantOption,
)

__all__ = [
    "ASSESS",
    "REASSESS",
    "ARCHAEOLOGY",
    "SINGLE",
    "PROBE_CONSTRAINT",
    "MODES",
    "ModeSpec",
    "spec",
    "parse_mode",
    "sweeps",
]

ASSESS = "assess"
REASSESS = "reassess"
ARCHAEOLOGY = "archaeology"
SINGLE = "single"
PROBE_CONSTRAINT = "probe-constraint"
MODES: Tuple[str, ...] = (ASSESS, REASSESS, ARCHAEOLOGY, SINGLE,
                          PROBE_CONSTRAINT)


@dataclass(frozen=True)
class ModeSpec:
    """What one mode sweeps and whether it prunes invalid combinations."""

    name: str
    #: Option statuses swept (ACTIVE is always among them, except in single).
    statuses: Tuple[str, ...]
    #: Whether a DISABLED option marked CERTAIN is swept.
    sweeps_certain: bool
    #: Whether constraint-violating combinations are dropped.
    prunes: bool
    #: True only for `single`: no fork is swept.
    single: bool
    description: str


_SPECS: Dict[str, ModeSpec] = {
    ASSESS: ModeSpec(
        ASSESS, (ACTIVE, CONSIDERED), False, True, False,
        "the active option and its considered rivals"),
    REASSESS: ModeSpec(
        REASSESS, (ACTIVE, CONSIDERED, DISABLED), False, True, False,
        "assess plus disabled options whose refutation is reassessable"),
    ARCHAEOLOGY: ModeSpec(
        ARCHAEOLOGY, (ACTIVE, CONSIDERED, DISABLED), True, True, False,
        "every option, including those retired with certainty"),
    SINGLE: ModeSpec(
        SINGLE, (), False, True, True,
        "the one configuration in force (override > env > named > active)"),
    PROBE_CONSTRAINT: ModeSpec(
        PROBE_CONSTRAINT, (ACTIVE, CONSIDERED), False, False, False,
        "the assess sweep without pruning; constraint violations are yielded "
        "and labelled INVALID"),
}


def parse_mode(text: str) -> str:
    """Canonical mode name for ``text`` (case- and ``_``/``-``-insensitive)."""
    name = str(text).strip().lower().replace("_", "-")
    if name not in _SPECS:
        raise ValueError("unknown mode %r; expected one of %s"
                         % (text, list(MODES)))
    return name


def spec(mode: str) -> ModeSpec:
    """The specification of ``mode`` (any spelling `parse_mode` accepts)."""
    return _SPECS[parse_mode(mode)]


def sweeps(mode: str, option: VariantOption) -> bool:
    """Whether ``mode`` sweeps ``option`` on a swept fork."""
    mode_spec = spec(mode)
    if option.status not in mode_spec.statuses:
        return False
    if option.status == DISABLED and option.certainty == CERTAIN:
        return mode_spec.sweeps_certain
    return True
