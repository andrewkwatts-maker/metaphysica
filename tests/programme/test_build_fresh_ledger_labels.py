"""XB-07: the parameter ledger classes every status run_all_simulations preserves.

The fresh build raised ``UnknownLabel: no class for status label 'DIAGNOSTIC'``
on ``neutrino.sum_masses``. PRESERVED_PARAMETER_STATUSES is read from the module
source with ast: importing run_all_simulations is heavy and not side-effect free.
"""
import ast
from pathlib import Path

import pytest

import metaphysica
from metaphysica.generators import parameter_ledger as pl

RUN_ALL = (Path(metaphysica.__file__).parent / "simulations"
           / "run_all_simulations.py")


def _preserved_statuses():
    tree = ast.parse(RUN_ALL.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "PRESERVED_PARAMETER_STATUSES" not in names:
            continue
        call = node.value
        assert isinstance(call, ast.Call) and call.args, "frozenset({...}) expected"
        return {elt.value for elt in call.args[0].elts}
    raise AssertionError("PRESERVED_PARAMETER_STATUSES not found in %s" % RUN_ALL)


def test_diagnostic_is_a_convention():
    assert pl.label_class("DIAGNOSTIC") == pl.CONVENTION


def test_every_preserved_status_is_classed_or_named_unclassed():
    preserved = _preserved_statuses()
    assert "DIAGNOSTIC" in preserved
    unclassed = set(pl.UNCLASSED_PRESERVED_LABELS)
    missing = preserved - set(pl.LABEL_CLASS) - unclassed
    assert not missing, "preserved statuses with no class: %s" % sorted(missing)


def test_unclassed_labels_are_not_classed_and_raise():
    for lab in pl.UNCLASSED_PRESERVED_LABELS:
        assert lab not in pl.LABEL_CLASS
        with pytest.raises(pl.UnknownLabel):
            pl.label_class(lab)


def test_ledger_builds_a_diagnostic_row():
    params = {"neutrino.sum_masses": {"value": 0.06, "status": "DIAGNOSTIC",
                                      "source": "x"}}
    rows = pl.build_ledger(params, {}, {"rows": []}, {})["rows"]
    assert len(rows) == 1


# PT-11: IDENTITY (three algebra.clifford_* rows, true by construction) is kept
# at export and classed CONVENTION, so it never ships as DERIVED and the ledger
# step does not raise UnknownLabel.
def test_identity_is_preserved_at_export():
    assert "IDENTITY" in _preserved_statuses()


def test_identity_is_a_convention():
    assert "IDENTITY" not in pl.UNCLASSED_PRESERVED_LABELS
    assert pl.label_class("IDENTITY") == pl.CONVENTION


def test_ledger_builds_an_identity_row_as_convention():
    name = "algebra.clifford_g2_invariant"
    params = {name: {"value": 1.0, "status": "IDENTITY", "source": "x",
                     "experimental_value": 1.0, "validation_status": "PASS"}}
    rows = pl.build_ledger(params, {}, {"rows": []}, {})["rows"]
    assert set(rows) == {name}
    row = rows[name]
    assert row["label"] == "IDENTITY"
    assert row["class"] == pl.CONVENTION
    # An identity is never scored: a PASS against a datum is not a test of it.
    assert row["falsifiability"]["state"] == "NOT_OBSERVABLE"
