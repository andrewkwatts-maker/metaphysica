"""Spinor counts and Weyl-mass check, each with a failing control."""

from __future__ import annotations

from fractions import Fraction

import pytest

from metaphysica.actions.dimensions import check_action
from metaphysica.actions.model import INPUT, Action, Coefficient, Field, ModelError, Term
from metaphysica.actions.spinors import (
    dirac_dim, majorana_allowed, majorana_real_components, majorana_weyl_allowed,
    product_spinor_dim, weyl_dim,
)


def test_four_d_dirac_and_weyl():
    assert (dirac_dim(4), weyl_dim(4)) == (4, 2)
    assert dirac_dim(4) != 2  # control: a wrong count is distinguishable


def test_ten_d_majorana_weyl_has_16_real_components():
    assert majorana_weyl_allowed(9, 1)
    assert majorana_real_components(9, 1, weyl=True) == 16
    assert majorana_real_components(9, 1, weyl=True) != 32


def test_eleven_d_majorana_is_32():
    assert majorana_allowed(10, 1) and not majorana_weyl_allowed(10, 1)
    assert majorana_real_components(10, 1) == 32


def test_four_d_euclidean_has_no_majorana_weyl():
    assert not majorana_weyl_allowed(4, 0)
    with pytest.raises(ValueError):
        majorana_real_components(4, 0, weyl=True)


def test_weyl_is_undefined_in_odd_dimension():
    with pytest.raises(ValueError):
        weyl_dim(13)


def test_product_rule_three_plus_three():
    assert product_spinor_dim(3, 3) == 2 * 2 * 2 == 8 == dirac_dim(6)
    assert product_spinor_dim(3, 3) != dirac_dim(3) * dirac_dim(3)  # control: naive tensor


@pytest.mark.parametrize("d1,d2", [(1, 1), (3, 3), (13, 13), (4, 3), (3, 4), (6, 4), (5, 7)])
def test_product_rule_equals_dirac_of_the_sum(d1, d2):
    assert product_spinor_dim(d1, d2) == dirac_dim(d1 + d2)


def _action(chirality, with_mass=True):
    ps = Field("Psi", "spinor", 4, Fraction(3, 2), chirality)
    kin = Term("kin", Coefficient("one", Fraction(0), INPUT, "p"), ("Psi", "Psi", "d"))
    mass = Term("mass", Coefficient("m", Fraction(1), INPUT, "p"), ("Psi", "Psi"))
    return Action("a", 4, (3, 1), (ps,), (kin, mass) if with_mass else (kin,))


def test_weyl_mass_term_fails_and_dirac_passes():
    bad = [c.id for c in check_action(_action("weyl")) if not c.holds]
    assert bad == ["weyl_mass:a:mass"]
    assert all(c.holds for c in check_action(_action(None)))
    assert all(c.holds for c in check_action(_action("weyl", with_mass=False)))


def test_unknown_chirality_is_rejected():
    with pytest.raises(ModelError):
        Field("Psi", "spinor", 4, Fraction(3, 2), "left")
