"""Lane 2A: the lifecycle of a selection is derived, never declared.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.testground.configurations.lifecycle import (
    Classifier,
    configuration_for,
    lifecycle_of,
    standing_of,
)
from metaphysica.testground.configurations.model import (
    ACTIVE,
    CONSIDERED,
    INVALID,
    RETIRED_CERTAIN,
    RETIRED_REASSESSABLE,
    Configuration,
)
from tests.testground.test_2a_support import (
    ACTIVE_SELECTION,
    MemoryStore,
    make_theory,
)


def _sel(**changes):
    return dict(ACTIVE_SELECTION, **changes)


@pytest.mark.parametrize("changes, expected", [
    ({}, ACTIVE),
    ({"seed": "p0"}, CONSIDERED),
    ({"render": "fancy"}, CONSIDERED),
    ({"seed": "dr"}, RETIRED_REASSESSABLE),
    ({"seed": "dc"}, RETIRED_CERTAIN),
    ({"origin": "input"}, INVALID),
    ({"seed": "p1", "shape": "flat"}, INVALID),
    ({"seed": "dc", "origin": "input"}, INVALID),   # invalid beats retired
])
def test_lifecycle_follows_the_precedence(changes, expected):
    assert lifecycle_of(make_theory(), _sel(**changes)) == expected


def test_the_active_stays_active_even_when_it_breaks_a_constraint():
    bad = _sel(origin="input")
    theory = make_theory(selection=bad)
    standing = standing_of(theory, bad)
    assert standing.lifecycle == ACTIVE
    assert any(r.startswith("violates origin=input") for r in
               standing.reasons)


def test_an_unimplemented_option_is_flagged_not_hidden():
    standing = standing_of(make_theory(), _sel(seed="p0", origin="input"))
    assert standing.lifecycle == CONSIDERED and standing.not_runnable
    assert standing.reasons == ("origin=input is not implemented",)


def test_every_reason_is_kept_whatever_the_label():
    standing = standing_of(make_theory(), _sel(seed="dc", origin="input"))
    assert standing.reasons == (
        "violates origin=input requires seed in {dr, p0} -- an input origin "
        "presupposes a p0 or dr seed",
        "origin=input is not implemented",      # forks in sorted order
        "uses DISABLED seed=dc (certain)",
    )


def test_a_configuration_is_accepted_as_the_selection():
    cfg = Configuration.of("tiny", _sel(seed="dr"))
    assert lifecycle_of(make_theory(), cfg) == RETIRED_REASSESSABLE


def test_unknown_forks_and_options_are_refused():
    with pytest.raises(KeyError):
        lifecycle_of(make_theory(), dict(ACTIVE_SELECTION, ghost="x"))
    with pytest.raises(ValueError):
        lifecycle_of(make_theory(), _sel(seed="zzz"))


def test_configuration_for_carries_names_and_decisions():
    store = MemoryStore("tiny", ACTIVE_SELECTION,
                        named={"alt": _sel(seed="p0")},
                        decided_by={"seed": ["D-015"], "shape": ["D-008"]})
    theory = make_theory(store=store)
    active = configuration_for(theory, ACTIVE_SELECTION)
    assert active.lifecycle == ACTIVE and active.name == "adopted"
    assert active.decided_by == (("seed", ("D-015",)), ("shape", ("D-008",)))
    alt = configuration_for(theory, _sel(seed="p0"))
    assert alt.name == "alt" and alt.decided_by == (("shape", ("D-008",)),)
    assert configuration_for(theory, _sel(seed="p1")).name is None
    assert configuration_for(theory, _sel(seed="p1"), name="x").name == "x"


def test_the_classifier_reads_the_store_once():
    store = MemoryStore("tiny", ACTIVE_SELECTION)
    classifier = Classifier(make_theory(store=store))
    reads = store.reads
    for seed in ("a", "p0", "p1", "dr", "dc"):
        classifier.configuration(_sel(seed=seed))
    assert store.reads == reads
