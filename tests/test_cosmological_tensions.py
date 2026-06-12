"""Tests for ``metaphysica.simulations.PM.cosmology.cosmological_tensions``.

Sprint 5 task #5 (Phase H) verification:

1. Numerical formulae match the PossibleImprovements.txt template
   (lines 1193-1226).
2. Validation gates pass:  ``65 < H0_resolved < 75`` and
   ``0.7 < S8_resolved < 0.9``.
3. The derivation chain reaches the b₃ = 24 seed via the
   ``eml_operator_tree`` adapter (formula text mentions ``b3`` / ``24``,
   so the ``b3_traceback`` flag fires automatically).
"""

from __future__ import annotations

import inspect
import math

import pytest

from metaphysica.simulations.core.eml_tree_adapter import eml_operator_tree
from metaphysica.simulations.PM.cosmology.cosmological_tensions import (
    CosmologicalTensionsResolver,
    DEFAULT_MIRROR_COUPLING,
    DEFAULT_RET_STABILIZED,
    DELTA_W_NEEDED_TO_RESOLVE_H0,
    F_EDE_TARGET_RESOLUTION,
    G_STAR_RECOMB,
    H0_BASELINE_KM_S_MPC,
    H0_LINEAR_RESPONSE,
    H0_PER_F_EDE,
    H0_TENSION_REMAINING_SIGMA,
    MIRROR_DE_AMPLITUDE,
    N_KK_BRIDGES,
    N_KK_FULL_TOWER,
    RET_DECAY_SCALE_GEV,
    RHO_KK_THRESHOLD_PREFACTOR,
    S8_BASELINE,
    S8_LINEAR_RESPONSE,
    S8_TENSION_REMAINING_SIGMA,
    T_RECOMB_EV,
    resolve_cosmological_tensions,
)


# ──────────────────────────────────────────────────────────────────────────
# Constructor defaults
# ──────────────────────────────────────────────────────────────────────────


def test_default_constructor_inputs() -> None:
    """Defaults match Sprint 4 ReT (174.033) and Sprint 5.1 mirror (1.2e-10)."""
    sim = CosmologicalTensionsResolver()
    assert sim.ReT == pytest.approx(174.033)
    assert sim.mirror_coupling == pytest.approx(1.2e-10)
    assert sim.ReT == pytest.approx(DEFAULT_RET_STABILIZED)
    assert sim.mirror_coupling == pytest.approx(DEFAULT_MIRROR_COUPLING)


def test_constructor_overrides_propagate() -> None:
    """Custom inputs flow through to the computation."""
    sim = CosmologicalTensionsResolver(
        mirror_coupling=5.0e-10, ReT_stabilized=200.0
    )
    assert sim.mirror_coupling == pytest.approx(5.0e-10)
    assert sim.ReT == pytest.approx(200.0)


def test_constructor_rejects_nonpositive_mirror_coupling() -> None:
    """Zero / negative mirror couplings are rejected."""
    with pytest.raises(ValueError):
        CosmologicalTensionsResolver(mirror_coupling=0.0)
    with pytest.raises(ValueError):
        CosmologicalTensionsResolver(mirror_coupling=-1e-10)


def test_constructor_rejects_nonpositive_ReT() -> None:
    """Zero / negative Re(T) values are rejected."""
    with pytest.raises(ValueError):
        CosmologicalTensionsResolver(ReT_stabilized=0.0)
    with pytest.raises(ValueError):
        CosmologicalTensionsResolver(ReT_stabilized=-1.0)


# ──────────────────────────────────────────────────────────────────────────
# Core formula checks (match template lines 1193-1226 exactly)
# ──────────────────────────────────────────────────────────────────────────


def test_mirror_dark_energy_contribution_formula() -> None:
    """Δw = 0.012 · exp(−Re(T)/200) · g_mirror at default inputs."""
    sim = CosmologicalTensionsResolver()
    delta_w = sim.mirror_dark_energy_contribution()
    expected = (
        MIRROR_DE_AMPLITUDE
        * math.exp(-DEFAULT_RET_STABILIZED / RET_DECAY_SCALE_GEV)
        * DEFAULT_MIRROR_COUPLING
    )
    assert math.isclose(delta_w, expected, rel_tol=1e-12)


def test_resolve_H0_tension_formula() -> None:
    """H₀_resolved = 73.04 + 5.8 · Δw."""
    sim = CosmologicalTensionsResolver()
    delta_w = 1e-3
    H0_resolved = sim.resolve_H0_tension(delta_w)
    expected = H0_BASELINE_KM_S_MPC + H0_LINEAR_RESPONSE * delta_w
    assert math.isclose(H0_resolved, expected, rel_tol=1e-12)
    # SH0ES anchor.
    assert H0_BASELINE_KM_S_MPC == pytest.approx(73.04)


def test_resolve_S8_tension_formula() -> None:
    """S₈_resolved = 0.83 − 0.085 · Δw."""
    sim = CosmologicalTensionsResolver()
    delta_w = 1e-3
    S8_resolved = sim.resolve_S8_tension(delta_w)
    expected = S8_BASELINE - S8_LINEAR_RESPONSE * delta_w
    assert math.isclose(S8_resolved, expected, rel_tol=1e-12)


def test_resolve_H0_tension_sign() -> None:
    """ΔH₀ is positive — mirror DE shifts H₀ *upward*."""
    sim = CosmologicalTensionsResolver()
    H0_at_zero = sim.resolve_H0_tension(0.0)
    H0_at_positive = sim.resolve_H0_tension(1.0)
    assert H0_at_positive > H0_at_zero


def test_resolve_S8_tension_sign() -> None:
    """ΔS₈ is negative — mirror DE *suppresses* S₈."""
    sim = CosmologicalTensionsResolver()
    S8_at_zero = sim.resolve_S8_tension(0.0)
    S8_at_positive = sim.resolve_S8_tension(1.0)
    assert S8_at_positive < S8_at_zero


# ──────────────────────────────────────────────────────────────────────────
# Pipeline / public dict shape
# ──────────────────────────────────────────────────────────────────────────


def test_derive_tension_resolution_returns_canonical_keys() -> None:
    """The full pipeline returns the documented-tension key set."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    expected_keys = {
        "delta_w_mirror",
        "H0_baseline_km_s_Mpc",
        "H0_resolved_km_s_Mpc",
        "S8_baseline",
        "S8_resolved",
        "H0_tension_remaining_sigma",
        "S8_tension_remaining_sigma",
        "status",
        "cosmological_tensions_status",
        "documented_divergence",
    }
    assert expected_keys.issubset(set(result.keys())), (
        f"missing keys: {expected_keys - set(result.keys())!r}"
    )


def test_derive_tension_resolution_status_is_documented_tension() -> None:
    """The status string flags the tension as DOCUMENTED, not resolved."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    assert "DOCUMENTED_TENSION" in result["status"], (
        "Sprint T1 #6: status must flag the tension as DOCUMENTED rather "
        "than claiming resolution, since Δw is ~10^13× too small."
    )
    # The previous "resolved" wording must NOT appear.
    assert "relaxed to <1sigma" not in result["status"]


def test_resolved_values_match_baselines_at_canonical_inputs() -> None:
    """At canonical inputs H0/S8 sit at their baselines — tension unmoved."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    # The "resolved" value is numerically indistinguishable from the
    # SH0ES H₀ anchor because Δw is ~6e-13.
    assert math.isclose(
        result["H0_resolved_km_s_Mpc"],
        H0_BASELINE_KM_S_MPC,
        abs_tol=1e-10,
    )
    assert math.isclose(
        result["S8_resolved"],
        S8_BASELINE,
        abs_tol=1e-12,
    )


def test_remaining_tension_sigmas_reported() -> None:
    """The dict reports the unmoved H0/S8 tension significances."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    assert result["H0_tension_remaining_sigma"] == pytest.approx(
        H0_TENSION_REMAINING_SIGMA
    )
    assert result["S8_tension_remaining_sigma"] == pytest.approx(
        S8_TENSION_REMAINING_SIGMA
    )
    # Both tensions remain above 1σ — i.e. NOT resolved.
    assert result["H0_tension_remaining_sigma"] > 1.0
    assert result["S8_tension_remaining_sigma"] > 1.0


def test_documented_divergence_present_and_well_formed() -> None:
    """``documented_divergence`` records the Δw magnitude gap."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    assert "documented_divergence" in result
    div = result["documented_divergence"]
    assert isinstance(div, dict)
    for key in (
        "delta_w_needed_to_resolve_H0",
        "delta_w_actual",
        "magnitude_gap",
        "note",
    ):
        assert key in div, f"documented_divergence missing key {key!r}"

    # The framework needs a Δw of order 10⁻² but produces ~6×10⁻¹³,
    # so the magnitude_gap is |−0.012 / 6e-13| ≈ 2×10¹⁰. The test
    # asserts the gap is huge (> 10⁹) to flag the magnitude shortfall
    # without pinning the exact figure (which depends on the precise
    # Δw_actual computed from current g_mirror and Re(T)).
    assert abs(div["magnitude_gap"]) > 1.0e9, (
        f"magnitude_gap = {div['magnitude_gap']!r} should exceed 10^9 "
        "to reflect the order-of-magnitude undershoot of the mirror "
        "coupling (actual ~2×10^10 with canonical inputs)."
    )
    # Needed Δw is the documented module-level constant.
    assert div["delta_w_needed_to_resolve_H0"] == pytest.approx(
        DELTA_W_NEEDED_TO_RESOLVE_H0
    )
    # Actual Δw matches the standalone field.
    assert div["delta_w_actual"] == pytest.approx(
        result["delta_w_mirror"]
    )


def test_module_entry_point_is_callable() -> None:
    """``resolve_cosmological_tensions`` is callable and returns a dict."""
    assert callable(resolve_cosmological_tensions)
    result = resolve_cosmological_tensions()
    assert isinstance(result, dict)
    assert "H0_resolved_km_s_Mpc" in result
    assert "S8_resolved" in result
    assert "delta_w_mirror" in result


def test_module_entry_matches_class_pipeline() -> None:
    """Module entry agrees numerically with the class pipeline."""
    module_result = resolve_cosmological_tensions()
    class_result = (
        CosmologicalTensionsResolver().derive_tension_resolution()
    )
    assert math.isclose(
        module_result["delta_w_mirror"],
        class_result["delta_w_mirror"],
        rel_tol=1e-15,
    )
    assert math.isclose(
        module_result["H0_resolved_km_s_Mpc"],
        class_result["H0_resolved_km_s_Mpc"],
        rel_tol=1e-15,
    )
    assert math.isclose(
        module_result["S8_resolved"],
        class_result["S8_resolved"],
        rel_tol=1e-15,
    )


# ──────────────────────────────────────────────────────────────────────────
# Validation gates (per Sprint 5 task #5 plan)
# ──────────────────────────────────────────────────────────────────────────


def test_H0_resolved_in_validation_window() -> None:
    """65 < H0_resolved < 75 at the canonical inputs."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    H0 = result["H0_resolved_km_s_Mpc"]
    assert 65.0 < H0 < 75.0, (
        f"H0_resolved = {H0!r} outside [65, 75]"
    )


def test_S8_resolved_in_validation_window() -> None:
    """0.7 < S8_resolved < 0.9 at the canonical inputs."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    S8 = result["S8_resolved"]
    assert 0.7 < S8 < 0.9, (
        f"S8_resolved = {S8!r} outside [0.7, 0.9]"
    )


def test_validation_gates_trigger_on_extreme_inputs() -> None:
    """Constructed inputs that would push H₀ outside [65, 75] raise."""
    # Massively amplified mirror coupling pushes H₀ above 75 (the
    # linear-response prefactor 5.8 makes the threshold easy to cross
    # at huge couplings).
    pathological = CosmologicalTensionsResolver(
        mirror_coupling=1.0e12, ReT_stabilized=DEFAULT_RET_STABILIZED
    )
    with pytest.raises(ValueError, match="H0_resolved"):
        pathological.derive_tension_resolution()


# ──────────────────────────────────────────────────────────────────────────
# Numerical expectations at default inputs
# ──────────────────────────────────────────────────────────────────────────


def test_delta_w_mirror_is_exponentially_small() -> None:
    """Δw ≈ 6.03e-13 at the canonical inputs (template + math.exp)."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    expected = (
        MIRROR_DE_AMPLITUDE
        * math.exp(-DEFAULT_RET_STABILIZED / RET_DECAY_SCALE_GEV)
        * DEFAULT_MIRROR_COUPLING
    )
    assert math.isclose(
        result["delta_w_mirror"], expected, rel_tol=1e-12
    )
    # Sanity: it's in the 1e-13 ballpark.
    assert 1e-14 < result["delta_w_mirror"] < 1e-11


def test_resolved_H0_close_to_baseline_at_canonical_inputs() -> None:
    """At Δw ≈ 6e-13 the H₀ shift is < 1e-11 km/s/Mpc."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    assert math.isclose(
        result["H0_resolved_km_s_Mpc"],
        H0_BASELINE_KM_S_MPC,
        rel_tol=0.0,
        abs_tol=1e-10,
    )


def test_resolved_S8_close_to_baseline_at_canonical_inputs() -> None:
    """At Δw ≈ 6e-13 the S₈ shift is < 1e-12."""
    result = CosmologicalTensionsResolver().derive_tension_resolution()
    assert math.isclose(
        result["S8_resolved"],
        S8_BASELINE,
        rel_tol=0.0,
        abs_tol=1e-12,
    )


# ──────────────────────────────────────────────────────────────────────────
# EML tree / b3 traceback provenance
# ──────────────────────────────────────────────────────────────────────────


def test_module_uses_eml_tree_adapter() -> None:
    """Module source must use the eml_operator_tree adapter."""
    from metaphysica.simulations.PM.cosmology import (
        cosmological_tensions as mod,
    )

    source = inspect.getsource(mod)
    assert "eml_operator_tree" in source, (
        "cosmological_tensions must use eml_operator_tree(...) for "
        "EML traceability."
    )


def test_tension_tree_is_eml_operator_tree() -> None:
    """The class carries an ``eml_operator_tree`` instance."""
    sim = CosmologicalTensionsResolver()
    assert isinstance(sim.tension_tree, eml_operator_tree)
    assert sim.tension_tree.name == "cosmological_tensions"


def test_b3_traceback_flag_in_persisted_tree() -> None:
    """All registered derivations carry the b₃ traceback flag.

    The formula text in :meth:`mirror_dark_energy_contribution`,
    :meth:`resolve_H0_tension`, :meth:`resolve_S8_tension`, and the
    summary entry all mention ``b3 = 24`` (or ``Re(T)`` which is the
    Sprint 4 stabilised modulus rooted at b3 = 24). The adapter's
    ``_formula_has_b3_traceback`` matcher therefore sets the flag.
    """
    sim = CosmologicalTensionsResolver()
    sim.derive_tension_resolution()
    tree = sim.tension_tree.get_tree()

    # All four entries appear with the b3 traceback flag set.
    for key in (
        "delta_w_mirror",
        "H0_resolved_km_s_Mpc",
        "S8_resolved",
        "full_cosmological_tension_resolution",
    ):
        assert key in tree, f"missing EML entry {key!r}"
        assert tree[key]["b3_traceback"] is True, (
            f"entry {key!r} should be flagged b3-traceable"
        )


# ──────────────────────────────────────────────────────────────────────────
# Module-level public surface
# ──────────────────────────────────────────────────────────────────────────


def test_exports() -> None:
    """``__all__`` exposes the documented public surface."""
    from metaphysica.simulations.PM.cosmology import (
        cosmological_tensions as mod,
    )

    assert "CosmologicalTensionsResolver" in mod.__all__
    assert "resolve_cosmological_tensions" in mod.__all__


# ──────────────────────────────────────────────────────────────────────────
# Sprint T6 #3 — Tier 3 KK early-dark-energy mechanism (T3.4 b)
# ──────────────────────────────────────────────────────────────────────────


def test_kk_ede_module_constants_sane() -> None:
    """The new T3.4 EDE constants take physically sensible values."""
    assert N_KK_FULL_TOWER == 288  # 12 bridges * b3 (24)
    assert N_KK_BRIDGES == 12
    # 30 * zeta(3) / pi^4 ~ 0.3702
    assert 0.36 < RHO_KK_THRESHOLD_PREFACTOR < 0.38
    # SM radiation g_* at recombination ~ 3.36
    assert 3.0 < G_STAR_RECOMB < 4.0
    # Karwal-Kamionkowski-style linear response: O(45 km/s/Mpc per f_EDE)
    assert 30.0 < H0_PER_F_EDE < 60.0
    # Target: 1-2% peak EDE (Planck-DESI midpoint).
    assert 0.005 < F_EDE_TARGET_RESOLUTION < 0.10
    # Recombination temperature in eV.
    assert 0.20 < T_RECOMB_EV < 0.40


def test_compute_kk_early_dark_energy_returns_canonical_keys() -> None:
    """The new method returns the documented payload keys."""
    sim = CosmologicalTensionsResolver()
    result = sim.compute_kk_early_dark_energy()
    expected = {
        "f_EDE_naive",
        "f_EDE_honest",
        "f_EDE_target",
        "delta_H0_pct_naive",
        "delta_H0_pct_honest",
        "delta_H0_km_s_Mpc",
        "m_kk_recomb_eV",
        "T_recomb_eV",
        "m_kk_for_target_f_EDE_eV",
        "N_KK_full_tower",
        "N_KK_bridges",
        "mechanism_viable",
        "carried_to_v28",
        "status",
    }
    assert expected.issubset(set(result.keys())), (
        f"missing keys: {expected - set(result.keys())!r}"
    )


def test_kk_ede_naive_288_formula_matches_template() -> None:
    """Naive formula: f_EDE = 288 / (M_KK / T) (template, lines 1-13)."""
    sim = CosmologicalTensionsResolver()
    result = sim.compute_kk_early_dark_energy(
        T_recomb=T_RECOMB_EV, m_kk_recomb=0.5
    )
    expected = float(N_KK_FULL_TOWER) / (0.5 / T_RECOMB_EV)
    assert math.isclose(
        result["f_EDE_naive"], expected, rel_tol=1e-12
    )
    # Sanity: ~150 — far above 1, demonstrating the naive formula is
    # unphysical.
    assert result["f_EDE_naive"] > 100.0


def test_kk_ede_honest_formula_uses_12_bridges_and_radiation_norm() -> None:
    """Honest formula: 12-bridge tower with radiation-d.o.f. normalisation."""
    sim = CosmologicalTensionsResolver()
    result = sim.compute_kk_early_dark_energy(
        T_recomb=T_RECOMB_EV, m_kk_recomb=0.5
    )
    expected = (
        RHO_KK_THRESHOLD_PREFACTOR
        / G_STAR_RECOMB
        * float(N_KK_BRIDGES)
        * (0.5 / T_RECOMB_EV)
    )
    assert math.isclose(
        result["f_EDE_honest"], expected, rel_tol=1e-12
    )
    # Sanity: ~2.5 at m_KK = T threshold — still too large, demonstrating
    # the framework needs sub-threshold m_KK for resolution.
    assert 1.0 < result["f_EDE_honest"] < 5.0


def test_kk_ede_inversion_lands_at_target_fraction() -> None:
    """The inverted m_KK gives exactly the target f_EDE."""
    sim = CosmologicalTensionsResolver()
    result = sim.compute_kk_early_dark_energy()
    # Plug m_kk_for_target back into the honest formula → f_EDE_target.
    f_ede_check = (
        RHO_KK_THRESHOLD_PREFACTOR
        / G_STAR_RECOMB
        * float(N_KK_BRIDGES)
        * (result["m_kk_for_target_f_EDE_eV"] / T_RECOMB_EV)
    )
    assert math.isclose(
        f_ede_check, F_EDE_TARGET_RESOLUTION, rel_tol=1e-10
    )


def test_kk_ede_target_mass_is_sub_threshold() -> None:
    """The required m_KK for f_EDE = 0.02 lies below the threshold T."""
    sim = CosmologicalTensionsResolver()
    result = sim.compute_kk_early_dark_energy()
    # Sub-threshold (m_KK ~ 0.015 * T_recomb ~ 4e-3 eV) — physically
    # consistent with a thermal bridge tower not contributing to ΔN_eff.
    assert 0.0 < result["m_kk_for_target_f_EDE_eV"] < T_RECOMB_EV
    # In particular ~ 4e-3 eV ~ 1.5% of T_recomb.
    ratio = result["m_kk_for_target_f_EDE_eV"] / T_RECOMB_EV
    assert 0.005 < ratio < 0.05


def test_kk_ede_delta_H0_matches_linear_response() -> None:
    """ΔH₀ = H0_PER_F_EDE · f_EDE_honest."""
    sim = CosmologicalTensionsResolver()
    result = sim.compute_kk_early_dark_energy()
    expected_dH0 = H0_PER_F_EDE * result["f_EDE_honest"]
    assert math.isclose(
        result["delta_H0_km_s_Mpc"], expected_dH0, rel_tol=1e-12
    )


def test_kk_ede_status_flags_v28() -> None:
    """The status string flags carry-forward to v28."""
    sim = CosmologicalTensionsResolver()
    result = sim.compute_kk_early_dark_energy()
    assert "KK_EDE_MECHANISM_SCOPED_V28" in result["status"]
    # The sub-threshold mass is viable as a *target*, but the v27
    # framework doesn't yet derive it from b3 / k_gimel — carried to v28.
    assert result["carried_to_v28"] is True
    assert result["mechanism_viable"] is True


def test_kk_ede_rejects_nonpositive_T_or_mass() -> None:
    """Guard against pathological inputs."""
    sim = CosmologicalTensionsResolver()
    with pytest.raises(ValueError):
        sim.compute_kk_early_dark_energy(T_recomb=0.0)
    with pytest.raises(ValueError):
        sim.compute_kk_early_dark_energy(T_recomb=-0.1)
    with pytest.raises(ValueError):
        sim.compute_kk_early_dark_energy(m_kk_recomb=0.0)
    with pytest.raises(ValueError):
        sim.compute_kk_early_dark_energy(m_kk_recomb=-1.0)


def test_kk_ede_registers_eml_tree_entries_with_b3() -> None:
    """The KK derivations register with b3 traceback."""
    sim = CosmologicalTensionsResolver()
    sim.compute_kk_early_dark_energy()
    tree = sim.tension_tree.get_tree()
    for key in (
        "f_EDE_kk_naive_288",
        "f_EDE_kk_honest_12bridges",
        "m_kk_for_target_f_EDE",
    ):
        assert key in tree, f"missing EML entry {key!r}"
        assert tree[key]["b3_traceback"] is True, (
            f"entry {key!r} should be flagged b3-traceable"
        )


def test_kk_ede_exports_present() -> None:
    """New constants are exported via ``__all__``."""
    from metaphysica.simulations.PM.cosmology import (
        cosmological_tensions as mod,
    )

    for name in (
        "N_KK_FULL_TOWER",
        "N_KK_BRIDGES",
        "G_STAR_RECOMB",
        "RHO_KK_THRESHOLD_PREFACTOR",
        "H0_PER_F_EDE",
        "F_EDE_TARGET_RESOLUTION",
        "T_RECOMB_EV",
    ):
        assert name in mod.__all__, f"missing export {name!r}"
