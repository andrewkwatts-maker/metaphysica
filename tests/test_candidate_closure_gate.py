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
    _THETA_12_SIGMA,
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


def test_muon_g2_scale_mismatch_is_pinned(by_id):
    """The proposal is not marginally off -- it misses its OWN claim by ~165x.

    Pinning the ratio (not just the value) keeps the magnitude of the failure
    on the record: alpha/(2*pi*b3*k_beth) = 4.1e-7 against a claimed 2.49e-9.
    A near-miss and a two-orders-of-magnitude miss must never blur together.
    """
    v = by_id["muon-g2-torsion"]
    assert v.computed / v.claimed == pytest.approx(164.9, rel=1e-2)


def test_kahler_ricci_sector_stays_frozen(by_id):
    """AUTHOR RULING 2026-08-23: frozen, zero active code, invent nothing.

    Two enforcements: the ruling must stay recorded in the gate, and no
    running-Re(T)/Kahler-Ricci implementation may appear in the source tree
    while the chi_i inputs remain uncomputed -- code showing up here means
    someone invented the cycles the ruling forbids.
    """
    from pathlib import Path

    v = by_id["running-ret-kahler-ricci"]
    assert v.verdict == "OPEN_PROPOSAL"
    assert v.extras.get("author_ruling") == "FROZEN_2026_08_23"
    assert "zero active code" in v.note

    src = Path(__file__).resolve().parents[1] / "src"
    offenders = [
        p for p in src.rglob("*.py")
        if "kahler_ricci" in p.name.lower() or "running_ret" in p.name.lower()
    ]
    assert not offenders, (
        f"frozen sector has grown implementation files: {offenders}"
    )


def test_open_proposal_adopts_nothing(by_id):
    """Originally this asserted the sector was PENDING an author ruling; the
    ruling has since been made (2026-08-23: frozen), so it now asserts the
    ruling is recorded and that still nothing numerical was adopted."""
    v = by_id["running-ret-kahler-ricci"]
    assert v.verdict == "OPEN_PROPOSAL"
    assert v.computed is None and v.claimed is None
    assert "AUTHOR RULING" in v.note


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

# ── failure-magnitude ledger ─────────────────────────────────────────────────
#
# Ratios are pinned against each proposal's OWN CLAIMED value, never against
# the experimental anchor. That distinction is load-bearing:
#
#   computed/claimed  is internal arithmetic -- fixed forever, safe to pin
#   computed/anchor   moves whenever PDG/NuFIT publish a revision, so pinning
#                     it exactly would make a legitimate data update look like
#                     a code regression
#
# The muon g-2 entry is the cautionary case: its anchor is ALREADY stale
# (2024-25 lattice-HVP results largely dissolved that tension). Had the ratio
# been pinned to the anchor, this suite would now be enforcing a number
# physics has moved past. Experimental comparisons stay as bounds.

#: (candidate_id, computed/claimed ratio, tolerance). One parametrized test,
#: not eight near-duplicates -- duplicated matrices drift apart.
_CLAIM_MISS_RATIOS = [
    ("vev-factor-dimension-ratio", 1.63518, 1e-3),
    ("alpha-gut-s5-volume", 1.22427, 1e-3),
    ("lambda-golay-capacity", 1.001e114, 1e-3),
    ("hubble-shift-alpha-leak", 0.296972, 1e-3),
    ("weinberg-d5-running", 1.57895, 1e-3),
    ("pmns-theta13-leak", 0.0359983, 1e-3),
    ("pmns-theta12-golden", 1.00003, 1e-3),
    ("muon-g2-torsion", 164.848, 1e-3),
    # Included deliberately though its verdict is PLAUSIBLE_UNTESTABLE: the
    # arithmetic agreeing with its claim to 0.3% is exactly why that verdict
    # is not FALSIFIED, and pinning it keeps the distinction honest.
    ("soft-susy-golay-suppression", 1.00341, 1e-3),
]


@pytest.mark.parametrize("cid,expected_ratio,tol", _CLAIM_MISS_RATIOS)
def test_claim_miss_ratio_is_pinned(by_id, cid, expected_ratio, tol):
    """How far each proposal misses ITS OWN advertised number, pinned.

    Turns a qualitative "FALSIFIED" label into a measurable engineering
    quantity, so a 1.6x miss and a 10^114 miss can never blur together in the
    record -- and so a silent change in any computed value trips the suite.
    """
    v = by_id[cid]
    assert v.claimed, f"{cid} has no claimed value to compare against"
    assert v.computed / v.claimed == pytest.approx(expected_ratio, rel=tol)


def test_theta12_is_the_one_that_matches_its_claim(by_id):
    """theta_12 is instructive: ratio 1.0 means the ARITHMETIC is honest.

    It is FALSIFIED on experiment (24.09 deg vs NuFIT's 33.44), not on
    self-consistency. Recording the difference matters -- "the algebra is
    wrong" and "the algebra is right but nature disagrees" are different
    failures and deserve different follow-up.
    """
    v = by_id["pmns-theta12-golden"]
    assert v.computed / v.claimed == pytest.approx(1.0, rel=1e-3)
    assert v.verdict == "FALSIFIED"
    assert abs(v.computed - v.anchor) / _THETA_12_SIGMA > 10


