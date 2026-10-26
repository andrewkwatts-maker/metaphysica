"""The dark_energy_betti fork sets n in w0 = -(n-1)/n (it used to be read by
no module, so all its options were inert), and its drift check refuses to
measure n when another dark_energy_mechanism sets w0."""
import pytest

from metaphysica.simulations.core import variants
from metaphysica.simulations.PM.cosmology import late_time_routes as ltr
from metaphysica.simulations.PM.geometry.geometric_anchors_core import GeometricAnchors

_BETTI = "METAPHYSICA_VARIANT_DARK_ENERGY_BETTI"
_MECH = "METAPHYSICA_VARIANT_DARK_ENERGY_MECHANISM"


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv(_BETTI, raising=False)
    monkeypatch.delenv(_MECH, raising=False)


def test_table_matches_fork_options():
    ids = set(variants.FORKS["dark_energy_betti"].option_ids())
    assert set(ltr.DE_BETTI_N) | {"b3_live"} == ids
    assert {v: k for k, v in variants._DE_BETTI_BY_N.items()} == ltr.DE_BETTI_N


def test_main_w0_unchanged():
    assert GeometricAnchors(b3=24).w_zero == -23.0 / 24.0


@pytest.mark.parametrize("option,n", [("b2_4", 4), ("octonion_8", 8), ("bridges_12", 12)])
def test_option_moves_w0(monkeypatch, option, n):
    monkeypatch.setenv(_BETTI, option)
    assert GeometricAnchors(b3=24).w_zero == pytest.approx(-(n - 1) / n)


def test_b3_live_follows_seed(monkeypatch):
    from metaphysica.simulations.PM.geometry.geometric_anchors import live_b3

    monkeypatch.setenv(_BETTI, "b3_live")
    n = live_b3()
    assert GeometricAnchors(b3=24).w_zero == pytest.approx(-(n - 1) / n)


def test_drift_check_refuses_under_mep(monkeypatch):
    from metaphysica.simulations.base.registry import PMRegistry

    monkeypatch.setenv(_MECH, "mep_11_13")
    reg = PMRegistry.get_instance()
    monkeypatch.setattr(reg, "get", lambda path, *a, **k: -11.0 / 13.0)
    with pytest.raises(variants.SourceUnmeasurable):
        variants._dark_energy_betti_adopted()
