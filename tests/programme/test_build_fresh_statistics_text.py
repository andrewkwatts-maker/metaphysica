"""XB-09: generate_statistics text says what the code computes, and every
zero or empty fallback for "no scored rows" raises instead of answering."""

import inspect
import json

import pytest

from metaphysica.generators import generate_statistics as gs


@pytest.mark.parametrize("report", [
    {},
    None,
    {"chi_squared_from_rows": {}},
    {"chi_squared_from_rows": {"scored_rows": []}},
])
def test_extractor_raises_without_scored_rows(report):
    with pytest.raises(ValueError, match="no scored rows"):
        gs.extract_sigma_deviations_from_statistical_report(report)


def test_collect_sigmas_raises_without_scored_rows():
    with pytest.raises(ValueError, match="no scored rows"):
        gs._collect_sigmas({"chi_squared_from_rows": {"scored_rows": []}})


def test_compute_statistics_raises_on_empty_sigmas():
    with pytest.raises(ValueError, match="no scored rows"):
        gs.compute_statistics([])


def test_success_rate_raises_on_zero_total():
    with pytest.raises(ValueError, match="no scored rows"):
        gs._success_rate({"total_predictions": 0, "within_2sigma": 0})


def test_success_rate_still_computes_and_passes_not_available():
    assert gs._success_rate({"total_predictions": 4, "within_2sigma": 3}) == "75.0%"
    assert gs._success_rate({"total_predictions": gs.NOT_AVAILABLE,
                             "within_2sigma": gs.NOT_AVAILABLE}) == gs.NOT_AVAILABLE


def test_compute_statistics_returns_only_the_counts_statistics_json_carries():
    stats = gs.compute_statistics([0.5, 3.0, 0.0, -1.5])
    assert stats == {"within_1sigma": 2, "within_2sigma": 3,
                     "exact_matches": 1, "total_predictions": 4}


def test_statistics_json_fit_keys_come_only_from_the_headline(tmp_path, monkeypatch):
    rigor = tmp_path / "statistical_rigor_report.json"
    rigor.write_text(json.dumps({
        "chi_squared_from_rows": {
            "scored_rows": [{"sigma": 0.5}, {"sigma": 3.0}],
            "all_scoring_rows": {"chi_squared": 9.25, "n": 2}},
        "summary": {"p_value_n_dof": 0.01, "status": "POOR_FIT"}}), encoding="utf-8")
    certs = tmp_path / "GATES_CERTIFICATES.json"
    certs.write_text(json.dumps({"certificates": []}), encoding="utf-8")
    monkeypatch.setattr(gs, "STATISTICAL_RIGOR_FILE", str(rigor))
    monkeypatch.setattr(gs, "GATES_CERT_FILE", str(certs))
    monkeypatch.setattr(gs, "PARAMETERS_FILE", str(tmp_path / "absent.json"))
    monkeypatch.setattr(gs, "_free_variable_count", lambda: 0)
    doc = gs.generate_statistics()
    fs = doc["framework_statistics"]
    assert (fs["chi_squared"], fs["chi_squared_rows"], fs["degrees_of_freedom"]) == (9.25, 2, 2)
    assert fs["degrees_of_freedom_is_ansatz"] is False and fs["p_value"] == 0.01
    for section in (fs, doc["validation"]):
        assert not {"chi_squared_reduced", "high_sigma_count", "note"} & set(section)
    assert "degrees_of_freedom" not in doc["validation"]


def test_text_names_no_retired_source_or_gate_dof():
    module_text = inspect.getsource(gs)
    assert "CERTIFICATES_v16_2_FINAL" not in module_text
    assert "verified gates - fitted parameters" not in gs.__doc__
    assert "effective_dof" not in gs.__doc__
    assert "all_scoring_rows n (the row count, not an ansatz" in gs.__doc__
    assert "p_value = summary.p_value_n_dof" in gs.__doc__
