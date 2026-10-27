"""Established physics computed from actions: checks, failing controls, BLOCKED rules."""

from __future__ import annotations

import dataclasses

import pytest

from metaphysica.actions import established as E
from metaphysica.actions import established_catalogue as C
from metaphysica.actions import established_gauge as G
from metaphysica.actions import established_matter as M
from metaphysica.actions.controls import four_d
from metaphysica.actions.controls import standard_ladder

SM = four_d.standard_model_like_action()
GAUGE = G.sm_gauge_action()


def _verdicts(action, checks, refs=None):
    return {v.id: v for v in E.run(action, checks, refs)}


def test_every_catalogue_check_reproduces_on_the_control_action():
    for v in E.run(GAUGE, C.action_checks()):
        assert v.verdict == E.REPRODUCED, (v.id, v.measured, v.detail)


def test_every_failing_control_fails():
    for v in E.run(GAUGE, C.action_controls()):
        assert v.verdict == E.FAILS, (v.id, v.measured)


def test_existing_four_d_controls_keep_their_results():
    assert all(c.run().holds for c in four_d.correspondences())
    assert not any(c.run().holds for c in four_d.controls())


def test_mostly_minus_with_plus_r_term_fails_the_sign_check():
    bad = dataclasses.replace(SM, convention="mostly_minus")
    assert E.run(bad, [C.action_checks()[1]])[0].verdict == E.FAILS
    flipped = dataclasses.replace(bad, terms=tuple(
        dataclasses.replace(t, sign=-1) if t.id == "eh" else t for t in bad.terms))
    assert E.run(flipped, [C.action_checks()[1]])[0].verdict == E.REPRODUCED


def test_wrong_gravity_coefficient_dimension_fails():
    eh = SM.terms[0]
    coef = dataclasses.replace(eh.coefficient, mass_dim=3)
    bad = dataclasses.replace(SM, terms=(dataclasses.replace(eh, coefficient=coef),)
                              + SM.terms[1:])
    assert E.run(bad, [C.action_checks()[1]])[0].verdict == E.FAILS


def test_open_or_absent_term_gives_blocked_naming_the_term():
    from metaphysica.simulations.PM.gauge import master_ladder as ML
    ladder = ML.build_ladder(ML.resolve_options())
    a4 = ladder.steps[-1].action
    refs = {"A4:L_SM": "audit s2"}
    out = _verdicts(a4, C.action_checks(), refs)
    gauge = out["gauge_anomaly_cancellation"]
    assert gauge.verdict == E.BLOCKED and gauge.blocked_on == (("A4:L_SM", "audit s2"),)
    assert out["gr_weak_field_poisson"].verdict == E.REPRODUCED
    assert _verdicts(SM, C.action_checks())["gauge_yang_mills_su3_su2_u1"].verdict == E.BLOCKED


def test_reduction_checks_and_controls():
    red = standard_ladder().steps[1].reduction
    good = _verdicts(red.child, M.reduction_checks(red))
    assert all(v.verdict == E.REPRODUCED for v in good.values()), good
    bad = _verdicts(red.child, M.reduction_controls(red))
    assert all(v.verdict == E.FAILS for v in bad.values())


def test_universal_coupling_fails_with_two_metrics():
    from metaphysica.actions.model import Field
    from fractions import Fraction
    two = dataclasses.replace(SM, fields=SM.fields + (Field("g2", "metric", 1, Fraction(0)),))
    assert E.run(two, [C.action_checks()[5]])[0].verdict == E.FAILS


def test_dirac_fails_with_wrong_spinor_dimension():
    psi = dataclasses.replace(SM.field("psi"), mass_dim=2)
    bad = dataclasses.replace(SM, fields=tuple(psi if f.name == "psi" else f for f in SM.fields))
    check = next(c for c in C.action_checks() if c.id == "matter_dirac_equation")
    assert E.run(bad, [check])[0].verdict == E.FAILS
