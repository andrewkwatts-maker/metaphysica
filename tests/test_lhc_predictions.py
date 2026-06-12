"""
Test suite for :mod:`metaphysica.simulations.PM.particle.lhc_predictions`.

Verifies that the Sprint T6 #4 (T3.7) LHC SUSY spectrum predictions:

* take ``m_{3/2}`` from the Sprint T6 #1 Kahler-lifted gravitino and
  derive every LHC observable (gluino, stop, neutralino, higgsino) from
  it,
* produce positive, finite, TeV-PeV-range masses,
* obey the expected analytic ratios
  (m_{g~} = 6.5 * 0.5 * m_{3/2},
   m_{t~}^2 = m_{3/2}^2 * (1 + 5.5 * 0.25),
   m_{chi0} = 0.25 * m_{3/2},
   m_{H~} = 0.8 * m_{3/2}),
* return one of three verdicts -- ``EXCLUDED_BY_RUN3``,
  ``PROBE_AT_HL_LHC`` or ``WAITS_FOR_FCC`` -- and that the verdict
  cleanly tracks the gravitino input,
* match between the module-level entry point
  :func:`get_lhc_predictions` and a direct :class:`LHCPredictions`
  instantiation,
* register a ``b3_traceback`` flag on every derivation (since every
  formula text mentions ``m_3_2`` -> b_3 chain).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math

import pytest

from metaphysica.simulations.PM.particle.lhc_predictions import (
    DEFAULT_M_3_2_TEV,
    LHCPredictions,
    get_lhc_predictions,
)


# Analytic coefficients used in the assertions below (kept here so the
# test acts as an independent ground truth against the module).
_GLUINO_COEFF = 6.5 * 0.5            # 6.5 * m_{1/2}, m_{1/2} = 0.5 m_{3/2}
_SQUARK_M12_SQ_COEFF = 5.5 * 0.25    # 5.5 * m_{1/2}^2, m_{1/2}^2 = 0.25 m_{3/2}^2
_BINO_COEFF = 0.5 * 0.5              # 0.5 * m_{1/2}
_HIGGSINO_COEFF = 0.8                # mu = 0.8 m_{3/2}


# ----------------------------------------------------------------------
# Core sanity checks
# ----------------------------------------------------------------------


def test_full_spectrum_keys():
    """:meth:`predictions` returns the seven expected keys."""
    spectrum = LHCPredictions().predictions()
    assert set(spectrum.keys()) == {
        "m_gluino_GeV",
        "m_stop_GeV",
        "m_neutralino_GeV",
        "m_higgsino_GeV",
        "lhc_run3_reach_gluino",
        "hl_lhc_reach_gluino",
        "verdict",
    }


def test_module_entry_point_matches_class():
    """``get_lhc_predictions`` matches a fresh :class:`LHCPredictions`."""
    via_entry = get_lhc_predictions()
    via_class = LHCPredictions().predictions()
    for k, v in via_class.items():
        if isinstance(v, str):
            assert via_entry[k] == v
        else:
            assert via_entry[k] == pytest.approx(v, rel=1e-12)


# ----------------------------------------------------------------------
# Sign and finiteness checks
# ----------------------------------------------------------------------


def test_positive_finite_masses():
    """All four predicted SUSY masses are positive and finite."""
    spectrum = LHCPredictions().predictions()
    for key in (
        "m_gluino_GeV",
        "m_stop_GeV",
        "m_neutralino_GeV",
        "m_higgsino_GeV",
    ):
        assert spectrum[key] > 0.0, f"{key} should be > 0, got {spectrum[key]!r}"
        assert math.isfinite(spectrum[key]), (
            f"{key} not finite: {spectrum[key]!r}"
        )


def test_masses_in_tev_pev_range():
    """All masses live in the TeV - PeV window expected of LHC-scale SUSY."""
    spectrum = LHCPredictions().predictions()
    # 100 GeV (PDG light-chargino floor) to 1e9 GeV (well above HL-LHC)
    for key in (
        "m_gluino_GeV",
        "m_stop_GeV",
        "m_neutralino_GeV",
        "m_higgsino_GeV",
    ):
        assert 1.0e2 < spectrum[key] < 1.0e9, (
            f"{key} out of TeV-PeV range: {spectrum[key]!r}"
        )


# ----------------------------------------------------------------------
# Analytic-ratio checks
# ----------------------------------------------------------------------


def test_gluino_mass_closed_form():
    """m_{g~} = 6.5 * 0.5 * m_{3/2}."""
    m_3_2_GeV = DEFAULT_M_3_2_TEV * 1.0e3
    spectrum = LHCPredictions().predictions()
    assert spectrum["m_gluino_GeV"] == pytest.approx(
        _GLUINO_COEFF * m_3_2_GeV, rel=1e-12,
    )


def test_stop_mass_closed_form():
    """m_{t~} = sqrt(m_{3/2}^2 + 5.5 * (0.5 m_{3/2})^2)."""
    m_3_2_GeV = DEFAULT_M_3_2_TEV * 1.0e3
    spectrum = LHCPredictions().predictions()
    expected = math.sqrt(m_3_2_GeV ** 2 * (1.0 + _SQUARK_M12_SQ_COEFF))
    assert spectrum["m_stop_GeV"] == pytest.approx(expected, rel=1e-12)


def test_neutralino_mass_closed_form():
    """m_{chi0} = 0.25 * m_{3/2} (bino-like)."""
    m_3_2_GeV = DEFAULT_M_3_2_TEV * 1.0e3
    spectrum = LHCPredictions().predictions()
    assert spectrum["m_neutralino_GeV"] == pytest.approx(
        _BINO_COEFF * m_3_2_GeV, rel=1e-12,
    )


def test_higgsino_mass_closed_form():
    """m_{H~} = 0.8 * m_{3/2} (mu-term)."""
    m_3_2_GeV = DEFAULT_M_3_2_TEV * 1.0e3
    spectrum = LHCPredictions().predictions()
    assert spectrum["m_higgsino_GeV"] == pytest.approx(
        _HIGGSINO_COEFF * m_3_2_GeV, rel=1e-12,
    )


def test_gluino_heavier_than_stop():
    """At the Sprint T6 default the gluino is heavier than the stop.

    With m_{3/2} = 1 TeV: m_{g~} ~ 3.25 TeV, m_{t~} ~ 1.84 TeV.  This
    is the standard ordering at universal moduli mediation and tests
    that the running coefficients have not been accidentally swapped.
    """
    spectrum = LHCPredictions().predictions()
    assert spectrum["m_gluino_GeV"] > spectrum["m_stop_GeV"]


def test_higgsino_heavier_than_neutralino():
    """mu = 0.8 m_{3/2} > 0.25 m_{3/2} = m_{chi0} by construction."""
    spectrum = LHCPredictions().predictions()
    assert spectrum["m_higgsino_GeV"] > spectrum["m_neutralino_GeV"]


# ----------------------------------------------------------------------
# Verdict resolution
# ----------------------------------------------------------------------


def test_verdict_default_is_waits_for_fcc():
    """At m_{3/2} = 1 TeV the gluino is ~3.25 TeV > 3.0 TeV HL-LHC reach."""
    spectrum = LHCPredictions().predictions()
    assert spectrum["verdict"] == "WAITS_FOR_FCC"


def test_verdict_excluded_for_light_gravitino():
    """At m_{3/2} = 0.5 TeV: m_{g~} ~ 1.625 TeV <= 2.2 TeV Run 3 reach."""
    spectrum = LHCPredictions(m_3_2_TeV=0.5).predictions()
    assert spectrum["verdict"] == "EXCLUDED_BY_RUN3"


def test_verdict_probe_at_hl_lhc_for_medium_gravitino():
    """At m_{3/2} = 0.85 TeV: m_{g~} ~ 2.76 TeV in (2.2, 3.0] TeV window."""
    spectrum = LHCPredictions(m_3_2_TeV=0.85).predictions()
    assert spectrum["verdict"] == "PROBE_AT_HL_LHC"


def test_verdict_membership():
    """Verdict is always one of the three expected strings."""
    spectrum = LHCPredictions().predictions()
    assert spectrum["verdict"] in {
        "EXCLUDED_BY_RUN3",
        "PROBE_AT_HL_LHC",
        "WAITS_FOR_FCC",
    }


# ----------------------------------------------------------------------
# Reach numbers are stable experimental inputs
# ----------------------------------------------------------------------


def test_run3_reach_is_2_2_tev():
    """LHC Run 3 reach pinned at 2.2 TeV (ATLAS/CMS 2024 projection)."""
    spectrum = LHCPredictions().predictions()
    assert spectrum["lhc_run3_reach_gluino"] == pytest.approx(2.2e3)


def test_hl_lhc_reach_is_3_tev():
    """HL-LHC reach pinned at 3.0 TeV (3 ab^-1 projection)."""
    spectrum = LHCPredictions().predictions()
    assert spectrum["hl_lhc_reach_gluino"] == pytest.approx(3.0e3)


# ----------------------------------------------------------------------
# EML tree registration / b3 traceback
# ----------------------------------------------------------------------


def test_eml_tree_records_all_observables():
    """Every predicted observable plus the rolled-up spectrum is registered."""
    sim = LHCPredictions()
    sim.predictions()
    tree = sim.lhc_tree.get_tree()
    for key in (
        "m_gluino_GeV",
        "m_stop_GeV",
        "m_neutralino_GeV",
        "m_higgsino_GeV",
        "full_lhc_spectrum",
        "verdict",
    ):
        assert key in tree, (
            f"{key!r} missing from EML lhc_predictions tree; "
            f"got keys={list(tree)!r}"
        )


def test_eml_tree_b3_traceback_on_gluino():
    """Gluino formula cites m_3_2 -> b3 chain, so b3_traceback=True."""
    sim = LHCPredictions()
    sim.predictions()
    tree = sim.lhc_tree.get_tree()
    entry = tree["m_gluino_GeV"]
    assert entry.get("b3_traceback") is True, (
        "m_gluino_GeV derivation should be flagged b3_traceback=True; "
        f"got entry={entry!r}"
    )


# ----------------------------------------------------------------------
# Custom-input sanity (different m_{3/2} propagates correctly)
# ----------------------------------------------------------------------


def test_custom_gravitino_scales_linearly_for_gluino():
    """Doubling m_{3/2} doubles m_{g~} (linear in m_{1/2})."""
    spectrum_1 = LHCPredictions(m_3_2_TeV=1.0).predictions()
    spectrum_2 = LHCPredictions(m_3_2_TeV=2.0).predictions()
    assert spectrum_2["m_gluino_GeV"] == pytest.approx(
        2.0 * spectrum_1["m_gluino_GeV"], rel=1e-12,
    )


def test_custom_gravitino_scales_linearly_for_stop():
    """Doubling m_{3/2} doubles m_{t~} (both terms scale as m_{3/2}^2)."""
    spectrum_1 = LHCPredictions(m_3_2_TeV=1.0).predictions()
    spectrum_2 = LHCPredictions(m_3_2_TeV=2.0).predictions()
    assert spectrum_2["m_stop_GeV"] == pytest.approx(
        2.0 * spectrum_1["m_stop_GeV"], rel=1e-12,
    )
