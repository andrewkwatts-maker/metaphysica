"""Wave A round 2, base/established.py.

Each test fails on the code before the fix:
* R2-20 topology.orientation_sum kept source "ESTABLISHED:V21_BRIDGE_REDUCTION"
  while its status (ANSATZ) and description said it is a typed count of the
  retired TCS #187 reading, so the source label claimed more than the row does.
* Review of R2-20: the fix repeated the comment of ORIENTATION_SUM_SOURCE at
  its use, growing _load_theory_constants from 108 to 110 lines.
* Review of R2-20: with the INPUT: source the override guard of the registry
  is as before only when the established loader sets the row first; over a
  row already set with status ESTABLISHED the loader is now refused (the test
  of that order fails on the code before R2-20, where the prefix let it pass).
"""
import ast
import inspect
import re

import pytest

from metaphysica.simulations.base import established
from metaphysica.simulations.base.established import (
    UNMEASURED_STATUSES, EstablishedPhysics)
from metaphysica.simulations.base.registry import PMRegistry

ORIENTATION_SUM = "topology.orientation_sum"

#: Lines of EstablishedPhysics._load_theory_constants, def line to last line.
#: Measured 2026-11-11 with ast over base/established.py: 108 at a52fb71^,
#: 110 at a52fb71 (R2-20), 108 after the review fix. The function is older
#: than the 60-line cap; the pin stops it growing.
LOAD_THEORY_CONSTANTS_LINES = 108


class _Recorder:
    """Stands in for PMRegistry: records every set_param call by path."""

    def __init__(self):
        self.rows = {}

    def set_param(self, **kwargs):
        self.rows[kwargs["path"]] = kwargs

    def has_param(self, path):
        return path in self.rows


@pytest.fixture(scope="module")
def theory_rows():
    rec = _Recorder()
    EstablishedPhysics._load_theory_constants(rec)
    return rec.rows


def test_orientation_sum_source_does_not_claim_established(theory_rows):
    row = theory_rows[ORIENTATION_SUM]
    assert row["status"] == "ANSATZ"
    assert not row["source"].startswith("ESTABLISHED")
    assert row["source"] == established.ORIENTATION_SUM_SOURCE
    assert row["source"] == "INPUT:TCS187_RETIRED_READING"


def test_orientation_sum_text_names_the_retired_reading(theory_rows):
    meta = theory_rows[ORIENTATION_SUM]["metadata"]
    for text in (meta["description"], meta["eml_description"]):
        assert "retired TCS #187 reading" in text


def test_no_unmeasured_theory_row_has_an_established_source(theory_rows):
    """A typed ansatz or speculative input is never labelled ESTABLISHED."""
    unmeasured = {path: row for path, row in theory_rows.items()
                  if row["status"] in UNMEASURED_STATUSES}
    assert ORIENTATION_SUM in unmeasured
    claimed = sorted(path for path, row in unmeasured.items()
                     if row["source"].startswith("ESTABLISHED"))
    assert claimed == []


def _function_lines(name):
    tree = ast.parse(inspect.getsource(established))
    found = [node for node in ast.walk(tree)
             if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(found) == 1, f"{name}: {len(found)} definitions"
    return found[0].end_lineno - found[0].lineno + 1


def test_load_theory_constants_has_not_grown():
    assert _function_lines("_load_theory_constants") <= LOAD_THEORY_CONSTANTS_LINES


@pytest.fixture
def fresh_registry(monkeypatch):
    """A registry of its own: the singleton slot is emptied, and restored after."""
    monkeypatch.setattr(PMRegistry, "_instance", None)
    return PMRegistry()


def test_override_guard_passes_when_the_loader_sets_the_row_first(fresh_registry, theory_rows):
    EstablishedPhysics._load_theory_constants(fresh_registry)
    assert fresh_registry.get_entry(ORIENTATION_SUM).status == "ANSATZ"
    fresh_registry.set_param(**theory_rows[ORIENTATION_SUM])  # the call of the loader, again
    entry = fresh_registry.get_entry(ORIENTATION_SUM)
    assert (entry.status, entry.source) == ("ANSATZ", established.ORIENTATION_SUM_SOURCE)


def test_override_guard_refuses_the_loader_over_an_established_row(fresh_registry):
    """The order of a registry where the row was first set as ESTABLISHED."""
    fresh_registry.set_param(ORIENTATION_SUM, 12, source="ESTABLISHED:set_before_the_loader",
                             status="ESTABLISHED")
    refusal = re.escape(f"Cannot override ESTABLISHED param '{ORIENTATION_SUM}'")
    with pytest.raises(ValueError, match=refusal):
        EstablishedPhysics._load_theory_constants(fresh_registry)
    assert fresh_registry.get_entry(ORIENTATION_SUM).status == "ESTABLISHED"
