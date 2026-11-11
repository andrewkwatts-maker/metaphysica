"""Tests for the 2D dark-energy plane gate.

The gate replaces two correlated 1D headlines (the w0 and wa marginals of the
registered point) with one Mahalanobis number scanned over the unpublished correlation. These
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


# ── the framework point is the registered one, not literals ─────────────────


def _registered_uv():
    """(u, v) of the registered (w0, wa) against the DR2 anchors.

    w0 = -(n-1)/n with n from the dark_energy_betti fork reader; wa =
    -1/sqrt(b3) with b3 from the seed reader. Nothing typed.
    """
    from metaphysica.simulations.PM.cosmology.late_time_routes import (
        de_betti_n, resolve_de_betti,
    )
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path, seed_values,
    )

    n = de_betti_n(resolve_de_betti())
    b3 = seed_values(resolve_path())[0]
    u = (-(n - 1) / n - _W0_OBS) / _W0_SIG
    v = (-1.0 / math.sqrt(b3) - _WA_OBS) / _WA_SIG
    return u, v


def test_point_is_the_registered_point():
    from metaphysica.simulations.core.canonical_values import CANON

    p = framework_point()
    assert p["w0"] == pytest.approx(CANON["w0"]["value"])
    assert p["wa"] == pytest.approx(CANON["wa"]["value"])


def test_marginals_match_the_registered_inputs():
    """|u| and |v| are the 1D numbers of the registered point, reproduced
    here so the double-counting claim is checkable."""
    p = framework_point()
    u = (p["w0"] - _W0_OBS) / _W0_SIG
    v = (p["wa"] - _WA_OBS) / _WA_SIG
    eu, ev = _registered_uv()
    assert u == pytest.approx(eu, abs=1e-9)
    assert v == pytest.approx(ev, abs=1e-9)


# ── the chi-square surface ──────────────────────────────────────────────────


def test_chi2_at_the_scan_minimum():
    """chi2 at each scanned rho is the Mahalanobis form of the registered
    (u, v); the scan minimum is the smallest of them."""
    u, v = _registered_uv()
    expected = {
        rho: (u * u - 2.0 * rho * u * v + v * v) / (1.0 - rho * rho)
        for rho in _RHO_SCAN
    }
    for rho, chi2 in expected.items():
        assert chi2_at_rho(rho) == pytest.approx(chi2, rel=1e-12)
    assert min(s.chi2 for s in scan_rho()) == pytest.approx(
        min(expected.values()), rel=1e-12)


def test_chi2_rejects_degenerate_correlation():
    with pytest.raises(ValueError):
        chi2_at_rho(1.0)
    with pytest.raises(ValueError):
        chi2_at_rho(-1.0)


def test_verdict_is_rho_robust():
    """The load-bearing claim: every rho in the band reads 3-3.5 sigma.

    If a future anchor update spreads this band past ~0.5 sigma, the
    'rho-robust' language must be withdrawn -- this test is what forces
    that withdrawal to be conscious.
    """
    sigmas = [s.sigma_equivalent for s in scan_rho()]
    assert 3.0 < min(sigmas) <= max(sigmas) < 3.5
    assert max(sigmas) - min(sigmas) < 0.5


def test_correlation_reduces_but_does_not_rescue():
    """The ellipse lowers the uncorrelated 2D sigma but the tension survives.

    Both sides are checked: the uncorrelated number exceeds every scanned
    one (correlation helps), and every scanned one stays above 3 sigma.
    """
    u, v = _registered_uv()
    uncorrelated = sigma_equivalent(u * u + v * v)
    scanned = [s.sigma_equivalent for s in scan_rho()]
    assert uncorrelated > max(scanned)
    assert all(s > 3.0 for s in scanned)


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
