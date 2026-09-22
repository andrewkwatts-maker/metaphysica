"""The identity ledger's per-branch verdicts are pinned, one test per identity.

WHY THIS EXISTS
---------------
`core/identity_ledger.py` exists so that the next broken integer coincidence
is a report rather than a crash. That only works if the report is itself
guarded: a ledger whose rows silently change verdict is a ledger nobody can
cite.

The record below was MEASURED on 2026-09-22 by running `identity_report()`
against the generated seed family. It is written out as a literal so the test
compares two independent things -- the frozen record and the live evaluation.
A test that recomputed the record from the ledger could not fail.

TWO DIRECTIONS, BOTH FAILABLE
-----------------------------
* a row that changes verdict on any branch fails here, so a physics edit
  cannot quietly heal or break a coincidence;
* a row that DISAPPEARS from the ledger fails here too, because the record is
  compared by set as well as by value -- deleting a broken identity is exactly
  the move this campaign refuses (falsified candidates stay LABELLED).

Adding a genuinely new identity is expected to fail this test once, and the
fix is to measure it and extend the record -- never to loosen the comparison.
"""
from __future__ import annotations

import pytest

from metaphysica.simulations.core.identity_ledger import (
    IDENTITIES,
    evaluate_identity,
    identity_by_id,
    identity_report,
)

#: identity id -> {branch: status}, MEASURED 2026-09-22 against the generated
#: Joyce family plus the off-family seed_24. Twelve of fifteen rows hold on
#: seed_24 ALONE -- that is the ledger's headline, and it is recorded here
#: rather than summarised, so a change to any single cell is visible.
RECORD = {
    "alpha_f_curvature_coefficient": "seed_24_only",
    "ancestral_roots_from_so_n": "seed_24_only",
    "bridge_pairs_half_b3": "seed_24_only",
    "chi_pressure_from_b3_squared": "seed_24_only",
    "d_bulk_is_b3_plus_two": "seed_24_only",
    "hidden_supports_seven_b3_minus_five": "seed_24_only",
    "modular_anomaly_b3_mod_24": "seed_24_only",
    "n_eff_cycles_b3_minus_14": "seed_24_only",
    "n_gen_from_b3_over_eight": "seed_24_only",
    "roots_total_twelve_b3": "seed_24_only",
    "shadow_dim_half_b3_plus_one": "seed_24_only",
    "shadow_torsion_total_is_b3": "seed_24_only",
    # The two that survive the adoption, and they are the two the ruling
    # actually rests on: the ruled n_gen route and reachability.
    "n_gen_from_b2_over_faces": "adopted_only",
    "reachability_b3_is_seven_plus_three_b2": "joyce_family_only",
    # chi_eff is UNRULED, so its row reports NOT_EVALUABLE rather than
    # picking a side. This is a verdict, not a gap.
    "chi_eff_over_b3_is_three": "not_evaluable",
}

#: The shapes above, expanded. Kept separate from RECORD so the mapping stays
#: readable while the comparison stays exact.
SHAPES = {
    "seed_24_only": {
        "seed_7_joyce": "BROKEN", "seed_19_joyce": "BROKEN",
        "seed_24": "HOLDS", "seed_31_joyce": "BROKEN",
        "seed_43_joyce": "BROKEN",
    },
    "adopted_only": {
        "seed_7_joyce": "BROKEN", "seed_19_joyce": "BROKEN",
        "seed_24": "BROKEN", "seed_31_joyce": "BROKEN",
        "seed_43_joyce": "HOLDS",
    },
    "joyce_family_only": {
        "seed_7_joyce": "HOLDS", "seed_19_joyce": "HOLDS",
        "seed_24": "BROKEN", "seed_31_joyce": "HOLDS",
        "seed_43_joyce": "HOLDS",
    },
    "not_evaluable": {
        "seed_7_joyce": "NOT_EVALUABLE", "seed_19_joyce": "NOT_EVALUABLE",
        "seed_24": "NOT_EVALUABLE", "seed_31_joyce": "NOT_EVALUABLE",
        "seed_43_joyce": "NOT_EVALUABLE",
    },
}


@pytest.fixture(scope="module")
def report():
    return identity_report()


def test_every_registered_identity_is_in_the_record():
    """A new identity must be measured, not merely added."""
    registered = {row.id for row in IDENTITIES}
    assert registered == set(RECORD), (
        "identity ledger and the measured record disagree; "
        "added=%s removed=%s"
        % (sorted(registered - set(RECORD)), sorted(set(RECORD) - registered))
    )


@pytest.mark.parametrize("identity_id", sorted(RECORD))
def test_identity_per_branch_status_matches_the_record(identity_id, report):
    """Each identity's verdict on each branch is what was measured."""
    row = next(r for r in report["identities"] if r["identity"] == identity_id)
    live = {branch: row["per_branch"][branch]["status"]
            for branch in report["branches"]}
    assert live == SHAPES[RECORD[identity_id]], (
        "%s changed verdict: %s" % (identity_id, live))


def test_every_identity_states_what_its_numbers_count():
    """The A4 bar: a row without `counts` is a number without an object."""
    for row in IDENTITIES:
        assert row.counts and len(row.counts) > 40, (
            "%s does not say what its numbers count" % row.id)
        assert row.source, "%s does not say where the claim is made" % row.id


def test_broken_identities_are_not_deleted_from_the_ledger():
    """The record keeps twelve rows that hold on seed_24 alone.

    Stated as a count so a future 'cleanup' that drops the dead coincidences
    fails here. They are the measured cost of the ruling; deleting them would
    erase the evidence that the framework's integer structure was anchored on
    a single off-family seed.
    """
    seed_24_only = [k for k, v in RECORD.items() if v == "seed_24_only"]
    assert len(seed_24_only) == 12, seed_24_only


def test_the_adopted_branch_keeps_exactly_the_two_ruled_relations(report):
    """What survives the adoption is derived, not coincidental.

    n_gen = b_2/4 is the RULED n_gen_source; b_3 = 7 + 3 b_2 is reachability.
    Those are the two criteria the adoption rests on, and they are the only
    two rows that hold on the adopted branch. If a third ever joins them it
    is a finding worth a register entry, so this asserts the exact set.
    """
    assert set(report["holds_on_adopted"]) == {
        "n_gen_from_b2_over_faces",
        "reachability_b3_is_seven_plus_three_b2",
    }, report["holds_on_adopted"]


def test_chi_eff_row_stays_unruled_unless_a_value_is_supplied():
    """Supplying chi_eff evaluates the row; not supplying it must not guess."""
    row = identity_by_id("chi_eff_over_b3_is_three")
    assert evaluate_identity(row, 43, 12, None)["status"] == "NOT_EVALUABLE"
    # 72/24 = 3 was the coincidence; both chi_eff readings are checkable.
    assert evaluate_identity(row, 24, 4, 72.0)["status"] == "HOLDS"
    assert evaluate_identity(row, 24, 4, 144.0)["status"] == "BROKEN"
    assert evaluate_identity(row, 43, 12, 72.0)["status"] == "BROKEN"


def test_report_never_ranks_branches(report):
    """The anti-tuning rule, asserted on the artifact itself."""
    assert report["verdict"] == "NO_SELECTION_MADE"
    assert "never" in report["ordering"]
    # branches are reported in a deterministic, non-preferential order
    assert report["branches"] == sorted(report["branches"])
