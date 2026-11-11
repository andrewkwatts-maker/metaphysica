"""Wave A close-out XG-01..XG-04: vacuum potential degree, SU2 scope, docstrings, HERMITIAN."""

from __future__ import annotations

import inspect
from fractions import Fraction

import pytest
import sympy as sp

from metaphysica.actions import field_equations as fe
from metaphysica.actions import spinors, zero_modes
from metaphysica.actions.field_equations import Factor, vacuum_checks
from metaphysica.actions.model import INPUT, Action, Coefficient, Field, Term

M2 = Coefficient("m_sq", Fraction(2), INPUT, "p")


def _scalar_action(*extra):
    g = Field("G", "metric", 1, Fraction(0))
    phi = Field("phi", "scalar", 1, Fraction(1))
    grav = Term("R", Coefficient("M_star_2", Fraction(2), INPUT, "p"), ("R",))
    kin = Term("kin", Coefficient("one", Fraction(0), INPUT, "p"), ("phi", "phi", "d"))
    return Action("s", 4, (3, 1), (g, phi), (grav, kin) + tuple(extra))


def _potential(action):
    coords = sp.symbols("x0:4")
    flat = Factor("R4", 4, sp.diag(-1, 1, 1, 1), coords)
    return [c for c in vacuum_checks(action, [flat]) if c.id == "vacuum_potential:s"][0]


def test_mass_term_keeps_the_vacuum():
    """Passing control: m^2 phi^2 vanishes with its first derivative at phi = 0."""
    chk = _potential(_scalar_action(Term("mass", M2, ("phi", "phi"))))
    assert chk.holds and chk.measured == "none"


def test_linear_and_constant_terms_spoil_the_vacuum():
    """Failing controls: a tadpole (V'(0) != 0) and a constant (V(0) != 0)."""
    lin = _potential(_scalar_action(Term("tad", M2, ("phi",)), Term("quart", M2, ("phi",) * 4)))
    assert not lin.holds and lin.measured == "tad"
    const = _potential(_scalar_action(Term("lam", M2, ())))
    assert not const.holds and const.measured == "lam"
    assert "0 or 1 scalar factors" in fe.__doc__


def test_su2_is_chiral_index_only(monkeypatch):
    assert "chiral_index" in zero_modes.__doc__ and "SU2" in zero_modes.__doc__
    assert "SU2" not in zero_modes.HOLONOMIES
    with pytest.raises(ValueError, match="not supported"):
        zero_modes.zero_modes((), 4, {0: 1, 1: 0, 2: 22}, "SU2")
    monkeypatch.setattr(zero_modes, "K3_DIM", 6)
    with pytest.raises(ValueError, match="dimension 6, got 4"):
        zero_modes.chiral_index(4, "SU2")


def test_one_time_rule_docstring():
    doc = spinors.check_spinor_terms.__doc__
    assert "hermitian form at one time" in doc and "holomorphic" in doc and "P4b" in doc


def test_hermitian_constant_not_a_literal():
    assert '"hermitian"' not in inspect.getsource(fe._matter_equation)
