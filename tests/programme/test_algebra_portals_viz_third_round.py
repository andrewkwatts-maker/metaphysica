"""L6 algebra-portals-viz round 3: named 24, off-path w(z), retired figures,
dataset Planck mass, one coherence chain, 4096 claim."""
import importlib
import math

import numpy as np
import pytest

from metaphysica.simulations.PM.algebra import e7_representation as e7, shadow_clifford as sc
from metaphysica.simulations.PM.consciousness import gnosis_unlocking as gnosis
from metaphysica.simulations.PM.consciousness import orch_or_pair_shielding as shield
from metaphysica.simulations.PM.portals import alp_portals
from metaphysica.simulations.visualizations import ricci_flow_evolution as rf


def _ctx(mod):
    return importlib.import_module("metaphysica.simulations.visualizations." + mod)


def test_alp_denominator_is_a_named_constant():
    assert alp_portals.G_AGG_DENOMINATOR == 24.0
    src = open(alp_portals.__file__, encoding="utf-8").read()
    assert "G_AGG_DENOMINATOR * math.pi * f_a_alp" in src
    assert "(24.0 * math.pi" not in src


def test_ricci_flow_w_parameters_derived_from_named_seed():
    from metaphysica.simulations.PM.geometry.b3_path import seed_values
    b3 = seed_values("seed_24")[0]
    assert rf.OFF_PATH_B3 == b3
    assert rf.W0_OFF_PATH == pytest.approx(-1 + 1 / b3)
    assert rf.WA_OFF_PATH == pytest.approx(-1 / math.sqrt(b3))
    src = open(rf.__file__, encoding="utf-8").read()
    assert "OFF_PATH_B3 = 24" not in src
    assert "w0 = -23 / 24" not in src


@pytest.mark.parametrize("mod", ["goldilocks_plot", "stability_heatmap",
                                 "theory_overview_diagrams"])
def test_off_path_figures_retired_from_paper(mod):
    assert _ctx(mod).RETIRED_FROM_PAPER is True


def test_e7_planck_mass_read_from_dataset():
    from metaphysica.config.reference_data import RealWorldData
    assert e7._M_PLANCK_GEV == RealWorldData.PLANCK_MASS[0]
    assert e7._M_PLANCK_GEV != 1.22e19


def _sim(mod):
    import inspect
    return [v for v in vars(mod).values() if inspect.isclass(v)
            and hasattr(v, "get_output_param_definitions")
            and v.__module__ == mod.__name__][0]()


def test_gnosis_chain_is_calibrated_and_penrose_is_labelled_separate():
    g = {p.path: p for p in _sim(gnosis).get_output_param_definitions()}
    for k in ("consciousness.tau_baseline", "consciousness.tau_gnosis",
              "consciousness.coherence_boost"):
        assert g[k].status == "CALIBRATED"
        assert "INPUT" in g[k].description
    s = {p.path: p for p in _sim(shield).get_output_param_definitions()}
    for k in ("consciousness.penrose_tau_ms", "consciousness.shielded_tau_ms",
              "consciousness.tau_base_ms"):
        assert "separate from the gnosis coherence chain" in s[k].description


def test_4096_claim_from_explicit_64x64_gammas():
    gam = sc.shadow_gammas()
    assert len(gam) == 13
    assert all(g.shape == (64, 64) for g in gam)
    rep = sc.shadow_clifford_report()
    assert rep["clifford_relations_hold"] is True
    assert rep["spinor_dim"] == 64
    assert rep["shadow_pair_spinor"] == 4096
    assert rep["reality_type"] == "quaternionic"
