"""Tests for ``metaphysica.simulations.PM.particle.axion_photon_coupling``.

Sprint 5 task #3 (v26.0) verification, re-scoped PER BRANCH when debt (a)
closed on 2026-09-22.

The module used to carry ``DEFAULT_B3 = 24`` ("Always 24") and returned a
frozen status string claiming the BabyIAXO window whatever it computed. It now
resolves b₃ through ``resolve_flavour_b3()`` like the rest of the flavour
sector, and the window verdict is COMPUTED. So the in-window claim is no
longer a property of the module -- it is a property of the branch:

    calibrated_24   g_aγγ = 1.500554e-11  INSIDE the window (the v26 contract)
    follow_seed     g_aγγ = 2.688492e-11  ABOVE the 2e-11 ceiling (adopted)

Both are MEASURED and both are pinned below. The breach on the adopted branch
is a RECORDED COST of the b3_seed ruling: it is not to be tuned back inside
the window by adjusting AXION_PHOTON_SCALE, and a test asserting the window
unconditionally would be asserting away the cost.
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


def test_the_window_claim_holds_on_the_calibrated_branch(monkeypatch):
    """The v26 contract, regression-pinned under its own branch."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING",
                       "calibrated_24")
    mod = _import_module()
    result = mod.AxionPhotonCoupling().derive_axion_coupling()
    g = result["g_aγγ_GeV"]
    assert result["axion_b3_consumed"] == 24
    assert g == pytest.approx(1.500554e-11, rel=1e-6)
    assert BABYIAXO_FLOOR < g < BABYIAXO_CEIL
    assert result["status"].startswith("lies within")


def test_the_window_claim_FAILS_on_the_adopted_branch(monkeypatch):
    """The recorded cost of the ruling, asserted as a breach.

    This is the honest replacement for an unconditional window assertion.
    If someone re-tunes AXION_PHOTON_SCALE to put the adopted branch back
    inside the window, THIS test fails -- which is the point: the breach is
    evidence, and evidence that can be quietly removed is not evidence.
    """
    monkeypatch.setenv("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING",
                       "follow_seed")
    mod = _import_module()
    result = mod.AxionPhotonCoupling().derive_axion_coupling()
    g = result["g_aγγ_GeV"]
    assert result["axion_b3_consumed"] == 43
    assert g == pytest.approx(2.688492e-11, rel=1e-6)
    assert g > BABYIAXO_CEIL, (
        "the adopted branch is back inside the BabyIAXO window; either the "
        "seed moved or the scale factor was re-tuned to preserve a headline"
    )
    assert result["status"].startswith("ABOVE the BabyIAXO")


def test_the_status_string_is_computed_not_asserted():
    """The frozen-prose defect itself, pinned."""
    mod = _import_module()
    assert mod.window_verdict(1.0e-11).startswith("lies within")
    assert mod.window_verdict(5.0e-11).startswith("ABOVE the BabyIAXO")
    assert mod.window_verdict(1.0e-13).startswith("below the BabyIAXO")


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
    # The status is a COMPUTED verdict now, so it is checked for shape rather
    # than for one frozen sentence (that sentence was the defect).
    assert "BabyIAXO" in result["status"]
    assert "GeV^-1" in result["status"]
    assert result["axion_b3_consumed"] in (24, 43)


def test_class_default_constructor_values():
    """Default constructor: fixed scales, and a b₃ that FOLLOWS THE FORK.

    `b3` used to be pinned at 24 here, which is exactly what made the module
    seed-blind: the test agreed with the default instead of checking where
    the default came from.
    """
    mod = _import_module()
    from metaphysica.simulations.PM.particle.yukawa_derivation import (
        resolve_flavour_b3,
    )

    instance = mod.AxionPhotonCoupling()
    assert instance.f_a == pytest.approx(1.0e10, rel=0.0)
    assert instance.ReT == pytest.approx(174.033, rel=0.0)
    assert instance.b3 == resolve_flavour_b3(), (
        "the axion module stopped following the flavour fork; debt (a) has "
        "regressed and the coupling is seed-blind again"
    )


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
    """C_aγγ = (b3/2π) · exp(−ReT/200), on whichever b₃ is live."""
    import math

    mod = _import_module()
    instance = mod.AxionPhotonCoupling()
    C = instance.compute_anomaly_coefficient()
    expected = (float(instance.b3) / (2.0 * math.pi)) * math.exp(-174.033 / 200.0)
    assert C == pytest.approx(expected, rel=1e-12)


def test_the_anomaly_coefficient_moves_with_the_branch():
    """Measured on both branches, so "it follows the fork" is not just shape."""
    import math

    mod = _import_module()
    at_24 = mod.AxionPhotonCoupling(b3=24).compute_anomaly_coefficient()
    at_43 = mod.AxionPhotonCoupling(b3=43).compute_anomaly_coefficient()
    assert at_24 == pytest.approx(
        (24.0 / (2.0 * math.pi)) * math.exp(-174.033 / 200.0), rel=1e-12)
    assert at_43 == pytest.approx(at_24 * 43.0 / 24.0, rel=1e-12)


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

    DIVERGENCE HEALED 2026-09-22, when debt (a) closed. The tree always
    followed the seed; the scalar path took ``self.b3`` from the module's own
    ``DEFAULT_B3 = 24``, so the two disagreed by exactly 43/24 on a default
    instance. Routing the constructor through ``resolve_flavour_b3()`` closed
    that gap.

    NOT to be confused with the ledger row ``portal-alp-photon-v23``, which
    this test's previous docstring named as the cost being recorded. That row
    belongs to ``PM.portals.alp_portals`` -- a different module, whose
    divergence is chi_eff-coupled and therefore NOT healed by this debt. It
    was checked rather than assumed (``tests/test_triple_track.py`` still
    passes with the row in place) and it stays in the ledger.

    This now pins AGREEMENT on the live branch, and disagreement under the
    calibrated branch where the scalar genuinely is 24 by choice. Both
    directions still fail if the routing regresses.
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

    # Tree and scalar now AGREE on the default instance, because the scalar
    # path resolves the same seed the tree does.
    scalar = instance.compute_anomaly_coefficient()
    assert instance.b3 == b3
    assert eml_compute(instance._C_tree) == pytest.approx(scalar, rel=1e-9)
    assert eml_compute(instance._C_tree) == pytest.approx(
        2.8666899862143924, rel=1e-9
    )

    # The calibrated branch keeps its own value, and there the tree (which
    # always follows the seed) and the scalar differ BY DESIGN -- that is what
    # "calibrated_24" means, and it is the costed branch, not a defect.
    calibrated = mod.AxionPhotonCoupling(b3=mod.CALIBRATED_B3)
    assert eml_compute(calibrated._C_tree) / \
        calibrated.compute_anomaly_coefficient() == pytest.approx(
            b3 / mod.CALIBRATED_B3, rel=1e-12)


@requires_eml
def test_b3_leaf_is_in_g_tree():
    """The EML tree for g_aγγ is anchored at ``b3_leaf()`` via C_aγγ.

    Same healing as ``test_b3_leaf_is_in_C_tree``, propagated through the
    linear g_aγγ relation. Both paths now give 2.688491815337442e-11 GeV^-1
    on the adopted branch.

    What that value means physically is the point of the whole debt, and is
    asserted rather than noted: 2.69e-11 sits ABOVE the BabyIAXO ceiling, so
    the axion sector's discovery-window claim does NOT hold on the adopted
    path. It held only while the scalar path was frozen at 24.
    """
    mod = _import_module()
    from metaphysica.simulations.core.eml_tree_adapter import eml_compute

    b3 = _seed_b3()
    instance = mod.AxionPhotonCoupling()
    assert instance._g_tree is not None
    C = instance.compute_anomaly_coefficient()
    g = instance.compute_g_a_gamma_gamma(C)
    assert instance.b3 == b3
    assert g == pytest.approx(2.688491815337442e-11, rel=1e-9)

    tree_value = eml_compute(instance._g_tree)
    assert tree_value == pytest.approx(g, rel=1e-9)
    assert not BABYIAXO_FLOOR < tree_value < BABYIAXO_CEIL, (
        "the adopted branch has re-entered the BabyIAXO window; if that is "
        "real the window tests and this pin must be re-measured together, "
        "not silently reconciled"
    )


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
