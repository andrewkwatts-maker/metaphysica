"""Lane 2A: enumeration modes decide which option statuses a sweep visits.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.testground.configurations import modes
from metaphysica.testground.switches.model import (
    CERTAIN,
    DISABLED,
    REASSESSABLE,
    VariantOption,
)

_ACTIVE = VariantOption("a", "s", "c", adopted=True)
_RIVAL = VariantOption("b", "s", "c", priority=1)
_DIS = VariantOption("c", "s", "c", status=DISABLED)
_DIS_R = VariantOption("d", "s", "c", status=DISABLED, certainty=REASSESSABLE)
_DIS_C = VariantOption("e", "s", "c", status=DISABLED, certainty=CERTAIN)


@pytest.mark.parametrize("mode, expected", [
    (modes.ASSESS, (True, True, False, False, False)),
    (modes.REASSESS, (True, True, True, True, False)),
    (modes.ARCHAEOLOGY, (True, True, True, True, True)),
    (modes.PROBE_CONSTRAINT, (True, True, False, False, False)),
    (modes.SINGLE, (False, False, False, False, False)),
])
def test_each_mode_sweeps_exactly_its_statuses(mode, expected):
    got = tuple(modes.sweeps(mode, o)
                for o in (_ACTIVE, _RIVAL, _DIS, _DIS_R, _DIS_C))
    assert got == expected


def test_an_undeclared_certainty_counts_as_reassessable():
    assert modes.sweeps(modes.REASSESS, _DIS)
    assert not modes.sweeps(modes.REASSESS, _DIS_C)


def test_only_probe_constraint_skips_pruning_and_only_single_is_single():
    assert [m for m in modes.MODES if not modes.spec(m).prunes] == [
        modes.PROBE_CONSTRAINT]
    assert [m for m in modes.MODES if modes.spec(m).single] == [modes.SINGLE]


@pytest.mark.parametrize("text", ["probe-constraint", "PROBE_CONSTRAINT",
                                  " Probe_Constraint "])
def test_mode_names_parse_leniently(text):
    assert modes.parse_mode(text) == modes.PROBE_CONSTRAINT


def test_an_unknown_mode_is_refused():
    with pytest.raises(ValueError, match="unknown mode"):
        modes.spec("everything")
