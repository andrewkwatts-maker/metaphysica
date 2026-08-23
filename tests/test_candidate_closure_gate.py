"""Tests for the candidate-closure gate.

These pin the ARITHMETIC of each verdict, not just the labels. The gate exists
because a batch of proposed closed forms arrived with claimed outputs their own
expressions do not produce -- the Weinberg formula claims 0.2312 but evaluates
to 0.365, theta_13 claims 8.618 deg but evaluates to 0.31 deg, and the Golay
Lambda expression claims 1.17e-120 while evaluating to 1.17e-6. If any of
these numbers ever CHANGES verdict (say, an SSOT seed moves), these tests make
the flip loud instead of silent.
"""
from __future__ import annotations

import json
import math

import pytest

from metaphysica.simulations.PM.validation.candidate_closure_gate import (
    evaluate_all_candidates,
    write_report,
)


@pytest.fixture(scope="module")
def by_id():
    return {v.candidate_id: v for v in evaluate_all_candidates()}


def test_every_candidate_has_a_verdict(by_id):
    assert len(by_id) == 14
    allowed = {"FALSIFIED", "ILL_FORMED", "NEAR_MISS_NOTED",
               "PLAUSIBLE_UNTESTABLE", "ALREADY_INTEGRATED", "OPEN_PROPOSAL"}
    assert {v.verdict for v in by_id.values()} <= allowed


def test_weinberg_formula_evaluates_to_its_actual_value(by_id):
    """(3/8)(1 - 2/24pi) = 0.36505, NOT the claimed 0.2312."""
    v = by_id["weinberg-d5-running"]
    assert v.computed == pytest.approx(0.365046, abs=1e-5)
    assert v.verdict == "FALSIFIED"
    # the gap to experiment is 58%, nowhere near "sub-sigma"
    assert abs(v.computed - v.anchor) / v.anchor > 0.5


def test_theta13_claim_is_a_28x_arithmetic_error(by_id):
    v = by_id["pmns-theta13-leak"]
    assert v.computed == pytest.approx(0.31023, abs=1e-4)
    assert v.claimed / v.computed > 25
    assert v.verdict == "FALSIFIED"


def test_theta12_arithmetic_is_right_but_experiment_disagrees(by_id):
    """arctan(1/sqrt(5)) really is 24.09 deg; NuFIT says 33.44 +/- 0.77."""
    v = by_id["pmns-theta12-golden"]
    assert v.computed == pytest.approx(24.0948, abs=1e-3)
    assert abs(v.computed - v.anchor) / 0.77 > 10  # >10 sigma
    assert v.verdict == "FALSIFIED"


def test_lambda_exponent_is_fabricated_by_114_orders(by_id):
    v = by_id["lambda-golay-capacity"]
    assert v.computed == pytest.approx(1.171e-6, rel=1e-3)
    assert v.claimed == pytest.approx(1.17e-120)
    assert math.log10(v.computed / v.claimed) > 100
    assert v.verdict == "FALSIFIED"


def test_hubble_shift_does_not_reach_planck(by_id):
    v = by_id["hubble-shift-alpha-leak"]
    assert v.computed == pytest.approx(1.2325, abs=1e-3)
    # 71.55 - 1.23 = 70.32, which is NOT 67.4
    assert v.computed != pytest.approx(4.15, abs=0.5)


def test_majorana_phase_is_ill_formed(by_id):
    """sqrt of a negative determinant ratio is not a real angle."""
    v = by_id["majorana-eta-picard"]
    assert v.verdict == "ILL_FORMED"
    assert v.computed is None


def test_soft_susy_is_the_one_self_consistent_proposal(by_id):
    """exp(-1.5*pi) * M_Pl_reduced lands at 2.19e16 GeV, near the GUT scale.

    Self-consistent arithmetic is necessary but not sufficient: m_soft has no
    measurement, so the verdict must NOT be a pass -- untestable is untestable.
    """
    v = by_id["soft-susy-golay-suppression"]
    assert v.computed == pytest.approx(2.187e16, rel=1e-3)
    assert v.verdict == "PLAUSIBLE_UNTESTABLE"


def test_near_miss_carries_the_look_elsewhere_caveat(by_id):
    v = by_id["vol-s5-ten-pi-coincidence"]
    assert v.verdict == "NEAR_MISS_NOTED"
    assert "look-elsewhere" in v.note


def test_muon_g2_notes_the_dissolved_tension(by_id):
    v = by_id["muon-g2-torsion"]
    assert v.computed == pytest.approx(4.105e-7, rel=1e-3)
    assert v.verdict == "FALSIFIED"
    assert "lattice" in v.note  # the target itself is stale


def test_open_proposal_adopts_nothing(by_id):
    v = by_id["running-ret-kahler-ricci"]
    assert v.verdict == "OPEN_PROPOSAL"
    assert v.computed is None and v.claimed is None
    assert "author ruling" in v.note


def test_gate_can_fail_if_a_verdict_flips():
    """Mutation-style guard: the falsified set is pinned by value.

    If an SSOT seed moved such that, say, the Weinberg expression started
    agreeing with experiment, this test fails and forces a human re-verdict
    rather than letting a label silently rot.
    """
    falsified = {
        v.candidate_id for v in evaluate_all_candidates()
        if v.verdict == "FALSIFIED"
    }
    assert falsified == {
        "vev-factor-dimension-ratio", "alpha-gut-s5-volume",
        "baryogenesis-golay-prefactor", "lambda-golay-capacity",
        "hubble-shift-alpha-leak", "weinberg-d5-running",
        "pmns-theta13-leak", "pmns-theta12-golden", "muon-g2-torsion",
    }


def test_report_never_reports_a_pass(tmp_path):
    """n_pass = 0 by construction: this ledger records verdicts on external
    proposals; it must never read as certifying framework predictions."""
    out = write_report(out_path=tmp_path / "candidate_closures.json")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["n_pass"] == 0
    assert payload["n_fail"] == 10  # 9 FALSIFIED + 1 ILL_FORMED
    assert payload["count"] == 14
    assert "FALSIFIED" in payload["verdict_counts"]
