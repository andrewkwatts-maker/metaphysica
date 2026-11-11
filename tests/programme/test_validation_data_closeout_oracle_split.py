"""XV-05: FalsificationOracle.evaluate_risk_profile split into functions of
60 lines or fewer, with the risk rows unchanged on every branch."""
import ast
import inspect
import textwrap

import pytest

from metaphysica.simulations.PM.validation import falsification_oracle as fo

THRESHOLDS = {
    "BabyIAXO_2025": {"coupling_limit_GeV_inv": 1e-11, "mass_range_eV": [1e-3, 1e-1]},
    "IAXO_2028": {"coupling_limit_GeV_inv": 1e-12},
    "CAST_current": {"coupling_limit_GeV_inv": 6.6e-11},
    "Eot_Wash_current": {"range_limit_m": 5e-5},
    "Hyper_K_2027": {"tau_p_limit_years": 1e35},
    "DUNE_2028": {"sterile_mixing_limit": 1e-3},
    "HL_LHC_2029": {"M_KK_limit_TeV": 10.0},
}
ROW_ORDER = ["ALP_Principia_Metric", "Fifth_Force", "Proton_Decay",
             "Sterile_Neutrino", "KK_Gravitons", "Cross_Pair_Bell"]


def _oracle(alp_mass=1e-2, alp_g=2e-11, ff=1e-6, tau=1e36, mix=1e-4, mkk=20.0):
    """Oracle with stub predictions and thresholds (no registry read)."""
    o = fo.FalsificationOracle.__new__(fo.FalsificationOracle)
    o.predictions = {
        "ALP_Principia_Metric": {"mass_eV": alp_mass, "coupling_g_agg_GeV_inv": alp_g},
        "fifth_force": {"range_lambda_m": ff},
        "proton_decay": {"tau_p_years": tau},
        "sterile_neutrino": {"mixing_angle_rad": mix},
        "kaluza_klein": {"M_KK_TeV": mkk},
        "cross_pair_bell": {"signature": "sig", "expected_if_false": "kill"},
    }
    o.exclusion_thresholds = THRESHOLDS
    return o


def _class_function_lengths():
    tree = ast.parse(textwrap.dedent(inspect.getsource(fo.FalsificationOracle)))
    return {n.name: n.end_lineno - n.lineno + 1 for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef)}


def test_evaluate_risk_profile_and_its_helpers_are_60_lines_or_fewer():
    lengths = _class_function_lengths()
    assert lengths["evaluate_risk_profile"] <= 60
    risk = {k: v for k, v in lengths.items() if "risk" in k or k.startswith("_alp")}
    assert all(v <= 60 for v in risk.values()), risk


def test_rows_come_in_the_published_order():
    assert list(_oracle().evaluate_risk_profile()) == ROW_ORDER


@pytest.mark.parametrize("mass, g, status, projected", [
    (1e-2, 1e-10, "EXCLUDED_BY_CURRENT_BOUND", "IMMINENT_TEST"),
    (1e-2, 2e-11, "IMMINENT_TEST", None),
    (1e-2, 5e-12, "TESTABLE", None),
    (1e-2, 1e-13, "MARGINAL", None),
    (1.0, 1e-10, "MARGINAL", None),
])
def test_alp_status_on_every_branch(mass, g, status, projected):
    row = _oracle(alp_mass=mass, alp_g=g).evaluate_risk_profile()["ALP_Principia_Metric"]
    assert row["status"] == status
    assert row.get("projected_sensitivity_status") == projected
    assert row["exceeds_current_helioscope_limit"] is (g >= 6.6e-11)
    assert ("current_limit_note" in row) is (g >= 6.6e-11)
    assert row["predicted_mass_meV"] == pytest.approx(mass * 1e3)


def test_alp_excluded_row_keeps_key_order():
    row = _oracle(alp_g=1e-10).evaluate_risk_profile()["ALP_Principia_Metric"]
    assert list(row)[:3] == ["status", "verdict", "falsification_risk"]
    assert list(row)[-4:] == ["current_helioscope_limit_GeV_inv",
                              "exceeds_current_helioscope_limit",
                              "projected_sensitivity_status", "current_limit_note"]
    assert row["falsification_risk"] == "EXCLUDED"


@pytest.mark.parametrize("kw, statuses", [
    (dict(ff=1e-4, tau=1e34, mix=1e-2, mkk=5.0),
     ("FALSIFIED", "IMMINENT_TEST", "TESTABLE", "TESTABLE")),
    (dict(ff=1e-6, tau=1e36, mix=1e-4, mkk=20.0),
     ("VIABLE", "SAFE", "MARGINAL", "SAFE")),
])
def test_other_rows_on_both_branches(kw, statuses):
    rp = _oracle(**kw).evaluate_risk_profile()
    names = ["Fifth_Force", "Proton_Decay", "Sterile_Neutrino", "KK_Gravitons"]
    assert tuple(rp[n]["status"] for n in names) == statuses
    assert list(rp["Fifth_Force"])[:3] == ["status", "verdict", "falsification_risk"]
    assert rp["Fifth_Force"]["margin"] == pytest.approx(kw["ff"] / 5e-5)
    assert rp["Proton_Decay"]["ratio"] == pytest.approx(kw["tau"] / 1e35)
    assert rp["KK_Gravitons"]["margin"] == pytest.approx(10.0 / kw["mkk"])
    assert rp["Cross_Pair_Bell"]["kill_condition"] == "kill"


def test_missing_threshold_raises():
    o = _oracle()
    o.exclusion_thresholds = {k: v for k, v in THRESHOLDS.items() if k != "CAST_current"}
    with pytest.raises(KeyError):
        o.evaluate_risk_profile()
