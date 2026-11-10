"""L6 algebra-portals-viz round 1: b3 text, ALP status, Clifford boost, Figure 3."""
import inspect
import pytest

from metaphysica.simulations.base.registry import PMRegistry
from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.algebra import (
    clifford_unification as cu, e7_representation as e7,
    e8x8_splitting as e8, freudenthal_triple as ft)
from metaphysica.simulations.PM.portals import alp_portals
from metaphysica.simulations.visualizations import figure3_alp_discovery_window as fig3


def _sim(mod):
    return [v for v in vars(mod).values() if inspect.isclass(v)
            and v.__module__ == mod.__name__ and hasattr(v, "get_section_content")][0]()


def _texts(sim):
    out = [str(sim.get_section_content().content_blocks)]
    for name in ("get_certificates", "validate_self"):
        if hasattr(sim, name):
            out.append(str(getattr(sim, name)()))
    return " ".join(out)


@pytest.mark.parametrize("mod", [ft, e7, e8])
def test_text_reads_active_b3(mod):
    sim = _sim(mod)
    with selection.forced({"b3_seed": "seed_43_joyce"}):
        t43 = _texts(sim)
    with selection.forced({"b3_seed": "seed_24"}):
        t24 = _texts(sim)
    assert t43 != t24
    assert "b3 = 24" not in t43 and "(24/27)" not in t43 and "W_np(24)" not in t43


def test_freudenthal_text_does_not_match_bulk():
    t = _texts(_sim(ft))
    assert "matching the bulk dimension exactly" not in t
    assert "V_bridge" not in inspect.getsource(ft).replace("no bridge", "")


def test_alp_rows_calibrated_and_scored_against_bound():
    reg = PMRegistry.get_instance()
    alp_portals.ALPPortalsV23().run(reg)
    for path in ("portals.alp_mass_ev", "portals.alp_photon_coupling_gev_inv",
                 "portals.alp_nucleon_coupling_gev_inv",
                 "portals.alp_fifth_force_range_m", "portals.alp_decay_constant_gev"):
        assert reg.get_entry(path).status == "CALIBRATED"
    g = reg.get_entry("portals.alp_photon_coupling_gev_inv")
    assert g.bound_type == "upper"
    assert g.experimental_value == alp_portals.STELLAR_COOLING_BOUND_GEV_INV
    assert g.validation_status == "FAIL"  # the failing result is kept


def test_clifford_boost_row_removed_and_no_swallowed_errors():
    out = cu.CliffordUnificationSimulation().run(None)
    assert "algebra.clifford_boost_conservation" not in out
    assert out["_all_pass"] and out["_checks_passed"] == 3
    src = inspect.getsource(cu.CliffordUnificationSimulation.run)
    assert "except" not in src
    sim = cu.CliffordUnificationSimulation()
    assert "algebra.clifford_boost_conservation" not in sim.output_params
    assert "Boost" not in str(sim.get_section_content().content_blocks)


def test_figure3_point_from_registry_rows():
    rows = {"parameters": {fig3.MASS_ROW: {"value": 111.0},
                           fig3.COUPLING_ROW: {"value": 1.2e-6}}}
    assert fig3.alp_point_from_registry(rows) == pytest.approx((111000.0, 1.2e-6))
    with pytest.raises(KeyError):
        fig3.alp_point_from_registry({"parameters": {}})
    assert "3.51" not in inspect.getsource(fig3).split("def main")[0].replace("m_a = 3.51", "")


def test_residue_registry_no_swallowed_loader_errors_or_literal_fallbacks():
    from metaphysica.simulations.PM.support import complete_residue_registry as crr
    src = inspect.getsource(crr)
    assert "except Exception" not in src and "_LOADER_OK" not in src
    with pytest.raises(KeyError):
        crr._pdg_v("higgs", "no_such_row")
    reg = crr.CompleteResidueRegistryV18()
    out = reg.run(PMRegistry.get_instance())
    f = [x for x in reg.get_formulas() if x.id == "neutrino-sum-prediction-v18"][0]
    assert f"{out['spectral.sum_m_nu']:.4f}" in f.plain_text
    assert "m1 ~ 0.001 eV" not in f.description
    assert "b₃=24" not in (crr.__doc__ or "")
    with pytest.raises(ValueError):
        crr.CompleteResidueRegistryV18._mass_ev(None)


def test_qec_mapping_reads_active_b3():
    from metaphysica.simulations.PM.algebra import qec_golay_bridge as q
    sim = _sim(q)
    with selection.forced({"b3_seed": "seed_43_joyce"}):
        rows = sim.get_mapping_table()
    assert rows[0]["classification"] == "MISMATCH" and "43" in rows[0]["pm_concept"]
    with selection.forced({"b3_seed": "seed_24"}):
        assert sim.get_mapping_table()[0]["classification"] == "MOTIVATED_IDENTIFICATION"


def test_neutrino_algebraic_missing_topology_row_raises():
    from metaphysica.simulations.PM.algebra import neutrino_algebraic as na
    PMRegistry.reset_instance()
    reg = PMRegistry.get_instance()
    reg.set_param("topology.elder_kads", 43, "t")
    with pytest.raises(KeyError):
        na.NeutrinoAlgebraicSimulation().run(reg)
    src = inspect.getsource(na.NeutrinoAlgebraicSimulation)
    assert "else float(_CHI_EFF)" not in src and "else float(_N_GEN)" not in src
    PMRegistry.reset_instance()
