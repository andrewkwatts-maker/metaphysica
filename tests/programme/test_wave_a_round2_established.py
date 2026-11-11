"""Wave A round 2, base/established.py.

Each test fails on the code before the fix:
* R2-20 topology.orientation_sum kept source "ESTABLISHED:V21_BRIDGE_REDUCTION"
  while its status (ANSATZ) and description said it is a typed count of the
  retired TCS #187 reading, so the source label claimed more than the row does.
"""
import pytest

from metaphysica.simulations.base import established
from metaphysica.simulations.base.established import (
    UNMEASURED_STATUSES, EstablishedPhysics)

ORIENTATION_SUM = "topology.orientation_sum"


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
