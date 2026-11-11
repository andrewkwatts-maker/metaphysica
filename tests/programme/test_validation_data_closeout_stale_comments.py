"""XV-13: stale comments and texts in the adversarial tester and the gate certificates."""
import inspect
import re

from metaphysica.generators import generate_72_certificates as g72
from metaphysica.simulations.PM.validation import adversarial_axiom_tester as aat


def test_bridge_norm_comment_states_b3_over_12():
    source = inspect.getsource(aat)
    assert "energy 2.0 per bridge" not in source
    assert "~√2" not in source
    assert "energy b3/12 per bridge" in source


def test_g12_wl_code_types_no_number():
    wl_code = g72.VERIFIABLE_GATES[12]["wl_code"]
    assert re.search(r"\d\.\d", wl_code) is None, wl_code
    assert "sin2_theta_W_pred" in wl_code


def test_mathematical_certificates_name_no_288_root_structure():
    for gate_id in g72.MATHEMATICAL_GATES:
        gate = {"id": gate_id, "name": f"G{gate_id}", "logic": "discrete spectrum"}
        cert = g72.create_certificate(gate, {})
        assert cert["verification_status"] == "MATHEMATICAL"
        assert "without a computational evaluation" in cert["note"]
        for field in ("note", "reason"):
            assert "288" not in cert[field], (gate_id, field, cert[field])


def test_not_testable_reasons_name_no_288_root_structure():
    for gate_id, entry in g72.NOT_TESTABLE_GATES.items():
        assert "288-root" not in entry["reason"], (gate_id, entry["reason"])


def test_spectral_loss_types_no_bridge_count_or_chi_eff():
    source = inspect.getsource(aat.AdversarialAxiomTester.spectral_loss)
    assert "chi_eff = 144" not in source
    assert "self.b3 / 12" not in source
    assert "bridge_params.shape[0]" in source
