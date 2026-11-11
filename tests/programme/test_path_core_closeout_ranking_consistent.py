"""XP-08: theories/pm/ranking._consistent maps ERRORED to missing and raises otherwise.

On the old code every exception from the switch search became None (missing),
and an ERRORED row (held back only by checks that could not run) was reported
as inconsistent (False).
"""
import pytest

from metaphysica.simulations.core import switch_search
from metaphysica.theories.pm import ranking


def _row(state, consistent):
    return {"state": state, "internally_consistent": consistent}


def test_errored_row_is_missing(monkeypatch):
    monkeypatch.setattr(switch_search, "evaluate_combination",
                        lambda sel: _row("ERRORED", False))
    assert ranking._consistent({"b3_seed": "x"}) is None


@pytest.mark.parametrize("state, consistent", [
    ("CONSISTENT", True), ("INCONSISTENT", False)])
def test_evaluated_row_is_its_verdict(monkeypatch, state, consistent):
    monkeypatch.setattr(switch_search, "evaluate_combination",
                        lambda sel: _row(state, consistent))
    assert ranking._consistent({}) is consistent


def test_search_failure_raises(monkeypatch):
    def broken(sel):
        raise RuntimeError("search defect")

    monkeypatch.setattr(switch_search, "evaluate_combination", broken)
    with pytest.raises(RuntimeError, match="search defect"):
        ranking._consistent({})


def test_row_without_state_raises(monkeypatch):
    monkeypatch.setattr(switch_search, "evaluate_combination",
                        lambda sel: {"internally_consistent": True})
    with pytest.raises(KeyError):
        ranking._consistent({})
