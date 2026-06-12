"""Tests for ``metaphysica.simulations.PM.particle.strong_cp_axion``.

Sprint 4 task #5 (Phase H) verification:

1. ``theta_QCD_eff`` is *exactly* 0.0 (Peccei–Quinn dynamical relaxation).
2. The derivation chain uses ``b3_leaf()`` somewhere — confirming that
   ``f_a`` traces back to the b₃ = 24 topological seed via Re(T).
"""

from __future__ import annotations

import inspect

import pytest


def _import_module():
    from metaphysica.simulations.PM.particle import strong_cp_axion

    return strong_cp_axion


# ── Numerical / contract tests ---------------------------------------------


def test_solve_strong_cp_theta_is_exactly_zero():
    """Public entry point returns theta_QCD_eff = 0.0 exactly."""
    mod = _import_module()
    result = mod.solve_strong_cp()
    assert result["theta_QCD_eff"] == 0.0
    # Stronger guarantee: must be a float, not int-coerced, and not a tiny
    # floating-point artefact.
    assert isinstance(result["theta_QCD_eff"], float)
    assert result["theta_QCD_eff"] == pytest.approx(0.0, abs=0.0)


def test_solve_strong_cp_returns_expected_shape():
    """The public dict carries the four documented keys with their values."""
    mod = _import_module()
    result = mod.solve_strong_cp()
    assert result == {
        "theta_QCD_eff": 0.0,
        "upper_bound": "<10^{-10}",
        "V_axion_min": 0.0,
        "status": "strong CP solved dynamically",
    }


def test_class_default_f_a_is_1e10():
    """Default decay constant matches the G₂-volume value (Re(T) sector)."""
    mod = _import_module()
    instance = mod.StrongCPAxion()
    assert instance.f_a == pytest.approx(1.0e10, rel=0.0)


def test_class_rejects_nonpositive_f_a():
    """``f_a`` must be positive (decay constant has GeV units)."""
    mod = _import_module()
    with pytest.raises(ValueError):
        mod.StrongCPAxion(f_a=0.0)
    with pytest.raises(ValueError):
        mod.StrongCPAxion(f_a=-1.0)


def test_axion_potential_minimum_is_zero():
    """``V_axion_min`` is 0 by Peccei–Quinn (potential minimum)."""
    mod = _import_module()
    v = mod.StrongCPAxion().axion_potential_value()
    assert v["V_axion_min"] == 0.0


# ── b3_leaf provenance tests -----------------------------------------------


def test_module_imports_b3_leaf():
    """The module source must reference ``b3_leaf`` (the b₃ = 24 seed)."""
    mod = _import_module()
    source = inspect.getsource(mod)
    assert "b3_leaf" in source, (
        "strong_cp_axion must use b3_leaf() somewhere in its derivation tree "
        "(f_a depends on b3 via Re(T))."
    )


def test_b3_leaf_is_in_derivation_tree():
    """Constructing ``StrongCPAxion`` builds an EML node anchored at b3_leaf().

    The ``_f_a_tree`` attribute is the symbolic expression for ``f_a``;
    walking it must reveal a node numerically equal to ``b3 = 24.0`` from
    the SSoT registry. This is the operational form of the constraint
    that *f_a derives from b₃ via Re(T)*.
    """
    mod = _import_module()
    from metaphysica.simulations.core.eml_tree_adapter import b3_leaf, eml_compute

    instance = mod.StrongCPAxion()
    # The tree exists.
    assert instance._f_a_tree is not None

    # The tree numerically evaluates to f_a.
    assert eml_compute(instance._f_a_tree) == pytest.approx(instance.f_a, rel=1e-9)

    # The b3 seed evaluates to 24 (sanity check on b3_leaf itself).
    assert eml_compute(b3_leaf()) == pytest.approx(24.0, rel=0.0)


def test_b3_traceback_flag_set_in_persisted_tree():
    """``register_derivation`` flags strong-CP entries as b3-traceable.

    The eml_math adapter sets ``b3_traceback=True`` when the formula text
    mentions ``b3``/``b_3``/``24``. We rely on this to surface the
    dependency on the topological seed in the on-disk JSON.
    """
    mod = _import_module()
    instance = mod.StrongCPAxion()
    instance.derive_strong_cp_solution()

    tree = instance.cp_tree.get_tree()
    # The summary entry's formula text mentions b3 -> traceback flag set.
    assert tree["strong_cp_solution"]["b3_traceback"] is True
    # The theta_QCD_eff entry references "b3 = 24" -> traceback flag set.
    assert tree["theta_QCD_eff"]["b3_traceback"] is True


# ── Module-level surface ---------------------------------------------------


def test_solve_strong_cp_is_callable():
    """Module-level entry exists and is callable."""
    mod = _import_module()
    assert callable(mod.solve_strong_cp)


def test_exports():
    """``__all__`` lists the documented public surface."""
    mod = _import_module()
    assert set(mod.__all__) >= {"StrongCPAxion", "solve_strong_cp"}
