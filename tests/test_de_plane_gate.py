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
    _RHO_ROBUST_SPREAD,
    _RHO_SCAN,
    anchors,
    build_payload,
    chi2_at_rho,
    framework_point,
    mass_sum_rows,
    scan_rho,
    sigma_equivalent,
    write_report,
)


# ── the framework point is the registered one, not literals ─────────────────


def _registered_point():
    """(w0, wa) from the fork reader (n) and the seed reader (b3), not CANON."""
    from metaphysica.simulations.PM.cosmology.late_time_routes import (
        de_betti_n, resolve_de_betti,
    )
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path, seed_values,
    )

    b3 = seed_values(resolve_path())[0]
    option = resolve_de_betti()
    n = b3 if option == "b3_live" else de_betti_n(option)
    return {"w0": -(n - 1) / n, "wa": -1.0 / math.sqrt(b3)}


def _registered_uv():
    """(u, v) of the registered (w0, wa) against the loaded DESI DR2 anchors,
    each scaled by the error on the side of the point. Nothing typed."""
    from metaphysica.simulations.data.experimental_data_loader import get_loader

    p = _registered_point()
    w0, wa = get_loader().get_desi("w0"), get_loader().get_desi("wa")
    u = (p["w0"] - w0.value) / w0.uncertainty_toward(p["w0"])
    v = (p["wa"] - wa.value) / wa.uncertainty_toward(p["wa"])
    return u, v


def _chi2(u, v, rho):
    return (u * u - 2.0 * rho * u * v + v * v) / (1.0 - rho * rho)


def test_point_is_the_registered_point():
    p = framework_point()
    expected = _registered_point()
    assert p["w0"] == pytest.approx(expected["w0"], abs=1e-12)
    assert p["wa"] == pytest.approx(expected["wa"], abs=1e-12)


def test_marginals_match_the_registered_inputs():
    """|u| and |v| are the 1D numbers of the registered point, reproduced
    here so the double-counting claim is checkable."""
    payload = build_payload()
    eu, ev = _registered_uv()
    assert payload["one_d_marginals_sigma"]["w0"] == pytest.approx(abs(eu), abs=1e-9)
    assert payload["one_d_marginals_sigma"]["wa"] == pytest.approx(abs(ev), abs=1e-9)


# ── the chi-square surface ──────────────────────────────────────────────────


def test_chi2_at_the_scan_minimum():
    """chi2 at each scanned rho is the Mahalanobis form of the registered
    (u, v), and the scan minimum sits at the rho the registered inputs pick."""
    u, v = _registered_uv()
    expected = {rho: _chi2(u, v, rho) for rho in _RHO_SCAN}
    for rho, chi2 in expected.items():
        assert chi2_at_rho(rho) == pytest.approx(chi2, rel=1e-12)
    scan = scan_rho()
    best = min(scan, key=lambda s: s.chi2)
    assert best.rho == min(expected, key=expected.get)
    assert best.chi2 == pytest.approx(min(expected.values()), rel=1e-12)


def test_chi2_rejects_degenerate_correlation():
    with pytest.raises(ValueError):
        chi2_at_rho(1.0)
    with pytest.raises(ValueError):
        chi2_at_rho(-1.0)


def test_verdict_is_rho_robust():
    """Each scanned sigma is sigma_equivalent of the registered Mahalanobis
    chi2; the band on the active path is narrower than _RHO_ROBUST_SPREAD.

    If a future anchor update spreads this band, the 'rho-robust' language
    must be withdrawn -- this test is what forces that withdrawal to be
    conscious.
    """
    u, v = _registered_uv()
    scan = scan_rho()
    for s in scan:
        assert s.sigma_equivalent == pytest.approx(
            sigma_equivalent(_chi2(u, v, s.rho)), rel=1e-9)
    sigmas = [s.sigma_equivalent for s in scan]
    assert max(sigmas) - min(sigmas) < _RHO_ROBUST_SPREAD
    assert 3.0 < min(sigmas) <= max(sigmas) < 3.5  # the band, second check


def test_correlation_reduces_but_does_not_rescue():
    """The ellipse lowers the uncorrelated 2D sigma but the tension survives.

    The uncorrelated number is sigma_equivalent(u^2 + v^2) of the registered
    point and exceeds every scanned one (correlation helps).
    """
    u, v = _registered_uv()
    payload = build_payload()
    uncorrelated = sigma_equivalent(u * u + v * v)
    assert payload["uncorrelated_2d_sigma"] == pytest.approx(uncorrelated, rel=1e-9)
    scanned = [s.sigma_equivalent for s in scan_rho()]
    assert uncorrelated > max(scanned)
    assert all(s > 3.0 for s in scanned)


def test_gate_can_fail():
    """Mutation: a point AT the DR2 best fit must read as no tension."""
    a = anchors()
    at_best_fit = {"w0": a["w0"][0], "wa": a["wa"][0]}
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
    from metaphysica.simulations.core.canonical_values import CANON
    from metaphysica.simulations.PM.validation.de_plane_gate import plane_verdict

    u, v = _registered_uv()
    sigmas = [sigma_equivalent(_chi2(u, v, rho)) for rho in _RHO_SCAN]
    assert payload["verdict"] == plane_verdict(CANON["w0"]["status"], sigmas)
    assert "kill_condition" in payload
    lo, hi = payload["sigma_range"]
    assert lo == pytest.approx(min(sigmas), rel=1e-9)
    assert hi == pytest.approx(max(sigmas), rel=1e-9)
    assert len(payload["rho_scan"]) == len(_RHO_SCAN)
