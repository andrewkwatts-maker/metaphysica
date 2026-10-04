"""A tiny in-test theory for the runner (lane 2C) tests -- no tests here.

Two forks: ``mode`` (call-time bound: read from the environment at every call)
and ``seed`` (import-time bound: read ONCE, when this module is imported -- the
hazard the plan's process groups exist for). The pipeline stages are
``python -c`` commands that write small JSON files into the run root.

This module is importable by fresh processes (the screen's ``theory_ref`` is
``"<this module>:import_time_theory"``), so it must stay side-effect free apart
from the one import-time read below.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence

from metaphysica.testground.configurations.model import ACTIVE, Configuration
from metaphysica.testground.signals.model import (ARTIFACT, FULL, LIVE, SCREEN,
                                                  Measurement, Signal,
                                                  SignalContext)
from metaphysica.testground.switches.model import (CONSIDERED, Fork,
                                                   VariantOption)
from metaphysica.testground.theory import Stage, Theory

THEORY_ID = "tiny"
PREFIX = "TG2C_VARIANT_"
MODE_VAR = PREFIX + "MODE"
SEED_VAR = PREFIX + "SEED"

#: Read ONCE at import: this process's value of the import-time-bound fork.
IMPORT_SEED = os.environ.get(SEED_VAR, "low")

MODE_COUNT = {"a": 0, "b": 1, "c": 2}
SEED_COUNT = {"low": 0, "high": 1}

#: Counts calls of the theory's invalidate_caches hook.
CALLS: Dict[str, int] = {"invalidate": 0}


def _option(oid: str, active: bool = False) -> VariantOption:
    status = "active" if active else CONSIDERED
    return VariantOption(oid, "option " + oid, "", adopted=active,
                         status=status)


def forks(seed_binding: str = "import_time",
          mode_binding: str = "call_time") -> Dict[str, Fork]:
    return {
        "mode": Fork("mode", "which mode?", "test", [
            _option("a", True), _option("b"), _option("c")],
            status="open", binding=mode_binding),
        "seed": Fork("seed", "which seed?", "test", [
            _option("low", True), _option("high")],
            status="open", binding=seed_binding),
    }


class Switches:
    def __init__(self, fork_map: Mapping[str, Fork]) -> None:
        self._forks = dict(fork_map)

    def forks(self) -> Mapping[str, Fork]:
        return self._forks

    def constraints(self) -> Sequence:
        return ()


class Store:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def active(self) -> Configuration:
        if self.fail:
            raise RuntimeError("store unavailable")
        return Configuration.of(THEORY_ID, {"mode": "a", "seed": "low"},
                                lifecycle=ACTIVE)

    def named(self) -> Mapping[str, Configuration]:
        return {}

    def write_active(self, cfg: Configuration, decision_id: str,
                     note: str = "") -> None:
        raise NotImplementedError


class Pipeline:
    def __init__(self, stages: Sequence[Stage]) -> None:
        self._stages = list(stages)

    def stages(self) -> Sequence[Stage]:
        return self._stages


class Signals:
    def __init__(self, signals: Sequence[Signal]) -> None:
        self._signals = list(signals)

    def signals(self) -> Sequence[Signal]:
        return self._signals


# -- pipeline stages -------------------------------------------------------

_WRITE_OUT = (
    "import json, os; json.dump({'mode': os.environ['%s'], "
    "'seed': os.environ['%s']}, open('out.json', 'w'), sort_keys=True)"
    % (MODE_VAR, SEED_VAR))
_WRITE_SCORE = (
    "import json; d = json.load(open('out.json')); "
    "json.dump({'score': %r[d['mode']] + %r[d['seed']]}, "
    "open('score.json', 'w'))" % (MODE_COUNT, SEED_COUNT))


def py_stage(stage_id: str, code: str, **kwargs) -> Stage:
    return Stage(stage_id, "compute", (sys.executable, "-c", code), **kwargs)


def default_stages() -> List[Stage]:
    return [py_stage("compute", _WRITE_OUT),
            py_stage("score", _WRITE_SCORE)]


def sleep_stage(seconds: float, **kwargs) -> Stage:
    return py_stage("sleep", "import time; time.sleep(%s)" % seconds, **kwargs)


def exit_stage(code: int, **kwargs) -> Stage:
    return py_stage("exit", "import sys; print('out'); "
                    "print('err', file=sys.stderr); sys.exit(%d)" % code,
                    **kwargs)


# -- signals ---------------------------------------------------------------

def _mode_live(ctx: SignalContext) -> Measurement:
    return Measurement("mode_live", count=MODE_COUNT[os.environ[MODE_VAR]])


def _seed_frozen(ctx: SignalContext) -> Measurement:
    return Measurement("seed_frozen", count=SEED_COUNT[IMPORT_SEED])


def _seed_env(ctx: SignalContext) -> Measurement:
    return Measurement("seed_env", count=SEED_COUNT[os.environ[SEED_VAR]])


def _artifact_score(ctx: SignalContext) -> Measurement:
    data = json.loads((Path(ctx.root) / "score.json").read_text())
    return Measurement("artifact_score", count=data["score"])


def _boom(ctx: SignalContext) -> Measurement:
    raise RuntimeError("boom")


MODE_LIVE = Signal("mode_live", "elegance", LIVE, SCREEN, _mode_live)
SEED_FROZEN = Signal("seed_frozen", "elegance", LIVE, SCREEN, _seed_frozen)
SEED_ENV = Signal("seed_env", "elegance", LIVE, SCREEN, _seed_env)
ARTIFACT_SCORE = Signal("artifact_score", "data", ARTIFACT, FULL,
                        _artifact_score)
BOOM = Signal("boom", "consistency", LIVE, SCREEN, _boom)


def default_signals() -> List[Signal]:
    return [MODE_LIVE, SEED_FROZEN, SEED_ENV, ARTIFACT_SCORE]


def _count_invalidations() -> None:
    CALLS["invalidate"] += 1


def make_theory(stages: Optional[Sequence[Stage]] = None,
                signals: Optional[Sequence[Signal]] = None,
                invalidate: Optional[Callable[[], None]] = None,
                fork_map: Optional[Mapping[str, Fork]] = None,
                store: Optional[Store] = None) -> Theory:
    return Theory(
        id=THEORY_ID, title="tiny runner theory", env_prefix=PREFIX,
        switches=Switches(fork_map if fork_map is not None else forks()),
        selections=store or Store(),
        pipeline=Pipeline(default_stages() if stages is None else stages),
        signals=Signals(default_signals() if signals is None else signals),
        invalidate_caches=invalidate or _count_invalidations)


def import_time_theory() -> Theory:
    """Factory used as a theory_ref by fresh-process screens."""
    return make_theory()


def cfg(mode: str = "a", seed: str = "low", **kwargs) -> Configuration:
    return Configuration.of(THEORY_ID, {"mode": mode, "seed": seed}, **kwargs)


def all_cfgs() -> List[Configuration]:
    return [cfg(m, s) for s in ("low", "high") for m in ("a", "b", "c")]


def theory_ref(attribute: str = "import_time_theory") -> str:
    return "%s:%s" % (__name__, attribute)
