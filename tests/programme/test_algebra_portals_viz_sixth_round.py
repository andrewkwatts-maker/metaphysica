"""L6 algebra-portals-viz review round: restored failing row, text from computed values,
fork-read topology, retirement that takes effect, EML tree equal to the function."""
import importlib
import inspect

import pytest

from metaphysica.simulations.PM.algebra import neutrino_algebraic as na
from metaphysica.simulations.PM.consciousness import orch_or_pair_shielding as shield
from metaphysica.simulations.PM.support import complete_residue_registry as crr
from metaphysica.simulations.visualizations import _retired
from metaphysica.simulations.core.variants import selection

RETIRED = ("goldilocks_plot", "stability_heatmap", "theory_overview_diagrams")


def _sim(mod):
    return [v for v in vars(mod).values() if inspect.isclass(v)
            and v.__module__ == mod.__name__ and hasattr(v, "get_section_content")][0]()


def test_proton_text_is_built_from_the_computed_values():
    v = crr.proton_decay_values()
    t = crr.proton_decay_text()
    assert t["tau"] == f"{v['tau_yr']:.3g} yr" and t["eff"] == f"{v['M_GUT_eff']:.3g} GeV"
    sim = crr.CompleteResidueRegistryV18()
    assert sim.get_residue(53).predicted_value == pytest.approx(v["tau_yr"])
    assert sim.get_residue(54).mass_gev == pytest.approx(v["M_GUT_eff"])
    text = " ".join([str(sim.get_formulas()), str(sim.get_output_param_definitions()),
                    str(sim.get_section_content().content_blocks)])
    for typed in ("4.24e39", "2.5e18", "1.24e17", "4.8×10³⁴", "M_Pl/sqrt(24)", "2×10¹⁷"):
        assert typed not in text, typed
    for key in ("tau", "base", "eff"):
        assert t[key] in text, key


def test_neutrino_overshoot_text_follows_the_computed_value():
    V = na._derived_values()
    text = _neutrino_text()
    assert na._overshoot(V) in text
    assert "+49%" in na._overshoot(V) and "38.7 sigma" in na._overshoot(V)
    for stale in ("12%", "~12", "~4 sigma", "~4sigma", "= 1/6"):
        assert stale not in text, stale


def _neutrino_text():
    sim = na.NeutrinoAlgebraicSimulation()
    return " ".join([str(sim.get_section_content().content_blocks),
                     str(sim.get_certificates()), str(sim.get_formulas())])


def test_neutrino_topology_comes_from_the_fork_readers():
    from metaphysica.simulations.core.active_path import topology
    from metaphysica.simulations.core.canonical_values import canon
    for path in ("seed_43_joyce", "seed_24"):
        with selection.forced({"b3_seed": path}):
            V = na._derived_values()
            topo = topology(path)
            assert (V.b3, V.n_gen, V.chi_eff) == (topo.b3, topo.n_gen, topo.chi_eff)
            assert V.alpha_leak == canon(path)["alpha_leak"]["value"]
    off = na._off_path()
    assert off.b3 == topology("seed_24").b3
    src = inspect.getsource(na)
    for typed in ("48.0 * n_gen", "_derive(24", "_OFF_PATH =", "b2 / 4.0", "b2 // 4"):
        assert typed not in src, typed


@pytest.mark.parametrize("name", RETIRED)
def test_retired_figure_modules_write_outside_the_paper_folder(name, tmp_path):
    mod = importlib.import_module("metaphysica.simulations.visualizations." + name)
    assert _retired.is_retired(mod)
    assert _retired.output_dir_for(mod, tmp_path) == tmp_path / "retired"
    src = inspect.getsource(mod)
    assert "output_dir_for" in src


def test_goldilocks_figure_lands_in_the_retired_folder(tmp_path, monkeypatch):
    import matplotlib
    matplotlib.use("Agg")
    from metaphysica.simulations.visualizations import goldilocks_plot as g
    monkeypatch.setattr(g, "OUTPUT_DIR", tmp_path)
    out = g.generate_goldilocks_plot()
    assert (tmp_path / "retired" / "goldilocks-b3-uniqueness.png").exists()
    assert not (tmp_path / "goldilocks-b3-uniqueness.png").exists()
    assert out is None or "retired" in str(out)


def test_paper_figure_list_excludes_retired_modules():
    from metaphysica.generators import all_plots
    listed = list(all_plots.VISUALIZATION_MODULES)
    live = _retired.paper_figures(listed)
    assert live == listed
    base = "metaphysica.simulations.visualizations."
    assert _retired.paper_figures(listed + [base + n for n in RETIRED]) == listed
    assert not _retired.is_retired(importlib.import_module(listed[0]))


def test_retired_shielding_has_no_section_and_no_certificate():
    sim = _sim(shield)
    assert shield.RETIRED_FROM_PAPER is True
    assert sim.get_section_content() is None
    assert sim.get_certificates() == []
    assert len(sim.get_output_param_definitions()) >= 2  # rows stay


def test_shielding_eml_tree_evaluates_to_the_shielding_function():
    from metaphysica.simulations.core.eml_integration import eml_scalar, ops
    formula = _sim(shield).get_formulas()[0]
    assert formula.category == "CALIBRATED"
    for n in (6.0, 12.0):
        vals = {"hbar": 1.0, "E_G": 1.0, "k": shield.K_SHIELDING, "n_pairs": n}
        tree = eval(formula.eml_tree_str, {"ops": ops, "eml_scalar": eml_scalar,
                                           "eml_vec": lambda k: eml_scalar(vals[k])})
        assert tree.tension() == pytest.approx(float(shield.shielding_enhancement(n)))
