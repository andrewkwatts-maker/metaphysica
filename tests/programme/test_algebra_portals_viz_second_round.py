"""L6 algebra-portals-viz round 2: shielding, theta13 text, statuses, guards."""
import inspect
import re

import numpy as np
import pytest

from metaphysica.simulations.PM.algebra import (
    e7_representation as e7, e8x8_splitting as e8, gaugino_condensation as gc,
    clifford_unification as cu, leech_lattice, neutrino_algebraic as na, octonions)
from metaphysica.simulations.PM.consciousness import (
    four_dice_sampling as dice, orch_or_pair_shielding as shield)


def _sim(mod):
    return [v for v in vars(mod).values() if inspect.isclass(v)
            and v.__module__ == mod.__name__ and hasattr(v, "get_section_content")][0]()


def _params(mod):
    return {p.path: p for p in _sim(mod).get_output_param_definitions()}


def test_shielding_one_function_everywhere():
    assert shield.shielding_enhancement(12) == pytest.approx(48.73, abs=0.01)
    model = shield.PairShielding(12) if hasattr(shield, "PairShielding") else None
    sim = _sim(shield)
    cert = sim.get_certificates()[0]["condition"]
    assert "48.7" in cert
    text = str(sim.get_formulas()) + str(sim.get_output_param_definitions())
    assert "exp(k*sqrt(n_pairs))" not in text
    assert "(n/6)^2" in text
    if model is not None:
        assert model.compute_shielding_factor() == pytest.approx(
            shield.shielding_enhancement(12))


def test_neutrino_text_follows_value_not_one_sixth():
    sim = _sim(na)
    text = " ".join([str(sim.get_section_content().content_blocks),
                     str(sim.get_formulas()), str(sim.get_output_param_definitions()),
                     str(sim.get_certificates()), str(sim.validate_self())])
    for stale in ("9.59", "1/6 ", "= 1/√6", "= 1/sqrt(6)", "~9σ", "8.8 sigma"):
        assert stale not in text, stale
    v = na._derived_values()
    assert f"{v.theta13_deg:.2f}" in text
    assert v.alpha_leak == pytest.approx(0.5465, abs=1e-3)


def test_e7_normalisation_is_not_the_coupling_in_force():
    ps = _params(e7)
    row = ps["algebra.e7_alpha_leak"]
    assert row.status == "ANSATZ" and "geometry.alpha_leak" in row.description
    assert ps["algebra.e7_alp_mass_gev"].status == "ANSATZ"
    assert "not an ALP mass" in ps["algebra.e7_alp_mass_gev"].name
    assert _params(e8)["algebra.e8_portal_coupling"].status == "ANSATZ"


def test_gaugino_and_e8_condensate_rows_calibrated():
    ps = _params(gc)
    for k in ("W_np_1", "W_np_2", "lambda_eff", "racetrack_T_min", "condensate_ratio"):
        assert ps["algebra.gaugino_" + k].status == "CALIBRATED", k
    p8 = _params(e8)
    assert p8["algebra.e8_hidden_condensate"].status == "CALIBRATED"
    assert p8["algebra.e8_heterotic_spectral_proxy"].status == "CALIBRATED"


def test_clifford_self_tests_are_identity_rows():
    ps = _params(cu)
    for k in ("g2_invariant", "flrw_invariant", "rotation_check"):
        assert ps["algebra.clifford_" + k].status == "IDENTITY"


def test_dice_rows_are_ansatz():
    ps = _params(dice)
    assert ps["consciousness.dice_branches"].status == "ANSATZ"
    assert ps["consciousness.dice_entropy"].status == "ANSATZ"


def test_octonion_fork_read_does_not_swallow_errors():
    src = inspect.getsource(octonions)
    assert "except Exception" not in src.split("g2_form_convention")[1][:900]


def test_algebra_init_has_no_import_guard():
    import metaphysica.simulations.PM.algebra as pkg
    assert "except ImportError" not in inspect.getsource(pkg)


def test_leech_enumeration_has_no_working_out_left():
    src = inspect.getsource(leech_lattice)
    for fluff in ("let me", "nah", "Hmm", "No wait"):
        assert fluff not in src
