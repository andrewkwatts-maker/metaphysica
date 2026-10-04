"""Shared fixtures for the lane 2D tests: a small stub theory and decision log.

Not a test module of its own beyond one sanity check; the other `test_2d_*`
modules import `make_theory`, `SAMPLE_LOG` and `make_assessment` from here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.constraints import Excludes, Requires
from metaphysica.testground.switches.model import (CERTAIN, CONSIDERED,
                                                   DISABLED, Fork,
                                                   VariantOption)
from metaphysica.testground.theory import Theory

THEORY_ID = "stub"

SAMPLE_LOG = """# Decision log — stub

Preamble paragraph.

## How decisions are made

Rules, not a decision.

---

## D-001 · 2026-09-30 · G0 · PRE-REGISTERED

**Question.** Does the seed close? It is asked first.

Second paragraph.

---

## D-001 · RESULT · 2026-09-30 · CONFIRMED (lead run)

It closes.

---

## D-002 · 2026-10-01 · RULINGS — the author's, on the seed

The author ruled for `a`.

```
## D-999 · inside a fence, not a heading
```

---

## D-001 / D-002 · INDEPENDENT VERIFICATION · 2026-10-01

Both confirmed.

---

## D-002 · ADDENDUM · the rule restated

Addendum text.
"""


def option(oid: str, status: str = CONSIDERED, consequence: str = "",
           **kw: Any) -> VariantOption:
    """A VariantOption with a default rationale text."""
    text = consequence or "BUYS: something for %s.\nCOSTS: a price." % oid
    return VariantOption(oid, "summary of %s" % oid, text,
                         adopted=status == "active", status=status, **kw)


def make_forks() -> Dict[str, Fork]:
    """Four forks: two physics (one depends on the other), policy, narrative."""
    seed = Fork(
        "seed", "Which seed?", "stub.seed",
        [option("a", "active", decision_refs=("D-002",)),
         option("b", priority=0),
         option("c", priority=1,
                consequence="BUYS: fit.\nRULED OUT 2026-09-06, on physics. "
                            "See ruling:2026-09-22."),
         option("d", DISABLED, certainty=CERTAIN,
                consequence="BUYS: x.\nDEMOTED 2026-10-01 (D-001): refuted."),
         option("e", DISABLED)],
        "RULED", notes="RULED 2026-10-01 by the author (D-002): seed a.",
        consumers=("stub.consumer",), binding="call_time")
    origin = Fork(
        "origin", "What sets the seed?", "stub.origin",
        [option("x", "active"), option("y", priority=1),
         option("z", priority=1, adds_discrete_input=True,
                kill_condition="if z fits worse", restored_from="repo@abc:z.py")],
        "OPEN", legacy_option="x")
    policy = Fork("policy", "Which policy?", "stub.policy",
                  [option("strict", "active"), option("loose", priority=1)],
                  "RULED", kind="policy")
    story = Fork("story", "What does it mean?", "stub.story",
                 [option("one", "active"),
                  option("two", priority=1, implemented=False)],
                 "OPEN", kind="narrative")
    # declared narrative first, so column order is not declaration order
    return {"story": story, "origin": origin, "seed": seed, "policy": policy}


def make_constraints() -> List[Any]:
    return [
        Requires("origin", "y", "seed", frozenset({"b"}),
                 "y is an origin only for seed b", "stub notes"),
        Excludes("seed", "c", "policy", "loose",
                 "c and loose cannot co-occur", "stub notes"),
    ]


ACTIVE_SELECTION = {"seed": "a", "origin": "x", "policy": "strict",
                    "story": "one"}


class StubSwitches:
    def __init__(self, forks: Mapping[str, Fork],
                 constraints: Sequence[Any]) -> None:
        self._forks, self._constraints = dict(forks), list(constraints)

    def forks(self) -> Mapping[str, Fork]:
        return self._forks

    def constraints(self) -> Sequence[Any]:
        return self._constraints


class StubStore:
    """A SelectionStore persisted as JSON, recording every write call."""

    def __init__(self, path: Path, selection: Mapping[str, str],
                 named: Optional[Mapping[str, Configuration]] = None,
                 decided_by: Tuple = (("seed", ("D-002",)),)) -> None:
        self.path = path
        self.calls: List[Tuple[str, Any]] = []
        self._active = Configuration.of(THEORY_ID, selection,
                                        lifecycle="ACTIVE", name="stub-active",
                                        decided_by=decided_by)
        self._named: Dict[str, Configuration] = dict(named or {})
        self.previous: List[str] = []
        self.data_tiebreak_dof = 0
        self._save()

    def _save(self) -> None:
        payload = {"active": self._active.mapping,
                   "digest": self._active.digest,
                   "decided_by": {f: list(i) for f, i in
                                  self._active.decided_by},
                   "named": {k: v.mapping for k, v in sorted(self._named.items())},
                   "previous": self.previous,
                   "data_tiebreak_dof": self.data_tiebreak_dof}
        self.path.write_text(json.dumps(payload, sort_keys=True, indent=1),
                             encoding="utf-8")

    def active(self) -> Configuration:
        return self._active

    def named(self) -> Mapping[str, Configuration]:
        return dict(self._named)

    def write_active(self, cfg: Configuration, decision_id: str,
                     note: str = "", data_tiebreak: bool = False) -> None:
        self.calls.append(("write_active", (cfg.digest, decision_id, note,
                                            data_tiebreak)))
        self.previous.append(self._active.digest)
        self.data_tiebreak_dof += int(data_tiebreak)
        self._active = cfg
        self._save()

    def write_named(self, name: str, cfg: Configuration) -> None:
        self.calls.append(("write_named", (name, cfg.digest)))
        assert name not in self._named, "a named configuration is never replaced"
        self._named[name] = cfg
        self._save()


class StubPipeline:
    def stages(self) -> Sequence[Any]:
        return ()


class StubSignals:
    def signals(self) -> Sequence[Any]:
        return ()


class StubDecisions:
    def __init__(self, path: Optional[Path]) -> None:
        self.path = path

    def decision_log_path(self) -> Optional[Path]:
        return self.path


def make_theory(tmp_path: Path, log_text: Optional[str] = SAMPLE_LOG,
                store: Any = None, narrative: Tuple = (),
                forks: Optional[Mapping[str, Fork]] = None,
                constraints: Optional[Sequence[Any]] = None) -> Theory:
    """A stub theory whose store and decision log live under ``tmp_path``."""
    log_path = tmp_path / "DECISION_LOG.md"
    if log_text is not None:
        log_path.write_bytes(log_text.encode("utf-8"))
    store = store or StubStore(tmp_path / "store.json", ACTIVE_SELECTION)
    return Theory(
        id=THEORY_ID, title="Stub theory", env_prefix="STUB_VARIANT_",
        switches=StubSwitches(forks or make_forks(),
                              make_constraints() if constraints is None
                              else constraints),
        selections=store, pipeline=StubPipeline(), signals=StubSignals(),
        decisions=StubDecisions(log_path), narrative=narrative)


def score_block(*keys: Tuple[int, ...]) -> Dict[str, Any]:
    names = ("validity", "closure", "consistency", "elegance", "data")
    return {n: {"key": list(k), "status": "MEASURED"}
            for n, k in zip(names, keys)}


def make_assessment(active: Configuration,
                    proposed: Optional[Mapping[str, str]] = None,
                    verdict: str = "RECOMMEND_CHANGE",
                    deciding: str = "closure",
                    fingerprint: Optional[str] = "fp-1",
                    trials_factor: Optional[int] = None,
                    proposed_verdict: str = "ADOPTABLE") -> Dict[str, Any]:
    """An assessment report shaped by path_assessment.schema.json."""
    proposed = dict(proposed or {**active.mapping, "seed": "b"})
    other = Configuration.of(THEORY_ID, proposed)
    rec: Dict[str, Any] = {"digest": other.digest,
                           "deciding_criterion": deciding,
                           "margins": {deciding: [1]}}
    if trials_factor is not None:
        rec["trials_factor"] = trials_factor
    report: Dict[str, Any] = {
        "schema": "metaphysica.path_assessment/1", "theory": THEORY_ID,
        "mode": "assess",
        "criteria_order": ["validity", "closure", "consistency", "elegance",
                           "data"],
        "configurations": [
            {"digest": active.digest, "name": active.name,
             "selection": active.mapping, "lifecycle": "ACTIVE",
             "verdict": "ADOPTABLE", "stage_reached": "screen", "group": 1,
             "scores": score_block((0,), (3, 1), (0,), (2, 0), (1, 0)),
             "reasons": []},
            {"digest": other.digest, "name": "stub-proposed",
             "selection": proposed, "lifecycle": "CONSIDERED",
             "verdict": proposed_verdict, "stage_reached": "screen",
             "group": 0,
             "scores": score_block((0,), (2, 1), (0,), (2, 0), (0, 0)),
             "reasons": []},
        ],
        "active": {"digest": active.digest},
        "recommendation": rec,
        "verdict": verdict,
    }
    if fingerprint is not None:
        report["engine_fingerprint"] = fingerprint
    return report


def test_the_stub_theory_is_self_consistent(tmp_path):
    theory = make_theory(tmp_path)
    forks = theory.switches.forks()
    assert {f: forks[f].default() for f in forks} == ACTIVE_SELECTION
    assert theory.selections.active().mapping == ACTIVE_SELECTION
    assert theory.decisions.decision_log_path().is_file()
    assert make_assessment(theory.selections.active())["active"]["digest"] == \
        theory.selections.active().digest
