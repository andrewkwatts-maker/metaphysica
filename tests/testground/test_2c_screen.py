"""Lane 2C: the in-process screen flips, measures and ALWAYS restores.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import os

import pytest

from metaphysica.testground.runner import screen as screen_mod
from metaphysica.testground.runner.plan import build_plan
from metaphysica.testground.runner.screen import (evaluate_configuration,
                                                  flipped_env, load_theory,
                                                  screen, screen_signals)
from metaphysica.testground.signals.model import (MEASURED, UNMEASURED,
                                                  Measurement, Signal)
from tests.testground import test_2c_support as tiny


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv(tiny.MODE_VAR, raising=False)
    monkeypatch.delenv(tiny.SEED_VAR, raising=False)
    tiny.CALLS["invalidate"] = 0


def _call_time_theory(**kwargs):
    return tiny.make_theory(fork_map=tiny.forks(seed_binding="call_time"),
                            **kwargs)


def test_the_environment_is_restored_after_the_screen(monkeypatch):
    monkeypatch.setenv(tiny.MODE_VAR, "outer")
    monkeypatch.setenv("UNRELATED_TG2C", "kept")
    before = dict(os.environ)
    result = screen(_call_time_theory(), tiny.all_cfgs())
    assert dict(os.environ) == before
    assert os.environ[tiny.MODE_VAR] == "outer"
    assert tiny.SEED_VAR not in os.environ
    assert len(result) == 6


def test_each_configuration_is_measured_under_its_own_selection():
    result = screen(_call_time_theory(), tiny.all_cfgs())
    for cfg in tiny.all_cfgs():
        by = result.by_signal(cfg.digest)
        assert by["mode_live"].count == tiny.MODE_COUNT[cfg.option("mode")]
        assert by["seed_env"].count == tiny.SEED_COUNT[cfg.option("seed")]
    assert tiny.CALLS["invalidate"] == 2 * 6  # before and after each one


def test_only_screen_cost_signals_are_evaluated():
    result = screen(_call_time_theory(), [tiny.cfg()])
    assert [m.signal for m in result[tiny.cfg().digest]] == [
        "mode_live", "seed_frozen", "seed_env"]
    assert screen_signals(tiny.default_signals()) == [
        tiny.MODE_LIVE, tiny.SEED_FROZEN, tiny.SEED_ENV]


def test_a_crashing_configuration_never_aborts_the_screen(monkeypatch):
    calls = {"n": 0}

    def flaky_invalidate():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("cache exploded")

    monkeypatch.setenv(tiny.MODE_VAR, "outer")
    theory = _call_time_theory(invalidate=flaky_invalidate,
                               signals=[tiny.MODE_LIVE, tiny.BOOM])
    result = screen(theory, [tiny.cfg("a"), tiny.cfg("b")])
    first, second = result[tiny.cfg("a").digest], result[tiny.cfg("b").digest]
    assert all(m.status == UNMEASURED for m in first)
    assert "cache exploded" in first[0].reasons[0]
    assert second[0].status == MEASURED and second[0].count == 1
    assert second[1].status == UNMEASURED and "boom" in second[1].reasons[0]
    assert os.environ[tiny.MODE_VAR] == "outer"
    assert result.unmeasured_digests() == [tiny.cfg("a").digest,
                                           tiny.cfg("b").digest]
    assert tiny.cfg("a").digest in result and tiny.cfg("c").digest not in result


def test_the_environment_is_restored_even_on_keyboard_interrupt(monkeypatch):
    def interrupt(ctx):
        raise KeyboardInterrupt

    monkeypatch.setenv(tiny.MODE_VAR, "outer")
    signal = tiny.Signal("stop", "elegance", "live", "screen", interrupt)
    # Signal.__call__ only catches Exception, so the interrupt propagates
    with pytest.raises(KeyboardInterrupt):
        evaluate_configuration(_call_time_theory(), tiny.cfg("c"), [signal])
    assert os.environ[tiny.MODE_VAR] == "outer"
    assert tiny.SEED_VAR not in os.environ


def test_settle_swallows_a_failing_invalidation():
    calls = {"n": 0}

    def fails_after_first():
        calls["n"] += 1
        if calls["n"] > 1:
            raise RuntimeError("late failure")

    theory = _call_time_theory(invalidate=fails_after_first)
    measured = evaluate_configuration(theory, tiny.cfg(), [tiny.MODE_LIVE])
    assert measured[0].status == MEASURED and calls["n"] == 2


def test_not_runnable_and_non_measurement_results_are_unmeasured():
    theory = _call_time_theory()
    nr = tiny.cfg("b", not_runnable=True, reasons=("option b unimplemented",))
    out = evaluate_configuration(theory, nr, [tiny.MODE_LIVE])
    assert out[0].status == UNMEASURED and "unimplemented" in out[0].reasons[0]
    bad = Signal("bad", "elegance", "live", "screen", lambda ctx: 42)
    out = evaluate_configuration(theory, tiny.cfg(), [bad])
    assert out[0].status == UNMEASURED and "int" in out[0].reasons[0]


def test_flipped_env_restores_previous_values(monkeypatch):
    monkeypatch.setenv("TG2C_A", "1")
    monkeypatch.delenv("TG2C_B", raising=False)
    with flipped_env({"TG2C_A": "2", "TG2C_B": "3"}):
        assert os.environ["TG2C_A"] == "2" and os.environ["TG2C_B"] == "3"
    assert os.environ["TG2C_A"] == "1" and "TG2C_B" not in os.environ


def test_progress_is_written_as_json_lines(tmp_path):
    path = tmp_path / "progress" / "screen.jsonl"
    seen = []
    screen(_call_time_theory(), [tiny.cfg("a"), tiny.cfg("b")], progress=path)
    screen(_call_time_theory(), [tiny.cfg("a")], progress=seen.append)
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert [e["event"] for e in events] == [
        "screen_start", "start", "finish", "start", "finish", "screen_end"]
    assert all(set(e) == {"event", "digest", "stage", "status", "t"}
               for e in events)
    assert events[2]["status"] == MEASURED
    assert [e["event"] for e in seen] == ["screen_start", "start", "finish",
                                          "screen_end"]


def test_import_time_options_differing_from_this_process_are_unmeasured():
    """Without a theory_ref the screen refuses to fake an import-time flip."""
    theory = tiny.make_theory()
    result = screen(theory, [tiny.cfg("b", "low"), tiny.cfg("b", "high")])
    low = result.by_signal(tiny.cfg("b", "low").digest)
    high = result.by_signal(tiny.cfg("b", "high").digest)
    assert low["mode_live"].count == 1
    assert all(m.status == UNMEASURED for m in high.values())
    assert "fresh process" in high["mode_live"].reasons[0]


def test_an_in_process_flip_of_an_import_time_fork_would_be_wrong():
    """The hazard the grouping exists for: the frozen value ignores the flip."""
    out = evaluate_configuration(tiny.make_theory(), tiny.cfg("a", "high"),
                                 [tiny.SEED_FROZEN, tiny.SEED_ENV])
    assert out[1].count == 1          # call-time read sees the flip
    assert out[0].count == 0          # import-time read does not


def test_an_unreadable_store_leaves_import_time_groups_unmeasured():
    theory = tiny.make_theory(store=tiny.Store(fail=True))
    result = screen(theory, [tiny.cfg()])
    measured = result[tiny.cfg().digest]
    assert all(m.status == UNMEASURED for m in measured)
    assert "unknown" in measured[0].reasons[0]


def test_an_import_time_fork_missing_from_the_active_is_unknown(monkeypatch):
    class PartialStore(tiny.Store):
        def active(self):
            return tiny.Configuration.of(tiny.THEORY_ID, {"mode": "a"})

    theory = tiny.make_theory(store=PartialStore())
    measured = screen(theory, [tiny.cfg()])[tiny.cfg().digest]
    assert "unknown" in measured[0].reasons[0]
    monkeypatch.setenv(tiny.SEED_VAR, "low")       # an env override decides
    assert screen(theory, [tiny.cfg()])[tiny.cfg().digest][0].count == 0


def test_import_time_groups_run_in_fresh_processes(tmp_path):
    theory = tiny.make_theory()
    cfgs = [tiny.cfg("a", "low"), tiny.cfg("c", "high"), tiny.cfg("b", "high")]
    path = tmp_path / "p.jsonl"
    result = screen(theory, cfgs, jobs=2, progress=path,
                    theory_ref=tiny.theory_ref())
    for cfg in cfgs:
        by = result.by_signal(cfg.digest)
        assert by["seed_frozen"].count == tiny.SEED_COUNT[cfg.option("seed")]
        assert by["mode_live"].count == tiny.MODE_COUNT[cfg.option("mode")]
    assert list(result) == [c.digest for c in cfgs]
    assert tiny.IMPORT_SEED == "low"            # this process is untouched
    assert tiny.SEED_VAR not in os.environ
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert sum(e["event"] == "finish" for e in events) == 3


def test_a_broken_theory_ref_marks_its_batch_unmeasured():
    result = screen(tiny.make_theory(), [tiny.cfg("a", "high")],
                    theory_ref="tests.testground.no_such_module_2c:x")
    measured = result[tiny.cfg("a", "high").digest]
    assert all(m.status == UNMEASURED for m in measured)
    assert "fresh-process screen failed" in measured[0].reasons[0]


def test_a_signal_the_fresh_theory_lacks_is_unmeasured():
    extra = Signal("extra", "elegance", "live", "screen",
                   lambda ctx: Measurement("extra", count=0))
    result = screen(tiny.make_theory(), [tiny.cfg("a", "high")],
                    signals=[tiny.MODE_LIVE, extra],
                    theory_ref=tiny.theory_ref())
    by = result.by_signal(tiny.cfg("a", "high").digest)
    assert by["mode_live"].status == MEASURED
    assert by["extra"].status == UNMEASURED
    assert "not provided" in by["extra"].reasons[0]


def test_batches_split_groups_to_keep_jobs_busy():
    theory = tiny.make_theory()
    plan = build_plan(theory, tiny.all_cfgs())
    assert [len(c) for _, c in screen_mod._batches(plan, 1)] == [3, 3]
    assert [len(c) for _, c in screen_mod._batches(plan, 4)] == [2, 1, 2, 1]
    assert [len(c) for _, c in screen_mod._batches(plan, 64)] == [1] * 6


def test_load_theory_accepts_an_instance_or_a_factory():
    assert load_theory(tiny.theory_ref()).id == tiny.THEORY_ID
    tiny.INSTANCE_2C = tiny.make_theory()
    try:
        assert load_theory(tiny.theory_ref("INSTANCE_2C")) is tiny.INSTANCE_2C
    finally:
        del tiny.INSTANCE_2C
    with pytest.raises(ValueError):
        load_theory("no_colon")
    with pytest.raises(TypeError):
        load_theory(tiny.theory_ref("all_cfgs"))
