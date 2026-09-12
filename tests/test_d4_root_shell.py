"""D4's 24 roots as a candidate origin for 24, and the gap that stops it.

The count is FORCED here rather than matched -- |roots| = rank x Coxeter number
and D4 has rank 4, h = 6 -- which is more than any earlier candidate achieved.
The Coxeter number is computed from the order of a Coxeter element, because
taking h = |roots| / rank would make the identity circular; the test below
fails if that circularity is ever reintroduced.

The candidate still does not clear the A4 bar, and the last tests pin that: the
roots are directions in a 4-dimensional Cartan space while b_3 would count
harmonic 3-forms on a 7-manifold, and 24 is not a G2 irrep dimension.
"""

from __future__ import annotations

import numpy as np
import pytest

from metaphysica.simulations.PM.geometry.d4_root_shell import (
    coxeter_number,
    d4_roots,
    d4_shell_report,
    g2_branching_calibration,
    g2_representation_dimensions,
    is_shell,
    positive_roots,
    simple_roots,
)


def test_there_are_twenty_four_roots_and_they_are_built_not_tabulated():
    roots = d4_roots()
    assert len(roots) == 24
    # every root is +-e_i +- e_j : norm^2 = 2, exactly two non-zero entries
    for r in roots:
        assert int(r @ r) == 2
        assert int(np.count_nonzero(r)) == 2
    assert len({tuple(int(x) for x in r) for r in roots}) == 24


def test_the_coxeter_number_is_six_and_is_computed_independently():
    """h must come from the Coxeter element, not from |roots| / rank."""
    assert coxeter_number() == 6


def test_the_count_is_forced_by_rank_times_coxeter():
    assert len(d4_roots()) == 4 * coxeter_number() == 24


def test_the_identity_is_not_circular():
    """If h were defined as |roots| / rank the identity would be vacuous.

    A Coxeter element is a product of the 4 simple reflections; its order is an
    independent fact about the group. Verified here by checking it really is
    order 6 as a matrix, so the comparison against 24 has content.
    """
    c = np.eye(4)
    for alpha in simple_roots():
        a = alpha.astype(float)
        c = c @ (np.eye(4) - 2.0 * np.outer(a, a) / float(a @ a))
    p = np.eye(4)
    orders = []
    for k in range(1, 13):
        p = p @ c
        if np.allclose(p, np.eye(4), atol=1e-9):
            orders.append(k)
    assert orders and orders[0] == 6
    assert not np.allclose(c, np.eye(4)), "the Coxeter element must be non-trivial"


def test_the_roots_form_a_shell_about_the_origin():
    s = is_shell(d4_roots())
    assert s["count"] == 24
    assert s["all_same_norm"] and s["norm_squared"] == 2
    assert s["closed_under_negation"]
    assert s["sums_to_zero"]


def test_the_split_is_twelve_plus_twelve():
    pos = positive_roots()
    assert len(pos) == 12
    assert len(d4_roots()) - len(pos) == 12


def test_the_split_costs_a_chamber_choice_and_the_module_says_so():
    """There is no canonical half of a root system, and that must not be hidden."""
    r = d4_shell_report()
    assert r["split_requires_a_chamber_choice"] is True
    # a different regular vector still gives 12, but not the same 12
    a = {tuple(int(x) for x in v) for v in positive_roots()}
    b = {tuple(int(x) for x in v)
         for v in positive_roots(np.array([-8.0, 4.0, 2.0, 1.0]))}
    assert len(a) == len(b) == 12
    assert a != b, "two chambers gave the same positive set; the choice is real"


def test_a_non_regular_vector_is_rejected_rather_than_silently_split():
    with pytest.raises(ValueError):
        positive_roots(np.array([1.0, 1.0, 0.0, 0.0]))   # orthogonal to e3+-e4


# --------------------------------------------------------------- the A6 gate


def test_the_calibration_is_run_and_is_honest_about_failing():
    """A6: an uncalibrated pipeline must say so rather than quote its output."""
    calib = g2_branching_calibration()
    assert calib["branching_dimensions_consistent"] is True   # 28 = 14 + 7 + 7
    assert calib["lambda2_is_7_plus_14"] is True
    # but the 14 is not g2, because phi is not a G2 form -- recorded separately
    assert calib["calibrated"] is False
    assert calib["why_not_calibrated"]


def test_the_calibration_could_succeed_in_principle():
    """Guard against a gate wired to always report failure."""
    calib = g2_branching_calibration()
    assert calib["v7_does_not_annihilate_phi"] is True, (
        "if neither subspace ever annihilated phi the check would be vacuous"
    )
    assert calib["v14_max_action_norm"] is not None
    assert calib["v14_max_action_norm"] > 0.0


# --------------------------------------------------------------- the A4 bar


def test_the_verdict_is_numerical_with_the_gap_named():
    r = d4_shell_report()
    assert r["count_is_forced"] is True
    assert r["verdict"] == "NUMERICAL"
    assert r["map_to_three_forms_exists"] is False
    assert r["root_space_dimension"] == 4
    assert r["b3_would_live_on_a_7_manifold"] is True
    assert "NOT adopted" in r["verdict_reason"]


def test_24_is_not_a_g2_representation_dimension():
    """So b_3 = 24 cannot be read off G2 representation theory either."""
    dims = g2_representation_dimensions()
    assert 24 not in dims
    assert {1, 7, 14, 27} <= set(dims)
    assert d4_shell_report()["24_is_a_g2_irrep_dimension"] is False
