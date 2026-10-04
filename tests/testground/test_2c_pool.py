"""Lane 2C: the pool -- concurrent equals sequential, progress, cancellation.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import threading
import time

import pytest

from metaphysica.testground.runner.cache import RunCache
from metaphysica.testground.runner.isolation import read_stamp
from metaphysica.testground.runner.pool import (CANCELLED, ERROR, OK,
                                                PoolTask, ProgressLog,
                                                full_run_tasks, run_pool)
from metaphysica.testground.runner.worker import COMPLETED
from tests.testground import test_2c_support as tiny

FP = "fedcba9876543210"
_KEYS = {"event", "digest", "stage", "status", "t"}


def _outputs(base, results):
    """Everything a run produced, minus timings and creation stamps."""
    seen = {}
    for r in results:
        root = base / "tiny" / FP / r.digest
        stamp = read_stamp(root)
        stamp.pop("created")
        seen[r.digest] = (r.status,
                          json.loads((root / "out.json").read_text()),
                          json.loads((root / "score.json").read_text()),
                          stamp)
    return seen


def test_concurrent_runs_equal_sequential_runs(tmp_path):
    theory = tiny.make_theory()
    cfgs = [tiny.cfg("a", "low"), tiny.cfg("c", "low"), tiny.cfg("b", "high"),
            tiny.cfg("c", "high")]
    seq = run_pool(full_run_tasks(theory, cfgs, tmp_path / "seq", FP, 60), 1)
    par = run_pool(full_run_tasks(theory, cfgs, tmp_path / "par", FP, 60), 4)
    assert [r.digest for r in seq] == sorted(c.digest for c in cfgs)
    assert [r.digest for r in par] == [r.digest for r in seq]
    assert all(r.status == COMPLETED for r in seq + par)
    assert _outputs(tmp_path / "seq", seq) == _outputs(tmp_path / "par", par)


def test_progress_is_json_lines_with_fixed_keys(tmp_path):
    theory = tiny.make_theory()
    cfgs = [tiny.cfg("a"), tiny.cfg("b")]
    path = tmp_path / "logs" / "progress.jsonl"
    run_pool(full_run_tasks(theory, cfgs, tmp_path / "runs", FP, 60), 2, path)
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert all(set(e) == _KEYS for e in events)
    assert events[0]["event"] == "pool_start"
    assert events[-1] == {**events[-1], "event": "pool_end", "status": OK}
    for cfg in cfgs:
        mine = [e for e in events if e["digest"] == cfg.digest]
        assert [e["event"] for e in mine] == ["start", "finish"]
        assert mine[1]["status"] == COMPLETED and mine[1]["stage"] == "full"


def test_results_are_ordered_by_digest_whatever_finishes_first():
    def task(digest, delay):
        def run(cancel):
            time.sleep(delay)
            return digest
        return PoolTask(digest, run)

    tasks = [task("c" * 16, 0.0), task("a" * 16, 0.3), task("b" * 16, 0.1)]
    results = run_pool(tasks, jobs=3)
    assert [r.digest for r in results] == ["a" * 16, "b" * 16, "c" * 16]
    assert [r.value for r in results] == ["a" * 16, "b" * 16, "c" * 16]
    assert all(r.status == OK for r in results)


def test_a_failing_task_is_an_error_and_the_others_still_run():
    def boom(cancel):
        raise RuntimeError("nope")

    results = run_pool([PoolTask("b" * 16, boom),
                        PoolTask("a" * 16, lambda cancel: 1)], jobs=2)
    assert [r.status for r in results] == [OK, ERROR]
    assert results[1].error == "RuntimeError: nope"


def test_cancellation_stops_unstarted_tasks(tmp_path):
    cancel = threading.Event()

    def first(c):
        c.set()
        return "ran"

    def never(c):  # pragma: no cover - must not run
        raise AssertionError("ran after cancel")

    path = tmp_path / "p.jsonl"
    results = run_pool([PoolTask("a" * 16, first), PoolTask("b" * 16, never),
                        PoolTask("c" * 16, never)], 1, path, cancel=cancel)
    assert [r.status for r in results] == [OK, CANCELLED, CANCELLED]
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert events[-1]["status"] == CANCELLED
    assert sum(e["event"] == "cancelled" for e in events) == 2


def test_an_interrupt_cancels_the_rest_and_propagates(tmp_path):
    def interrupt(c):
        raise KeyboardInterrupt

    def slow(c):
        c.wait(5)
        return "stopped" if c.is_set() else "timeout"

    path = tmp_path / "p.jsonl"
    tasks = [PoolTask("a" * 16, interrupt)] + [
        PoolTask("%016d" % i, slow) for i in range(4)]
    with pytest.raises(KeyboardInterrupt):
        run_pool(tasks, 1, path)
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert events[-1] == {**events[-1], "event": "pool_end",
                          "status": CANCELLED}


def test_never_started_futures_are_reported_cancelled(tmp_path, monkeypatch):
    """A future cancelled by the executor itself is reported, not lost."""
    from concurrent.futures import Future

    from metaphysica.testground.runner import pool as pool_mod

    def fake_wait(pending, timeout, return_when):
        for future in pending:
            future.cancel()
        return set(pending), set()

    fut = Future()
    monkeypatch.setattr(pool_mod, "wait", fake_wait)
    log = ProgressLog(tmp_path / "p.jsonl")
    out = pool_mod._collect({fut: 0}, [PoolTask("a" * 16, lambda c: 1)],
                            threading.Event(), log)
    assert out[0].status == CANCELLED


def test_a_failing_progress_callback_never_stops_a_run():
    def broken(record):
        raise OSError("pipe closed")

    log = ProgressLog(broken)
    assert log.emit("start", "a" * 16, "full", "RUNNING")["event"] == "start"
    assert log.failures == 1


def test_pool_tasks_reuse_the_cache(tmp_path):
    theory, cfgs = tiny.make_theory(), [tiny.cfg("a"), tiny.cfg("c", "high")]
    cache = RunCache(tmp_path)
    run_pool(full_run_tasks(theory, cfgs, tmp_path, FP, 60, cache=cache), 2)
    again = run_pool(full_run_tasks(theory, cfgs, tmp_path, FP, 60,
                                    cache=cache), 2)
    assert all(r.value.cached for r in again)
    assert cache.stats() == {"hits": 2, "misses": 2}
