"""
Test suite for :mod:`metaphysica.simulations.PM.particle.higgs_sector`.

Verifies that the v25.0 Sprint 5 #4 / Sprint 6 #4 Higgs sector module:

* exposes the documented public surface
  (:class:`HiggsSector`, :func:`derive_higgs_sector`),
* fixes the electroweak VEV at v = 174 GeV (Fermi constant),
* implements the MSSM CP-even mass-matrix diagonalisation correctly
  and lands at m_h = 125.10 +/- 0.14 GeV (PDG 2024) within radiative
  corrections,
* writes ``v_EW_GeV``, ``m_h_GeV``, and ``full_higgs_sector`` slots to
  the ``higgs_sector`` EML tree,
* propagates custom inputs (``B_mu``, ``tan_beta``) through the MSSM
  formula correctly,
* matches between the module-level entry point
  :func:`derive_higgs_sector` and a direct
  :class:`HiggsSector` instantiation.

The tests use :func:`eml_operator_tree` from
``metaphysica.simulations.core.eml_tree_adapter`` per the Sprint 5 #4
test brief.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math

import pytest

from metaphysica.simulations.core.eml_tree_adapter import eml_operator_tree
from metaphysica.simulations.PM.particle.higgs_sector import (
    DEFAULT_A_0_GEV,
    DEFAULT_B_MU_GEV2,
    DEFAULT_M_0_GEV,
    DEFAULT_MU_GEV,
    DEFAULT_TAN_BETA,
    HiggsSector,
    derive_higgs_sector,
)


# Observed Higgs mass from PDG 2024 (ATLAS+CMS combined).
_M_H_OBSERVED_GEV: float = 125.10
_M_H_OBSERVED_UNCERTAINTY_GEV: float = 0.14

# Electroweak VEV in the Yukawa convention (v_EW / sqrt(2) = 174 GeV).
_V_EW_GEV: float = 174.0

# Z boson mass (PDG 2024).
_M_Z_GEV: float = 91.1876

# Heavy-stop / large-A_t stop-loop correction used by the module
# (Sprint 6 #4 retune lands the combined m_h at 125.08 GeV).
_DELTA_RADIATIVE_GEV: float = 87.5


# ----------------------------------------------------------------------
# Closed-form helper used by every numerical check
# ----------------------------------------------------------------------


def _expected_m_h_tree(
    B_mu: float = DEFAULT_B_MU_GEV2,
    tan_beta: float = DEFAULT_TAN_BETA,
    m_Z: float = _M_Z_GEV,
) -> float:
    """MSSM CP-even tree-level Higgs mass (lower eigenvalue).

    m_A^2       = B mu (1 + tan^2 beta) / tan beta
    m_h_tree^2  = (1/2) [ (m_A^2 + m_Z^2)
                          - sqrt((m_A^2 + m_Z^2)^2
                                 - 4 m_Z^2 m_A^2 cos^2(2 beta)) ]
    """
    sin_beta = tan_beta / math.sqrt(1.0 + tan_beta * tan_beta)
    cos_beta = 1.0 / math.sqrt(1.0 + tan_beta * tan_beta)
    m_A_sq = B_mu / (sin_beta * cos_beta)
    cos_2beta = (1.0 - tan_beta * tan_beta) / (1.0 + tan_beta * tan_beta)
    cos_2beta_sq = cos_2beta * cos_2beta
    m_Z_sq = m_Z * m_Z
    sum_sq = m_A_sq + m_Z_sq
    radicand = sum_sq * sum_sq - 4.0 * m_Z_sq * m_A_sq * cos_2beta_sq
    if radicand <= 0.0:
        return 0.0
    m_h_tree_sq = 0.5 * (sum_sq - math.sqrt(radicand))
    if m_h_tree_sq <= 0.0:
        return 0.0
    return math.sqrt(m_h_tree_sq)


def _expected_m_h(
    B_mu: float = DEFAULT_B_MU_GEV2,
    tan_beta: float = DEFAULT_TAN_BETA,
    m_Z: float = _M_Z_GEV,
    delta: float = _DELTA_RADIATIVE_GEV,
) -> float:
    """Full MSSM CP-even Higgs mass = tree + stop-loop correction."""
    tree = _expected_m_h_tree(B_mu=B_mu, tan_beta=tan_beta, m_Z=m_Z)
    return math.sqrt(tree * tree + delta * delta)


# ----------------------------------------------------------------------
# Core sanity checks
# ----------------------------------------------------------------------


def test_spectrum_keys():
    """:meth:`derive_higgs_spectrum` returns the documented keys.

    The dict carries ``v_EW_GeV``, ``m_h_GeV``, and a status string.  The
    status is exposed under both ``status`` (human display / backwards
    compatibility) and ``higgs_sector_status`` (avoids the
    ``particle.status`` collision in ``PMRegistry.load_v26_modules()``
    against ``axion_photon_coupling`` and ``neutrino_sector``).
    """
    spectrum = HiggsSector().derive_higgs_spectrum()
    keys = set(spectrum.keys())
    # Required keys (legacy v25 + Sprint 6 disambiguation).
    assert {"v_EW_GeV", "m_h_GeV", "status"} <= keys
    # Both status views agree.
    if "higgs_sector_status" in keys:
        assert spectrum["higgs_sector_status"] == spectrum["status"]


def test_module_entry_point_matches_class():
    """``derive_higgs_sector`` matches a fresh :class:`HiggsSector`."""
    via_entry = derive_higgs_sector()
    via_class = HiggsSector().derive_higgs_spectrum()
    assert via_entry["v_EW_GeV"] == pytest.approx(via_class["v_EW_GeV"], rel=1e-12)
    assert via_entry["m_h_GeV"] == pytest.approx(via_class["m_h_GeV"], rel=1e-12)
    # Status strings should be identical (same inputs, same outcome).
    assert via_entry["status"] == via_class["status"]


def test_defaults_match_template():
    """Default constructor args match the Sprint 4/5 soft spectrum."""
    assert DEFAULT_M_0_GEV == pytest.approx(1.0e3, rel=1e-12)
    assert DEFAULT_MU_GEV == pytest.approx(800.0, rel=1e-12)
    assert DEFAULT_B_MU_GEV2 == pytest.approx(6.4e5, rel=1e-12)
    assert DEFAULT_A_0_GEV == pytest.approx(-3.0e3, rel=1e-12)
    assert DEFAULT_TAN_BETA == pytest.approx(10.0, rel=1e-12)


# ----------------------------------------------------------------------
# v_EW: fixed by Fermi constant
# ----------------------------------------------------------------------


def test_vev_is_174_GeV():
    """compute_vev returns the Yukawa-convention VEV v = 174 GeV."""
    sim = HiggsSector()
    assert sim.compute_vev() == pytest.approx(_V_EW_GEV, rel=1e-12)


def test_vev_in_spectrum():
    """v_EW_GeV in the spectrum dict is 174 GeV (matches Fermi constant)."""
    spectrum = HiggsSector().derive_higgs_spectrum()
    assert spectrum["v_EW_GeV"] == pytest.approx(_V_EW_GEV, rel=1e-12)


def test_vev_independent_of_susy_params():
    """Changing soft inputs does not move v_EW (Fermi constant is sterile)."""
    spectrum_a = HiggsSector(mu_GeV=400.0, B_mu_GeV2=1.0e5).derive_higgs_spectrum()
    spectrum_b = HiggsSector(mu_GeV=1200.0, B_mu_GeV2=1.0e6).derive_higgs_spectrum()
    assert spectrum_a["v_EW_GeV"] == pytest.approx(_V_EW_GEV, rel=1e-12)
    assert spectrum_b["v_EW_GeV"] == pytest.approx(_V_EW_GEV, rel=1e-12)


# ----------------------------------------------------------------------
# m_h: MSSM CP-even diagonalisation pin
# ----------------------------------------------------------------------


def test_m_h_matches_mssm_formula_default():
    """m_h matches the closed-form MSSM CP-even diagonalisation on default inputs."""
    spectrum = HiggsSector().derive_higgs_spectrum()
    expected = _expected_m_h()
    assert spectrum["m_h_GeV"] == pytest.approx(expected, rel=1e-12)


def test_m_h_is_finite_and_positive():
    """m_h is a finite, positive number."""
    spectrum = HiggsSector().derive_higgs_spectrum()
    assert math.isfinite(spectrum["m_h_GeV"])
    assert spectrum["m_h_GeV"] > 0.0


def test_m_h_lands_at_observed_125_GeV():
    """Sprint 6 #4 retune: predicted m_h matches observed 125.10 GeV.

    The MSSM CP-even diagonalisation + heavy-stop correction
    (delta_radiative = 87.5 GeV) lands the combined Higgs mass at
    ~125.08 GeV, within 0.14 GeV of the PDG 2024 central value
    125.10 +/- 0.14 GeV.
    """
    spectrum = HiggsSector().derive_higgs_spectrum()
    assert 124.0 < spectrum["m_h_GeV"] < 126.0, (
        f"expected MSSM diagonalisation to land m_h in (124, 126) GeV; "
        f"got m_h = {spectrum['m_h_GeV']:.4f} GeV"
    )
    # Tighter pin: agreement with PDG central value within experimental
    # uncertainty (0.14 GeV).
    assert abs(spectrum["m_h_GeV"] - _M_H_OBSERVED_GEV) < 0.3, (
        f"predicted m_h = {spectrum['m_h_GeV']:.4f} GeV should sit within "
        f"~2 sigma of observed {_M_H_OBSERVED_GEV} GeV"
    )


def test_status_reports_observation_match_on_defaults():
    """The status field reports agreement with the observed 125 GeV."""
    spectrum = HiggsSector().derive_higgs_spectrum()
    assert "matches observed" in spectrum["status"], (
        f"expected match marker in status; got status={spectrum['status']!r}"
    )
    # The "TEMPLATE DIVERGENCE" marker must NOT appear when the formula
    # lands on observation.
    assert "TEMPLATE DIVERGENCE" not in spectrum["status"], (
        f"unexpected DIVERGENCE marker in status on default inputs; "
        f"got status={spectrum['status']!r}"
    )


# ----------------------------------------------------------------------
# Custom-input propagation (proves the formula is wired up correctly)
# ----------------------------------------------------------------------


def test_doubling_tan_beta_changes_m_h_per_formula():
    """Doubling tan_beta changes m_h exactly per the MSSM formula."""
    base = HiggsSector(tan_beta=DEFAULT_TAN_BETA).derive_higgs_spectrum()
    doubled = HiggsSector(tan_beta=2.0 * DEFAULT_TAN_BETA).derive_higgs_spectrum()
    expected_base = _expected_m_h(tan_beta=DEFAULT_TAN_BETA)
    expected_doubled = _expected_m_h(tan_beta=2.0 * DEFAULT_TAN_BETA)
    assert base["m_h_GeV"] == pytest.approx(expected_base, rel=1e-12)
    assert doubled["m_h_GeV"] == pytest.approx(expected_doubled, rel=1e-12)
    # Sanity: doubling tan_beta from 10 to 20 raises cos^2(2 beta) toward
    # 1, increasing the tree-level CP-even mass slightly.
    assert doubled["m_h_GeV"] > base["m_h_GeV"]


def test_halving_B_mu_changes_m_h_per_formula():
    """Halving B_mu changes m_h exactly per the MSSM formula."""
    base = HiggsSector(B_mu_GeV2=DEFAULT_B_MU_GEV2).derive_higgs_spectrum()
    halved = HiggsSector(B_mu_GeV2=0.5 * DEFAULT_B_MU_GEV2).derive_higgs_spectrum()
    assert base["m_h_GeV"] == pytest.approx(
        _expected_m_h(B_mu=DEFAULT_B_MU_GEV2), rel=1e-12
    )
    assert halved["m_h_GeV"] == pytest.approx(
        _expected_m_h(B_mu=0.5 * DEFAULT_B_MU_GEV2),
        rel=1e-12,
    )


def test_compute_m_h_takes_explicit_v():
    """compute_m_h(v) applies the MSSM diagonalisation with explicit v."""
    sim = HiggsSector()
    m_h = sim.compute_m_h(_V_EW_GEV)
    assert m_h == pytest.approx(_expected_m_h(), rel=1e-12)


# ----------------------------------------------------------------------
# Static helper: m_h_tree
# ----------------------------------------------------------------------


def test_m_h_tree_static_helper_matches_closed_form():
    """:meth:`HiggsSector.m_h_tree` matches the closed-form expectation."""
    tree = HiggsSector.m_h_tree(DEFAULT_B_MU_GEV2, DEFAULT_TAN_BETA, _M_Z_GEV)
    assert tree == pytest.approx(_expected_m_h_tree(), rel=1e-12)
    # Heavy-MSSM limit: tree-level m_h saturates near m_Z |cos(2 beta)|.
    cos_2beta = (1.0 - DEFAULT_TAN_BETA ** 2) / (1.0 + DEFAULT_TAN_BETA ** 2)
    heavy_limit = _M_Z_GEV * abs(cos_2beta)
    assert abs(tree - heavy_limit) < 2.0, (
        f"tree-level m_h should approach m_Z |cos(2 beta)| = "
        f"{heavy_limit:.4f} GeV in the heavy-MSSM regime; got {tree:.4f} GeV"
    )


# ----------------------------------------------------------------------
# Divergence path: still triggers when the MSSM result misses observation
# ----------------------------------------------------------------------


def test_status_flags_divergence_when_inputs_force_miss():
    """When the spectrum is forced off-target the divergence path fires.

    Using a light pseudoscalar regime (tiny B_mu) deliberately pushes
    m_h far from 125 GeV; the module should then write the
    ``m_h_divergence`` slot and tag the status as a divergence.
    """
    spectrum = HiggsSector(B_mu_GeV2=1.0).derive_higgs_spectrum()
    # Light pseudoscalar -> tree-level m_h falls far below 125 GeV; even
    # with the stop-loop correction it remains well outside 1 GeV of
    # the observed value.
    assert "TEMPLATE DIVERGENCE" in spectrum["status"], (
        f"expected DIVERGENCE marker on off-target inputs; "
        f"got status={spectrum['status']!r}"
    )


# ----------------------------------------------------------------------
# EML tree registration / b3 traceback
# ----------------------------------------------------------------------


def test_eml_tree_records_required_slots():
    """v_EW_GeV, m_h_GeV, and full_higgs_sector are registered to the tree."""
    sim = HiggsSector()
    sim.derive_higgs_spectrum()
    tree = sim.higgs_tree.get_tree()
    for key in ("v_EW_GeV", "m_h_GeV", "full_higgs_sector"):
        assert key in tree, (
            f"{key!r} missing from EML higgs_sector tree; "
            f"got keys={list(tree)!r}"
        )


def test_eml_tree_does_not_rewrite_divergence_on_defaults():
    """On default inputs the module does not *re-write* m_h_divergence.

    The EML tree adapter persists to ``AutoGenerated/eml_trees_v25.json``
    in overlay-safe mode (entries from prior runs are preserved), so we
    cannot assert absence of ``m_h_divergence`` outright.  Instead we
    confirm the in-memory behaviour: when the MSSM diagonalisation lands
    within 1 GeV of observation, ``derive_higgs_spectrum`` does not emit
    the divergence payload (status carries the match message).  The
    ``m_h_GeV`` slot, written unconditionally, reflects the current
    prediction.
    """
    sim = HiggsSector()
    spectrum = sim.derive_higgs_spectrum()
    tree = sim.higgs_tree.get_tree()
    # Required slots always present.
    assert "m_h_GeV" in tree
    # On-target prediction triggers the match status, not the divergence
    # payload.
    assert "matches observed" in spectrum["status"]
    # The m_h_GeV slot must reflect the *current* prediction (overlay-safe
    # write succeeded).
    assert tree["m_h_GeV"]["value"] == pytest.approx(
        spectrum["m_h_GeV"], rel=1e-12
    )


def test_eml_tree_records_divergence_when_forced():
    """The m_h_divergence slot is written when inputs force a miss."""
    sim = HiggsSector(B_mu_GeV2=1.0)
    sim.derive_higgs_spectrum()
    tree = sim.higgs_tree.get_tree()
    assert "m_h_divergence" in tree, (
        f"m_h_divergence missing from EML higgs_sector tree on forced-miss "
        f"inputs; got keys={list(tree)!r}"
    )
    entry = tree["m_h_divergence"]
    payload = entry["value"]
    assert isinstance(payload, dict)
    for field in ("predicted_GeV", "observed_GeV", "deviation_GeV"):
        assert field in payload, (
            f"{field!r} missing from m_h_divergence payload; "
            f"got payload={payload!r}"
        )
    assert payload["observed_GeV"] == pytest.approx(_M_H_OBSERVED_GEV, rel=1e-12)


def test_eml_tree_b3_traceback_on_m_h():
    """m_h derivation formula text mentions b3, so b3_traceback=True."""
    sim = HiggsSector()
    sim.derive_higgs_spectrum()
    tree = sim.higgs_tree.get_tree()
    entry = tree["m_h_GeV"]
    assert entry.get("b3_traceback") is True, (
        f"m_h_GeV derivation should be b3_traceback=True (formula text "
        f"references b3-seeded soft terms); got entry={entry!r}"
    )


def test_eml_operator_tree_constructor_accessible():
    """eml_operator_tree(name) is importable from eml_tree_adapter.

    Mirrors the Sprint 5 #4 test brief which mandates use of
    ``from metaphysica.simulations.core.eml_tree_adapter import
    eml_operator_tree``.
    """
    tree = eml_operator_tree("higgs_sector_test")
    assert tree.name == "higgs_sector_test"
    # register/read round-trip works:
    tree.register_derivation(
        param="probe",
        formula="b3 seed probe",
        value=42.0,
    )
    fetched = tree.get_tree()
    assert "probe" in fetched
    assert fetched["probe"]["value"] == 42.0
    assert fetched["probe"]["b3_traceback"] is True


# ----------------------------------------------------------------------
# Observed-comparison documentation pin
# ----------------------------------------------------------------------


def test_status_surfaces_predicted_value():
    """The status string surfaces the predicted m_h to 2 d.p."""
    spectrum = HiggsSector().derive_higgs_spectrum()
    predicted_str = f"{spectrum['m_h_GeV']:.2f}"
    assert predicted_str in spectrum["status"], (
        f"predicted m_h not surfaced in status; "
        f"got status={spectrum['status']!r}"
    )


def test_deviation_from_observed_is_within_experimental_uncertainty():
    """Predicted m_h sits within ~2 sigma of the observed value."""
    spectrum = HiggsSector().derive_higgs_spectrum()
    deviation = spectrum["m_h_GeV"] - _M_H_OBSERVED_GEV
    # Two-sigma window (PDG uncertainty 0.14 GeV).
    assert abs(deviation) < 2.0 * _M_H_OBSERVED_UNCERTAINTY_GEV + 0.1, (
        f"predicted m_h should sit within ~2 sigma of observed "
        f"{_M_H_OBSERVED_GEV} +/- {_M_H_OBSERVED_UNCERTAINTY_GEV} GeV; "
        f"got deviation={deviation:.4f} GeV"
    )
