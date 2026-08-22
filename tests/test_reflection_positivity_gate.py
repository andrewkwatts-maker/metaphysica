"""Tests for the reflection-positivity gate.

The gate is the framework's only falsifiable structural test, so its own
failure modes matter as much as its verdict. In particular it must not be
possible to pass it vacuously without that being reported.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from metaphysica.simulations.PM.validation.reflection_positivity_gate import (
    bridge_cross_block,
    reflection_positivity_report,
    shadow_swap,
)


def test_swap_is_an_involution():
    """The RP reflection must square to +I. This is what R_perp fails."""
    S = shadow_swap(12)
    assert np.allclose(S @ S, np.eye(24))


def test_r_perp_is_not_an_involution():
    """R_perp has order 4, so it cannot be the RP reflection.

    Guards the 2026-08-21 correction: an earlier proposal used R_perp as the
    involution, which would have failed the gate for a purely algebraic
    reason (its Gram form is antisymmetric) and been read as a ghost.
    """
    rep = reflection_positivity_report()
    assert rep["involution"]["r_perp_is_involution"] is False
    # antisymmetric => symmetric part is exactly zero
    assert rep["involution"]["r_perp_symmetric_part_norm"] == pytest.approx(0.0)


def test_acute_bridges_pass():
    """Positive cross-coupling (theta < 90 deg) is reflection positive."""
    g = np.array([[1.0, math.cos(math.radians(60))],
                  [math.cos(math.radians(60)), 1.0]])
    rep = reflection_positivity_report([g] * 12)
    assert rep["verdict"] == "PASS"
    assert rep["positive_semidefinite"] is True
    assert rep["vacuous"] is False


def test_obtuse_bridges_fail():
    """Negative cross-coupling (theta > 90 deg) is a ghost mode.

    This is the falsification direction: the gate must actually be able to
    fail, otherwise it is not a test.
    """
    g = np.array([[1.0, math.cos(math.radians(120))],
                  [math.cos(math.radians(120)), 1.0]])
    rep = reflection_positivity_report([g] * 12)
    assert rep["verdict"] == "FAIL"
    assert rep["positive_semidefinite"] is False
    assert len(rep["offending_pairs"]) == 12


def test_orthogonal_bridges_report_vacuous_not_pass():
    """The framework's own configuration sits on the RP boundary.

    Every bridge is orthogonal (theta = pi/2), so each cross-coupling is
    L1*L2*cos(pi/2) = 0 and the cross block is the zero matrix -- trivially
    PSD. That must be reported as MARGINAL_VACUOUS rather than PASS, or the
    gate would be claiming a success it did not earn.
    """
    rep = reflection_positivity_report()
    assert rep["verdict"] == "MARGINAL_VACUOUS"
    assert rep["vacuous"] is True
    assert rep["max_abs_coupling"] < 1e-12


def test_derived_constraint_is_recorded():
    """The gate's real output is a constraint on the bridge angle."""
    rep = reflection_positivity_report()
    c = rep["derived_constraint"]
    assert "90" in c["statement"]
    assert c["framework_theta_deg"] == pytest.approx(90.0)


def test_cross_block_matches_metric_off_diagonal():
    """The cross block is exactly the metric's off-diagonal, per pair."""
    gs = [np.array([[1.0, 0.25], [0.25, 1.0]]),
          np.array([[2.0, -0.5], [-0.5, 3.0]])]
    C = bridge_cross_block(gs)
    assert C[0, 0] == pytest.approx(0.25)
    assert C[1, 1] == pytest.approx(-0.5)


def test_potential_is_degenerate_under_theta_to_pi_minus_theta():
    """The racetrack potential cannot tell an acute bridge from its mirror.

    T = L1*L2*sin(theta) and sin is symmetric about pi/2, so
    V(theta) = V(pi - theta) exactly. This is why the RP gate matters: it
    breaks a degeneracy the framework's own dynamics leaves open.
    """
    from metaphysica.simulations.PM.geometry.bridge_geometry import BridgeSystem
    bs = BridgeSystem()
    for deg in (30.0, 45.0, 75.0, 89.0):
        m1 = np.column_stack(
            [np.ones(12), np.ones(12), np.full(12, math.radians(deg))]).ravel()
        m2 = np.column_stack(
            [np.ones(12), np.ones(12), np.full(12, math.radians(180.0 - deg))]).ravel()
        assert bs.racetrack_potential(m1) == pytest.approx(
            bs.racetrack_potential(m2), rel=1e-12)


def test_write_report_produces_valid_json(tmp_path):
    """The gate is wired into the build, so it must emit a machine-readable
    report like every other wired gate. It previously only printed, which is
    why it sat unwired.
    """
    import json

    from metaphysica.simulations.PM.validation.reflection_positivity_gate import (
        write_report,
    )

    out = write_report(out_path=tmp_path / "reflection_positivity.json")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["n_pass"] + payload["n_fail"] <= payload["count"]
    assert payload["verdict"] in {"PASS", "FAIL", "MARGINAL_VACUOUS"}
    assert "MARGINAL_VACUOUS" in payload["note"]


def test_vacuous_cross_block_is_not_reported_as_pass(tmp_path):
    """A zero cross block must NOT read as PASS.

    At theta = 90 degrees the metric coupling is switched off entirely, so
    there is nothing whose positivity could be certified. Reporting PASS there
    would be the same defect as an input anchor validating itself.
    """
    from metaphysica.simulations.PM.validation.reflection_positivity_gate import (
        reflection_positivity_report,
    )

    rep = reflection_positivity_report()
    if abs(rep["min_eigenvalue"]) < 1e-12:
        assert rep["verdict"] == "MARGINAL_VACUOUS", (
            "a vanishing cross block was reported as a genuine verdict"
        )
