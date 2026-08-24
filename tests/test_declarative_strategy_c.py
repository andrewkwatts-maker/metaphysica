"""Tests for Strategy C (Structural) with mutation probes.

The structural checks must FAIL when a certificate's fields are broken.
"""
import json
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from metaphysica.simulations.PM.validation.declarative_strategies.strategy_c_structural import (
    check_gate,
    run_all,
    _run_checks,
    ConsistencyCheck,
)


# ---------------------------------------------------------------------------
# Minimal valid certificate for injection
# ---------------------------------------------------------------------------

def _valid_cert(gate_id: int = 1, gate_name: str = "Test Gate") -> dict:
    return {
        "proof_id": f"G{gate_id:02d}_test",
        "gate_id": gate_id,
        "gate_name": gate_name,
        "label": "test label",
        "category": "Topology",
        "phase": 1,
        "block": "A",
        "version": "24.2",
        "wl_code": "N = 288; If[N == 288, \"LOCKED\", \"OPEN\"]",
        "result": "LOCKED",
        "formula": "N_total = 288",
        "verification_status": "VERIFIED",
        "evaluation_status": "DECLARATIVE",
        "evaluation": {"tier": "none", "status": "DECLARATIVE"},
        "derivation_status": "RIGOROUS",
        "note": "test note",
        "timestamp": "2026-08-24T04:22:41.974492Z",
        "hash": "91478cdb7ab380a3",
    }


# ---------------------------------------------------------------------------
# Baseline: all 6 sample gates pass structural checks
# ---------------------------------------------------------------------------

def test_strategy_c_all_pass():
    results = run_all()
    failures = [
        (r.gate_id, [f"{c.field_name}: {c.detail}" for c in r.failures])
        for r in results if r.verdict != "PASS"
    ]
    assert failures == [], f"Structural failures: {failures}"


def test_strategy_c_no_numbers_invented():
    results = run_all()
    for r in results:
        assert r.numbers_invented == 0


# ---------------------------------------------------------------------------
# Mutation tests: break individual fields, confirm FAIL
# ---------------------------------------------------------------------------

def _check_passes(cert, field):
    checks = _run_checks(cert)
    return any(c.field_name == field and c.passed for c in checks)


def _check_fails(cert, field):
    checks = _run_checks(cert)
    return any(c.field_name == field and not c.passed for c in checks)


def test_mutation_missing_proof_id():
    cert = _valid_cert()
    del cert["proof_id"]
    assert _check_fails(cert, "proof_id"), "Should FAIL when proof_id missing"


def test_mutation_missing_formula():
    cert = _valid_cert()
    del cert["formula"]
    assert _check_fails(cert, "formula"), "Should FAIL when formula missing"


def test_mutation_empty_formula():
    cert = _valid_cert()
    cert["formula"] = "   "
    assert _check_fails(cert, "formula_nonempty"), "Should FAIL when formula is whitespace"


def test_mutation_empty_wl_code():
    cert = _valid_cert()
    cert["wl_code"] = ""
    assert _check_fails(cert, "wl_code_nonempty"), "Should FAIL when wl_code is empty"


def test_mutation_empty_result():
    cert = _valid_cert()
    cert["result"] = ""
    assert _check_fails(cert, "result_nonempty"), "Should FAIL when result is empty"


def test_mutation_invalid_hash():
    cert = _valid_cert()
    cert["hash"] = "not-hex-at-all"
    assert _check_fails(cert, "hash_is_hex"), "Should FAIL when hash is not hex"


def test_mutation_empty_hash():
    cert = _valid_cert()
    cert["hash"] = ""
    assert _check_fails(cert, "hash_is_hex"), "Should FAIL when hash is empty"


def test_mutation_gate_id_out_of_range():
    cert = _valid_cert(gate_id=73)
    assert _check_fails(cert, "gate_id_range"), "Should FAIL when gate_id=73"


def test_mutation_gate_id_zero():
    cert = _valid_cert(gate_id=0)
    assert _check_fails(cert, "gate_id_range"), "Should FAIL when gate_id=0"


def test_mutation_bad_timestamp():
    cert = _valid_cert()
    cert["timestamp"] = "not-a-date"
    assert _check_fails(cert, "timestamp_parseable"), "Should FAIL when timestamp is garbage"


def test_mutation_unknown_evaluation_status():
    cert = _valid_cert()
    cert["evaluation_status"] = "INVENTED_STATUS"
    assert _check_fails(cert, "evaluation_status_valid"), "Should FAIL for unknown status"


def test_mutation_evaluation_missing_tier():
    cert = _valid_cert()
    cert["evaluation"] = {"status": "DECLARATIVE"}  # no 'tier' key
    assert _check_fails(cert, "evaluation_subobject"), "Should FAIL when 'tier' missing"


def test_mutation_wrong_type_gate_id():
    cert = _valid_cert()
    cert["gate_id"] = "1"  # string instead of int
    assert _check_fails(cert, "gate_id"), "Should FAIL when gate_id is a string"


# ---------------------------------------------------------------------------
# Confirm: a structurally valid cert passes all checks
# ---------------------------------------------------------------------------

def test_valid_cert_passes_all():
    cert = _valid_cert()
    checks = _run_checks(cert)
    failures = [c for c in checks if not c.passed]
    assert failures == [], f"Valid cert should have no failures, got: {failures}"


# ---------------------------------------------------------------------------
# Confirm: missing cert file reports FAIL
# ---------------------------------------------------------------------------

def test_missing_cert_file():
    # Gate 99 does not exist in the certificates directory
    result = check_gate(99)
    assert result.verdict == "FAIL"
    assert any("not found" in c.detail for c in result.checks)
