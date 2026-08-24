"""Tests for the 2D dark-energy plane gate.

The gate replaces two correlated 1D headlines (3.62 sigma on w0, 2.98 on wa)
with one Mahalanobis number scanned over the unpublished correlation. These
tests pin the arithmetic and, critically, the ROBUSTNESS claim -- the whole
point is that the verdict does not depend on the invented-number-shaped hole
where rho should be.
"""
from __future__ import annotations

import json
import math

import pytest

from metaphysica.simulations.PM.validation.de_plane_gate import (
    _RHO_SCAN,
    _W0_OBS,
    _W0_SIG,
    _WA_OBS,
    _WA_SIG,
    chi2_at_rho,
    framework_point,
    mass_sum_rows,
    scan_rho,
    sigma_equivalent,
    write_report,
)


# ── the framework point comes from the seed, not from literals ──────────────


def test_point_is_derived_from_b3():
    from metaphysica.simulations.core.canonical_values import B3

    p = framework_point()
    assert p["w0"] == pytest.approx(-(B3 - 1) / B3)          # -23/24
    assert p["wa"] == pytest.approx(-1 / math.sqrt(B3))      # -1/sqrt(24)


def test_marginals_match_the_register_headlines():
    """|u| = 3.62 and |v| = 3.05 are the register's own 1D numbers --
    reproduced here so the double-counting claim is checkable."""
    p = framework_point()
    u = (p["w0"] - _W0_OBS) / _W0_SIG
    v = (p["wa"] - _WA_OBS) / _WA_SIG
    assert abs(u) == pytest.approx(3.620, abs=0.005)
    assert abs(v) == pytest.approx(3.051, abs=0.005)


# ── the chi-square surface ──────────────────────────────────────────────────


def test_chi2_at_the_scan_centre():
    """Pinned: chi2(-0.85) = 13.11, the scan minimum."""
    assert chi2_at_rho(-0.85) == pytest.approx(13.11, abs=0.02)


def test_chi2_rejects_degenerate_correlation():
    with pytest.raises(ValueError):
        chi2_at_rho(1.0)
    with pytest.raises(ValueError):
        chi2_at_rho(-1.0)


def test_verdict_is_rho_robust():
    """The load-bearing claim: 3.19-3.41 sigma across the whole band.

    If a future anchor update spreads this band past ~0.5 sigma, the
    'rho-robust' language must be withdrawn -- this test is what forces
    that withdrawal to be conscious.
    """
    sigmas = [s.sigma_equivalent for s in scan_rho()]
    assert min(sigmas) == pytest.approx(3.19, abs=0.02)
    assert max(sigmas) == pytest.approx(3.41, abs=0.02)
    assert max(sigmas) - min(sigmas) < 0.5


def test_correlation_reduces_but_does_not_rescue():
    """The ellipse helps (4.35 -> ~3.2) but the tension survives.

    Pinning BOTH sides keeps the narrative honest in both directions:
    anyone claiming 4.4 sigma is ignoring the correlation, and anyone
    claiming ~1 sigma is inventing one.
    """
    p = framework_point()
    u = (p["w0"] - _W0_OBS) / _W0_SIG
    v = (p["wa"] - _WA_OBS) / _WA_SIG
    uncorrelated = sigma_equivalent(u * u + v * v)
    assert uncorrelated == pytest.approx(4.35, abs=0.02)
    assert all(s.sigma_equivalent > 3.0 for s in scan_rho())


def test_gate_can_fail():
    """Mutation: a point AT the DR2 best fit must read as no tension."""
    at_best_fit = {"w0": _W0_OBS, "wa": _WA_OBS}
    assert chi2_at_rho(-0.85, at_best_fit) == pytest.approx(0.0, abs=1e-12)
    assert sigma_equivalent(0.0) == pytest.approx(0.0, abs=1e-6)


def test_sigma_equivalent_is_sane():
    """chi2 = 2.30 at 2 dof has p = exp(-1.15) = 0.317, i.e. 1.00 sigma
    two-sided. (The first pin here guessed 1.52 by conflating the 1D
    ellipse-axis convention with the two-sided Gaussian one -- the failing
    test corrected its author, which is the direction the arrow should
    point.) Monotone after."""
    assert sigma_equivalent(2.30) == pytest.approx(1.00, abs=0.01)
    values = [sigma_equivalent(c) for c in (1.0, 5.0, 10.0, 20.0)]
    assert values == sorted(values)


# ── the neutrino-mass conditional ───────────────────────────────────────────


def test_mass_rows_report_both_bounds():
    rows = [r for r in mass_sum_rows() if r.get("parameter")]
    if not rows:
        pytest.skip("parameters.json not available")
    for r in rows:
        assert r["under_lcdm"] in ("PASS", "FAIL")
        assert r["under_own_cosmology"] in ("PASS", "FAIL")


def test_the_conditional_actually_conditions():
    """At least one registered sum fails LCDM while passing the framework's
    own cosmology -- the self-consistency point the register makes in prose.

    If every row passes both bounds the conditional is vacuous, and if any
    row fails BOTH, the framework's own dark-energy sector no longer saves
    its neutrino sector and register 1.5 escalates.
    """
    rows = [r for r in mass_sum_rows() if r.get("parameter")]
    if not rows:
        pytest.skip("parameters.json not available")
    conditional = [
        r for r in rows
        if r["under_lcdm"] == "FAIL" and r["under_own_cosmology"] == "PASS"
    ]
    assert conditional, "no row exercises the conditional -- vacuous"
    assert not [
        r for r in rows
        if r["under_lcdm"] == "FAIL" and r["under_own_cosmology"] == "FAIL"
    ], "a mass sum fails even the relaxed bound -- register 1.5 escalates"


def test_report_schema(tmp_path):
    out = write_report(out_path=tmp_path / "de_plane_gate.json")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["verdict"] == "TENSION_3SIGMA_ROBUST"
    assert "kill_condition" in payload
    lo, hi = payload["sigma_range"]
    assert 3.0 < lo <= hi < 3.5
    assert len(payload["rho_scan"]) == len(_RHO_SCAN)
