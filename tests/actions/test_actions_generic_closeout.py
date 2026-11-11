"""Wave A close-out XG-01..XG-04: vacuum potential degree, SU2 scope, docstrings, HERMITIAN."""

from __future__ import annotations

import inspect
from fractions import Fraction

import pytest
import sympy as sp

from metaphysica.actions import field_equations as fe
from metaphysica.actions import spinors, zero_modes
from metaphysica.actions.field_equations import Factor, vacuum_checks
from metaphysica.actions.model import INPUT, OPEN, Action, Coefficient, Field, Term

M2 = Coefficient("m_sq", Fraction(2), INPUT, "p")
C_OPEN = Coefficient("c_open", Fraction(4), OPEN)
CONST_WHY = "T_MN proportional to G_MN, not zero: the Ricci-flat metric fails the Einstein equation"
LINEAR_WHY = "V'(0) != 0: phi = 0 fails the scalar equation"
OPEN_WHY = "no fixed form: not evaluable"


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


def test_open_term_without_factors_is_not_a_constant_potential():
    """R2-02: an open term has no fixed form; it is not evaluable, and not read as a constant."""
    bridge = Term("bridge", C_OPEN, (), open=True)
    assert not fe._spoils_vacuum(bridge, _scalar_action(bridge))
    chk = _potential(_scalar_action(bridge))
    assert not chk.holds and chk.measured == "not evaluable (open): bridge"
    assert chk.detail == ("constant term (%s): none; linear term (%s): none; open term (%s): "
                          "bridge; none may be present" % (CONST_WHY, LINEAR_WHY, OPEN_WHY))


def test_open_term_with_two_scalar_factors_does_not_pass():
    """R2-02: phi^2 passes only when closed (control above); listed as open it is not evaluable."""
    chk = _potential(_scalar_action(Term("mix", C_OPEN, ("phi", "phi"), open=True)))
    assert not chk.holds and chk.measured == "not evaluable (open): mix"
    deriv = _potential(_scalar_action(Term("op", C_OPEN, ("phi", "phi", "d"), open=True)))
    assert not deriv.holds and deriv.measured == "not evaluable (open): op"


def test_open_terms_are_reported_apart_from_closed_ones():
    """R2-02 and R2-03: each kind is named with the equation it breaks."""
    chk = _potential(_scalar_action(Term("lam", M2, ()), Term("tad", M2, ("phi",)),
                                    Term("bridge", C_OPEN, (), open=True)))
    assert not chk.holds and chk.measured == "lam,tad; not evaluable (open): bridge"
    assert chk.detail == ("constant term (%s): lam; linear term (%s): tad; open term (%s): "
                          "bridge; none may be present" % (CONST_WHY, LINEAR_WHY, OPEN_WHY))


def test_text_says_a_constant_breaks_the_einstein_equation():
    """R2-03: a constant gives T_MN != 0 on the Ricci-flat metric; phi = 0 still solves Box."""
    const = _potential(_scalar_action(Term("lam", M2, ())))
    assert "phi = 0 is not a vacuum" not in const.detail
    assert const.detail.startswith("constant term (%s): lam; linear term (%s): none"
                                   % (CONST_WHY, LINEAR_WHY))
    doc = " ".join(fe.__doc__.split())
    assert "no potential term spoils phi = 0" not in doc and "V(0) != 0" not in doc
    assert ("the Ricci-flat metric fails the Einstein equation (phi = 0 still solves "
            "Box phi = 0)") in doc
    assert "a linear term gives V'(0) != 0, so phi = 0 fails the scalar equation" in doc


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
