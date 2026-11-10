"""L1 path-core: names that stood for b3, b2, chi_eff or n_gen follow the path.

Each test fails on the code before the fix, where the value was typed at
the retired seed_24 (b3 = 24, b2 = 4) or as a fixed 23/24.
"""
import math

import pytest

from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.geometry.b3_path import resolve_path, seed_values

PATHS = [None, "seed_24"]


def _forced(seed):
    return selection.forced({"b3_seed": seed}) if seed else selection.forced({})


@pytest.mark.parametrize("seed", PATHS)
def test_topology_and_canonical_names_agree_with_seed_values(seed):
    from metaphysica.simulations.core import canonical_values as cv
    from metaphysica.simulations.core.active_path import topology

    with _forced(seed):
        b3, b2 = seed_values(resolve_path())
        topo = topology()
        assert (topo.b3, topo.b2) == (b3, b2)
        assert (cv.B3, cv.B2) == (b3, b2)
        assert cv.CHI_EFF == topo.chi_eff == 2 * cv.CHI_SECTOR
        assert cv.CANON["wa"]["value"] == pytest.approx(-1 / math.sqrt(b3))
        assert cv.CANON["alpha_leak"]["value"] == pytest.approx(
            1 / math.sqrt(topo.chi_eff / b3))


def test_adopted_seed_is_joyce():
    from metaphysica.simulations.core.active_path import topology

    topo = topology()
    assert (topo.b3, topo.b2, topo.n_gen, topo.chi_eff) == (43, 12, 3, 144)


def test_frozen_w0_is_an_input_not_a_prediction():
    from metaphysica.simulations.core.canonical_values import canon

    with selection.forced({"dark_energy_betti": "b3_24"}):
        assert canon()["w0"]["status"] == "INPUT"
    with selection.forced({"dark_energy_betti": "b3_live"}):
        entry = canon()["w0"]
        assert entry["status"] == "PREDICTED"
        assert entry["value"] == pytest.approx(-42 / 43)


def test_canon_h0_is_read_from_the_artifact():
    from metaphysica.simulations.core.canonical_values import canon
    from metaphysica.simulations.core.parameter_artifact import parameter_value

    assert canon()["H0_km_s_Mpc"]["value"] == parameter_value("cosmology.H0_local")


@pytest.mark.parametrize("option,n", [("b3_24", 24), ("b3_live", 43)])
def test_registry_tzimtzum_follows_the_dark_energy_fork(option, n):
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    with selection.forced({"dark_energy_betti": option}):
        reg = FormulasRegistry()
        assert reg._tzimtzum_pressure == pytest.approx((n - 1) / n)
        assert reg.calculate_w0() == pytest.approx(-(n - 1) / n)
        assert reg.verify_tzimtzum_fraction()


def test_registry_text_has_no_retired_seed_numbers():
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    reg = FormulasRegistry()
    for name in ("calculate_h0_local", "calculate_w0", "sophian_drag"):
        attr = getattr(FormulasRegistry, name)
        doc = (attr.fget if isinstance(attr, property) else attr).__doc__
        assert "= 71.55 km/s/Mpc" not in doc
        assert "DERIVED" not in doc.split("STATUS")[-1][:20]
    assert reg.CODATA_COMPTON == 2.42631023538e-12


def test_hebrew_symbol_values_follow_the_path():
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    with _forced("seed_24"):
        b3 = seed_values(resolve_path())[0]
        term = FormulasRegistry().get_latex_term("elder_kads")
        assert term["value"] == b3 == 24
    term = FormulasRegistry().get_latex_term("elder_kads")
    assert term["value"] == 43


def test_dependency_resolver_seeds_and_h0_follow_the_path():
    from metaphysica.simulations.core.dependency_resolver import (
        build_seed_values,
        resolve_with_seeds,
    )
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    seeds = build_seed_values()
    assert seeds["seeds.elder_kads"] == 43
    assert resolve_with_seeds("cosmology.H0_local") == pytest.approx(
        FormulasRegistry().h0_local)
    assert resolve_with_seeds("cosmology.w0_derived") == pytest.approx(-23 / 24)


def test_config_chirality_reads_the_path():
    from metaphysica.config.parameters import (
        FermionChiralityParameters,
        FluxQuantization,
        TorsionClass,
    )

    with _forced("seed_24"):
        assert TorsionClass.B3 == 24 and FluxQuantization.B2 == 4
    assert TorsionClass.B3 == 43 and FluxQuantization.B2 == 12
    chir = FermionChiralityParameters.get_fermion_chirality()
    assert chir["n_generations"] == 3 and chir["path"] == "seed_43_joyce"
    assert "12/4" in chir["formula"]
    assert FermionChiralityParameters.RETIRED_TCS187_CHI_EFF == 144
    assert TorsionClass.T_TOPOLOGICAL == -1.0


def test_unknown_fork_raises():
    from metaphysica.simulations.core.variants import resolve

    with pytest.raises(KeyError):
        resolve("no_such_fork")


@pytest.mark.parametrize("forced", [{"b3_seed": "no_such_option"},
                                    {"dark_energy_betti": "no_such_option"}])
def test_unknown_option_raises(forced):
    from metaphysica.simulations.core.canonical_values import canon

    with pytest.raises((KeyError, ValueError)):
        with selection.forced(forced):
            canon()
