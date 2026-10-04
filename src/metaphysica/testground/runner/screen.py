"""Screen: the cheap in-process pass over many configurations.

Only signals of cost SCREEN are evaluated. For each configuration the
environment is set to ``theory.env_for(selection)``, the theory's call-time
caches are invalidated, the signals are evaluated, and the previous
environment is ALWAYS restored (and the caches invalidated again) -- whatever
the signals do. One configuration's failure is recorded as UNMEASURED for that
configuration and never aborts the screen.

Import-time-bound forks cannot be flipped in-process. When the plan has any,
and a ``theory_ref`` (``"module:attribute"``, the attribute being a Theory or a
zero-argument factory) is given, each group of import-time options is screened
in its own fresh process, with the group's environment set BEFORE the theory is
imported. Without a ``theory_ref``, only configurations whose import-time
options match this process are evaluated; the rest are UNMEASURED with the
reason, never silently measured under the wrong import-time state.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import importlib
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import (Dict, Iterable, Iterator, List, Mapping, Optional,
                    Sequence, Tuple, Union)

from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.runner.isolation import stamped_context
from metaphysica.testground.runner.plan import (RunGroup, RunPlan, build_plan,
                                                group_key)
from metaphysica.testground.runner.pool import RUNNING, ProgressLog, Sink
from metaphysica.testground.signals.model import (SCREEN, UNMEASURED,
                                                  Measurement, Signal)
from metaphysica.testground.theory import Theory

__all__ = [
    "ScreenResult",
    "screen_signals",
    "flipped_env",
    "evaluate_configuration",
    "load_theory",
    "screen",
]

Measurements = Tuple[Measurement, ...]


@dataclass(frozen=True)
class ScreenResult:
    """Measurements per configuration digest, in plan order."""

    theory: str
    plan: RunPlan
    measurements: Dict[str, Measurements]

    @property
    def order(self) -> List[str]:
        return self.plan.digests()

    def __getitem__(self, digest: str) -> Measurements:
        return self.measurements[digest]

    def __contains__(self, digest: object) -> bool:
        return digest in self.measurements

    def __iter__(self) -> Iterator[str]:
        return iter(self.order)

    def __len__(self) -> int:
        return len(self.measurements)

    def by_signal(self, digest: str) -> Dict[str, Measurement]:
        return {m.signal: m for m in self.measurements[digest]}

    def unmeasured_digests(self) -> List[str]:
        return [d for d in self.order
                if any(m.status == UNMEASURED for m in self.measurements[d])]


def screen_signals(signals: Iterable[Signal]) -> List[Signal]:
    """The signals the screen may evaluate (cost SCREEN only)."""
    return [signal for signal in signals if signal.cost == SCREEN]


@contextmanager
def flipped_env(env: Mapping[str, str]) -> Iterator[None]:
    """Set ``env`` for the block; restore every touched variable afterwards."""
    previous = {key: os.environ.get(key) for key in env}
    try:
        os.environ.update(env)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _all_unmeasured(signals: Sequence[Signal], why: str) -> Measurements:
    return tuple(Measurement.unmeasured(s.id, why) for s in signals)


def _checked(signal: Signal, value: object) -> Measurement:
    if isinstance(value, Measurement):
        return value
    return Measurement.unmeasured(
        signal.id, "signal returned %s, not a Measurement" % type(value).__name__)


def _settle(theory: Theory) -> None:
    """Invalidate caches after restoring the environment (never raises)."""
    try:
        theory.invalidate_caches()
    except Exception:
        pass


def evaluate_configuration(theory: Theory, cfg: Configuration,
                           signals: Sequence[Signal],
                           root: Optional[Union[str, Path]] = None
                           ) -> Measurements:
    """Evaluate ``signals`` for ``cfg`` with its environment set in-process."""
    if cfg.not_runnable:
        why = "; ".join(cfg.reasons) or "declared not runnable"
        return _all_unmeasured(signals, "configuration is NOT_RUNNABLE: " + why)
    try:
        with flipped_env(theory.env_for(cfg.mapping)):
            theory.invalidate_caches()
            ctx = stamped_context(cfg, root)
            return tuple(_checked(s, s(ctx)) for s in signals)
    except Exception as exc:
        return _all_unmeasured(signals, "configuration raised %s: %s"
                               % (type(exc).__name__, exc))
    finally:
        _settle(theory)


def load_theory(ref: str) -> Theory:
    """Import ``"module:attribute"``; call the attribute if it is a factory."""
    module_name, _, attribute = ref.partition(":")
    if not module_name or not attribute:
        raise ValueError("theory_ref %r is not 'module:attribute'" % ref)
    target = getattr(importlib.import_module(module_name), attribute)
    theory = target if isinstance(target, Theory) else target()
    if not isinstance(theory, Theory):
        raise TypeError("theory_ref %r gave %s, not a Theory"
                        % (ref, type(theory).__name__))
    return theory


def _status(measurements: Measurements) -> str:
    return UNMEASURED if any(m.status == UNMEASURED
                             for m in measurements) else "MEASURED"


def _process_key(theory: Theory,
                 forks: Sequence[str]) -> Optional[Tuple[Tuple[str, str], ...]]:
    """This process's import-time options (env override, else the active)."""
    try:
        active = theory.selections.active().mapping if forks else {}
    except Exception:
        return None
    key = []
    for fork in sorted(forks):
        value = os.environ.get(theory.env_var(fork), active.get(fork))
        if value is None:
            return None
        key.append((fork, value))
    return tuple(key)


def _screen_in_process(theory: Theory, plan: RunPlan,
                       signals: Sequence[Signal],
                       log: ProgressLog) -> Dict[str, Measurements]:
    here = _process_key(theory, plan.import_time_forks)
    measured: Dict[str, Measurements] = {}
    for entry in plan:
        cfg = entry.configuration
        log.emit("start", cfg.digest, SCREEN, RUNNING)
        key = group_key(cfg, plan.import_time_forks)
        if key != here:
            measured[cfg.digest] = _all_unmeasured(signals, (
                "import-time-bound options %s differ from this process (%s); "
                "screening them needs a fresh process (give theory_ref)")
                % (dict(key), dict(here) if here is not None else "unknown"))
        else:
            measured[cfg.digest] = evaluate_configuration(theory, cfg, signals)
        log.emit("finish", cfg.digest, SCREEN, _status(measured[cfg.digest]))
    return measured


def _batches(plan: RunPlan, jobs: int
             ) -> List[Tuple[RunGroup, Tuple[Configuration, ...]]]:
    """Split groups into contiguous chunks so ``jobs`` processes stay busy."""
    per_group = max(1, -(-max(1, jobs) // max(1, len(plan.groups))))
    batches = []
    for group in plan.groups:
        cfgs = group.configurations
        size = -(-len(cfgs) // min(per_group, len(cfgs)))
        for start in range(0, len(cfgs), size):
            batches.append((group, cfgs[start:start + size]))
    return batches


def _screen_batch(theory_ref: str, group_env: Dict[str, str],
                  cfgs: Tuple[Configuration, ...], signal_ids: Tuple[str, ...]
                  ) -> List[Tuple[str, Measurements]]:
    """Child-process entry: set the group env, THEN import the theory."""
    os.environ.update(group_env)
    theory = load_theory(theory_ref)
    signals = [s for s in theory.signals.signals() if s.id in signal_ids]
    return [(cfg.digest, evaluate_configuration(theory, cfg, signals))
            for cfg in cfgs]


def _in_declared_order(signals: Sequence[Signal],
                       found: Measurements) -> Measurements:
    by_id = {m.signal: m for m in found}
    return tuple(by_id.get(s.id) or Measurement.unmeasured(
        s.id, "signal not provided by the theory in a fresh process")
        for s in signals)


def _screen_in_fresh_processes(theory: Theory, plan: RunPlan,
                               signals: Sequence[Signal], jobs: int,
                               theory_ref: str,
                               log: ProgressLog) -> Dict[str, Measurements]:
    batches = _batches(plan, jobs)
    ids = tuple(s.id for s in signals)
    measured: Dict[str, Measurements] = {}
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=min(max(1, jobs), len(batches)),
                             mp_context=context,
                             max_tasks_per_child=1) as executor:
        futures = {}
        for group, cfgs in batches:
            for cfg in cfgs:
                log.emit("start", cfg.digest, SCREEN, RUNNING)
            futures[executor.submit(_screen_batch, theory_ref,
                                    group.env(theory), cfgs, ids)] = cfgs
        for future in as_completed(futures):
            cfgs = futures[future]
            try:
                pairs = future.result()
            except Exception as exc:
                why = "fresh-process screen failed: %s: %s" % (
                    type(exc).__name__, exc)
                pairs = [(c.digest, _all_unmeasured(signals, why))
                         for c in cfgs]
            for digest, found in pairs:
                measured[digest] = _in_declared_order(signals, found)
                log.emit("finish", digest, SCREEN, _status(measured[digest]))
    return measured


def screen(theory: Theory, cfgs: Iterable[Configuration],
           signals: Optional[Sequence[Signal]] = None, jobs: int = 1,
           progress: Sink = None, *, theory_ref: Optional[str] = None,
           unknown_as_import_time: bool = False) -> ScreenResult:
    """Screen ``cfgs`` on the SCREEN-cost subset of ``signals``.

    ``jobs`` only matters for fresh-process screening (in-process evaluation
    is sequential: the environment is process-global). ``progress`` is a
    JSON-lines path or a callable receiving each event.
    """
    chosen = screen_signals(signals if signals is not None
                            else theory.signals.signals())
    plan = build_plan(theory, cfgs, SCREEN,
                      unknown_as_import_time=unknown_as_import_time)
    log = ProgressLog(progress)
    log.emit("screen_start", None, SCREEN, RUNNING)
    if plan.import_time_forks and theory_ref and len(plan):
        measured = _screen_in_fresh_processes(theory, plan, chosen, jobs,
                                              theory_ref, log)
    else:
        measured = _screen_in_process(theory, plan, chosen, log)
    log.emit("screen_end", None, SCREEN, "DONE")
    return ScreenResult(theory.id, plan, measured)
