"""Tests for metaphysica.simulations.PM.cosmology.baryogenesis."""
from __future__ import annotations

import math

import pytest

pytest.importorskip("eml_spectral", reason="eml-spectral not installed; install with pip install metaphysica[sims]")

from metaphysica.simulations.PM.cosmology.baryogenesis import (
    ModuliBaryogenesis,
    get_baryogenesis,
)


# ----------------------------------------------------------------------
# Core formula checks
# ----------------------------------------------------------------------


def test_lepton_asymmetry_formula() -> None:
    """epsilon_L = 0.01 * exp(-Re(T) / 100) at default Re(T)."""
    sim = ModuliBaryogenesis()
    epsilon_L = sim.lepton_asymmetry()
    expected = 0.01 * math.exp(-174.033 / 100.0)
    assert math.isclose(epsilon_L, expected, rel_tol=1e-12)


def test_topological_dilution_formula() -> None:
    """D_top = exp(-b3 / 2) with b3 = 24 -> D_top = exp(-12)."""
    sim = ModuliBaryogenesis()
    d_top = sim.topological_dilution()
    expected = math.exp(-12.0)
    # EML evaluation has finite precision; accept ~1e-9 relative tolerance.
    assert math.isclose(d_top, expected, rel_tol=1e-9)


def test_compute_eta_B_formula() -> None:
    """eta_B = (28/79) * epsilon_L * D_top * (Gamma / H), with H = 1.66e-2."""
    sim = ModuliBaryogenesis()
    epsilon_L = sim.lepton_asymmetry()
    d_top = sim.topological_dilution()
    eta_B = sim.compute_eta_B(epsilon_L)
    expected = (
        (28.0 / 79.0)
        * epsilon_L
        * d_top
        * (sim.decay_width / 1.66e-2)
    )
    assert math.isclose(eta_B, expected, rel_tol=1e-9)


def test_derive_baryogenesis_returns_canonical_keys() -> None:
    """derive_baryogenesis() returns the canonical key set.

    Post-T1.2 rewiring: canonical eta_B comes from the v18 G2 cycle +
    Jarlskog derivation; the Sprint 6.2 moduli-decay estimate is exposed
    via the ``secondary_estimate`` key for cross-checking.
    """
    result = ModuliBaryogenesis().derive_baryogenesis()
    assert set(result.keys()) == {
        "epsilon_L",
        "D_top",
        "eta_B",
        "eta_B_source",
        "secondary_estimate",
        "observed_comparison",
    }
    # Canonical comparison line should mention the 6e-10 ballpark.
    assert "6.19e-10" in result["observed_comparison"]
    # Secondary estimate still carries the Sprint 6.2 ~2.3e-10 value.
    secondary = result["secondary_estimate"]
    assert isinstance(secondary, dict)
    assert "eta_B" in secondary
    assert 1e-11 < secondary["eta_B"] < 1e-9


def test_module_entry_point() -> None:
    """get_baryogenesis() is a callable returning the same canonical dict."""
    result = get_baryogenesis()
    assert isinstance(result, dict)
    assert "eta_B" in result
    assert "epsilon_L" in result
    assert "D_top" in result


# ----------------------------------------------------------------------
# Validation criterion (per Sprint 4 task #6 plan)
# ----------------------------------------------------------------------


def test_eta_B_in_observed_range() -> None:
    """eta_B must lie in the observationally allowed window [1e-11, 1e-8].

    Post-T1.2 rewiring: canonical eta_B = 6.19e-10 (v18 geometric), which
    must additionally be within 3 sigma of the Planck+BBN central value
    (6.12 +/- 0.04) x 10^-10.
    """
    result = ModuliBaryogenesis().derive_baryogenesis()
    eta_B = result["eta_B"]
    assert 1e-11 < eta_B < 1e-8, (
        f"eta_B = {eta_B:.3e} is outside the observed window "
        f"[1e-11, 1e-8]"
    )
    # Canonical (v18) source: 1.6 sigma from Planck+BBN.
    eta_obs = 6.12e-10
    sigma_obs = 0.04e-10
    sigma_dev = abs(eta_B - eta_obs) / sigma_obs
    assert sigma_dev < 3.0, (
        f"eta_B = {eta_B:.3e} is {sigma_dev:.2f} sigma from Planck+BBN "
        f"(canonical v18 derivation expected ~1.6 sigma)"
    )


# ----------------------------------------------------------------------
# Parameter wiring
# ----------------------------------------------------------------------


def test_constructor_defaults() -> None:
    """Default constructor uses ReT = 174.033 and decay_width = 1e-3."""
    sim = ModuliBaryogenesis()
    assert sim.ReT == pytest.approx(174.033)
    assert sim.decay_width == pytest.approx(1e-3)


def test_constructor_overrides() -> None:
    """Custom ReT / decay_width values flow through to the computation."""
    sim = ModuliBaryogenesis(ReT=200.0, decay_width=2e-3)
    assert sim.ReT == pytest.approx(200.0)
    assert sim.decay_width == pytest.approx(2e-3)
    expected_eL = 0.01 * math.exp(-2.0)
    assert math.isclose(sim.lepton_asymmetry(), expected_eL, rel_tol=1e-12)
