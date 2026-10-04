"""Pool: run many configurations at once, with a JSON-lines progress log.

Full runs are subprocess-bound (the worker spends its time waiting on a fresh
process), so the pool is a ``ThreadPoolExecutor`` around worker calls; the
isolation lives in the subprocesses and their scratch roots, not in the pool.

Progress events are one JSON object per line: ``{event, digest, stage, status,
t}`` with ``t`` in seconds since the epoch. Results come back sorted by digest
(then stage), whatever order the workers finished in, so a concurrent run is
directly comparable with a sequential one.

Cancellation-safe: when the cancel event is set (or the caller presses Ctrl-C)
no further task starts, tasks not yet started are reported CANCELLED, running
tasks receive the event (the worker kills its subprocess tree), and the
progress log is closed cleanly.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import threading
import time
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path
from typing import (Any, Callable, Dict, Iterable, List, Optional, Sequence,
                    Union)

from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.runner.cache import RunCache
from metaphysica.testground.runner.worker import run_configuration
from metaphysica.testground.signals.model import FULL
from metaphysica.testground.theory import Theory

__all__ = [
    "OK",
    "ERROR",
    "CANCELLED",
    "RUNNING",
    "ProgressLog",
    "PoolTask",
    "PoolResult",
    "run_pool",
    "full_run_tasks",
]

OK = "OK"
ERROR = "ERROR"
CANCELLED = "CANCELLED"
RUNNING = "RUNNING"
_WAIT_SLICE_S = 0.25

Sink = Union[str, Path, Callable[[Dict[str, Any]], None], None]


class ProgressLog:
    """Thread-safe JSON-lines progress: a file path, a callable, or nothing."""

    def __init__(self, sink: Sink = None) -> None:
        self._lock = threading.Lock()
        self._callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._path: Optional[Path] = None
        self.failures = 0
        if callable(sink):
            self._callback = sink
        elif sink is not None:
            self._path = Path(sink)
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, digest: Optional[str] = None,
             stage: Optional[str] = None,
             status: Optional[str] = None) -> Dict[str, Any]:
        record = {"event": event, "digest": digest, "stage": stage,
                  "status": status, "t": round(time.time(), 3)}
        with self._lock:
            if self._path is not None:
                with open(self._path, "a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
            if self._callback is not None:
                try:
                    self._callback(record)
                except Exception:  # a progress sink never stops a run
                    self.failures += 1
        return record


@dataclass(frozen=True)
class PoolTask:
    """A unit of work; ``run`` receives the pool's cancel event."""

    digest: str
    run: Callable[[threading.Event], Any]
    stage: str = FULL


@dataclass(frozen=True)
class PoolResult:
    """A task's outcome. ``status`` is the value's own status when it has one."""

    digest: str
    stage: str
    status: str
    value: Any = None
    error: str = ""
    wall_s: float = 0.0
    index: int = 0


def _status_of(value: Any) -> str:
    status = getattr(value, "status", None)
    return status if isinstance(status, str) else OK


def _execute(index: int, task: PoolTask, cancel: threading.Event,
             log: ProgressLog) -> PoolResult:
    if cancel.is_set():
        log.emit("cancelled", task.digest, task.stage, CANCELLED)
        return PoolResult(task.digest, task.stage, CANCELLED, index=index)
    log.emit("start", task.digest, task.stage, RUNNING)
    started = time.perf_counter()
    try:
        value = task.run(cancel)
    except Exception as exc:  # one task's failure never aborts the pool
        result = PoolResult(task.digest, task.stage, ERROR,
                            error="%s: %s" % (type(exc).__name__, exc),
                            wall_s=time.perf_counter() - started, index=index)
    else:
        result = PoolResult(task.digest, task.stage, _status_of(value), value,
                            wall_s=time.perf_counter() - started, index=index)
    log.emit("finish", task.digest, task.stage, result.status)
    return result


def _ordered(results: Iterable[PoolResult]) -> List[PoolResult]:
    return sorted(results, key=lambda r: (r.digest, r.stage, r.index))


def _collect(futures: Dict[Future, int], tasks: Sequence[PoolTask],
             cancel: threading.Event,
             log: ProgressLog) -> Dict[int, PoolResult]:
    """Wait for every future; never-started ones are reported CANCELLED."""
    results: Dict[int, PoolResult] = {}
    pending = set(futures)
    while pending:
        done, pending = wait(pending, timeout=_WAIT_SLICE_S,
                             return_when=FIRST_COMPLETED)
        for future in done:
            index = futures[future]
            if future.cancelled():
                task = tasks[index]
                log.emit("cancelled", task.digest, task.stage, CANCELLED)
                results[index] = PoolResult(task.digest, task.stage,
                                            CANCELLED, index=index)
            else:
                results[index] = future.result()
    return results


def run_pool(tasks: Sequence[PoolTask], jobs: int = 1,
             progress_path: Sink = None, *,
             cancel: Optional[threading.Event] = None) -> List[PoolResult]:
    """Run ``tasks`` on ``jobs`` threads; results sorted by digest."""
    tasks = list(tasks)
    cancel = cancel if cancel is not None else threading.Event()
    log = ProgressLog(progress_path)
    log.emit("pool_start", None, None, RUNNING)
    executor = ThreadPoolExecutor(max_workers=max(1, int(jobs)),
                                  thread_name_prefix="testground-pool")
    futures = {executor.submit(_execute, i, task, cancel, log): i
               for i, task in enumerate(tasks)}
    try:
        results = _collect(futures, tasks, cancel, log)
    except BaseException:
        cancel.set()
        for future, index in futures.items():
            if future.cancel():
                log.emit("cancelled", tasks[index].digest, tasks[index].stage,
                         CANCELLED)
        executor.shutdown(wait=True, cancel_futures=True)
        log.emit("pool_end", None, None, CANCELLED)
        raise
    executor.shutdown(wait=True)
    log.emit("pool_end", None, None, CANCELLED if cancel.is_set() else OK)
    return _ordered(results.values())


def full_run_tasks(theory: Theory, configurations: Iterable[Configuration],
                   base_dir: Union[str, Path], fingerprint: str,
                   timeout: Optional[float] = None, *,
                   cache: Optional[RunCache] = None,
                   refresh: bool = False,
                   unset_env: Sequence[str] = ()) -> List[PoolTask]:
    """One pool task per configuration: isolate, run (or reuse), cache."""
    def task_for(cfg: Configuration) -> PoolTask:
        def run(cancel: threading.Event) -> Any:
            return run_configuration(theory, cfg, base_dir, fingerprint,
                                     timeout, cache=cache, refresh=refresh,
                                     cancel=cancel, unset_env=unset_env)
        return PoolTask(cfg.digest, run, FULL)
    return [task_for(cfg) for cfg in configurations]
