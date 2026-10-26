"""A certificate's declared result text must not carry numbers the run disagrees with.

G12's hand-written ``result`` says "0.23190 vs 0.23122 (0.68 sigma ...)" while
its executed registry check computes 17.12 sigma (GATES_CERTIFICATES.json,
gate 12). G50 says "1.63 sigma", the check computes 18.16. The declared text
stays (it is the claim) but the certificate must list the numbers only the
prose carries.
"""
from metaphysica.generators import generate_72_certificates as g

G12 = {"tier": "registry", "status": "COMPUTED_FAIL", "checks": [
    {"path": "constants.sin2_theta_W_pred", "value": 0.23190478152123015,
     "expected": 0.23122, "sigma": 17.119538030753443, "ok": False}]}


def test_g12_prose_sigma_is_reported_as_unmatched():
    text = "0.23190 vs 0.23122 (0.68 sigma with 0.001 theory uncertainty)"
    assert g.result_unmatched_numbers(text, G12) == ["0.68", "0.001"]  # 0.001 is the quoted theory uncertainty: carried by prose only


def test_matching_prose_is_not_reported():
    assert g.result_unmatched_numbers("0.2319 vs 0.23122 (17.12 sigma)", G12) == []


def test_small_scientific_values_use_printed_precision():
    ev = {"checks": [{"value": 6.846485445932354e-10, "expected": 6.12e-10, "sigma": 18.16}]}
    assert g.result_unmatched_numbers("eta_B = 6.19e-10", ev) == ["6.19e-10"]
    assert g.result_unmatched_numbers("eta_B = 6.85e-10", ev) == []


def test_gate_without_checks_is_not_judged():
    assert g.result_unmatched_numbers("3.5 and 4.5", {"tier": "none"}) == []


def test_create_certificate_carries_the_field():
    gate = {"id": 12, "name": "Weinberg angle"}
    if 12 not in g.VERIFIABLE_GATES:
        return
    orig = g.evaluate_gate
    g.evaluate_gate = lambda *a, **k: G12
    try:
        cert = g.create_certificate(gate, [])
    finally:
        g.evaluate_gate = orig
    assert "0.68" in cert["result_unmatched_numbers"]
