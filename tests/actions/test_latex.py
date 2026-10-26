"""Generic LaTeX rendering of an Action (theory-agnostic)."""
from __future__ import annotations

from fractions import Fraction as Fr

import pytest

from metaphysica.actions.latex import action_latex
from metaphysica.actions.model import (
    INPUT, OPEN, Action, Coefficient, Field, ModelError, Term,
)


def _action(times, dim, terms):
    fields = (Field("G", "metric", 1, Fr(0)), Field("T", "scalar", 1, Fr(0)))
    return Action("X", dim, (dim - times, times), fields, tuple(terms))


def _t(tid, latex=None, sign=1, open_=False):
    c = Coefficient("c_" + tid, Fr(0), OPEN if open_ else INPUT, None if open_ else "p")
    return Term(tid, c, ("T",), 0, sign, open_, latex)


def test_two_times_use_abs_measure_in_declared_order():
    out = action_latex(_action(2, 6, [_t("a", "A"), _t("b", "B", -1), _t("c", None, 1, True)]))
    assert out.startswith(r"S_{6} = \int d^{6}x\,\sqrt{|g|}")
    assert out.index("A") < out.index("- B") < out.index(r"\mathrm{c\_c}")


def test_one_time_uses_minus_g_and_negative_first_sign():
    out = action_latex(_action(1, 4, [_t("a", "A", -1)]))
    assert r"\sqrt{-g}" in out and "[ - A " in out


def test_three_times_has_no_measure():
    with pytest.raises(ModelError, match="no measure"):
        action_latex(_action(3, 6, [_t("a", "A")]))


def test_no_terms_fails_early():
    with pytest.raises(ModelError, match="no terms"):
        action_latex(_action(1, 4, []))
