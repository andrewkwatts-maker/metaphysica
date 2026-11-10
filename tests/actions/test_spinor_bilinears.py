"""Weyl bilinears: the rule equals the explicit-gamma oracle; the action check has a failing case."""

from __future__ import annotations

from fractions import Fraction

import pytest

from metaphysica.actions.model import INPUT, Action, Coefficient, Field, ModelError, Term
from metaphysica.actions.spinor_bilinears import (
    C_CHOICES, NONZERO, TOTAL_DERIVATIVE, ZERO, check_spinor_bilinears,
    explicit_weyl_bilinears, weyl_bilinears,
)

SIGNATURES = [(1, 1), (3, 1), (5, 1), (7, 1), (9, 1), (2, 2), (4, 2), (6, 2), (8, 2), (10, 2)]


@pytest.mark.parametrize("c_choice", C_CHOICES)
@pytest.mark.parametrize("s,t", SIGNATURES)
def test_rule_equals_oracle(s, t, c_choice):
    assert weyl_bilinears(s, t) == explicit_weyl_bilinears(s, t, c_choice)


@pytest.mark.slow
@pytest.mark.parametrize("c_choice", C_CHOICES)
def test_rule_equals_oracle_at_24_2(c_choice):
    assert weyl_bilinears(24, 2) == explicit_weyl_bilinears(24, 2, c_choice)


def test_known_cases():
    four = weyl_bilinears(3, 1)
    assert four["hermitian"] == {"kinetic": NONZERO, "mass": ZERO}
    assert four["holomorphic"] == {"kinetic": ZERO, "mass": NONZERO}  # 4D Majorana mass
    assert weyl_bilinears(5, 1)["holomorphic"]["kinetic"] == TOTAL_DERIVATIVE
    two_times = weyl_bilinears(24, 2)
    assert two_times["hermitian"] == {"kinetic": ZERO, "mass": NONZERO}
    assert two_times["holomorphic"] == {"kinetic": NONZERO, "mass": ZERO}


def test_one_time_rule_fails_at_two_times():
    """Control: the one-time answer (hermitian kinetic survives) is wrong at (10, 2)."""
    assert explicit_weyl_bilinears(10, 2)["hermitian"]["kinetic"] != NONZERO


def test_odd_dimension_and_bad_choice_raise():
    with pytest.raises(ValueError):
        weyl_bilinears(12, 1)
    with pytest.raises(ValueError):
        explicit_weyl_bilinears(3, 1, "hermitian")


def _action(sig, bilinear, mass=False):
    D = sum(sig)
    psi = Field("Psi", "spinor", 2 ** (D // 2 - 1), Fraction(D - 1, 2), "weyl")
    one = Coefficient("one", Fraction(0), INPUT, "p")
    terms = [Term("kin", one, ("Psi", "Psi", "d"), bilinear=bilinear)]
    if mass:
        terms.append(Term("mass", Coefficient("m", Fraction(1), INPUT, "p"), ("Psi", "Psi"),
                          bilinear=bilinear))
    return Action("a", D, sig, (psi,), tuple(terms))


def test_check_reads_the_signature():
    assert [c.holds for c in check_spinor_bilinears(_action((3, 1), None))] == [True]
    bad = check_spinor_bilinears(_action((24, 2), None, mass=True))
    assert [(c.id, c.holds) for c in bad] == [("spinor_bilinear:a:kin", False),
                                               ("spinor_bilinear:a:mass", True)]
    assert bad[0].measured == ZERO


def test_holomorphic_kinetic_passes_at_two_times():
    got = check_spinor_bilinears(_action((24, 2), "holomorphic", mass=True))
    assert [(c.measured, c.holds) for c in got] == [(NONZERO, True), (ZERO, False)]


def test_term_rejects_unknown_bilinear():
    with pytest.raises(ModelError):
        Term("kin", Coefficient("one", Fraction(0), INPUT, "p"), ("d",), bilinear="majorana")
