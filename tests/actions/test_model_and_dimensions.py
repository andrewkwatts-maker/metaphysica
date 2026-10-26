"""Model validation and the dimension rules of the action-ladder engine."""

from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path

import pytest

from metaphysica.actions.controls import four_d
from metaphysica.actions.dimensions import canonical_dim, check_action
from metaphysica.actions.model import (
    DERIVED, INPUT, OPEN, Action, Coefficient, Field, ModelError, Term,
)

_PKG = Path(__file__).resolve().parents[2] / "src" / "metaphysica" / "actions"
_FORBIDDEN = ("metaphysica.simulations", "metaphysica.generators", "metaphysica.website")


def _coef(src=INPUT, prov="p", dim=0):
    return Coefficient("c", Fraction(dim), src, prov)


def _action(terms, dim=4, sig=(3, 1), fields=()):
    return Action("a", dim, sig, tuple(fields), tuple(terms))


def test_actions_imports_nothing_from_theory_code():
    offenders = []
    for path in _PKG.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else [node.module] if isinstance(node, ast.ImportFrom) and node.module
                     else [])
            offenders += [(path.name, n) for n in names if n.startswith(_FORBIDDEN)]
    assert not offenders, offenders


def test_unknown_field_name_is_refused():
    with pytest.raises(ModelError):
        _action([Term("t", _coef(), ("ghost",))])


def test_signature_must_sum_to_dim():
    with pytest.raises(ModelError):
        _action([], dim=5, sig=(3, 1))


def test_duplicate_term_ids_are_refused():
    t = Term("t", _coef(), ("R",))
    with pytest.raises(ModelError):
        _action([t, t])


def test_provider_is_required_unless_open():
    with pytest.raises(ModelError):
        Coefficient("c", Fraction(0), DERIVED, None)
    Coefficient("c", Fraction(0), OPEN, None)


def test_unknown_kind_and_source_are_refused():
    with pytest.raises(ModelError):
        Field("f", "tensor", 1, Fraction(1))
    with pytest.raises(ModelError):
        Coefficient("c", Fraction(0), "GUESSED", "p")
    Field("f", "form:3", 1, Fraction(1))


def test_canonical_dimensions():
    assert canonical_dim("scalar", 4) == 1
    assert canonical_dim("spinor", 4) == Fraction(3, 2)
    assert canonical_dim("vector", 6) == 2
    assert canonical_dim("spinor", 11) == 5


def test_standard_4d_action_balances_and_6d_quartic_does_not():
    assert all(c.holds for c in check_action(four_d.standard_model_like_action()))
    bad = [c.id for c in check_action(four_d.six_d_quartic_action()) if not c.holds]
    assert bad == ["dim:phi4_6d:quartic"]


def test_open_coefficient_only_on_open_term():
    open_c = Coefficient("L_C", Fraction(4), OPEN, None)
    ok = _action([Term("t", open_c, (), open=True)])
    assert all(c.holds for c in check_action(ok))
    bad = _action([Term("t", open_c, (), open=False)])
    assert [c.id for c in check_action(bad) if not c.holds] == ["open:a:t"]
