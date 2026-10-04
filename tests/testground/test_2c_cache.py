"""Lane 2C: the run cache -- hit while the fingerprint holds, miss when it moves.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metaphysica.testground.runner import cache as cache_mod
from metaphysica.testground.runner.cache import (RESULT_NAME, RUNS_DIR_ENV,
                                                 RunCache, default_runs_dir)
from metaphysica.testground.runner.fingerprint import engine_fingerprint
from metaphysica.testground.runner.isolation import STAMP_NAME, prepare_root
from tests.testground import test_2c_support as tiny


def _engine(tmp_path):
    src = tmp_path / "engine_src"
    src.mkdir()
    (src / "physics.py").write_text("ALPHA = 1\n", encoding="utf-8")
    return src


def _store(cache, base, fp, payload=None):
    theory, cfg = tiny.make_theory(), tiny.cfg()
    prepare_root(base, theory, cfg, fp)
    cache.put(theory.id, cfg.digest, fp, payload or {"status": "COMPLETED"})
    return cfg


def test_hit_on_an_unchanged_fingerprint_and_miss_when_it_changes(tmp_path):
    src = _engine(tmp_path)
    runs = tmp_path / "runs"
    cache = RunCache(runs)
    fp1 = engine_fingerprint([src])
    cfg = _store(cache, runs, fp1, {"status": "COMPLETED", "n": 1})
    assert engine_fingerprint([src]) == fp1
    assert cache.get("tiny", cfg.digest, fp1) == {"status": "COMPLETED", "n": 1}
    (src / "physics.py").write_text("ALPHA = 2\n", encoding="utf-8")
    fp2 = engine_fingerprint([src])
    assert fp2 != fp1
    assert cache.get("tiny", cfg.digest, fp2) is None
    assert cache.stats() == {"hits": 1, "misses": 1}


def test_invalidate_removes_every_other_fingerprint(tmp_path):
    cache = RunCache(tmp_path)
    cfg = _store(cache, tmp_path, "aaaaaaaaaaaaaaaa")
    _store(cache, tmp_path, "bbbbbbbbbbbbbbbb")
    (tmp_path / "tiny" / ".tmp-ignored").mkdir()
    assert cache.fingerprints("tiny") == ["aaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb"]
    assert cache.stale_fingerprints("tiny", "bbbbbbbbbbbbbbbb") == [
        "aaaaaaaaaaaaaaaa"]
    removed = cache.invalidate("tiny", "bbbbbbbbbbbbbbbb")
    assert [p.name for p in removed] == ["aaaaaaaaaaaaaaaa"]
    assert cache.get("tiny", cfg.digest, "aaaaaaaaaaaaaaaa") is None
    assert cache.get("tiny", cfg.digest, "bbbbbbbbbbbbbbbb") is not None
    assert cache.fingerprints("nobody") == []


def test_a_result_needs_a_matching_stamp(tmp_path):
    cache = RunCache(tmp_path)
    with pytest.raises(ValueError, match="refusing to cache"):
        cache.put("tiny", tiny.cfg().digest, "aaaaaaaaaaaaaaaa", {})
    cfg = _store(cache, tmp_path, "aaaaaaaaaaaaaaaa")
    root = cache.root("tiny", cfg.digest, "aaaaaaaaaaaaaaaa")
    stamp = json.loads((root / STAMP_NAME).read_text())
    stamp["engine_fingerprint"] = "cccccccccccccccc"
    (root / STAMP_NAME).write_text(json.dumps(stamp))
    assert cache.get("tiny", cfg.digest, "aaaaaaaaaaaaaaaa") is None


@pytest.mark.parametrize("content", [
    "{broken", "[1]",
    json.dumps({"theory": "tiny", "digest": "x", "fingerprint": "y",
                "payload": {}}),
    json.dumps({"theory": "tiny", "payload": "not a dict"}),
])
def test_corrupt_or_foreign_results_are_misses(tmp_path, content):
    cache = RunCache(tmp_path)
    cfg = _store(cache, tmp_path, "aaaaaaaaaaaaaaaa")
    root = cache.root("tiny", cfg.digest, "aaaaaaaaaaaaaaaa")
    (root / RESULT_NAME).write_text(content)
    assert cache.get("tiny", cfg.digest, "aaaaaaaaaaaaaaaa") is None


def test_the_default_base_is_the_repo_runs_dir_or_the_override(
        tmp_path, monkeypatch):
    monkeypatch.delenv(RUNS_DIR_ENV, raising=False)
    repo = Path(cache_mod.__file__).resolve().parents[4]
    assert default_runs_dir() == repo / ".runs"
    assert RunCache().base_dir == repo / ".runs"
    monkeypatch.setenv(RUNS_DIR_ENV, str(tmp_path / "elsewhere"))
    assert default_runs_dir() == tmp_path / "elsewhere"


def test_without_a_repo_the_default_is_the_working_directory(
        tmp_path, monkeypatch):
    monkeypatch.delenv(RUNS_DIR_ENV, raising=False)
    fake = tmp_path / "a" / "b" / "c" / "d" / "e" / "cache.py"
    monkeypatch.setattr(cache_mod, "__file__", str(fake))
    monkeypatch.chdir(tmp_path)
    assert default_runs_dir() == tmp_path / ".runs"
