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


def test_mathematical_certificate_note_names_no_288_root_manifold():
    gate_id = next(iter(g72.MATHEMATICAL_GATES))
    gate = {"id": gate_id, "name": "Mass Gap", "logic": "discrete spectrum"}
    cert = g72.create_certificate(gate, {})
    assert cert["verification_status"] == "MATHEMATICAL"
    assert "288-root manifold" not in cert["note"]
    assert "without a computational evaluation" in cert["note"]
