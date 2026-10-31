"""`testground rank`: lexicographic order, tie-break, reasonable, missing (toy theory).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json

import pytest

from metaphysica.testground import cli
from metaphysica.testground.rank import (REASONABLE_DELTA_CHI2, RankEntry,
                                         load_entries, rank_entries,
                                         validate_ranking)
from metaphysica.testground.theory import RunReading
from metaphysica.theories.toy import THEORY, model


def _e(pid, **kw):
    base = dict(consistent=True, ladder_failed=0, ladder_total=2,
                gates_failed=0, gates_applicable=2, chi2=1.0, dof=2)
    base.update(kw)
    return RankEntry(pid, {} if pid == "sel" else {"f": pid}, RunReading(**base))


def _ids(doc):
    return [r["path_id"] for r in doc["rows"]]


def test_tiers_are_lexicographic_not_summed():
    entries = [_e("sel", chi2=50.0),
               _e("fits_best_but_inconsistent", consistent=False, chi2=0.0),
               _e("ladder_fail", ladder_failed=1, chi2=0.0),
               _e("gate_fail", gates_failed=1, chi2=0.0),
               _e("clean", chi2=9.0)]
    doc = rank_entries(entries, "sel")
    assert _ids(doc) == ["clean", "sel", "gate_fail", "ladder_fail",
                         "fits_best_but_inconsistent"]
    assert [r["rank"] for r in doc["rows"]] == [1, 2, 3, 4, 5]


def test_chi2_breaks_a_tie_and_equal_keys_share_a_rank():
    doc = rank_entries([_e("sel", chi2=3.0), _e("lower", chi2=2.0),
                        _e("same", chi2=3.0)], "sel")
    assert _ids(doc)[0] == "lower"
    ranks = {r["path_id"]: r["rank"] for r in doc["rows"]}
    assert ranks == {"lower": 1, "same": 2, "sel": 2}


def test_reasonable_needs_consistency_ladder_and_delta_chi2():
    far = 1.0 + REASONABLE_DELTA_CHI2 + 0.5
    doc = rank_entries([_e("sel", ladder_failed=1), _e("ok"),
                        _e("edge", chi2=1.0 + REASONABLE_DELTA_CHI2),
                        _e("too_far", chi2=far),
                        _e("worse_ladder", ladder_failed=2),
                        _e("inconsistent", consistent=False)], "sel")
    flags = {r["path_id"]: r["reasonable"] for r in doc["rows"]}
    assert flags == {"sel": True, "ok": True, "edge": True, "too_far": False,
                     "worse_ladder": False, "inconsistent": False}
    assert {r["path_id"]: r["delta_chi2"] for r in doc["rows"]}["ok"] == 0.0


def test_missing_input_sorts_last_and_is_never_filled_in():
    gap = RankEntry("gap", {"f": "gap"}, RunReading(
        consistent=True, ladder_failed=0, gates_failed=None, chi2=None,
        missing=("validation_report.json", "parameters.json")))
    doc = rank_entries([_e("sel", gates_failed=5, chi2=99.0), gap], "sel")
    row = next(r for r in doc["rows"] if r["path_id"] == "gap")
    assert _ids(doc) == ["sel", "gap"]
    assert row["chi2"] is None and row["gates_failed"] is None
    assert row["delta_chi2"] is None and row["reasonable"] is False
    assert row["missing"] == ["parameters.json", "validation_report.json"]


def test_unknown_consistency_is_not_claimed_either_way():
    doc = rank_entries([_e("sel"), _e("unknown", consistent=None)], "sel")
    row = next(r for r in doc["rows"] if r["path_id"] == "unknown")
    assert row["consistent"] is None and row["reasonable"] is False


def test_selected_must_be_a_finished_run():
    with pytest.raises(ValueError):
        rank_entries([_e("a")], "sel")


def test_validate_flags_a_broken_document():
    doc = rank_entries([_e("sel")], "sel")
    assert validate_ranking(doc) == []
    del doc["rows"][0]["chi2"]
    doc["searched"] = 7
    assert len(validate_ranking(doc)) == 2


def _finish(base, name, selection):
    root = base / name
    root.mkdir(parents=True)
    model.write_artifact(root, {**THEORY.selections.active().mapping, **selection})
    (root / "configuration.json").write_text(json.dumps(
        {"selection": selection}), encoding="utf-8")
    (root / "run_log.json").write_text(json.dumps({"status": "COMPLETED"}),
                                       encoding="utf-8")


def test_toy_runs_rank_through_the_cli(tmp_path):
    fp = tmp_path / "runs" / "toy" / "fp1"
    _finish(fp, "d0", {})
    _finish(fp, "d1", {"matching": "tree"})            # breaks the Ward identity
    _finish(fp, "d2", {"mass_rule": "dirac_only"})     # tachyonic: inconsistent
    (fp / "unfinished").mkdir()
    out = tmp_path / "path_ranking.json"
    code = cli.main(["rank", "--runs-dir", str(tmp_path / "runs"),
                     "--out", str(out)], theory=THEORY)
    assert code == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert validate_ranking(doc) == []
    assert doc["searched"] == 3 and doc["selected"] == "d0"
    assert _ids(doc) == ["d0", "d1", "d2"]
    assert [r["consistent"] for r in doc["rows"]] == [True, True, False]
    assert doc["rows"][1]["ladder_failed"] == 1


def test_load_entries_skips_runs_without_a_finished_log(tmp_path):
    _finish(tmp_path, "done", {})
    (tmp_path / "done2").mkdir()
    (tmp_path / "done2" / "configuration.json").write_text(
        json.dumps({"selection": {}}), encoding="utf-8")
    assert [e.path_id for e in load_entries(THEORY, tmp_path)] == ["done"]


def test_two_fingerprints_need_a_choice(tmp_path):
    for fp in ("a", "b"):
        _finish(tmp_path / "runs" / "toy" / fp, "d0", {})
    code = cli.main(["rank", "--runs-dir", str(tmp_path / "runs"), "--out",
                     str(tmp_path / "o.json")], theory=THEORY)
    assert code != 0
    code = cli.main(["rank", "--runs-dir", str(tmp_path / "runs"),
                     "--fingerprint", "a", "--out", str(tmp_path / "o.json")],
                    theory=THEORY)
    assert code == 0
