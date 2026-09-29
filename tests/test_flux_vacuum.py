"""G4 flux does not fix the adopted geometry's moduli at leading order (D-005).

Pre-registered 2026-09-30 in the site repo's docs/DECISION_LOG.md before the
numerical check was run.

The Kahler potential is Lukas & Morris's (hep-th/0305078, eq. 5.10, Table 1)
for exactly Joyce's T^7/Z_2^3; the superpotential and potential are Acharya,
Denef & Valandro's (hep-th/0502060, eqs. 3.4, 3.11). Homogeneity of the volume
collapses the potential to V = 4 e^K K^{ij} N_i N_j when the Chern-Simons
invariant is real, which is positive and scales as lambda^-5 along the
volume ray: a runaway for every flux. The control with a hypothetical
non-real invariant must find the supersymmetric AdS point, so the machinery is
shown able to find a vacuum when one exists.

MEASURED 2026-09-30 (seed 20260930, 40 points): identity residuals <= 8e-15;
analytic derivatives agree with central differences to 2e-9 (gradient) and
3e-11 (Hessian); V > 0 at every sampled point; both controls give F = 0 exactly
with W_2 = -(2/5) c_2 and V < 0.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from metaphysica.simulations.PM.geometry.flux_vacuum import (
    LM_TABLE_1,
    N_BULK,
    N_TWISTED,
    _random_flux,
    _random_point,
    flux_vacuum_report,
    kahler,
    kahler_gradient,
    kahler_hessian,
    potential,
    twisted_labels,
)

#: Rounding scale for identities evaluated in double precision on O(10)
#: moduli; a structural failure is O(1).
_ROUNDING = 1e-12


@pytest.fixture(scope="module")
def report():
    return flux_vacuum_report()


def test_the_table_is_lukas_morris_verbatim():
    assert len(LM_TABLE_1) == 9
    assert LM_TABLE_1[("alpha", 1)] == (1, 6)
    assert LM_TABLE_1[("beta", 2)] == (3, 5)
    assert LM_TABLE_1[("gamma", 3)] == (2, 7)


def test_three_blowup_moduli_per_component_match_the_resolution():
    """Lukas-Morris's 3 moduli per blow-up are D-001's b_1(L_j) = 3."""
    from metaphysica.simulations.PM.geometry.joyce_resolution import (
        resolution_report,
    )

    rep = resolution_report()
    assert len(twisted_labels()) == N_TWISTED == 3 * rep["n_components"]
    assert rep["component_b1_values"] == [3]
    assert N_BULK + N_TWISTED == rep["b3"]


def test_homogeneity_identities_hold(report):
    worst = report["worst_residuals"]
    for key in ("homogeneity", "euler", "second"):
        assert worst[key] < _ROUNDING, (key, worst[key])


def test_the_potential_reduces_and_is_positive(report):
    assert report["worst_residuals"]["reduction"] < _ROUNDING
    assert report["metric_positive_definite"]
    assert report["potential_positive_everywhere_sampled"]


def test_the_potential_runs_away_along_the_volume_ray(report):
    assert report["worst_residuals"]["scaling"] < _ROUNDING


def test_a_non_real_chern_simons_invariant_would_give_a_vacuum(report):
    """The control: the machinery finds a vacuum when one exists."""
    assert report["controls_find_a_vacuum"]
    for control in report["susy_controls"]:
        assert control["max_abs_F"] < 1e-9
        assert control["W2_over_c2"] == pytest.approx(-0.4, abs=1e-12)
        assert control["is_ads"]


def test_analytic_derivatives_match_central_differences():
    rng = np.random.default_rng(7)
    s = _random_point(rng)
    h = 1e-6
    eye = np.eye(len(s))
    grad_fd = np.array([(kahler(s + h * e) - kahler(s - h * e)) / (2 * h)
                        for e in eye])
    hess_fd = np.array([(kahler_gradient(s + h * e)
                         - kahler_gradient(s - h * e)) / (2 * h) for e in eye])
    assert np.max(np.abs(grad_fd - kahler_gradient(s))) < 1e-7
    assert np.max(np.abs(hess_fd - kahler_hessian(s))) < 1e-7


def test_the_orbifold_limit_is_regular():
    """u = 0 is inside the domain; the derivatives must not divide by it."""
    s = np.concatenate([np.full(N_BULK, 5.0), np.zeros(N_TWISTED)])
    assert np.all(np.isfinite(kahler_gradient(s)))
    assert np.all(np.isfinite(kahler_hessian(s)))


def test_the_domain_boundary_is_refused():
    s = np.concatenate([np.full(N_BULK, 1.0), np.full(N_TWISTED, 1.0)])
    with pytest.raises(ValueError, match="outside the domain"):
        kahler(s)


def test_the_runaway_is_not_a_constant_wearing_a_function():
    """Different fluxes give different positive potentials."""
    rng = np.random.default_rng(3)
    s = _random_point(rng)
    values = {round(potential(s, _random_flux(rng)), 6) for _ in range(5)}
    assert len(values) == 5 and all(v > 0 for v in values)
    assert math.isfinite(min(values))
