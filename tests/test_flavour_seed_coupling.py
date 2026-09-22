"""The flavour fork: a formula that claims b_3 must consume b_3.

flavour_seed_coupling (2026-09-22, with the b3_seed adoption): the v25
flavour formulas write b_3 in their text (theta_13 = arcsin(sqrt(2/3) *
sqrt(2) * sin(pi/b3))) but were calibrated at 24 and registered
particle.b3 = 24 with status DERIVED regardless of the seed -- the last
seed-blind writer. The fork resolves it:

  follow_seed (ADOPTED)  the formulas consume the live seed's b_3 = 43;
                         theta_13 = 4.8351 deg (MEASURED 2026-09-22), far
                         off NuFIT -- the honest state of the ansatz, and
                         the falsification pressure it earned by claiming
                         a topological origin.
  calibrated_24          the v25 calibration, runnable for costing; its
                         full original contract is regression-pinned in
                         test_yukawa_derivation.py / test_yukawa_textures.py.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.particle.yukawa_derivation import (
    DEFAULT_B3,
    get_geometric_pmns,
    resolve_flavour_b3,
)


def test_the_adopted_branch_consumes_the_live_seed(monkeypatch):
    monkeypatch.delenv("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING",
                       raising=False)
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    assert resolve_flavour_b3() == 43


def test_the_calibrated_branch_keeps_its_24(monkeypatch):
    monkeypatch.setenv("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING",
                       "calibrated_24")
    assert resolve_flavour_b3() == DEFAULT_B3 == 24


def test_the_flavour_fork_composes_with_the_seed_fork(monkeypatch):
    """follow_seed means FOLLOW: the off-path seed gives the off-path b_3."""
    monkeypatch.delenv("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING",
                       raising=False)
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    assert resolve_flavour_b3() == 24


def test_theta_13_diverges_on_the_adopted_branch_and_says_so(monkeypatch):
    """MEASURED 2026-09-22: theta_13 = 4.8351 deg at b_3 = 43. The ansatz's
    NuFIT agreement was a property of the calibration, and the adopted
    branch must publish the divergence rather than the memory of 8.67."""
    monkeypatch.delenv("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING",
                       raising=False)
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    result = get_geometric_pmns()
    assert result["b3"] == 43
    assert result["theta_13_deg"] == pytest.approx(4.8351, abs=1e-3)
    assert abs(result["theta_13_deg"] - 8.58) > 3.0, (
        "theta_13 on the adopted branch somehow recovered its NuFIT "
        "agreement; that would be a genuine derivation and must be "
        "recorded on the register, not absorbed by this test"
    )


def test_the_two_branches_disagree_which_is_the_point(monkeypatch):
    monkeypatch.setenv("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING",
                       "calibrated_24")
    calibrated = get_geometric_pmns()["theta_13_deg"]
    monkeypatch.delenv("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING",
                       raising=False)
    adopted = get_geometric_pmns()["theta_13_deg"]
    assert calibrated == pytest.approx(8.6686, abs=1e-3)
    assert adopted != pytest.approx(calibrated, abs=1.0), (
        "the fork stopped mattering: both branches give the same theta_13, "
        "so either the resolution broke or the formula no longer reads b_3"
    )
