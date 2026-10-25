"""The prose's path comparison reads one committed snapshot, never autogen_dir.

FOUND 2026-10-25: core_text read ``autogen_dir()/paths``. A path run writes to
a fresh output directory with no ``paths/``, so its abstract, introduction and
~30 superseded-path callouts printed OPEN where main printed figures, and
every path would have differed from main in those sections.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json

import pytest

from metaphysica.simulations.PM.paper import core_text, path_snapshot


def _summary(passed, failed, chi2):
    return {"scoreboard": {"PASS": passed, "FAIL": failed},
            "chi2": {"value": chi2, "dof": 4}}


def _paths_dir(tmp_path):
    d = tmp_path / "paths"
    (d / "main").mkdir(parents=True)
    (d / "b3_seed--seed_24").mkdir()
    (d / "index.json").write_text(json.dumps(
        {"engine": {"commit": "abc"}, "generated": "t0"}), encoding="utf-8")
    (d / "main" / "summary.json").write_text(
        json.dumps(_summary(1, 2, 30.0)), encoding="utf-8")
    (d / "b3_seed--seed_24" / "summary.json").write_text(
        json.dumps(_summary(3, 1, 10.0)), encoding="utf-8")
    return d


def test_snapshot_round_trips_and_records_its_sweep(tmp_path):
    snap = tmp_path / "snap.json"
    path_snapshot.write(_paths_dir(tmp_path), snap)
    data = json.loads(snap.read_text(encoding="utf-8"))
    assert data["engine"] == {"commit": "abc"} and data["generated"] == "t0"
    assert path_snapshot.load("b3_seed--seed_24", snap)["chi2"]["value"] == 10.0


def test_build_fails_early_without_a_summary(tmp_path):
    d = _paths_dir(tmp_path)
    (d / "main" / "summary.json").unlink()
    with pytest.raises(FileNotFoundError):
        path_snapshot.build(d)


def test_missing_snapshot_reads_as_none(tmp_path):
    assert path_snapshot.load("main", tmp_path / "absent.json") is None


def test_prose_ignores_the_output_directory(tmp_path, monkeypatch):
    """An empty output dir (a path run) must not change the comparison."""
    before = core_text._path_summary("main")
    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    assert core_text._path_summary("main") == before
    assert before == path_snapshot.load("main")
