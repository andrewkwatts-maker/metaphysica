"""geometry.w_zero is aliased to cosmology.w0_derived, so it must follow the
dark_energy_mechanism fork (bug: mep_11_13 published -23/24 via the alias)."""
from metaphysica.simulations.PM.geometry.geometric_anchors_core import GeometricAnchors

_ENV = "METAPHYSICA_VARIANT_DARK_ENERGY_MECHANISM"


def test_main_keeps_thawing_w0(monkeypatch):
    monkeypatch.delenv(_ENV, raising=False)
    assert GeometricAnchors(b3=24).w_zero == -23.0 / 24.0


def test_mep_path_aliases_the_mep_w0(monkeypatch):
    monkeypatch.setenv(_ENV, "mep_11_13")
    assert abs(GeometricAnchors(b3=24).w_zero - (-11.0 / 13.0)) < 1e-12
