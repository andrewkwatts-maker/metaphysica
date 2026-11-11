"""XB-08: the pre-rigor pass registers its unavailable rows as NOT_EVALUABLE.

Before the fix every parameters.json row written by generate_statistics carried
status COMPUTED, including rows whose value is "not available in this build".
Every test writes only into tmp_path.
"""
from __future__ import annotations

import json

from metaphysica.generators import generate_statistics as gs
from metaphysica.generators import headline_stats as hs

CERTS = {"certificates": [
    {"gate_id": "1", "evaluation_status": "COMPUTED_PASS"},
    {"gate_id": "2", "evaluation_status": "COMPUTED_FAIL"},
    {"gate_id": "3", "verification_status": "PENDING_LOCK"}]}


def _pre_rigor_rows(tmp_path, monkeypatch):
    """Run the pre-rigor pass against tmp_path and return the written rows."""
    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    certs = tmp_path / "GATES_CERTIFICATES.json"
    certs.write_text(json.dumps(CERTS), encoding="utf-8")
    params = tmp_path / "parameters.json"
    params.write_text(json.dumps({"parameters": {}}), encoding="utf-8")
    monkeypatch.setattr(gs, "GATES_CERT_FILE", str(certs))
    monkeypatch.setattr(gs, "STATISTICAL_RIGOR_FILE", str(tmp_path / "absent.json"))
    monkeypatch.setattr(gs, "PARAMETERS_FILE", str(params))
    monkeypatch.setattr(gs, "_free_variable_count", lambda: 0)
    gs.generate_statistics(pre_rigor=True)
    return json.loads(params.read_text(encoding="utf-8"))["parameters"]


def test_unavailable_pre_rigor_rows_are_not_evaluable(tmp_path, monkeypatch):
    rows = _pre_rigor_rows(tmp_path, monkeypatch)
    for key in ("validation.total_predictions", "validation.success_rate",
                "framework_statistics.chi_squared", "framework_statistics.p_value"):
        assert rows[key]["value"] == hs.NOT_AVAILABLE, key
        assert rows[key]["status"] == "NOT_EVALUABLE", key
        assert rows[key]["note"], key


def test_no_row_claims_computed_without_a_value(tmp_path, monkeypatch):
    rows = _pre_rigor_rows(tmp_path, monkeypatch)
    computed = [k for k, r in rows.items()
                if r["status"] == "COMPUTED" and r["value"] == hs.NOT_AVAILABLE]
    assert computed == []


def test_gate_counts_stay_computed(tmp_path, monkeypatch):
    rows = _pre_rigor_rows(tmp_path, monkeypatch)
    for key in ("framework_statistics.total_gates", "framework_statistics.pass_count"):
        assert rows[key]["status"] == "COMPUTED", key
    assert rows["framework_statistics.total_gates"]["value"] == 3
