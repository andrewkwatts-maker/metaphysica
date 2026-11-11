"""XB-02: the two statistics passes of the build.

The pre-rigor pass ("Build validation statistics", --pre-rigor) gives gate
counts only and never opens a rigor report; the default pass ("Refresh
validation statistics from this build's rigor report") requires that report.
Every test writes only into tmp_path.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from metaphysica.generators import generate_statistics as gs
from metaphysica.generators import headline_stats as hs

SRC = Path(gs.__file__).resolve().parents[1]
FIT = {"chi_squared": "chi_squared", "chi_squared_rows": "rows",
       "degrees_of_freedom": "dof", "p_value": "p_value", "status": "verdict"}
CERTS = {"certificates": [
    {"gate_id": "1", "evaluation_status": "COMPUTED_PASS"},
    {"gate_id": "2", "evaluation_status": "COMPUTED_FAIL"},
    {"gate_id": "3", "verification_status": "PENDING_LOCK"}]}
REPORT = {
    "chi_squared_from_rows": {
        "scored_rows": [{"path": "a", "sigma": 0.5}, {"path": "b", "sigma": 3.0}],
        "all_scoring_rows": {"chi_squared": 9.25, "n": 2}},
    "edof_analysis": {"effective_dof": 3, "effective_dof_is_ansatz": True,
                      "p_value": 0.026},
    "summary": {"status": "POOR_FIT", "p_value": 0.0098, "p_value_n_dof": 0.0098}}


def _setup(tmp_path, monkeypatch, report=None):
    """Point every path of the generator at tmp_path; write certs (and a report)."""
    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    certs, rigor = tmp_path / "GATES_CERTIFICATES.json", tmp_path / "statistical_rigor_report.json"
    certs.write_text(json.dumps(CERTS), encoding="utf-8")
    if report is not None:
        rigor.write_text(json.dumps(report), encoding="utf-8")
    monkeypatch.setattr(gs, "GATES_CERT_FILE", str(certs))
    monkeypatch.setattr(gs, "STATISTICAL_RIGOR_FILE", str(rigor))
    monkeypatch.setattr(gs, "PARAMETERS_FILE", str(tmp_path / "parameters.json"))
    monkeypatch.setattr(gs, "_free_variable_count", lambda: 0)


def _assert_fit_not_available(stats):
    fs = stats["framework_statistics"]
    for key in FIT:
        assert fs[key] == hs.NOT_AVAILABLE, key
    assert stats["validation"]["total_predictions"] == hs.NOT_AVAILABLE
    assert stats["validation"]["success_rate"] == hs.NOT_AVAILABLE
    assert fs["total_gates"] == 3 and fs["pass_count"] == 1


def test_pre_rigor_without_report_gives_gate_counts(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    _assert_fit_not_available(gs.generate_statistics(pre_rigor=True))


def test_pre_rigor_ignores_a_report_that_is_present(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, report=REPORT)
    _assert_fit_not_available(gs.generate_statistics(pre_rigor=True))


def test_pre_rigor_headline_never_opens_the_rigor_report(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, report=REPORT)
    h = hs.pre_rigor_headline(tmp_path / "GATES_CERTIFICATES.json")
    assert all(h[key] == hs.NOT_AVAILABLE for key in hs.FIT_KEYS)
    assert h["gates_total"] == 3


def test_default_pass_without_report_raises(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    with pytest.raises(FileNotFoundError, match="statistical_rigor_report.json"):
        gs.generate_statistics()


def test_default_pass_reads_the_fit_from_the_report(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, report=REPORT)
    stats = gs.generate_statistics()
    fs, vs = stats["framework_statistics"], stats["validation"]
    assert (fs["chi_squared"], fs["chi_squared_rows"]) == (9.25, 2)
    assert (fs["degrees_of_freedom"], fs["p_value"], fs["status"]) == (2, 0.0098, "POOR_FIT")
    assert (vs["total_predictions"], vs["within_2sigma"]) == (2, 1)


def test_load_json_file_raises_on_missing_and_bad_files(tmp_path):
    with pytest.raises(FileNotFoundError, match="nope.json"):
        gs.load_json_file(str(tmp_path / "nope.json"))
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="bad.json"):
        gs.load_json_file(str(bad))


def test_four_source_fallback_is_gone():
    for name in ("extract_sigma_deviations_from_gates",
                 "extract_sigma_deviations_from_param_certs",
                 "extract_sigma_deviations_from_parameters"):
        assert not hasattr(gs, name), name


def test_build_runs_the_first_pass_with_pre_rigor():
    import importlib
    steps = importlib.import_module("metaphysica.build").STEPS
    cmds = {name: cmd for name, cmd, _ in steps}
    assert cmds["Build validation statistics"][-1] == "--pre-rigor"
    refresh = cmds["Refresh validation statistics from this build's rigor report"]
    assert "--pre-rigor" not in refresh


def test_runner_no_longer_calls_generate_statistics():
    text = (SRC / "simulations" / "run_all_simulations.py").read_text(encoding="utf-8")
    assert "generate_statistics" not in text
