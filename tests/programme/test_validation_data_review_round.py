"""L7 validation-data repair round: defects found by review."""
import inspect
import json
import pytest

from metaphysica.generators import headline_stats as hs
from metaphysica.simulations.PM.validation import observables, statistical_rigor_validator as srv
from metaphysica.simulations.data.experimental_data_loader import ExperimentalValue
from metaphysica.simulations.validation import fit_partition as fp

SCORING = {"PASS", "MARGINAL", "TENSION", "FAIL"}


def _row(path, pred, exp, unc, reg="DERIVED"):
    return {"path": path, "status": "FAIL", "registry_status": reg,
            "predicted_value": pred, "experimental_value": exp,
            "uncertainty": unc, "sigma": abs(pred - exp) / unc,
            "comparable": True}


def test_falsified_candidates_are_not_grouped_as_duplicates():
    rows = [_row("ckm.V_us", 0.22, 0.2243, 0.0005),
            _row("algebra.gaugino_cabibbo_derived", 0.3, 0.2243, 0.0005, "FALSIFIED"),
            _row("neutrino.theta_13_pred", 8.5, 8.6, 0.1),
            _row("neutrino.theta13_derived", 12.0, 8.6, 0.1, "FALSIFIED")]
    p = observables.partition_rows(rows, SCORING)
    paths = {r["path"] for r in p["scored"]}
    assert {"algebra.gaugino_cabibbo_derived", "neutrino.theta13_derived"} <= paths
    s = fp.fit_summary(p["scored"])
    assert s["all_scoring_rows"]["chi_squared"] > s["excluding_falsified"]["chi_squared"]
    assert {w["path"] for w in s["withdrawn_rows"]} == {
        "algebra.gaugino_cabibbo_derived", "neutrino.theta13_derived"}


def test_no_constraints_count_literal_in_statistics():
    from metaphysica.generators import generate_statistics as gs
    assert '"constraints_count"' not in inspect.getsource(gs)


def test_unexecuted_gates_are_not_run_not_locked():
    certs = [{"gate_id": "1", "evaluation_status": "COMPUTED_PASS"},
             {"gate_id": "2", "verification_status": "VERIFIED"},
             {"gate_id": "3", "verification_status": "PENDING_LOCK"}]
    t = hs.tally_gates(certs)
    assert (t["locked"], t["open"], t["not_run"]) == (1, 0, 2)


def test_g79_has_no_import_fallback_that_locks():
    from metaphysica.simulations.PM.validation.certificate_gates import g79_g80
    src = inspect.getsource(g79_g80)
    g79 = src[src.index("def cert_g79"):src.index("def cert_g80")]
    assert "except ImportError" not in g79


def test_gates_have_no_default_for_missing_registry_keys():
    from metaphysica.simulations.PM.validation.certificate_gates import core, cosmo, lattice
    for mod in (core, cosmo, lattice):
        src = inspect.getsource(mod)
        assert "elder_kads', 24)" not in src and "sum_m_nu_upper', 0.12" not in src
    from metaphysica.simulations.PM.validation.CERTIFICATES import PrincipiaValidator
    stub = object.__new__(PrincipiaValidator)
    stub.reg = {}
    with pytest.raises(KeyError):
        stub._require_param("geometry.elder_kads")


def test_asymmetric_error_is_taken_on_the_prediction_side():
    ev = ExperimentalValue(-0.86, 0.215, "", "t", uncertainty_plus=0.23,
                           uncertainty_minus=0.20)
    from metaphysica.simulations.PM.cosmology.dark_energy_thawing import (
        DarkEnergyEvolution as T)
    # w0wa scoring reads the loader's row: wa above centre -> plus error.
    assert ev.uncertainty_toward(-0.5) == 0.23
    assert ev.uncertainty_toward(-1.2) == 0.20
    assert hasattr(T, "_desi_uncertainty_toward")
    assert T._desi_uncertainty_toward("wa", -0.5) == pytest.approx(0.23)
    assert T._desi_uncertainty_toward("wa", -1.5) == pytest.approx(0.20)


def _validator(tmp_path):
    rows = [{"path": "gauge.a", "value": 5.0, "experimental_value": 1.0,
             "experimental_uncertainty": 0.1, "verdict": "FAIL",
             "registry_status": "DERIVED", "bound_type": "measured", "sigma": 40.0}]
    f = tmp_path / "validation_report.json"
    f.write_text(json.dumps({"validations": rows}), encoding="utf-8")
    return srv.StatisticalRigorValidator(str(f))


def test_headline_verdict_is_not_the_edof_ansatz(tmp_path):
    rep = _validator(tmp_path).generate_report()
    s = rep["summary"]
    assert s["status"] == "POOR_FIT" and s["status_edof_ansatz"] == rep["edof_analysis"]["status"]
    assert "row-count" in s["status_basis"]
    # A fit that is POOR on N rows must not borrow the EDOF=3 reading.
    assert hs._fit(rep)["verdict"] == s["status"]
