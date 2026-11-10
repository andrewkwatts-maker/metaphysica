"""L7 validation-data: the published report text and counts come from rows."""
import inspect
import json
from pathlib import Path

import pytest

from metaphysica.generators import headline_stats as hs
from metaphysica.simulations.PM.validation import statistical_rigor_validator as srv

ROOT = Path(__file__).resolve().parents[2] / "src" / "metaphysica"


def _validator(tmp_path):
    rows = [
        {"path": "gauge.a", "value": 1.2, "experimental_value": 1.0,
         "experimental_uncertainty": 0.1, "verdict": "FAIL",
         "registry_status": "DERIVED", "bound_type": "measured", "sigma": 2.0},
        {"path": "ckm.fit", "value": 1.0, "experimental_value": 1.0,
         "experimental_uncertainty": 0.1, "verdict": "PASS",
         "registry_status": "FITTED", "bound_type": "measured", "sigma": 0.0},
        {"path": "geometry.alpha_inverse", "value": 2.0, "experimental_value": 1.0,
         "experimental_uncertainty": 0.5, "verdict": "FAIL",
         "registry_status": "GEOMETRIC", "bound_type": "measured", "sigma": 2.0},
        {"path": "electromagnetic.alpha_inv", "value": 2.0, "experimental_value": 1.0,
         "experimental_uncertainty": 0.5, "verdict": "FAIL",
         "registry_status": "GEOMETRIC", "bound_type": "measured", "sigma": 2.0},
    ]
    f = tmp_path / "validation_report.json"
    f.write_text(json.dumps({"validations": rows}), encoding="utf-8")
    return srv.StatisticalRigorValidator(str(f))


def test_fit_excludes_fitted_rows_and_duplicates(tmp_path):
    v = _validator(tmp_path)
    assert v.dof_claimed == 2
    assert v.chi_sq == pytest.approx(4.0 + 4.0)
    rep = v.generate_report()
    assert rep["summary"]["n_scored"] == 2 and rep["summary"]["n_duplicates"] == 1
    assert rep["summary"]["n_non_predictions"] == 1


def test_report_has_no_jacobian_rank_or_deprecated_theory_block(tmp_path):
    rep = _validator(tmp_path).generate_report()
    text = json.dumps(rep)
    for key in ("jacobian_analysis", "effective_rank", "peer_review_response",
                "theory_uncertainty_correction_deprecated",
                "full_dimensional_independence", "appropriate fit quality"):
        assert key not in text
    assert not hasattr(srv.StatisticalRigorValidator, "generate_jacobian_matrix")
    assert not hasattr(srv.StatisticalRigorValidator,
                       "recalculate_with_theory_uncertainty")


def test_edof_text_carries_no_off_path_formula():
    src = inspect.getsource(srv)
    for stale in ("6 x b3", "6×b₃", "b₃/2 + 1/φ²", "k_gimel = b3/2 + 1/phi^2"):
        assert stale not in src


def test_edof_is_labelled_ansatz(tmp_path):
    rep = _validator(tmp_path).generate_report()
    assert rep["edof_analysis"]["effective_dof_is_ansatz"] is True
    assert "ANSATZ" in rep["edof_analysis"]["justification"]


def test_no_stale_headline_literals_in_owned_files():
    files = [ROOT / "simulations/PM/validation/statistical_rigor_validator.py",
             ROOT / "generators/headline_stats.py",
             ROOT / "generators/generate_statistics.py",
             ROOT / "generators/generate_72_certificates.py"]
    for f in files:
        text = f.read_text(encoding="utf-8")
        for lit in ("126,748", "126748", "2,239,16", "5032", "42/42"):
            assert lit not in text, (f.name, lit)


def _certs():
    spec = [("1", "COMPUTED_PASS", "VERIFIED"), ("2", "COMPUTED_PASS", "VERIFIED"),
            ("3", "COMPUTED_FAIL", "VERIFIED"), ("4", None, "VERIFIED"),
            ("5", None, "PENDING_LOCK"), ("6", None, "NOT_TESTABLE"),
            ("7", "NOT_APPLICABLE", "VERIFIED")]
    return [{"gate_id": g, "evaluation_status": e, "verification_status": s}
            for g, e, s in spec]


def test_gate_summary_separates_executed_from_declarative():
    s = hs.gate_summary(_certs())
    assert s == {"total": 6, "axiom": 1, "testable": 5, "executed_pass": 2,
                 "executed_fail": 1, "declarative": 2, "open": 1}
    t = hs.tally_gates(_certs())
    assert (t["locked"], t["open"], t["not_run"]) == (2, 1, 2)


def test_fit_reader_raises_on_missing_keys():
    with pytest.raises(KeyError):
        hs._fit({})
    with pytest.raises(KeyError):
        hs._fit({"chi_squared_from_rows": {"all_scoring_rows": {}},
                 "edof_analysis": {}, "summary": {"status": "POOR_FIT",
                              "p_value_n_dof": 0.0}})


def test_statistics_success_counts_use_the_scored_rows():
    from metaphysica.generators import generate_statistics as gs
    rep = {"chi_squared_from_rows": {"scored_rows": [
        {"path": "a", "sigma": 0.5}, {"path": "b", "sigma": 3.0}]}}
    sig = gs.extract_sigma_deviations_from_statistical_report(rep)
    stats = gs.compute_statistics(sig)
    assert stats["total_predictions"] == 2 and stats["within_2sigma"] == 1
