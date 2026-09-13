"""The free set: independent knobs, with every removal checked.

The load-bearing test is test_a_broken_formula_is_not_accepted. A reducer that
removes rows on assertion would shrink the count to anything you like, so the
CKM reduction is re-verified numerically here and a deliberately wrong formula
must be refused.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.core.free_set import (
    REASON_CLAIMED,
    REASON_DERIVED,
    REASON_DUPLICATE,
    REASON_NOT_A_KNOB,
    build_free_set,
    duplicate_groups,
    not_model_knobs,
    verify_ckm_block,
)


@pytest.fixture(scope="module")
def report():
    return build_free_set()


def test_the_free_set_is_smaller_than_the_row_count(report):
    assert report["free_set_size"] < report["ledger_rows"]
    assert report["free_set_size"] + report["removed_count"] == report["ledger_rows"]


def test_nothing_is_removed_without_a_reason(report):
    allowed = {REASON_DERIVED, REASON_DUPLICATE, REASON_NOT_A_KNOB}
    for name, rec in report["removed"].items():
        assert rec["reason"] in allowed, (name, rec)
        assert rec["detail"], "removal of %s carries no detail" % name


def test_unverified_claims_stay_in_the_free_set(report):
    """An unchecked reduction must not shrink the count."""
    for name in report["unverified_claims"]:
        assert name in report["free_set"], (
            "%s was removed on an unverified claim" % name
        )


# ------------------------------------------------- the CKM reduction, checked


def test_the_ckm_rows_are_reproduced_from_the_wolfenstein_inputs():
    block = verify_ckm_block()
    if not block["available"]:
        pytest.skip("Wolfenstein inputs not registered")
    assert block["derived"], "no CKM rows were checked at all"
    for name, rec in block["derived"].items():
        assert rec["reproduced"], (
            "%s: registered %s but the free set gives %s (rel err %.2e)"
            % (name, rec["registered"], rec["from_free_set"], rec["rel_error"])
        )


def test_a_broken_formula_is_not_accepted(monkeypatch):
    """THE load-bearing test.

    If the verifier accepted anything, the reduction would be worthless. Feed it
    a registry whose V_cb disagrees with A*lambda^2 and the row must NOT be
    reported as reproduced.
    """
    import metaphysica.simulations.core.free_set as fs

    real = fs._params()
    if "ckm.V_cb" not in real:
        pytest.skip("ckm.V_cb not registered")

    broken = dict(real)
    broken["ckm.V_cb"] = dict(real["ckm.V_cb"])
    broken["ckm.V_cb"]["value"] = real["ckm.V_cb"]["value"] * 1.5

    block = fs.verify_ckm_block(broken)
    assert block["derived"]["ckm.V_cb"]["reproduced"] is False, (
        "a 50% wrong value was still reported as derived"
    )


def test_a_broken_row_returns_to_the_free_set(monkeypatch):
    """And the reduction must actually respond, not just the verifier."""
    import metaphysica.simulations.core.free_set as fs

    real = fs._params()
    if "ckm.V_cb" not in real:
        pytest.skip("ckm.V_cb not registered")
    broken = dict(real)
    broken["ckm.V_cb"] = dict(real["ckm.V_cb"])
    broken["ckm.V_cb"]["value"] = real["ckm.V_cb"]["value"] * 1.5

    monkeypatch.setattr(fs, "_params", lambda: broken)
    report = fs.build_free_set(broken)
    assert "ckm.V_cb" in report["free_set"]
    assert report["unverified_claims"].get("ckm.V_cb", {}).get("reason") == REASON_CLAIMED


# ------------------------------------------------------- structural removals


def test_an_error_bar_is_not_a_free_parameter():
    """The clearest sign the old count measured sites rather than knobs."""
    knobs = not_model_knobs()
    if "geometry.w0_error_DESI" in knobs:
        assert "uncertainty" in knobs["geometry.w0_error_DESI"]
    report = build_free_set()
    assert "geometry.w0_error_DESI" not in report["free_set"]


def test_the_pmns_angles_are_counted_once_each(report):
    groups = duplicate_groups()
    for canonical in ("pmns.theta_12", "pmns.theta_13", "pmns.theta_23"):
        members = groups.get(canonical, [])
        if len(members) < 2:
            continue
        survivors = [m for m in members if m in report["free_set"]]
        assert len(survivors) == 1, (
            "%s survives %d times: %s" % (canonical, len(survivors), survivors)
        )


def test_duplicate_groups_name_real_rows():
    """Guard against a group that silently matches nothing and removes nothing."""
    groups = duplicate_groups()
    assert any(len(v) >= 2 for v in groups.values()), (
        "no duplicate group matched two registered rows; the reduction is inert"
    )
