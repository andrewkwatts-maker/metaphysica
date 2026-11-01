"""headline_statistics reads one source and never invents a value."""
import json

import pytest

from metaphysica.generators.headline_stats import headline_statistics


def _write(tmp_path, certs, rigor):
    (tmp_path / "g.json").write_text(json.dumps({"certificates": certs}))
    (tmp_path / "r.json").write_text(json.dumps(rigor))
    return tmp_path / "r.json", tmp_path / "g.json"


def test_tally_skips_not_applicable_and_reports_open(tmp_path):
    certs = [
        {"gate_id": "1", "evaluation_status": "COMPUTED_PASS"},
        {"gate_id": "2", "evaluation_status": "COMPUTED_FAIL"},
        {"gate_id": "3", "verification_status": "NOT_TESTABLE"},
        {"gate_id": "4", "evaluation_status": "NOT_APPLICABLE",
         "verification_status": "VERIFIED"},
    ]
    rigor = {"chi_squared_from_rows": {"all_scoring_rows": {"chi_squared": 9.0, "n": 5}},
             "edof_analysis": {"effective_dof": 3, "p_value": 0.0, "status": "POOR_FIT"}}
    h = headline_statistics(*_write(tmp_path, certs, rigor))
    assert (h["gates_total"], h["gates_locked"], h["gates_open"]) == (3, 1, 1)
    assert h["gates_open_ids"] == ["2"] and h["verdict"] == "POOR_FIT"
    assert h["formulas_checked_ok"] is None and "formulas_checked_ok" in h["missing"]


def test_missing_artifact_fails_early(tmp_path):
    with pytest.raises(FileNotFoundError):
        headline_statistics(tmp_path / "no.json", tmp_path / "no2.json")


def test_appendix_f_text_has_no_stale_literals():
    """Appendix F gate text is generated, not the old hard-coded tally."""
    import inspect
    from metaphysica.simulations.PM.paper.appendices import appendix_f_72gates as a
    src = inspect.getsource(a)
    assert "41 of 43" not in src and "126,748.86" not in src
    assert set(a._gate_text()) >= {"locked", "testable", "open_ids", "chi2"}
