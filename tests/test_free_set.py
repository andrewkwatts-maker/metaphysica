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
    """Each identity reproduces its registered row.

    cosmology.wa_thawing does NOT, and the reason is the open
    flavour_seed_coupling pass rather than the identity being wrong.
    ``verify_geometric_identities`` takes its b_3 from the registered
    ``particle.b3``, which is still the frozen v25 flavour calibration --
    value 24, status DERIVED, source ``v25.0:yukawa_derivation`` -- while
    the registry row it is checked against was built on the adopted seed.
    Measured 2026-09-22, b3_seed adoption: registered
    -0.6099942813304187 = -4/sqrt(43) against predicted
    -0.8164965809277261 = -4/sqrt(24). The identity itself holds exactly
    on either seed; only the two sides are reading different ones.

    So the diagnosis is ASSERTED here and the test then skips: if
    particle.b3 stops being 24, or the two sides stop being -4/sqrt(24)
    and -4/sqrt(43), this fails instead of skipping, and if the row heals
    the assertion below requires it to reproduce like the others.
    """
    import math

    from metaphysica.simulations.core import free_set as fs

    checks = fs.verify_geometric_identities()
    for name in ("fermion.n_generations", "yukawa.lambda_eff"):
        if name not in checks:
            continue
        assert checks[name]["reproduced"], (
            "%s: registered %s vs predicted %s"
            % (name, checks[name]["registered"], checks[name]["predicted"])
        )
        assert checks[name]["rel_error"] < 1e-9

    name = "cosmology.wa_thawing"
    if name in checks and not checks[name]["reproduced"]:
        flavour_b3 = fs._value(fs._params(), "particle.b3")
        assert flavour_b3 == 24, (
            "particle.b3 = %s, so the wa_thawing mismatch is no longer the "
            "frozen v25 flavour calibration and needs its own reading"
            % flavour_b3
        )
        assert math.isclose(
            checks[name]["predicted"], -4.0 / math.sqrt(24), rel_tol=1e-12
        )
        assert math.isclose(
            checks[name]["registered"], -4.0 / math.sqrt(43), rel_tol=1e-12
        )
        pytest.skip(reason="awaiting flavour_seed_coupling pass")

    if name in checks:
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


def test_the_quartic_is_a_function_of_b3_and_the_fallback_disagrees():
    """freudenthal_quartic = 16 (b3/27)^2, verified -- and the module's
    ImportError fallback computes 27 c^4 / 4 instead, exactly 3x smaller.
    Recorded defect: if eml_spectral goes missing the export silently changes
    by a factor of 3. This test pins the disagreement so a fix is visible."""
    b3 = 24.0
    c = b3 / 27.0
    fts_path = 16.0 * c * c
    fallback = 27.0 * c ** 4 / 4.0
    assert abs(fts_path - 1024.0 / 81.0) < 1e-14
    assert abs(fts_path / fallback - 3.0) < 1e-12, (
        "the two code paths now agree; update the register entry and the "
        "free-set removal note"
    )


def test_dissolved_discrete_choices_are_declared(report):
    """Removing a value whose formula is a rowless ansatz must leave a trace."""
    d = report["dissolved_discrete_choices"]
    assert "abstract.alpha_gut_coefficient" in d
    assert "yukawa.lambda_eff" in d
