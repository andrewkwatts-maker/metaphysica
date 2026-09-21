"""The A1 resolution must be an object, not a citation.

WHAT THIS FILE PINS
===================
`intersection_tensor` reads its -2 off "the intersection form on an A_n
resolution is minus the A_n Cartan matrix". That was a correct citation attached
to a literal: nothing in the tree could produce the number. These tests hold the
Eguchi-Hanson module to producing it from a metric and an integral.

EVERY COUNT HERE HAS A PERTURBATION THAT BREAKS IT
==================================================
The standing rule is that a test which cannot fail is a defect. So:

  * the duality claim is checked against the OTHER radial power, which carries
    the opposite duality, and against a form that is neither;
  * the closure claim is checked against the float path, which must RAISE
    rather than return a comfortable zero;
  * the -2 is compared against the value `intersection_tensor` derives, not
    against a literal typed here;
  * the a-independence of the L^2 norm is paired with a check that a genuinely
    threads through the module, so "nothing moved" cannot be passed by an
    argument that was ignored.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

sp = pytest.importorskip("sympy")

from metaphysica.simulations.PM.geometry import eguchi_hanson as eh
from metaphysica.simulations.PM.geometry.exterior_algebra import Form, exterior_d
from metaphysica.simulations.PM.geometry.intersection_tensor import (
    A1_SELF_INTERSECTION,
)


# ------------------------------------------------------------- the metric

def test_the_metric_is_ricci_flat_exactly_not_to_a_tolerance():
    """Symbolic zero in (r, theta, a). No threshold is involved."""
    ric = eh.ricci_tensor()
    assert ric.shape == (4, 4)
    for entry in ric:
        assert sp.simplify(entry) == 0
    assert eh.ricci_is_exactly_zero() is True


def test_the_bolt_parameter_actually_reaches_the_metric():
    """Guards every 'a does not matter' claim below from being vacuous.

    If `a` were ignored, the a-independence of the L^2 norm would be true for
    an uninteresting reason. It is not ignored: g_{psi psi} carries it.
    """
    r, theta, phi, psi, a = eh.symbols()
    g = eh.metric_matrix()
    assert a in g[3, 3].free_symbols
    assert a in g[0, 0].free_symbols
    at_one = eh.metric_matrix(a_value=1.0)
    at_two = eh.metric_matrix(a_value=2.0)
    assert sp.simplify(at_one[3, 3] - at_two[3, 3]) != 0


def test_the_metric_degenerates_exactly_at_the_bolt():
    """r = a is where the S^3 collapses to the exceptional S^2, so g_{psi psi}
    must vanish there and only there."""
    r, theta, phi, psi, a = eh.symbols()
    g = eh.metric_matrix()
    assert sp.simplify(g[3, 3].subs(r, a)) == 0
    assert sp.simplify(g[3, 3].subs(r, 2 * a)) != 0


def test_ale_decay_is_measured_and_converges_to_minus_four():
    rep = eh.ale_decay_report()
    assert rep["expected_exponent"] == eh.ALE_DECAY_EXPONENT == -4
    assert rep["matches_ale"] is True
    assert rep["residual"] < eh.ALE_FIT_TOLERANCE
    # The decisive check: the residual must SHRINK as the grid moves outward.
    # A wrong integer power sits a whole unit away and does not converge.
    assert rep["residual_shrinks_outward"] is True
    assert rep["outer_grid_residual"] < rep["residual"]


def test_a_wrong_decay_power_would_be_caught_by_the_tolerance():
    """The tolerance must be tight enough to refuse the neighbouring powers.

    Without this, ALE_FIT_TOLERANCE could be loosened until anything passed.
    """
    for wrong in (-3, -5):
        assert abs(wrong - eh.ALE_DECAY_EXPONENT) > eh.ALE_FIT_TOLERANCE


# --------------------------------------------------------- the 2-form

def test_the_exceptional_two_form_is_closed_structurally():
    assert eh.two_form_is_closed() is True
    r, theta, phi, psi, a = eh.symbols()
    d_eta = exterior_d(eh.exceptional_two_form(), [r, theta, phi, psi])
    # An EMPTY component map, not a small number.
    assert dict(d_eta.components) == {}


def test_the_closure_check_cannot_be_passed_by_a_float_stub():
    """exterior_d must REFUSE floats rather than return zeros.

    This is the whole reason the symbolic path is used here:
    g2_differential.compute_d_phi returns np.zeros(...) unconditionally, and an
    assertion against it proves nothing.
    """
    floats = Form(dim=4, degree=2, components={(0, 1): 1.0, (2, 3): -2.5})
    r, theta, phi, psi, a = eh.symbols()
    with pytest.raises(TypeError):
        exterior_d(floats, [r, theta, phi, psi])


def test_the_two_form_carries_the_bolt_parameter():
    r, theta, phi, psi, a = eh.symbols()
    eta = eh.exceptional_two_form()
    assert any(a in v.free_symbols for v in eta.components.values())


# ------------------------------------------------------------ duality

def test_the_physical_form_is_anti_self_dual_in_the_hyperkahler_orientation():
    rep = eh.duality_report()
    assert rep["duality_in_e0123_orientation"] == "SELF_DUAL"
    assert rep["duality_in_hyperkahler_orientation"] == "ANTI_SELF_DUAL"


def test_flipping_the_radial_power_flips_the_duality():
    """THE FALSIFIER. h ~ r^{+2} solves the same equation and is the
    non-normalisable branch; it must carry the OPPOSITE duality. If
    duality_type returned a constant this test fails.
    """
    physical = eh.duality_report(radial_power=-2)
    other = eh.duality_report(radial_power=2)
    assert other["duality_in_e0123_orientation"] == "ANTI_SELF_DUAL"
    assert (other["duality_in_e0123_orientation"]
            != physical["duality_in_e0123_orientation"])
    assert (other["duality_in_hyperkahler_orientation"]
            != physical["duality_in_hyperkahler_orientation"])


def test_a_form_that_is_neither_is_classified_as_neither():
    """The classifier must have a third answer, or 'is anti-self-dual' is
    worth nothing."""
    assert eh.duality_type(sp.Integer(1), sp.Integer(3)) == "NEITHER"
    assert eh.duality_type(sp.Integer(1), sp.Integer(1)) == "SELF_DUAL"
    assert eh.duality_type(sp.Integer(1), sp.Integer(-1)) == "ANTI_SELF_DUAL"


def test_an_overall_sign_flip_does_not_change_the_duality():
    """-eta spans the same line, so the duality is a property of the class."""
    assert (eh.duality_report(sign=-1)["duality_in_e0123_orientation"]
            == eh.duality_report(sign=1)["duality_in_e0123_orientation"])


# ------------------------------------------------- the norm, and the finding

def test_the_l2_norm_is_eight_pi_squared_exactly():
    assert sp.simplify(eh.l2_norm_squared() - 8 * sp.pi ** 2) == 0


def test_the_l2_norm_does_not_depend_on_the_bolt_parameter():
    """THE RECORDED FINDING, and it contradicts what this module was asked for.

    An L^2 norm of a 2-form on a 4-manifold is invariant under constant
    rescaling of the metric, so it cannot be proportional to a^2. Paired with
    `test_the_bolt_parameter_actually_reaches_the_metric` so that this is a
    statement about the geometry rather than about an ignored argument.
    """
    r, theta, phi, psi, a = eh.symbols()
    assert a not in eh.l2_norm_squared().free_symbols


def test_the_a_squared_quantity_that_does_exist_is_an_area():
    r, theta, phi, psi, a = eh.symbols()
    area = eh.bolt_area()
    assert sp.simplify(area - sp.pi * a ** 2) == 0
    # and it MOVES with a, unlike the norm
    assert sp.simplify(eh.bolt_area(1.0)) != sp.simplify(eh.bolt_area(2.0))
    assert sp.simplify(eh.bolt_area(2.0) / eh.bolt_area(1.0)) == 4


def test_the_period_over_the_bolt_is_minus_four_pi():
    assert sp.simplify(eh.bolt_period() - (-4 * sp.pi)) == 0


# ------------------------------------------- the -2, from geometry this time

def test_the_normalised_self_intersection_reproduces_the_a1_cartan_entry():
    """The point of the module: -2 as a computed integral, not a quoted matrix.

    Compared against the value `intersection_tensor` derives rather than
    against a literal, so if that module's A1 entry ever moves this fails
    instead of silently agreeing with a stale copy.
    """
    assert eh.normalised_self_intersection("hyperkahler") == A1_SELF_INTERSECTION


def test_the_self_intersection_sign_is_orientation_dependent_and_named():
    assert sp.simplify(eh.self_intersection("hyperkahler")
                       + eh.self_intersection("e0123")) == 0
    assert eh.self_intersection("hyperkahler") < 0
    with pytest.raises(ValueError, match="orientation"):
        eh.self_intersection("whatever")


def test_the_report_states_what_each_result_is_a_result_of():
    rep = eh.eguchi_hanson_report()
    assert rep["ricci_flat_exactly"] is True
    assert rep["two_form_closed"] is True
    assert rep["matches_a1_cartan_entry"] is True
    assert rep["l2_norm_depends_on_a"] is False
    assert rep["bolt_area_is_an_area_not_a_norm"] is True
    assert rep["psi_period_over_pi"] == 2
    assert rep["transverse_group_order"] == 2
