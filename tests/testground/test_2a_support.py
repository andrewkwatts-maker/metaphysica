"""A tiny in-test theory for the lane-2A tests (switches, configurations).

Five forks, two constraints, an in-memory store and a YAML store helper. The
sweep is small enough to count by hand (see `HAND_COUNTS`).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

import yaml

from metaphysica.testground.configurations.model import (
    ACTIVE,
    Configuration,
    digest_of,
)
from metaphysica.testground.constraints import Excludes, Requires
from metaphysica.testground.switches.model import (
    CERTAIN,
    DISABLED,
    Fork,
    VariantOption,
)
from metaphysica.testground.theory import Theory

ENV_PREFIX = "TINY_VARIANT_"


def _opt(id_: str, **kw) -> VariantOption:
    return VariantOption(id_, "summary of " + id_, "consequence of " + id_,
                         **kw)


def tiny_forks() -> Dict[str, Fork]:
    """seed (5 options), origin, shape (physics); render (policy); meaning
    (narrative). p1 is declared before p0 so priority must beat declaration."""
    return {
        "seed": Fork("seed", "which seed?", "test", [
            _opt("a", adopted=True),
            _opt("p1", priority=1),
            _opt("p0", priority=0),
            _opt("dr", status=DISABLED),
            _opt("dc", status=DISABLED, certainty=CERTAIN),
        ], "OPEN", legacy_option="a"),
        "origin": Fork("origin", "where from?", "test", [
            _opt("native", adopted=True),
            _opt("input", priority=1, implemented=False),
        ], "OPEN"),
        "shape": Fork("shape", "what shape?", "test", [
            _opt("round", adopted=True),
            _opt("flat", priority=1),
        ], "RULED"),
        "render": Fork("render", "how drawn?", "test", [
            _opt("plain", adopted=True),
            _opt("fancy"),
        ], "OPEN", kind="policy"),
        "meaning": Fork("meaning", "what it means", "test", [
            _opt("literal", adopted=True),
            _opt("figurative"),
        ], "OPEN", kind="narrative"),
    }


def tiny_constraints() -> List:
    return [
        Requires("origin", "input", "seed", frozenset({"p0", "dr"}),
                 "an input origin presupposes a p0 or dr seed", "test"),
        Excludes("shape", "flat", "seed", "p1",
                 "a flat shape is not a p1 path", "test"),
    ]


ACTIVE_SELECTION = {"seed": "a", "origin": "native", "shape": "round",
                    "render": "plain", "meaning": "literal"}

#: mode -> (raw, total yielded, not runnable), counted by hand.
HAND_COUNTS = {
    "assess": (12, 7, 2),
    "reassess": (16, 11, 4),
    "archaeology": (20, 13, 4),
    "probe-constraint": (12, 12, 6),
    "single": (1, 1, 0),
}

#: The assess order, by hand: seed slowest; seed a, p0, p1; origin native,
#: input; shape round, flat; invalid combinations skipped.
ASSESS_ORDER = [
    ("a", "native", "round"),
    ("a", "native", "flat"),
    ("p0", "native", "round"),
    ("p0", "native", "flat"),
    ("p0", "input", "round"),
    ("p0", "input", "flat"),
    ("p1", "native", "round"),
]


class Switches:
    def __init__(self, forks: Mapping[str, Fork],
                 constraints: Sequence) -> None:
        self._forks = dict(forks)
        self._constraints = list(constraints)

    def forks(self) -> Mapping[str, Fork]:
        return self._forks

    def constraints(self) -> Sequence:
        return self._constraints


class MemoryStore:
    """A SelectionStore held in memory, counting its reads."""

    def __init__(self, theory_id: str, selection: Mapping[str, str],
                 named: Optional[Mapping[str, Mapping[str, str]]] = None,
                 name: str = "adopted",
                 decided_by: Optional[Mapping[str, Sequence[str]]] = None,
                 ) -> None:
        self.theory_id = theory_id
        self._active = Configuration.of(
            theory_id, selection, lifecycle=ACTIVE, name=name,
            decided_by=tuple(sorted((f, tuple(v)) for f, v in
                                    (decided_by or {}).items())))
        self._named = {k: Configuration.of(theory_id, v, name=k)
                       for k, v in (named or {}).items()}
        self.reads = 0
        self.writes: List = []

    def active(self) -> Configuration:
        self.reads += 1
        return self._active

    def named(self) -> Mapping[str, Configuration]:
        self.reads += 1
        return dict(self._named)

    def write_active(self, cfg: Configuration, decision_id: str,
                     note: str = "") -> None:
        self.writes.append((cfg, decision_id, note))
        self._active = cfg


class _Nothing:
    def stages(self):
        return ()

    def signals(self):
        return ()


def make_theory(store=None, forks: Optional[Mapping[str, Fork]] = None,
                constraints: Optional[Sequence] = None,
                theory_id: str = "tiny",
                selection: Optional[Mapping[str, str]] = None) -> Theory:
    forks = tiny_forks() if forks is None else forks
    constraints = tiny_constraints() if constraints is None else constraints
    if store is None:
        store = MemoryStore(theory_id, ACTIVE_SELECTION if selection is None
                            else selection,
                            decided_by={"seed": ["D-015"],
                                        "shape": ["D-008"]})
    return Theory(id=theory_id, title="tiny", env_prefix=ENV_PREFIX,
                  switches=Switches(forks, constraints), selections=store,
                  pipeline=_Nothing(), signals=_Nothing())


def write_active_yaml(path: Path, selection: Mapping[str, str],
                      theory: str = "tiny", digest: Optional[str] = None,
                      **extra) -> Path:
    doc = {"theory": theory, "name": "adopted",
           "selection": dict(selection),
           "digest": digest_of(selection) if digest is None else digest}
    doc.update(extra)
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return path


def random_theory(rng: random.Random, n_forks: int, n_constraints: int,
                  ) -> Theory:
    """A random theory: random statuses, priorities, kinds and constraints."""
    forks: Dict[str, Fork] = {}
    for f in range(n_forks):
        options = [_opt("o0", adopted=True)]
        for k in range(1, rng.randint(2, 4)):
            roll = rng.random()
            if roll < 0.55:
                options.append(_opt("o%d" % k, priority=rng.choice((0, 1)),
                                    implemented=rng.random() > 0.2))
            elif roll < 0.8:
                options.append(_opt("o%d" % k, status=DISABLED))
            else:
                options.append(_opt("o%d" % k, status=DISABLED,
                                    certainty=CERTAIN))
        rng.shuffle(options)
        kind = rng.choice(("physics", "physics", "physics", "policy",
                           "narrative"))
        forks["f%d" % f] = Fork("f%d" % f, "q", "test", options, "OPEN",
                                kind=kind)
    ids = list(forks)
    constraints = []
    for _ in range(n_constraints):
        a, b = rng.sample(ids, 2)
        oa = rng.choice(forks[a].option_ids())
        if rng.random() < 0.5:
            needs = frozenset(rng.sample(forks[b].option_ids(),
                                         rng.randint(1, 2)))
            constraints.append(Requires(a, oa, b, needs, "r", "test"))
        else:
            ob = rng.choice(forks[b].option_ids())
            constraints.append(Excludes(a, oa, b, ob, "x", "test"))
    selection = {fid: fork.default() for fid, fork in forks.items()}
    return make_theory(forks=forks, constraints=constraints,
                       selection=selection, theory_id="random")


def test_the_tiny_theory_is_well_formed():
    theory = make_theory()
    assert list(theory.switches.forks()) == list(ACTIVE_SELECTION)
    assert {f: fork.default() for f, fork in tiny_forks().items()} == \
        ACTIVE_SELECTION
