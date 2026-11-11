"""Close-out XP-02, XP-10: registry rows carry the status of what they are.

Each test fails on the code before the close-out:
* XP-02 the lambda_S named constant (sqrt of the frozen 24) carried no status;
* XP-10 consciousness.coherence_fraction and topology.orientation_sum were
  registered ESTABLISHED with themselves as the experimental value, so a typed
  input was validated at sigma 0. The close-out review moved their status from
  INPUT (no ledger class) to the ledger's SPECULATIVE and ANSATZ.
"""
import pytest

from metaphysica.simulations.base.established import EstablishedPhysics


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


@pytest.mark.parametrize("path, status", [
    ("consciousness.coherence_fraction", "SPECULATIVE"),
    ("topology.orientation_sum", "ANSATZ")])
def test_typed_inputs_are_not_validated_against_themselves(theory_rows, path, status):
    row = theory_rows[path]
    assert row["status"] == status
    assert "experimental_value" not in row
    assert "bound_type" not in row


def test_every_theory_row_status_has_a_ledger_class(theory_rows):
    """Close-out review: the INPUT status raised UnknownLabel in the ledger."""
    from metaphysica.generators.parameter_ledger import ANSATZ, label_class

    for path, row in theory_rows.items():
        label_class(row["status"])  # raises UnknownLabel on an unclassed status
    for path in ("consciousness.coherence_fraction", "topology.orientation_sum"):
        assert label_class(theory_rows[path]["status"]) == ANSATZ


def test_orientation_sum_says_it_is_not_derived_on_the_path(theory_rows):
    desc = theory_rows["topology.orientation_sum"]["metadata"]["description"]
    assert "TCS #187" in desc and "not derived" in desc


def test_lambda_s_named_constant_is_an_ansatz():
    import importlib

    mod = importlib.import_module("metaphysica.simulations.core.FormulasRegistry")
    assert mod.FROZEN_PLEROMA_STATUS == "ANSATZ"
    entry = mod.FormulasRegistry().generate_named_constants_json()[
        "constants"]["hossenfelder_root"]
    assert entry["status"] == "ANSATZ"
    assert "owner decision" in entry["status_reason"]
