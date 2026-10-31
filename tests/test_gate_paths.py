"""Gates read the selected path's values; premises gate applicability."""
import pytest

from metaphysica.simulations.PM.paper.appendices import gate_paths
from metaphysica.simulations.PM.paper.appendices.appendix_f_72gates import GateRegistry
from metaphysica.simulations.PM.paper.appendices.gate_paths import (
    FAIL, MissingGateInput, NOT_APPLICABLE, PASS,
)

BASE = {"roots": 288, "active": 125, "hidden": 163, "torsion": 24,
        "per_shadow": 12, "b3": 43}
DEFAULT_SEL = {"b3_seed": "seed_43_joyce"}


def data(**kw):
    return {**BASE, "selection": DEFAULT_SEL, **kw}


def test_gate_reads_path_value_not_literal():
    # G6 compares pins to the registry's per-shadow count, so 30 pins / 15 pass
    assert GateRegistry.evaluate_gate(6, data(torsion=30, per_shadow=15))[0] == PASS
    assert GateRegistry.evaluate_gate(6, data(torsion=30))[0] == FAIL


def test_b3_gate_uses_selected_b3():
    sel = {"b3_seed": "seed_24"}
    assert GateRegistry.evaluate_gate(31, data(selection=sel, b3=24))[0] == PASS
    assert GateRegistry.evaluate_gate(31, data(selection=sel, b3=43))[0] == FAIL


def test_not_applicable_when_path_lacks_premise():
    state, why = GateRegistry.evaluate_gate(31, data())
    assert state == NOT_APPLICABLE and "seed_24" in why


def test_missing_value_fails_early_with_row_name():
    bad = data()
    del bad["torsion"]
    with pytest.raises(MissingGateInput, match="topology.shadow_torsion_total"):
        GateRegistry.evaluate_gate(6, bad)


def test_audit_counts_and_path_id():
    audit = GateRegistry.run_full_audit(data())
    assert audit["applicable"] == audit["passed"] + audit["failed"]
    assert audit["applicable"] + audit["not_applicable"] == 72
    assert audit["not_applicable_gates"] == [31]
    assert audit["failed"] == 0 and audit["path_id"] == gate_paths.path_id(DEFAULT_SEL)
