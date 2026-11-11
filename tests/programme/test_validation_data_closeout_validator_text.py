"""XV-04: docstrings and comments of statistical_rigor_validator match the code.

No docstring or comment quotes the old chi^2 ~ 0.23 / DOF = 25 / TOO_GOOD
fallback or names a method the validator no longer has, and the docstrings of
the methods XV-04 rewrote say what they return.
"""

import ast
import io
import tokenize
from pathlib import Path

import pytest

from metaphysica.simulations.PM.validation import statistical_rigor_validator as srv

SOURCE = Path(srv.__file__).read_text(encoding="utf-8")
CLASS = srv.StatisticalRigorValidator


def _docstrings():
    """Every module, class and function docstring of the validator."""
    tree = ast.parse(SOURCE)
    nodes = [tree] + [n for n in ast.walk(tree) if isinstance(
        n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
    return [ast.get_docstring(n) or "" for n in nodes]


def _comments():
    """Every ``#`` comment of the validator."""
    tokens = tokenize.generate_tokens(io.StringIO(SOURCE).readline)
    return [t.string for t in tokens if t.type == tokenize.COMMENT]


TEXT = "\n".join(_docstrings() + _comments())


@pytest.mark.parametrize("stale", [
    "0.23", "DOF = 25", "DoF = 25", "chi_sq~0.23",
    "recalculate_with_theory_uncertainty", "_chi_squared_split",
    "generate_jacobian_matrix", "ONLY fitted parameter",
])
def test_no_stale_text_in_docstrings_or_comments(stale):
    assert stale not in TEXT


@pytest.mark.parametrize("name", [
    "recalculate_with_theory_uncertainty", "_chi_squared_split",
    "generate_jacobian_matrix"])
def test_named_methods_really_are_gone(name):
    assert not hasattr(CLASS, name)


@pytest.mark.parametrize("method, words", [
    ("calculate_effective_dof", ("Return 3",)),
    ("free_variable_count", ("Return", "published_free_variable_count")),
    ("calculate_p_value_with_edof", ("Return", "p_value", "status")),
])
def test_docstring_names_what_the_method_returns(method, words):
    doc = getattr(CLASS, method).__doc__
    assert doc.strip().startswith("Return")
    for word in words:
        assert word in doc


def test_effective_dof_docstring_matches_return_value():
    assert CLASS.calculate_effective_dof.__doc__.strip().startswith(
        f"Return {CLASS.calculate_effective_dof(None)},")
