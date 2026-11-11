"""Wave A round 2, alp_portals R2-12 to R2-15 (and the alp part of R2-16).

R2-12: the CAST certificate is a second, sourced bound read from one named constant.
R2-13: the stellar certificate says below or above from stellar_bound_check.
R2-14: the photon formula carries the row's status and no typed copy of the bound.
R2-15: the coupling paragraph labels the retired seed's numbers and keeps the computed verdict.
R2-16: the new text lives in helpers of 60 lines or fewer; `run` did not grow.
"""
import inspect
import re

from metaphysica.simulations.PM.portals import alp_portals as alp

PHOTON = "portals.alp_photon_coupling_gev_inv"
PHOTON_FORMULA = "portal-alp-photon-v23"
HELPERS = (
    "off_path_label", "_latex_sci", "_bound_certificate", "bound_certificates",
    "photon_formula_description", "photon_formula_derivation_steps",
    "photon_coupling_paragraph", "cast_bound_check", "_bound_side",
)


class _Capture:
    def __init__(self):
        self.rows = {}

    def set_param(self, path, **kw):
        self.rows[path] = kw


def _cert(sim, cert_id):
    return next(c for c in sim.get_certificates() if c["id"] == cert_id)


def _photon_formula(sim):
    return next(f for f in sim.get_formulas() if f.id == PHOTON_FORMULA)


def _formula_text(formula):
    steps = formula.derivation["steps"]
    return " ".join([formula.description]
                    + [s["description"] for s in steps] + [s["formula"] for s in steps])


def _coupling_paragraph(sim):
    blocks = sim.get_section_content().content_blocks
    return next(str(b.content) for b in blocks if "weighted channel" in str(b.content))


def test_r2_12_cast_certificate_is_a_second_sourced_bound(monkeypatch):
    sim = alp.ALPPortalsV23()
    cast = _cert(sim, "CERT_ALP_CAST_BOUND")
    assert cast["source"] == alp.CAST_BOUND_SOURCE and "arXiv:1705.02290" in cast["source"]
    assert f"{alp.CAST_BOUND_GEV_INV:.2g}" in cast["assertion"]
    assert "separate from the stellar-cooling one" in cast["assertion"]
    assert cast["status"] == alp.cast_bound_check(sim.compute_alp().g_a_gamma_gamma) == "FAIL"
    assert " is above the CAST 2017 helioscope bound" in cast["assertion"]
    # The CAST verdict follows the CAST constant alone; the stellar one does not move.
    monkeypatch.setattr(alp, "CAST_BOUND_GEV_INV", 1.0)
    cast = _cert(sim, "CERT_ALP_CAST_BOUND")
    assert cast["status"] == "PASS" and cast["condition"].endswith("< 1")
    assert " is below the CAST 2017 helioscope bound" in cast["assertion"]
    assert _cert(sim, "CERT_ALP_STELLAR_COOLING")["status"] == "FAIL"


def test_r2_12_cast_certificate_states_the_mass_range_of_its_bound():
    sim = alp.ALPPortalsV23()
    m_alp = sim.compute_alp().m_alp
    side = "inside" if m_alp < alp.CAST_BOUND_MAX_MASS_EV else "outside"
    assertion = _cert(sim, "CERT_ALP_CAST_BOUND")["assertion"]
    assert f"m_a < {alp.CAST_BOUND_MAX_MASS_EV:g} eV" in assertion
    assert f"m_ALP = {m_alp:.3g} eV is {side} that range" in assertion


def test_r2_13_stellar_certificate_says_the_side_the_check_computes(monkeypatch):
    sim = alp.ALPPortalsV23()
    cert = _cert(sim, "CERT_ALP_STELLAR_COOLING")
    assert cert["status"] == "FAIL"
    assert " is above the stellar cooling bound" in cert["assertion"]
    assert "below" not in cert["assertion"]
    assert cert["source"] == alp.STELLAR_COOLING_SOURCE and cert["source_unverified"]
    monkeypatch.setattr(alp, "STELLAR_COOLING_BOUND_GEV_INV", 1.0)
    cert = _cert(sim, "CERT_ALP_STELLAR_COOLING")
    assert cert["status"] == "PASS"
    assert " is below the stellar cooling bound" in cert["assertion"]
    assert "above" not in cert["assertion"]


def test_r2_14_photon_formula_has_the_row_status_and_one_computed_bound(monkeypatch):
    sim = alp.ALPPortalsV23()
    reg = _Capture()
    sim.run(reg)
    formula = _photon_formula(sim)
    assert formula.category == reg.rows[PHOTON]["status"] == "CALIBRATED"
    g = sim.compute_alp().g_a_gamma_gamma
    assert "below the stellar cooling bound" not in _formula_text(formula)
    assert alp.stellar_bound_sentence(g) in formula.description
    assert "bound check FAIL" in formula.description
    last = formula.derivation["steps"][-1]["formula"]
    assert r"\geq " + alp._latex_sci(alp.STELLAR_COOLING_BOUND_GEV_INV) in last
    # One bound: changing the constant changes the verdict and the relation, and no
    # typed copy of the old value stays behind in the text.
    monkeypatch.setattr(alp, "STELLAR_COOLING_BOUND_GEV_INV", 1.0)
    formula = _photon_formula(sim)
    text = _formula_text(formula)
    assert "bound check PASS" in formula.description
    assert r"< 1.00 \times 10^{0}" in formula.derivation["steps"][-1]["formula"]
    assert "10^{-10}" not in text and "1e-10" not in text


def test_r2_14_photon_formula_labels_the_retired_seed_numbers():
    sim = alp.ALPPortalsV23()
    label = alp.off_path_label()
    assert alp.OFF_PATH_SEED == "seed_24" and "seed_24" in label and "retired" in label
    steps = _photon_formula(sim).derivation["steps"]
    assert f"1/sqrt(6) at the {label}" in steps[0]["description"]
    assert r"\sqrt{6}" not in steps[0]["formula"]
    assert f"alpha_leak = {sim.alpha_leak:.3g}" in steps[-1]["description"]
    assert f"are those of the {label}" in steps[-1]["description"]
    assert f"{sim.alpha_leak:.3f} \\times {sim.chi_eff:g}" in steps[-1]["formula"]
    assert "0.408" not in steps[-1]["formula"]


def test_r2_15_paragraph_labels_retired_numbers_and_keeps_the_computed_verdict():
    sim = alp.ALPPortalsV23()
    label = alp.off_path_label()
    text = _coupling_paragraph(sim)
    assert "falls below" not in text
    assert f"α<sub>leak</sub> = {sim.alpha_leak:.3g} on the path in force" in text
    assert f"(1/√6 at the {label})" in text
    assert f"χ<sub>eff</sub> = {sim.chi_eff:g} per shadow" in text
    assert re.search(r"10<sup>−11</sup> GeV<sup>−1</sup> is that of the " + re.escape(label), text)
    # The bound is stated once, inside the computed sentence.
    assert alp.stellar_bound_sentence(sim.compute_alp().g_a_gamma_gamma) in text
    assert text.count(f"{alp.STELLAR_COOLING_BOUND_GEV_INV:.2g} GeV") == 1
    assert text.count("bound check") == 1


def test_r2_16_new_text_is_in_helpers_and_run_did_not_grow():
    for name in HELPERS:
        assert len(inspect.getsourcelines(getattr(alp, name))[0]) <= 60, name
    # 91 lines: inspect.getsourcelines(ALPPortalsV23.run) measured 2026-11-11 on the file
    # as of commit d5c3792, the size WAVE_A_ROUND2.md row R2-16 records for `run`.
    assert len(inspect.getsourcelines(alp.ALPPortalsV23.run)[0]) <= 91
