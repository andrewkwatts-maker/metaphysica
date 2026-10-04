"""Lane 2C: a full run executes the stages in fresh processes inside the root.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import os
import threading
import time

import pytest

from metaphysica.testground.runner.cache import RunCache
from metaphysica.testground.runner.isolation import prepare_root
from metaphysica.testground.runner.screen import evaluate_configuration
from metaphysica.testground.runner.worker import (
    CANCELLED, COMPLETED, LOG_DIR, NOT_RUNNABLE, RUN_LOG_NAME, RunResult,
    StageResult, run_configuration, run_full, stage_env)
from metaphysica.testground.signals.model import MEASURED, UNMEASURED
from tests.testground import test_2c_support as tiny

FP = "0123456789abcdef"


def _root(tmp_path, theory, cfg):
    return prepare_root(tmp_path, theory, cfg, FP)


def test_a_full_run_writes_into_its_root_and_logs_each_stage(tmp_path):
    theory, cfg = tiny.make_theory(), tiny.cfg("c", "high")
    root = _root(tmp_path, theory, cfg)
    result = run_full(theory, cfg, root, timeout=60)
    assert result.status == COMPLETED and result.reason == ""
    assert result.completed and result.cacheable
    assert json.loads((root / "out.json").read_text()) == {
        "mode": "c", "seed": "high"}
    assert json.loads((root / "score.json").read_text()) == {"score": 3}
    log = json.loads((root / RUN_LOG_NAME).read_text())
    assert log["status"] == COMPLETED and log["fingerprint"] == FP
    assert [s["id"] for s in log["stages"]] == ["compute", "score"]
    assert all(s["exit_code"] == 0 and s["ok"] for s in log["stages"])
    assert all(s["wall_s"] >= 0 for s in log["stages"])
    assert sorted(p.name for p in (root / LOG_DIR).iterdir()) == [
        "00-compute.stderr.log", "00-compute.stdout.log",
        "01-score.stderr.log", "01-score.stdout.log"]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["tiny"]


def test_artifact_signals_read_the_stamped_root_after_the_run(tmp_path):
    theory, cfg = tiny.make_theory(), tiny.cfg("b", "low")
    root = _root(tmp_path, theory, cfg)
    run_full(theory, cfg, root, timeout=60)
    good = evaluate_configuration(theory, cfg, [tiny.ARTIFACT_SCORE], root=root)
    assert good[0].status == MEASURED and good[0].count == 1
    other = evaluate_configuration(theory, tiny.cfg("c"), [tiny.ARTIFACT_SCORE],
                                   root=root)
    assert other[0].status == UNMEASURED      # stamp mismatch, never stale


def test_the_stage_env_adds_only_the_selection(monkeypatch):
    monkeypatch.delenv("METAPHYSICA_OUT", raising=False)
    theory, cfg = tiny.make_theory(), tiny.cfg("b", "high")
    env = stage_env(theory, cfg)
    added = {k: v for k, v in env.items() if os.environ.get(k) != v}
    assert added == {tiny.MODE_VAR: "b", tiny.SEED_VAR: "high"}
    assert "METAPHYSICA_OUT" not in env


def test_an_inherited_metaphysica_out_is_passed_through_not_set(monkeypatch):
    monkeypatch.setenv("METAPHYSICA_OUT", "/somewhere/else")
    env = stage_env(tiny.make_theory(), tiny.cfg())
    assert env["METAPHYSICA_OUT"] == "/somewhere/else"


def test_named_inherited_variables_can_be_kept_out_of_a_run(tmp_path,
                                                            monkeypatch):
    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path / "shared"))
    env = stage_env(tiny.make_theory(), tiny.cfg(), ("METAPHYSICA_OUT",))
    assert "METAPHYSICA_OUT" not in env
    theory = tiny.make_theory(stages=[tiny.py_stage(
        "probe", "import json, os; json.dump(os.environ.get("
        "'METAPHYSICA_OUT'), open('probe.json', 'w'))")])
    result = run_configuration(theory, tiny.cfg(), tmp_path / "runs", FP, 60,
                               unset_env=("METAPHYSICA_OUT",))
    assert json.loads((tmp_path / "runs" / "tiny" / FP / tiny.cfg().digest
                       / "probe.json").read_text()) is None
    assert result.status == COMPLETED and not (tmp_path / "shared").exists()


def test_a_timed_out_stage_marks_the_configuration_not_runnable(tmp_path):
    theory = tiny.make_theory(stages=[tiny.sleep_stage(30),
                                      tiny.default_stages()[0]])
    cfg = tiny.cfg()
    root = _root(tmp_path, theory, cfg)
    started = time.monotonic()
    result = run_full(theory, cfg, root, timeout=1.0)
    assert time.monotonic() - started < 20
    assert result.status == NOT_RUNNABLE
    assert "timed out" in result.reason and "sleep" in result.reason
    assert len(result.stages) == 1 and result.stages[0].timed_out
    assert result.timed_out and not result.cacheable
    assert not (root / "out.json").exists()       # later stages never ran


def test_a_stage_timeout_overrides_the_default(tmp_path):
    theory = tiny.make_theory(stages=[tiny.sleep_stage(30, timeout_s=0.5)])
    root = _root(tmp_path, theory, tiny.cfg())
    result = run_full(theory, tiny.cfg(), root, timeout=600)
    assert result.stages[0].timed_out and result.stages[0].timeout_s == 0.5


def test_exit_codes_are_judged_against_the_tolerated_set(tmp_path):
    cfg = tiny.cfg()
    tolerated = tiny.make_theory(stages=[tiny.exit_stage(72,
                                         tolerated_exit_codes=(0, 72))])
    result = run_full(tolerated, cfg, _root(tmp_path, tolerated, cfg))
    assert result.status == COMPLETED and result.stages[0].exit_code == 72
    assert "out" in result.stages[0].stdout_tail
    assert "err" in result.stages[0].stderr_tail
    failing = tiny.make_theory(stages=[tiny.exit_stage(3)])
    result = run_full(failing, cfg, _root(tmp_path, failing, cfg))
    assert result.status == NOT_RUNNABLE
    assert result.reason == "stage exit exited 3 (tolerated: [0])"
    assert result.cacheable


def test_a_stage_that_cannot_start_is_not_runnable(tmp_path):
    theory = tiny.make_theory(stages=[tiny.Stage(
        "ghost", "compute", ("definitely-not-a-real-exe-2c",))])
    result = run_full(theory, tiny.cfg(), _root(tmp_path, theory, tiny.cfg()))
    assert result.status == NOT_RUNNABLE
    assert "could not start" in result.reason
    assert result.stages[0].exit_code is None


def test_a_declared_not_runnable_configuration_is_not_run(tmp_path):
    theory = tiny.make_theory()
    cfg = tiny.cfg("b", not_runnable=True, reasons=("b is unimplemented",))
    root = _root(tmp_path, theory, cfg)
    result = run_full(theory, cfg, root)
    assert result.status == NOT_RUNNABLE and "unimplemented" in result.reason
    assert result.stages == () and not (root / "out.json").exists()


def test_an_unstamped_root_is_refused(tmp_path):
    with pytest.raises(ValueError, match="not stamped"):
        run_full(tiny.make_theory(), tiny.cfg(), tmp_path)


def test_a_cancelled_run_is_cancelled_and_never_cached(tmp_path):
    theory = tiny.make_theory(stages=[tiny.sleep_stage(30)])
    cancel = threading.Event()
    threading.Timer(0.5, cancel.set).start()
    cache = RunCache(tmp_path)
    result = run_configuration(theory, tiny.cfg(), tmp_path, FP, timeout=60,
                               cache=cache, cancel=cancel)
    assert result.status == CANCELLED and result.stages[0].cancelled
    assert "cancelled" in result.reason and not result.cacheable
    assert cache.get(theory.id, tiny.cfg().digest, FP) is None


def test_run_configuration_caches_and_reuses(tmp_path):
    theory, cfg = tiny.make_theory(), tiny.cfg("b", "high")
    cache = RunCache(tmp_path)
    first = run_configuration(theory, cfg, tmp_path, FP, 60, cache=cache)
    log_time = (tmp_path / "tiny" / FP / cfg.digest / RUN_LOG_NAME).stat().st_mtime_ns
    second = run_configuration(theory, cfg, tmp_path, FP, 60, cache=cache)
    assert not first.cached and second.cached
    assert second == first
    assert cache.stats() == {"hits": 1, "misses": 1}
    assert (tmp_path / "tiny" / FP / cfg.digest / RUN_LOG_NAME).stat().st_mtime_ns == log_time
    third = run_configuration(theory, cfg, tmp_path, FP, 60, cache=cache,
                              refresh=True)
    assert not third.cached and third.status == COMPLETED


def test_timeouts_are_not_cached(tmp_path):
    theory = tiny.make_theory(stages=[tiny.sleep_stage(30)])
    cache = RunCache(tmp_path)
    run_configuration(theory, tiny.cfg(), tmp_path, FP, 0.5, cache=cache)
    assert cache.get(theory.id, tiny.cfg().digest, FP) is None


def test_the_cache_must_share_the_run_base(tmp_path):
    with pytest.raises(ValueError, match="cache lives"):
        run_configuration(tiny.make_theory(), tiny.cfg(), tmp_path / "a", FP,
                          cache=RunCache(tmp_path / "b"))


def test_tails_of_missing_logs_are_empty(tmp_path):
    from metaphysica.testground.runner import worker
    assert worker._tail(tmp_path / "absent.log", 100) == ""
    (tmp_path / "x.log").write_bytes(b"abcdef")
    assert worker._tail(tmp_path / "x.log", 3) == "def"
    assert worker._tail(tmp_path / "x.log", 0) == ""


def test_results_round_trip_through_dicts():
    stage = StageResult("s", "compute", ("x",), 0, (0,), None, 0.1,
                        stdout_tail="o")
    result = RunResult("tiny", "d" * 16, "/r", COMPLETED, "", (stage,), 1.0,
                       FP)
    again = RunResult.from_dict(json.loads(json.dumps(result.to_dict())))
    assert again == result and stage.failure_reason() == ""
