"""Tests for metaphysica.simulations.PM.cosmology.baryogenesis."""
from __future__ import annotations

import math

import pytest

from metaphysica.simulations.PM.cosmology.baryogenesis import (
    ModuliBaryogenesis,
    get_baryogenesis,
)
from metaphysica.simulations.core.FormulasRegistry import get_registry

# ----------------------------------------------------------------------
# The b_3 seed this process is running on.
#
# Every number below rides on b_3: D_top = exp(-b3/2) directly, and the
# canonical eta_B through the v18 G2 cycle count k_bary = b_3 - 14. The
# b3_seed fork was adopted on 2026-09-22 (seed_43_joyce, (b_3, b_2) =
# (43, 12)); seed_24 stays runnable as the labelled off-path branch via
# METAPHYSICA_VARIANT_B3_SEED=seed_24. The registry singleton is built once
# per process, so the branch cannot be flipped mid-process -- the per-seed
# expectations are therefore tabulated and selected by the live seed, and
# each entry was MEASURED by running this module under that branch.
# ----------------------------------------------------------------------


def _live_b3() -> int:
    """The b_3 the module itself consumes, read from the same source it reads."""
    return int(get_registry().elder_kads)


# ----------------------------------------------------------------------
# Core formula checks
# ----------------------------------------------------------------------


def test_lepton_asymmetry_formula() -> None:
    """epsilon_L = 0.01 * exp(-Re(T) / 100) at default Re(T)."""
    sim = ModuliBaryogenesis()
    epsilon_L = sim.lepton_asymmetry()
    expected = 0.01 * math.exp(-174.033 / 100.0)
    assert math.isclose(epsilon_L, expected, rel_tol=1e-12)


#: b_3 -> D_top = exp(-b3 / 2). Measured 2026-09-22, b3_seed adoption, by
#: running ModuliBaryogenesis().topological_dilution() under each branch.
_D_TOP_BY_B3 = {
    24: 6.14421235332821e-06,      # off-path branch, exp(-12)
    43: 4.5990553786523166e-10,    # ADOPTED seed_43_joyce, exp(-21.5)
}


def test_topological_dilution_formula() -> None:
    """D_top = exp(-b3 / 2), with b3 read from the live seed."""
    b3 = _live_b3()
    sim = ModuliBaryogenesis()
    d_top = sim.topological_dilution()
    # the formula, against the seed the module actually consumed
    expected = math.exp(-b3 / 2.0)
    # EML evaluation has finite precision; accept ~1e-9 relative tolerance.
    assert math.isclose(d_top, expected, rel_tol=1e-9)
    # and the measured value for this branch, so a silent seed swap is caught
    assert math.isclose(d_top, _D_TOP_BY_B3[b3], rel_tol=1e-9), (
        f"D_top = {d_top:.6e} at b_3 = {b3} does not match the value measured "
        f"on that branch; the dilution scale moved without the seed moving"
    )


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
    # The comparison line is COMPUTED from the live eta_B (debt (c), closed
    # 2026-09-22). It used to be a frozen string reading "6.19e-10 ... within
    # 1.1 % (2.2 sigma)" whatever the pipeline produced, so asserting a
    # literal substring here was asserting that the caption had not been
    # edited -- not that the comparison was right. Checked for structure and
    # for agreement with the value actually returned.
    line = result["observed_comparison"]
    assert "%.6e" % result["eta_B"] in line, line
    assert "Planck 2018 + BBN" in line
    assert "sigma" in line and "%" in line
    assert "[experimental uncertainty only]" in line, (
        "the comparison stopped naming which uncertainty it used; the same "
        "value is 18.16 sigma on the experimental uncertainty and 2.40 under "
        "the theory-uncertainty policy, and conflating them is the defect"
    )
    # Secondary estimate still carries the Sprint 6.2 ~2.3e-10 value.
    secondary = result["secondary_estimate"]
    assert isinstance(secondary, dict)
    assert "eta_B" in secondary
    # The Sprint 6.2 estimate is dominated by D_top = exp(-b3/2), so it moves
    # four orders of magnitude with the seed. Measured 2026-09-22, b3_seed
    # adoption: 2.3018305698236694e-10 at b_3 = 24, 1.722962302427502e-14 at
    # b_3 = 43 (ADOPTED). Pinned per branch rather than bounded, because a
    # window wide enough to hold both would no longer constrain anything.
    secondary_by_b3 = {
        24: 2.3018305698236694e-10,
        43: 1.722962302427502e-14,
    }
    assert math.isclose(
        secondary["eta_B"], secondary_by_b3[_live_b3()], rel_tol=1e-9
    )


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


#: Planck+BBN central value and its 1 sigma.
_ETA_B_OBSERVED = 6.12e-10
_ETA_B_OBSERVED_SIGMA = 0.04e-10

#: b_3 -> (canonical eta_B, sigma vs Planck+BBN, does it agree within 3 sigma).
#: Measured 2026-09-22, b3_seed adoption, by running derive_baryogenesis()
#: under each branch. The canonical value is the v18 geometric derivation,
#: whose G2 cycle count k_bary = b_3 - 14 rides on the seed, so the seed
#: ruling moved it off the Planck agreement it had at 24. That loss is the
#: ruling's RECORDED cost -- pinned here, not hidden behind a wider bound.
_CANONICAL_ETA_B = {
    24: (6.185164569435048e-10, 1.6291142358762039, True),
    43: (6.846485445932354e-10, 18.162136148308868, False),
}


def test_eta_B_in_observed_range() -> None:
    """eta_B must lie in the observationally allowed window [1e-11, 1e-8].

    Post-T1.2 rewiring: canonical eta_B is the v18 geometric value. On the
    off-path seed_24 branch it sits 1.63 sigma from the Planck+BBN central
    value (6.12 +/- 0.04) x 10^-10; on the ADOPTED seed_43_joyce branch it
    sits 18.16 sigma away. Both are pinned, and the agreement flag is
    asserted either way, so neither the agreement nor its loss can drift
    unnoticed.
    """
    b3 = _live_b3()
    expected_eta_B, expected_sigma, agrees_with_planck = _CANONICAL_ETA_B[b3]

    result = ModuliBaryogenesis().derive_baryogenesis()
    eta_B = result["eta_B"]
    assert 1e-11 < eta_B < 1e-8, (
        f"eta_B = {eta_B:.3e} is outside the observed window "
        f"[1e-11, 1e-8]"
    )
    assert math.isclose(eta_B, expected_eta_B, rel_tol=1e-9), (
        f"eta_B = {eta_B:.6e} at b_3 = {b3} is not the value measured on "
        f"that branch ({expected_eta_B:.6e})"
    )

    sigma_dev = abs(eta_B - _ETA_B_OBSERVED) / _ETA_B_OBSERVED_SIGMA
    assert math.isclose(sigma_dev, expected_sigma, rel_tol=1e-9)
    assert (sigma_dev < 3.0) is agrees_with_planck, (
        f"eta_B = {eta_B:.3e} is {sigma_dev:.2f} sigma from Planck+BBN at "
        f"b_3 = {b3}; the recorded state of that branch is "
        f"{'agreement' if agrees_with_planck else 'disagreement'}"
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
