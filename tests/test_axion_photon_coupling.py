"""Tests for ``metaphysica.simulations.PM.particle.axion_photon_coupling``.

Sprint 5 task #3 (v26.0) verification:

1. The derived ``g_aγγ`` lies inside the BabyIAXO 2028 discovery
   window ``8·10⁻¹² < g_aγγ < 2·10⁻¹¹ GeV⁻¹`` — falsification criterion
   for the framework's axion sector.
2. The derivation tree is anchored at ``b3_leaf()`` (the b₃ = 24
   Ten-Pillar seed) so the dependency walker can trace
   ``g_aγγ → b₃``.
"""

from __future__ import annotations

import inspect

import pytest


# ── Validation window (BabyIAXO 2028 sensitivity) --------------------------

BABYIAXO_FLOOR = 8.0e-12   # GeV^-1
BABYIAXO_CEIL = 2.0e-11    # GeV^-1


def _import_module():
    from metaphysica.simulations.PM.particle import axion_photon_coupling

    return axion_photon_coupling


# ── Numerical / contract tests ---------------------------------------------


def test_derive_axion_photon_coupling_in_babyiaxo_window():
    """g_aγγ lies inside the BabyIAXO 2028 discovery window."""
    mod = _import_module()
    result = mod.derive_axion_photon_coupling()
    g = result["g_aγγ_GeV"]
    assert BABYIAXO_FLOOR < g < BABYIAXO_CEIL, (
        f"g_aγγ = {g:.3e} GeV^-1 falls outside the BabyIAXO window "
        f"({BABYIAXO_FLOOR:.1e}, {BABYIAXO_CEIL:.1e})"
    )


def test_derive_axion_photon_coupling_return_shape():
    """The public dict carries the three documented keys with their values."""
    mod = _import_module()
    result = mod.derive_axion_photon_coupling()
    # Was `assert {"g_aγγ_GeV", "f_a_GeV", "status"}` -- a non-empty set
    # literal, so always true. It checked that three strings had been typed,
    # not that the returned dict carried them, and the docstring's claim was
    # going unverified. The three `result[...]` reads below would have raised
    # KeyError anyway, so the line was inert twice over; the subset assertion
    # is what the docstring actually says.
    assert {"g_aγγ_GeV", "f_a_GeV", "status"} <= set(result), (
        "the documented keys are missing from the returned dict: %s"
        % sorted({"g_aγγ_GeV", "f_a_GeV", "status"} - set(result))
    )
    assert isinstance(result["g_aγγ_GeV"], float)
    assert result["f_a_GeV"] == pytest.approx(1.0e10, rel=0.0)
    assert result["status"] == "lies within BabyIAXO/IAXO discovery window"


def test_class_default_constructor_values():
    """Default constructor matches the v26.0 / Sprint 4 / Ten-Pillar values."""
    mod = _import_module()
    instance = mod.AxionPhotonCoupling()
    assert instance.f_a == pytest.approx(1.0e10, rel=0.0)
    assert instance.ReT == pytest.approx(174.033, rel=0.0)
    assert instance.b3 == 24


def test_class_rejects_nonpositive_inputs():
    """All three constructor args must be positive."""
    mod = _import_module()
    with pytest.raises(ValueError):
        mod.AxionPhotonCoupling(f_a=0.0)
    with pytest.raises(ValueError):
        mod.AxionPhotonCoupling(f_a=-1.0)
    with pytest.raises(ValueError):
        mod.AxionPhotonCoupling(ReT_stabilized=0.0)
    with pytest.raises(ValueError):
        mod.AxionPhotonCoupling(b3=0)


def test_compute_anomaly_coefficient_matches_expected():
    """C_aγγ = (b3/2π) · exp(−ReT/200) ≈ 1.60 for defaults."""
    import math

    mod = _import_module()
    instance = mod.AxionPhotonCoupling()
    C = instance.compute_anomaly_coefficient()
    expected = (24.0 / (2.0 * math.pi)) * math.exp(-174.033 / 200.0)
    assert C == pytest.approx(expected, rel=1e-12)
    # Sanity: roughly 1.6 ± 0.1.
    assert 1.5 < C < 1.7


def test_compute_g_a_gamma_gamma_uses_alpha_em():
    """The g_aγγ formula reproduces (α_EM/(2π f_a)) · C · S."""
    import math

    mod = _import_module()
    instance = mod.AxionPhotonCoupling()
    C = instance.compute_anomaly_coefficient()
    g = instance.compute_g_a_gamma_gamma(C)
    expected = (
        (mod.ALPHA_EM / (2.0 * math.pi * instance.f_a))
        * C
        * mod.AXION_PHOTON_SCALE
    )
    assert g == pytest.approx(expected, rel=1e-12)


# ── b3_leaf provenance tests -----------------------------------------------


def test_module_imports_b3_leaf():
    """The module source must reference ``b3_leaf`` (the b₃ = 24 seed)."""
    mod = _import_module()
    source = inspect.getsource(mod)
    assert "b3_leaf" in source, (
        "axion_photon_coupling must use b3_leaf() somewhere in its "
        "derivation tree (C_aγγ depends on b3 directly)."
    )


# ── EML-tree tests -----------------------------------------------------------
#
# These inspect the EML operator tree itself (walking nodes, calling
# eml_compute), so they genuinely require the optional eml-math/eml-spectral
# extra. They SKIP rather than FAIL when it is absent -- a missing optional
# cross-check must not read as a broken derivation. The physics tests above
# deliberately carry no such marker: they must pass with or without EML.

def _eml_missing() -> bool:
    from metaphysica.simulations.core.eml_integration import EML_AVAILABLE
    return not EML_AVAILABLE


requires_eml = pytest.mark.skipif(
    _eml_missing(), reason="requires the optional eml-math/eml-spectral extra"
)

def _seed_b3() -> int:
    """The live b_3 of the adopted b3_seed branch."""
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    return seed_values(resolve_path())[0]


@requires_eml
def test_b3_leaf_is_in_C_tree():
    """The EML tree for C_aγγ is anchored at ``b3_leaf()``.

    Walking ``_C_tree`` reveals a node numerically equal to the live seed's
    b₃. This is the operational form of the constraint that *C_aγγ derives
    from b₃*.

    Measured 2026-09-22, b3_seed adoption: ``b3_leaf()`` now evaluates to
    43.0, and the tree with it, but the module's scalar path still takes
    ``self.b3`` from its own module constant ``DEFAULT_B3 = 24``. So the
    tree and the scalar DISAGREE by exactly 43/24 on the default instance --
    the recorded cost carried by ``portal-alp-photon-v23`` in
    ``core.ruled_divergences``, retired by that row's wording pass. It is
    pinned here in both directions rather than smoothed over: the ratio is
    asserted exactly, and constructing the class on the seed is asserted to
    bring the two back into agreement, which is what proves the tree is a
    faithful transcription of the formula and the gap is the stale default.
    """
    mod = _import_module()
    from metaphysica.simulations.core.eml_tree_adapter import (
        b3_leaf,
        eml_compute,
    )

    b3 = _seed_b3()
    instance = mod.AxionPhotonCoupling()
    # The tree exists.
    assert instance._C_tree is not None
    # The b3 leaf follows the seed (sanity check on b3_leaf itself).
    assert eml_compute(b3_leaf()) == pytest.approx(float(b3), rel=0.0)
    assert eml_compute(b3_leaf()) == pytest.approx(43.0, rel=0.0)

    # The default instance's scalar path is still seed-blind, and the gap is
    # exactly the ratio of the two b_3 values -- nothing else drifted.
    scalar = instance.compute_anomaly_coefficient()
    assert mod.DEFAULT_B3 == 24
    assert scalar == pytest.approx(1.6000130155615222, rel=1e-9)
    assert eml_compute(instance._C_tree) == pytest.approx(
        2.8666899862143924, rel=1e-9
    )
    assert eml_compute(instance._C_tree) / scalar == pytest.approx(
        b3 / mod.DEFAULT_B3, rel=1e-12
    )

    # Fed the seed explicitly, tree and scalar agree exactly.
    seeded = mod.AxionPhotonCoupling(b3=b3)
    assert eml_compute(seeded._C_tree) == pytest.approx(
        seeded.compute_anomaly_coefficient(), rel=1e-9
    )


@requires_eml
def test_b3_leaf_is_in_g_tree():
    """The EML tree for g_aγγ is anchored at ``b3_leaf()`` via C_aγγ.

    Same recorded divergence as ``test_b3_leaf_is_in_C_tree``, propagated
    through the linear g_aγγ relation. Measured 2026-09-22, b3_seed
    adoption: the tree gives 2.688491815337442e-11 GeV^-1 (b₃ = 43) against
    the default instance's 1.5005535713511313e-11 (DEFAULT_B3 = 24).
    Note what the seeded value means physically, recorded here because it
    is the ruling's cost and not a rounding detail: 2.69e-11 GeV^-1 sits
    ABOVE the BabyIAXO ceiling this file's window test uses, so the axion
    sector's discovery-window claim survives only on the stale default.
    """
    mod = _import_module()
    from metaphysica.simulations.core.eml_tree_adapter import eml_compute

    b3 = _seed_b3()
    instance = mod.AxionPhotonCoupling()
    assert instance._g_tree is not None
    C = instance.compute_anomaly_coefficient()
    g = instance.compute_g_a_gamma_gamma(C)
    assert g == pytest.approx(1.5005535713511313e-11, rel=1e-9)

    tree_value = eml_compute(instance._g_tree)
    assert tree_value == pytest.approx(2.688491815337442e-11, rel=1e-9)
    assert tree_value / g == pytest.approx(b3 / mod.DEFAULT_B3, rel=1e-12)
    assert not BABYIAXO_FLOOR < tree_value < BABYIAXO_CEIL, (
        "the seed-following tree value has re-entered the BabyIAXO window; "
        "if that is real the window test and this pin must be re-measured "
        "together, not silently reconciled"
    )

    # Fed the seed explicitly, tree and scalar agree exactly.
    seeded = mod.AxionPhotonCoupling(b3=b3)
    seeded_g = seeded.compute_g_a_gamma_gamma(
        seeded.compute_anomaly_coefficient()
    )
    assert eml_compute(seeded._g_tree) == pytest.approx(seeded_g, rel=1e-9)


@requires_eml
def test_b3_traceback_flag_set_in_persisted_tree():
    """``register_derivation`` flags axion-photon entries as b3-traceable.

    The eml_tree_adapter sets ``b3_traceback=True`` when the formula
    text mentions ``b3``/``b_3``/``24``. We rely on this to surface the
    dependency on the topological seed in the on-disk JSON.
    """
    mod = _import_module()
    instance = mod.AxionPhotonCoupling()
    instance.derive_axion_coupling()

    tree = instance.axion_tree.get_tree()
    # The summary entry's formula text mentions "b3 = 24" -> flagged.
    assert tree["axion_photon_coupling_summary"]["b3_traceback"] is True
    # The C_aγγ entry references "b3" -> flagged.
    assert tree["C_a_gamma_gamma"]["b3_traceback"] is True
    # The g_aγγ entry references "b3 = 24" -> flagged.
    assert tree["g_a_gamma_gamma_GeV"]["b3_traceback"] is True


# ── Module-level surface ---------------------------------------------------


def test_derive_axion_photon_coupling_is_callable():
    """Module-level entry exists and is callable."""
    mod = _import_module()
    assert callable(mod.derive_axion_photon_coupling)


def test_exports():
    """``__all__`` lists the documented public surface."""
    mod = _import_module()
    assert set(mod.__all__) >= {
        "AxionPhotonCoupling",
        "derive_axion_photon_coupling",
    }
