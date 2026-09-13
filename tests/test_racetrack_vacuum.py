"""The racetrack vacuum, solved completely — and falsifiably.

Companion to test_racetrack_is_an_ansatz_not_a_vacuum.py: that file pins what
the OLD minimiser was not (its objective was |W|^2, its closed form was not
stationary). This file pins what the corrected solve IS: the declared
equations stabilise Re(T) at a supersymmetric AdS minimum matching the 37.85
incumbent, the BBN- and Higgs-calibrated values are not stationary points, and
every one of those statements must move when the declared coefficients move —
otherwise this file is reporting constants, not solving equations.
"""

from __future__ import annotations

import math

import pytest

from metaphysica.simulations.PM.cosmology.racetrack_vacuum import (
    INCUMBENT_RE_T,
    scalar_potential,
    stationary_points,
    susy_condition_roots,
    vacuum_report,
)


@pytest.fixture(scope="module")
def report():
    return vacuum_report()


# ------------------------------------------------------------ the vacuum


def test_the_declared_equations_stabilise_the_modulus(report):
    for label in ("cy_no_scale", "g2_seven_thirds"):
        branch = report["branches"][label]
        assert branch["n_minima"] == 1, (
            "%s: expected exactly one minimum, found %d"
            % (label, branch["n_minima"])
        )
        assert branch["vacuum_re_t"] > 0


def test_the_vacuum_is_supersymmetric(report):
    """D_T W = 0 and full stationarity of V agree at the minimum."""
    branch = report["branches"]["cy_no_scale"]
    assert len(branch["susy_roots"]) == 1
    assert branch["vacuum_re_t"] == pytest.approx(branch["susy_roots"][0],
                                                  rel=1e-3)


def test_the_vacuum_is_ads_with_a_ds_saddle_above_it(report):
    branch = report["branches"]["cy_no_scale"]
    minima = [p for p in branch["stationary_points"] if p["kind"] == "minimum"]
    saddles = [p for p in branch["stationary_points"] if p["kind"] != "minimum"]
    assert minima[0]["V"] < 0, "the SUSY racetrack vacuum must be AdS"
    assert any(p["V"] > 0 and p["re_t"] > minima[0]["re_t"] for p in saddles), (
        "the barrier before runaway is part of the physics and must be found"
    )


def test_the_axion_direction_is_stabilised_too(report):
    """A minimum along Re(T) alone would not be a vacuum."""
    branch = report["branches"]["cy_no_scale"]
    minimum = [p for p in branch["stationary_points"]
               if p["kind"] == "minimum"][0]
    assert minimum["V_axion"] > 0


# --------------------------------------------- the six-way Re(T) verdict


def test_37_85_is_the_vacuum_of_the_declared_equations(report):
    branch = report["branches"]["cy_no_scale"]
    assert branch["vacuum_re_t"] == pytest.approx(37.85, abs=0.05)
    matches = [c for c in report["incumbent_comparison"]
               if c["is_the_vacuum_n3"]]
    assert [c["incumbent"] for c in matches] == [37.85]


def test_the_bbn_and_higgs_values_are_not_stationary_points(report):
    """7.086 and 9.865 are in live use; nothing declared produces them."""
    for label in ("cy_no_scale", "g2_seven_thirds"):
        pts = report["branches"][label]["stationary_points"]
        for cand in (7.086, 9.865, 1.833, 3.739, 174.03):
            assert not any(abs(p["re_t"] - cand) / cand < 0.01 for p in pts), (
                "%s appeared as a stationary point under %s; the register's "
                "contradiction entry is stale" % (cand, label)
            )


def test_the_kahler_fork_moves_the_vacuum_by_under_two_percent(report):
    assert report["kahler_sensitivity"] is not None
    assert report["kahler_sensitivity"] < 0.02


# ------------------------------------------------ falsifiability guards


def test_the_vacuum_moves_when_the_ratio_moves():
    """The solve must read its inputs. B/A -> -0.25 shifts ln|A/B| by ln 2,
    so the vacuum must move by roughly ln(2)/(a-b) ~ 34, not stay put."""
    a = 2 * math.pi / 24
    b = 2 * math.pi / 26
    moved = stationary_points(3, coeffs=(1.0, -0.25, a, b))
    minima = [p for p in moved if p["kind"] == "minimum"]
    assert minima, "changing B/A must not destroy the vacuum entirely"
    assert abs(minima[0]["re_t"] - 37.85) > 5.0, (
        "the vacuum did not respond to the coefficient it depends on"
    )


def test_the_exponents_are_read_from_the_declared_source():
    from metaphysica.simulations.PM.cosmology.dynamical_lambda import (
        DynamicalLambdaRelaxation,
    )

    r = vacuum_report()
    assert r["declared"]["a"] == DynamicalLambdaRelaxation.RACETRACK_a
    assert r["declared"]["b"] == DynamicalLambdaRelaxation.RACETRACK_b
    assert r["declared"]["B_over_A"] == pytest.approx(-0.5)


def test_w_vanishes_at_the_known_point():
    """Cross-check against the register's recorded W = 0 location, 34.419."""
    r = vacuum_report()
    assert r["w_zero_at"] == pytest.approx(34.419, abs=0.01)


def test_the_report_does_not_adopt(report):
    assert "author" in report["not_adopted"]
    assert "7.086" in report["not_adopted"]


def test_the_potential_is_finite_and_real_everywhere_sampled():
    for t in (0.7, 5.0, 37.85, 120.0):
        for th in (0.0, 3.0):
            v = scalar_potential(t, th, 3)
            assert math.isfinite(v)
