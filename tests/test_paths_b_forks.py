"""D-022: the recovered n_gen_source and spectral_index_route options are runnable.

One test per fork: the default resolves to the adopted option, and each option
changes (or, where the source supplies identical inputs, provably reads) its consumer.
"""
import pytest

from metaphysica.simulations.core import variants as v

ENV = "METAPHYSICA_VARIANT_"


def test_spectral_index_route_default_is_adopted(monkeypatch):
    monkeypatch.delenv(ENV + "SPECTRAL_INDEX_ROUTE", raising=False)
    fork = v.FORKS["spectral_index_route"]
    assert v.resolve("spectral_index_route") == "golden_modulated"
    assert fork.read_adopted() == fork.default()


def _n_s_pair():
    from metaphysica.simulations.PM.cosmology.inflation import G2Inflation
    from metaphysica.simulations.PM.geometry.geometric_anchors_core import (
        GeometricAnchors,
    )

    return G2Inflation().derive_observables()["n_s"], GeometricAnchors().n_s


def test_spectral_index_route_changes_both_n_s_consumers(monkeypatch):
    monkeypatch.delenv(ENV + "SPECTRAL_INDEX_ROUTE", raising=False)
    base = _n_s_pair()
    assert base[0] == pytest.approx(1 - 2 * 1.6180339887498949 ** 2 / 144)
    seen = {}
    for opt in ("one_minus_2_over_b3", "re_t_slow_roll"):
        monkeypatch.setenv(ENV + "SPECTRAL_INDEX_ROUTE", opt)
        seen[opt] = _n_s_pair()
        assert seen[opt][0] != base[0], opt
        assert seen[opt][1] != base[1], opt
    assert seen["one_minus_2_over_b3"][0] == pytest.approx(1 - 2 / 24)
    assert seen["re_t_slow_roll"][0] == pytest.approx(0.9996, abs=5e-5)


def test_n_gen_source_default_is_adopted(monkeypatch):
    monkeypatch.delenv(ENV + "N_GEN_SOURCE", raising=False)
    assert v.resolve("n_gen_source") == "b2_over_faces"


def test_n_gen_source_chi_routes_read_registry_chi_eff(monkeypatch):
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    monkeypatch.delenv(ENV + "N_GEN_SOURCE", raising=False)
    reg = FormulasRegistry()
    assert reg.n_gen == 3
    monkeypatch.setenv(ENV + "N_GEN_SOURCE", "chi_over_24")
    assert reg.n_gen == reg.chi_eff_sector / 24 == 3
    monkeypatch.setattr(FormulasRegistry, "chi_eff_sector", 96)
    assert reg.n_gen == 4
    monkeypatch.setenv(ENV + "N_GEN_SOURCE", "chi_eff_over_48")
    monkeypatch.setattr(FormulasRegistry, "chi_eff_total", 192)
    assert reg.n_gen == 4


def test_n_gen_report_and_guard_follow_the_chi_routes(monkeypatch):
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry
    from metaphysica.simulations.PM.geometry import b3_path

    monkeypatch.setenv(ENV + "N_GEN_SOURCE", "chi_over_24")
    assert b3_path.n_gen_report()["n_gen"] == 3
    assert b3_path.require_three_generations() == 3
    monkeypatch.setattr(FormulasRegistry, "chi_eff_sector", 96)
    assert b3_path.n_gen_report()["n_gen"] == 4
    with pytest.raises(ValueError):
        b3_path.require_three_generations()
    monkeypatch.setenv(ENV + "N_GEN_SOURCE", "chi_eff_over_48")
    monkeypatch.setattr(FormulasRegistry, "chi_eff_total", 192)
    assert b3_path.n_gen_report()["n_gen"] == 4


def test_unknown_n_gen_source_is_refused():
    from metaphysica.simulations.PM.geometry import b3_path

    with pytest.raises(ValueError):
        b3_path._n_gen_value("nonsense", 1.0, 1.0)


# ---- stage 2: h0_route, dark_energy_mechanism, Jacobian seed --------------------

def test_h0_route_default_is_adopted(monkeypatch):
    monkeypatch.delenv(ENV + "H0_ROUTE", raising=False)
    fork = v.FORKS["h0_route"]
    assert v.resolve("h0_route") == "odowd_composite"
    assert fork.read_adopted() == fork.default()


def test_h0_route_changes_h0_local(monkeypatch):
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    monkeypatch.delenv(ENV + "H0_ROUTE", raising=False)
    reg = FormulasRegistry()
    base = reg.h0_local
    monkeypatch.setenv(ENV + "H0_ROUTE", "ricci_flow")
    assert reg.h0_local == pytest.approx(76.34, abs=0.01)
    monkeypatch.setenv(ENV + "H0_ROUTE", "kk_bridge")
    kk = reg.h0_local
    assert kk != base and kk == pytest.approx(67.4, abs=1e-3)


def test_dark_energy_mechanism_default_is_adopted(monkeypatch):
    monkeypatch.delenv(ENV + "DARK_ENERGY_MECHANISM", raising=False)
    fork = v.FORKS["dark_energy_mechanism"]
    assert v.resolve("dark_energy_mechanism") == "thawing_quintessence"
    assert fork.read_adopted() == fork.default()


def test_dark_energy_mechanism_changes_both_w0_consumers(monkeypatch):
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry
    from metaphysica.simulations.PM.cosmology.dark_energy import DarkEnergyV16 as DarkEnergy

    monkeypatch.delenv(ENV + "DARK_ENERGY_MECHANISM", raising=False)
    reg = FormulasRegistry()
    base = (reg.w0_dark_energy, DarkEnergy()._derive_dark_energy_eos(12.0))
    monkeypatch.setenv(ENV + "DARK_ENERGY_MECHANISM", "mep_11_13")
    alt = (reg.w0_dark_energy, DarkEnergy()._derive_dark_energy_eos(12.0))
    assert alt == (pytest.approx(-11 / 13), pytest.approx(-11 / 13))
    assert alt[0] != base[0] and alt[1] != base[1]


def test_jacobian_stub_is_reproducible():
    import numpy as np
    from metaphysica.simulations.PM.validation.statistical_rigor_validator import (
        StatisticalRigorValidator,
    )

    a = StatisticalRigorValidator().generate_jacobian_matrix()
    np.random.seed(1)
    b = StatisticalRigorValidator().generate_jacobian_matrix()
    assert np.array_equal(a, b)
