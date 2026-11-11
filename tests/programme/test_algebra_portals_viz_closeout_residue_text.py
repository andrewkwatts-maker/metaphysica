"""L6 close-out, complete_residue_registry: XA-01 (GUT text from the computed value),
XA-07 (Dm2 terms, M_Pl text and row from the loader and the dataset), XA-11 (docstring first)."""
import pytest

from metaphysica.config.reference_data import RealWorldData
from metaphysica.simulations.data.experimental_data_loader import get_loader
from metaphysica.simulations.PM.support import complete_residue_registry as crr


def _formula(sim, fid):
    return next(f for f in sim.get_formulas() if f.id == fid)


def test_section_gut_scale_is_the_computed_effective_value():
    sim = crr.CompleteResidueRegistryV18()
    text = str(sim.get_section_content().content_blocks)
    assert "2×10¹⁷" not in text
    assert f"({crr.proton_decay_text()['eff']}) is reproduced" in text


def test_neutrino_splitting_terms_read_the_loader():
    sim = crr.CompleteResidueRegistryV18()
    terms = _formula(sim, "neutrino-sum-prediction-v18").terms
    for key, nufit in (("Dm2_21", "delta_m21_sq"), ("Dm2_31", "delta_m31_sq")):
        assert f"{get_loader().get_nufit(nufit).value:.4g} eV^2" in terms[key]


def test_planck_mass_text_and_row_read_the_dataset():
    sim = crr.CompleteResidueRegistryV18()
    pt = crr.proton_decay_text()
    terms = _formula(sim, "gut-scale-g2-v18").terms
    assert terms["M_Pl"].startswith(f"Planck mass = {pt['M_Pl']} GeV")
    assert pt["b3"] in terms["b3"] and pt["chi"] in terms["chi_eff"]
    row = sim.get_residue(61)
    assert row.mass_gev == pytest.approx(RealWorldData.PLANCK_MASS[0], rel=0, abs=0)
    assert row.uncertainty == RealWorldData.PLANCK_MASS[1]


def test_get_formulas_docstring_is_first():
    assert crr.CompleteResidueRegistryV18.get_formulas.__doc__
