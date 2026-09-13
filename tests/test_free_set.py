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


# ------------------------------------------------ geometric identities


def test_the_geometric_identities_are_exact():
    from metaphysica.simulations.core.free_set import verify_geometric_identities

    checks = verify_geometric_identities()
    for name in ("fermion.n_generations", "yukawa.lambda_eff",
                 "cosmology.wa_thawing"):
        if name not in checks:
            continue
        assert checks[name]["reproduced"], (
            "%s: registered %s vs predicted %s"
            % (name, checks[name]["registered"], checks[name]["predicted"])
        )
        assert checks[name]["rel_error"] < 1e-9


def test_the_discrete_choice_stays_free(report):
    """Removing lambda_eff must not smuggle out the phi ansatz itself."""
    if "yukawa.best_scaling" in report["removed"]:
        raise AssertionError("the discrete scaling choice was removed; the "
                             "free content of the yukawa ansatz is the choice")
    assert "yukawa.best_scaling" in report["free_set"]


def test_the_wa_removal_does_not_revive_the_retired_formula():
    """The detail must name the retirement, so nobody reads it as adoption."""
    from metaphysica.simulations.core.free_set import build_free_set

    rec = build_free_set()["removed"].get("cosmology.wa_thawing")
    if rec is None:
        return
    assert "RETIRED" in rec["detail"]
    assert "not a revival" in rec["detail"]


def test_a_broken_identity_returns_to_the_free_set(monkeypatch):
    import metaphysica.simulations.core.free_set as fs

    real = fs._params()
    if "fermion.n_generations" not in real:
        return
    broken = dict(real)
    broken["fermion.n_generations"] = dict(real["fermion.n_generations"])
    broken["fermion.n_generations"]["value"] = 5
    monkeypatch.setattr(fs, "_params", lambda: broken)
    report = fs.build_free_set(broken)
    assert "fermion.n_generations" in report["free_set"]
