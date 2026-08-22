"""Tests for ``metaphysica.simulations.PM.particle.neutrino_sector``.

Sprint 5 task #6 (greedy Nygaard lift) verification:

1. ``sigma_m_refined_eV`` lies in the validation window (0, 0.12) eV.
2. ``sigma_m_refined_eV`` clears the DESI 2026 95% CL ceiling (0.072 eV).
3. The mirror correction equals ``0.015 · g_b · 1e10`` exactly.
4. The derivation chain uses ``eml_operator_tree`` and traces back to
   the b₃ = 24 topological seed via ``b3_leaf()``.
"""

from __future__ import annotations

import inspect

import pytest

from metaphysica.simulations.core.eml_tree_adapter import eml_operator_tree


def _import_module():
    from metaphysica.simulations.PM.particle import neutrino_sector

    return neutrino_sector


# ── Numerical / contract tests ---------------------------------------------


def test_refine_neutrino_sector_in_window():
    """Module entry returns refined Σm in the (0, 0.12) eV window."""
    mod = _import_module()
    result = mod.refine_neutrino_sector()
    sigma = result["sigma_m_refined_eV"]
    assert 0.0 < sigma < 0.12, (
        f"sigma_m_refined_eV = {sigma!r} outside (0, 0.12) eV window"
    )


def test_refine_neutrino_sector_clears_desi_2026():
    """Refined Σm must beat the DESI 2026 0.072 eV ceiling."""
    mod = _import_module()
    result = mod.refine_neutrino_sector()
    assert result["sigma_m_refined_eV"] < mod.DESI_2026_CEILING


def test_refine_neutrino_sector_shape():
    """Module entry returns the four documented keys with right types."""
    mod = _import_module()
    result = mod.refine_neutrino_sector()
    assert {
        "sigma_m_base_eV",
        "sigma_m_refined_eV",
        "hierarchy",
        "status",
    }.issubset(set(result))
    assert isinstance(result["sigma_m_base_eV"], float)
    assert isinstance(result["sigma_m_refined_eV"], float)
    assert result["hierarchy"] == "inverted (preferred)"
    # Default-input status should reflect DESI consistency.
    assert "0.072" in result["status"]


def test_sigma_m_base_matches_inverted_hierarchy_formula():
    """Σm_base = m1 + m2 + m3 with the documented inverted ordering."""
    import math

    mod = _import_module()
    inst = mod.NeutrinoSectorRefinement()
    expected_m3 = mod.DEFAULT_M_LIGHTEST
    expected_m1 = math.sqrt(expected_m3 * expected_m3 + mod.DELTA_M21_SQ)
    expected_m2 = math.sqrt(expected_m1 * expected_m1 + mod.DELTA_M31_SQ)
    expected_sum = expected_m1 + expected_m2 + expected_m3

    sigma_base = inst.compute_inverted_hierarchy_sum()
    assert sigma_base == pytest.approx(expected_sum, rel=1e-12)


def test_mirror_correction_exact():
    """Mirror correction is ``0.015 · g_b · 1e10`` eV exactly."""
    mod = _import_module()
    inst = mod.NeutrinoSectorRefinement(bridge_coupling=1.2e-10)
    expected_correction = 0.015 * 1.2e-10 * 1.0e10  # = 0.018
    # Feed an arbitrary base value; the difference must be the correction.
    sigma_base = 0.05
    sigma_refined = inst.apply_mirror_correction(sigma_base)
    assert (sigma_base - sigma_refined) == pytest.approx(
        expected_correction, rel=1e-12
    )


def test_class_default_constructor_values():
    """Default constructor uses ``m_lightest = 1e-3`` and ``g_b = 1.2e-10``."""
    mod = _import_module()
    inst = mod.NeutrinoSectorRefinement()
    assert inst.m_lightest == pytest.approx(1.0e-3, rel=0.0)
    assert inst.bridge_coupling == pytest.approx(1.2e-10, rel=0.0)


def test_class_rejects_nonpositive_m_lightest():
    """``m_lightest`` must be positive."""
    mod = _import_module()
    with pytest.raises(ValueError):
        mod.NeutrinoSectorRefinement(m_lightest=0.0)
    with pytest.raises(ValueError):
        mod.NeutrinoSectorRefinement(m_lightest=-1.0e-3)


def test_class_rejects_nonpositive_bridge_coupling():
    """``bridge_coupling`` must be positive."""
    mod = _import_module()
    with pytest.raises(ValueError):
        mod.NeutrinoSectorRefinement(bridge_coupling=0.0)
    with pytest.raises(ValueError):
        mod.NeutrinoSectorRefinement(bridge_coupling=-1.2e-10)


def test_refined_sum_consistency():
    """Refined = base − correction (full pipeline self-consistency)."""
    mod = _import_module()
    inst = mod.NeutrinoSectorRefinement()
    result = inst.derive_neutrino_spectrum()
    base = result["sigma_m_base_eV"]
    refined = result["sigma_m_refined_eV"]
    expected_correction = (
        mod.MIRROR_PREFACTOR * inst.bridge_coupling * 1.0e10
    )
    assert (base - refined) == pytest.approx(expected_correction, rel=1e-12)


# ── b3_leaf / EML provenance tests -----------------------------------------


def test_module_imports_eml_operator_tree():
    """The module source must reference ``eml_operator_tree``."""
    mod = _import_module()
    source = inspect.getsource(mod)
    assert "eml_operator_tree" in source, (
        "neutrino_sector must use eml_operator_tree() for derivation tracking"
    )


def test_module_imports_b3_leaf():
    """The module source must reference ``b3_leaf`` (the b₃ = 24 seed)."""
    mod = _import_module()
    source = inspect.getsource(mod)
    assert "b3_leaf" in source, (
        "neutrino_sector must use b3_leaf() in its derivation tree "
        "(m_lightest traces to b3 = 24 via G2 Yukawa)"
    )


# ── EML-tree tests -----------------------------------------------------------
#
# These walk the EML operator tree itself, so they genuinely require the
# optional eml-math/eml-spectral extra. They SKIP rather than FAIL when it is
# absent: a missing optional cross-check must not read as a broken derivation.
# The physics tests in this file deliberately carry no such marker -- they must
# pass with or without EML.

def _eml_missing() -> bool:
    from metaphysica.simulations.core.eml_integration import EML_AVAILABLE
    return not EML_AVAILABLE


requires_eml = pytest.mark.skipif(
    _eml_missing(), reason="requires the optional eml-math/eml-spectral extra"
)

@requires_eml
def test_b3_leaf_in_m_lightest_tree():
    """Constructing the class builds an EML tree anchored at ``b3_leaf()``.

    Walking the symbolic tree must evaluate numerically to ``m_lightest``,
    while the underlying b3 seed evaluates to 24.0.
    """
    mod = _import_module()
    from metaphysica.simulations.core.eml_tree_adapter import (
        b3_leaf,
        eml_compute,
    )

    inst = mod.NeutrinoSectorRefinement()
    assert inst._m_lightest_tree is not None
    assert eml_compute(inst._m_lightest_tree) == pytest.approx(
        inst.m_lightest, rel=1e-9
    )
    assert eml_compute(b3_leaf()) == pytest.approx(24.0, rel=0.0)


def test_b3_traceback_flag_set_in_persisted_tree():
    """Formula text mentioning ``b3``/``24`` triggers the traceback flag."""
    mod = _import_module()
    inst = mod.NeutrinoSectorRefinement()
    inst.derive_neutrino_spectrum()

    tree = inst.nu_tree.get_tree()
    # m_lightest formula mentions "b3 = 24" -> traceback flag set.
    assert tree["m_lightest_eV"]["b3_traceback"] is True
    # sigma_m_base formula mentions "b3 = 24" -> traceback flag set.
    assert tree["sigma_m_base_eV"]["b3_traceback"] is True
    # Summary formula mentions "b3 = 24" -> traceback flag set.
    assert tree["refined_neutrino_sum_mass"]["b3_traceback"] is True


def test_nu_tree_is_eml_operator_tree():
    """``nu_tree`` must be an ``eml_operator_tree`` named ``neutrino_sector``."""
    mod = _import_module()
    inst = mod.NeutrinoSectorRefinement()
    assert isinstance(inst.nu_tree, eml_operator_tree)
    assert inst.nu_tree.name == "neutrino_sector"


# ── Module-level surface ---------------------------------------------------


def test_refine_neutrino_sector_is_callable():
    """Module-level entry point exists and is callable."""
    mod = _import_module()
    assert callable(mod.refine_neutrino_sector)


def test_exports():
    """``__all__`` lists the documented public surface."""
    mod = _import_module()
    assert set(mod.__all__) >= {
        "NeutrinoSectorRefinement",
        "refine_neutrino_sector",
        "DEFAULT_M_LIGHTEST",
        "DEFAULT_BRIDGE_COUPLING",
        "DELTA_M21_SQ",
        "DELTA_M31_SQ",
        "MIRROR_PREFACTOR",
        "DESI_2026_CEILING",
    }


def test_does_not_conflict_with_neutrino_mixing():
    """The new module must not shadow ``neutrino_mixing`` symbols.

    ``neutrino_mixing`` owns the PMNS-angle derivation; ``neutrino_sector``
    owns the sum-mass refinement. They must be independently importable
    and expose disjoint public callables.
    """
    from metaphysica.simulations.PM.particle import (
        neutrino_mixing,
        neutrino_sector,
    )

    mixing_attrs = {a for a in dir(neutrino_mixing) if not a.startswith("_")}
    sector_attrs = {a for a in dir(neutrino_sector) if not a.startswith("_")}
    # No overlapping *callable* public surface (constants like np / math
    # are allowed to coincide).
    overlapping_callables = {
        a
        for a in mixing_attrs & sector_attrs
        if callable(getattr(neutrino_mixing, a, None))
        and callable(getattr(neutrino_sector, a, None))
        and not isinstance(getattr(neutrino_mixing, a), type(neutrino_mixing))
    }
    # ``refine_neutrino_sector`` is unique to neutrino_sector.
    assert "refine_neutrino_sector" not in mixing_attrs
    # ``NeutrinoSectorRefinement`` is unique to neutrino_sector.
    assert "NeutrinoSectorRefinement" not in mixing_attrs
    # Whatever overlap there is, it must not include our own entry points.
    assert "refine_neutrino_sector" not in overlapping_callables
    assert "NeutrinoSectorRefinement" not in overlapping_callables
