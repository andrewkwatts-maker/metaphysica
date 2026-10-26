"""Established-physics controls for the action-ladder engine."""

from __future__ import annotations

from fractions import Fraction

import sympy as sp

from metaphysica.actions.controls import four_d, kaluza_klein, ricci_flat_compactification
from metaphysica.actions.ladder import Ladder, Step
from metaphysica.actions.model import DERIVED, INPUT, Action, Coefficient, Field, Term
from metaphysica.actions.reduction import InternalSpace, Reduction


def _five_d() -> Action:
    ms3 = Coefficient("M_star^3", Fraction(3), INPUT, "input:M_star")
    g = Field("g", "metric", 1, Fraction(0))
    return Action("gr_5d", 5, (4, 1), (g,), (Term("eh", ms3, ("R",)),))


def _four_d_reduced() -> Action:
    mpl = Coefficient("M_Pl^2", Fraction(2), DERIVED, "reduction:S1")
    unit = Coefficient("1", Fraction(0), INPUT, "convention")
    fields = (Field("g", "metric", 1, Fraction(0)), Field("A", "vector", 4, Fraction(1)),
              Field("phi", "scalar", 1, Fraction(1)))
    terms = (Term("eh", mpl, ("R",)), Term("maxwell", unit, ("A", "d", "A", "d")),
             Term("dilaton", unit, ("phi", "d", "phi", "d")))
    return Action("gr_maxwell_dilaton_4d", 4, (3, 1), fields, terms)


def standard_ladder() -> Ladder:
    """Textbook ladder: 5D GR -> (S1) -> 4D GR + Maxwell + dilaton -> 4D checks."""
    five, four = _five_d(), _four_d_reduced()
    ms3, vol = sp.Symbol("M_star^3", positive=True), sp.Symbol("Vol", positive=True)
    circle = InternalSpace("S1", 1, True, {0: 1, 1: 1}, "Vol")
    red = Reduction(five, four, circle, {"M_Pl^2": ms3 * vol})
    return Ladder((
        Step("gr_5d", five),
        Step("gr_maxwell_dilaton_4d", four, red,
             kaluza_klein.correspondences()
             + ricci_flat_compactification.correspondences()),
        Step("checks_4d", four_d.standard_model_like_action(), None,
             four_d.correspondences()),
    ))
