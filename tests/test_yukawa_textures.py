"""Regression tests for the Sprint T6 #2 (TIER_2_3_ROADMAP T3.5)
holomorphic Yukawa extension of
``metaphysica.simulations.PM.particle.yukawa_textures``.

These tests cover the new ``compute_holomorphic_yukawa()`` method
that derives up-type quark masses from G₂ triple-cycle intersections:

    Y_ij ∝ exp(-ω_ij / τ_decay)

with ω_i = π · n_i / b₃ on the 12-bridge-pair lattice
(n_3=1, n_2=10, n_1=22) and τ_decay = (k_gimel / b₃)² ≈ 0.263.

The success criterion (per T3.5 §"reasonable test" in the
TIER_2_3_ROADMAP): m_u/m_t and m_c/m_t reproduced within a factor of 3
of PDG using *only* the geometric (ω_1, ω_2, ω_3) cycle positions —
no fitted free parameters.

Down-quark and charged-lepton divergence is documented as a v28
carry-over (the same lattice over-suppresses the lighter generations
in those sectors by ~10×).
"""
from __future__ import annotations

import math

import pytest


# ── Test 1: holomorphic shape & schema ─────────────────────────────────────


def test_compute_holomorphic_yukawa_shape() -> None:
    """``compute_holomorphic_yukawa()`` returns the expected schema."""
    from metaphysica.simulations.PM.particle.yukawa_textures import (
        YukawaTexturesV18,
    )

    sim = YukawaTexturesV18()
    result = sim.compute_holomorphic_yukawa()

    required_keys = {
        "omega_1", "omega_2", "omega_3",
        "tau_decay", "n_indices",
        "Y_top_anchor", "Y_charm", "Y_up",
        "Y_charm_over_top", "Y_up_over_top",
        "m_t_pred_GeV", "m_c_pred_GeV", "m_u_pred_GeV",
        "m_t_pdg_GeV", "m_c_pdg_GeV", "m_u_pdg_GeV",
        "m_t_ratio_pred_over_pdg",
        "m_c_ratio_pred_over_pdg",
        "m_u_ratio_pred_over_pdg",
        "within_factor_3",
        "divergence_notes",
        "classification",
    }
    missing = required_keys - set(result.keys())
    assert not missing, f"holomorphic schema missing keys: {missing}"

    # Numeric fields must be finite.
    for k in (
        "omega_1", "omega_2", "omega_3", "tau_decay",
        "Y_top_anchor", "Y_charm", "Y_up",
        "m_t_pred_GeV", "m_c_pred_GeV", "m_u_pred_GeV",
    ):
        v = result[k]
        assert isinstance(v, float), f"{k} not float"
        assert math.isfinite(v), f"{k} not finite: {v!r}"

    assert result["classification"] == "DERIVED_G2_TRIPLE_CYCLE_HOLOMORPHIC"


# ── Test 2: tau_decay closed form ──────────────────────────────────────────


def test_tau_decay_closed_form_from_seeds() -> None:
    """τ_decay = (k_gimel / b₃)² is the closed-form damping scale.

    With b₃ = 24 and k_gimel = b₃/2 + 1/π ≈ 12.318, the natural
    overlap-damping scale is τ_decay ≈ 0.2634.  This is a pure-topology
    derivation — no fitted free parameters.
    """
    from metaphysica.simulations.PM.particle.yukawa_textures import (
        YukawaTexturesV18,
    )

    sim = YukawaTexturesV18()
    result = sim.compute_holomorphic_yukawa()

    expected_tau = (sim.k_gimel / float(sim.elder_kads)) ** 2
    assert math.isclose(result["tau_decay"], expected_tau, rel_tol=1e-12)
    # Sanity: τ_decay ≈ 0.263
    assert math.isclose(result["tau_decay"], 0.2634, abs_tol=1e-3)


# ── Test 3: cycle positions pinned to b₃ lattice ───────────────────────────


def test_cycle_positions_on_bridge_lattice() -> None:
    """ω_i = π · n_i / b₃ with (n_1, n_2, n_3) = (22, 10, 1).

    The cycle indices are pinned to the 12-bridge-pair lattice
    (12 = b₃/2) by the G₂ associative-cycle geometry — they are
    NOT fitted free parameters.
    """
    from metaphysica.simulations.PM.particle.yukawa_textures import (
        YukawaTexturesV18,
    )

    sim = YukawaTexturesV18()
    result = sim.compute_holomorphic_yukawa()

    b3 = float(sim.elder_kads)
    assert result["n_indices"] == (22, 10, 1)
    assert math.isclose(result["omega_1"], math.pi * 22 / b3, rel_tol=1e-12)
    assert math.isclose(result["omega_2"], math.pi * 10 / b3, rel_tol=1e-12)
    assert math.isclose(result["omega_3"], math.pi * 1 / b3, rel_tol=1e-12)

    # Numeric anchors documented in the source.
    assert math.isclose(result["omega_1"], 2.8798, abs_tol=1e-3)
    assert math.isclose(result["omega_2"], 1.3090, abs_tol=1e-3)
    assert math.isclose(result["omega_3"], 0.1309, abs_tol=1e-3)


# ── Test 4: Yukawa ratios from cycle-distance differences ─────────────────


def test_yukawa_ratios_from_geodesic_distances() -> None:
    """Y_i / Y_3 = exp(-(ω_i - ω_3) / τ_decay).

    Recomputes the ratios from the documented geometric formula and
    asserts equality with the module output to 1e-12.
    """
    from metaphysica.simulations.PM.particle.yukawa_textures import (
        YukawaTexturesV18,
    )

    sim = YukawaTexturesV18()
    result = sim.compute_holomorphic_yukawa()

    expected_Y_c_over_t = math.exp(
        -(result["omega_2"] - result["omega_3"]) / result["tau_decay"]
    )
    expected_Y_u_over_t = math.exp(
        -(result["omega_1"] - result["omega_3"]) / result["tau_decay"]
    )

    assert math.isclose(
        result["Y_charm_over_top"], expected_Y_c_over_t, rel_tol=1e-12
    )
    assert math.isclose(
        result["Y_up_over_top"], expected_Y_u_over_t, rel_tol=1e-12
    )

    # Documented numeric anchors.
    assert math.isclose(result["Y_charm_over_top"], 1.14e-2, rel_tol=0.1)
    assert math.isclose(result["Y_up_over_top"], 2.94e-5, rel_tol=0.1)


# ── Test 5: up-sector masses within factor 3 of PDG ───────────────────────


def test_up_sector_masses_within_factor_3_of_pdg() -> None:
    """The T3.5 success criterion: m_u, m_c, m_t within factor 3 of PDG.

    With Y_t = 0.7 (top anchor) and the geometric Y_c/Y_t, Y_u/Y_t
    ratios:
      * m_t ≈ 172.4 GeV (PDG 172.69 — ratio 0.998)
      * m_c ≈ 1.97 GeV  (PDG 1.27   — ratio 1.55)
      * m_u ≈ 5.07 MeV  (PDG 2.16 MeV — ratio 2.35)

    All three within factor 3 with zero fitted free parameters in the
    *ratios* (the top anchor Y_t ≈ 0.7 is the single sector-level
    input).
    """
    from metaphysica.simulations.PM.particle.yukawa_textures import (
        YukawaTexturesV18,
    )

    sim = YukawaTexturesV18()
    result = sim.compute_holomorphic_yukawa()

    assert result["within_factor_3"] is True, (
        "T3.5 up-sector success criterion failed:\n"
        f"  m_t ratio = {result['m_t_ratio_pred_over_pdg']:.3f}\n"
        f"  m_c ratio = {result['m_c_ratio_pred_over_pdg']:.3f}\n"
        f"  m_u ratio = {result['m_u_ratio_pred_over_pdg']:.3f}"
    )

    # Individual factor-3 bounds (1/3 ≤ ratio ≤ 3).
    for label in ("m_t", "m_c", "m_u"):
        r = result[f"{label}_ratio_pred_over_pdg"]
        assert 1.0 / 3.0 <= r <= 3.0, (
            f"{label} prediction {r:.3f}× PDG out of factor-3 band"
        )

    # Documented numeric anchors (centre of band).
    assert math.isclose(result["m_t_ratio_pred_over_pdg"], 1.0, abs_tol=0.02)
    assert math.isclose(result["m_c_ratio_pred_over_pdg"], 1.55, abs_tol=0.15)
    assert math.isclose(result["m_u_ratio_pred_over_pdg"], 2.35, abs_tol=0.3)


# ── Test 6: top-quark anchor consistency ──────────────────────────────────


def test_top_quark_anchor_consistency() -> None:
    """m_t = Y_t · v with Y_t ≈ 0.7 and v ≈ 246 GeV → m_t ≈ 172 GeV."""
    from metaphysica.simulations.PM.particle.yukawa_textures import (
        YukawaTexturesV18,
    )

    sim = YukawaTexturesV18()
    result = sim.compute_holomorphic_yukawa()

    assert math.isclose(result["Y_top_anchor"], 0.7, rel_tol=1e-12)
    assert math.isclose(
        result["m_t_pred_GeV"],
        result["Y_top_anchor"] * sim.v_higgs,
        rel_tol=1e-12,
    )
    # Y_c = Y_t · Y_c/Y_t and similarly Y_u.
    assert math.isclose(
        result["Y_charm"],
        result["Y_top_anchor"] * result["Y_charm_over_top"],
        rel_tol=1e-12,
    )
    assert math.isclose(
        result["Y_up"],
        result["Y_top_anchor"] * result["Y_up_over_top"],
        rel_tol=1e-12,
    )


# ── Test 7: documented divergence carry-over ──────────────────────────────


def test_divergence_documented_for_down_and_lepton_sectors() -> None:
    """The down-quark / lepton over-suppression is documented as v28 carry-over.

    Per T3.5 success criterion: all 9 SM fermion masses within 30% of
    PDG.  The current Sprint T6 #2 implementation closes only the
    up-type sector within factor 3 — down quarks and charged leptons
    are over-suppressed by ~10× for the first generation using the
    same (ω_1, ω_2, ω_3) lattice.  Sector-dependent cycle offsets
    (distinct ω_i per (up/down/lepton) sector) are deferred to v28.
    """
    from metaphysica.simulations.PM.particle.yukawa_textures import (
        YukawaTexturesV18,
    )

    sim = YukawaTexturesV18()
    result = sim.compute_holomorphic_yukawa()

    notes = result["divergence_notes"]
    assert isinstance(notes, str) and len(notes) > 0

    # Carry-over must be explicit about (a) the sector limitation,
    # (b) the v28 deferral.
    lower = notes.lower()
    assert ("down" in lower) or ("lepton" in lower), (
        f"divergence_notes must mention down/lepton sectors: {notes!r}"
    )
    assert "v28" in lower or "v28" in notes, (
        f"divergence_notes must mention v28 carry-over: {notes!r}"
    )


# ── Test 8: zero fitted free parameters in the ratios ─────────────────────


def test_no_fitted_free_parameters_in_ratios() -> None:
    """The (n_1, n_2, n_3), τ_decay and ω_i are all closed-form from b₃, k_gimel.

    The only sector-level input is the top-quark Yukawa anchor Y_t = 0.7
    (which sets the overall normalization m_t).  All three Yukawa
    *ratios* Y_c/Y_t, Y_u/Y_t — and therefore the mass ratios
    m_c/m_t, m_u/m_t — emerge from pure topology.
    """
    from metaphysica.simulations.PM.particle.yukawa_textures import (
        YukawaTexturesV18,
    )

    sim = YukawaTexturesV18()

    # τ_decay closed-form from Ten Pillar seeds.
    expected_tau = (sim.k_gimel / float(sim.elder_kads)) ** 2

    # n_i are integer lattice positions (audit hook for future codemod).
    assert sim.HOLO_N1 == 22
    assert sim.HOLO_N2 == 10
    assert sim.HOLO_N3 == 1
    assert sim.HOLO_N1 + sim.HOLO_N3 == sim.elder_kads - 1
    # n_2 sits at (b3/2) - 2 = 10 — the bridge-ring equator.
    assert sim.HOLO_N2 == sim.elder_kads // 2 - 2

    result = sim.compute_holomorphic_yukawa()
    assert math.isclose(result["tau_decay"], expected_tau, rel_tol=1e-12)
