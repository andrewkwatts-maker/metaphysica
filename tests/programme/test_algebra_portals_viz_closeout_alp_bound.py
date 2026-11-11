"""L6 close-out, alp_portals XA-10: one stellar-cooling bound in the value, the definition,
the section text and the bound check; the check reports FAIL; the row is flagged
source_unverified. (Reading the bound from the data loader waits on the L7 data entry.)"""
from metaphysica.simulations.PM.portals import alp_portals as alp

PHOTON = "portals.alp_photon_coupling_gev_inv"


class _Capture:
    def __init__(self):
        self.rows = {}

    def set_param(self, path, **kw):
        self.rows[path] = kw


def _section_text(sim):
    sec = sim.get_section_content()
    return " ".join([sec.abstract] + [str(b.content) for b in sec.content_blocks])


def _photon_def(sim):
    return next(p for p in sim.get_output_param_definitions() if p.path == PHOTON)


def test_one_bound_everywhere_and_the_check_fails():
    sim = alp.ALPPortalsV23()
    g = sim.compute_alp().g_a_gamma_gamma
    assert alp.stellar_bound_check(g) == "FAIL"
    sentence = alp.stellar_bound_sentence(g)
    assert "bound check FAIL" in sentence and f"{g:.3g}" in sentence
    text = _section_text(sim)
    assert sentence in text and "6.6 × 10" not in text
    p = _photon_def(sim)
    assert p.experimental_bound == alp.STELLAR_COOLING_BOUND_GEV_INV
    assert sentence in p.description and "6.6e-11" not in p.description
    cert = next(c for c in sim.get_certificates() if c["id"] == "CERT_ALP_STELLAR_COOLING")
    assert cert["status"] == "FAIL"


def test_changing_the_one_bound_changes_every_place(monkeypatch):
    monkeypatch.setattr(alp, "STELLAR_COOLING_BOUND_GEV_INV", 1.0)
    sim = alp.ALPPortalsV23()
    assert "bound check PASS" in _section_text(sim)
    assert _photon_def(sim).experimental_bound == 1.0
    cert = next(c for c in sim.get_certificates() if c["id"] == "CERT_ALP_STELLAR_COOLING")
    assert cert["status"] == "PASS" and cert["condition"].endswith("< 1")


def test_registered_row_flags_the_bound_source_unverified():
    reg = _Capture()
    alp.ALPPortalsV23().run(reg)
    row = reg.rows[PHOTON]
    assert row["status"] == "CALIBRATED"
    assert row["experimental_value"] == alp.STELLAR_COOLING_BOUND_GEV_INV
    assert row["metadata"]["source_unverified"]
