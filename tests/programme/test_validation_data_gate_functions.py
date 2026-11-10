"""VD-34: no gate function over 60 lines; table-driven run order; behaviour kept."""
import ast
import math
from pathlib import Path

import pytest

from metaphysica.generators import generate_72_certificates as gen72
from metaphysica.simulations.PM.validation import CERTIFICATES
from metaphysica.simulations.PM.validation.CERTIFICATES import (
    PrincipiaValidator, _SECTOR_RUN_ORDER)

VAL = Path(CERTIFICATES.__file__).parent
FILES = [VAL / "CERTIFICATES.py", *sorted((VAL / "certificate_gates").glob("*.py")),
         Path(gen72.__file__)]


def _long_functions(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [(n.name, n.end_lineno - n.lineno + 1) for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.end_lineno - n.lineno + 1 > 60]


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_functions_are_60_lines_or_fewer(path):
    assert _long_functions(path) == []


def test_run_order_names_real_gates_once():
    names = [n for _, group in _SECTOR_RUN_ORDER for n in group]
    assert len(names) == len(set(names)) == 27
    assert all(callable(getattr(PrincipiaValidator, n)) for n in names)


def _validator(params):
    v = PrincipiaValidator.__new__(PrincipiaValidator)
    v.reg, v.results, v.global_tension, v.pairs = dict(params), {}, 0.0, 12
    return v


def test_cosmo_guards_fail_on_missing_and_wrong_anchor():
    v = _validator({})
    v.cert_cosmo_013_wa()
    assert v.results["COSMO-013"]["status"] == "FAILED"
    v = _validator({"geometry.elder_kads": 43, "geometry.k_gimel": 1.0})
    v.cert_cosmo_014_neutrino_sum()
    row = v.results["COSMO-014"]
    assert row["status"] == "FAILED" and row["actual"] == 43
    v = _validator({"geometry.elder_kads": 24, "geometry.k_gimel": 12.0})
    v.cert_cosmo_014_neutrino_sum()
    assert "k_gimel cross-check failed" in v.results["COSMO-014"]["metric"]


def test_cosmo_rows_keep_honesty_blocks_at_the_anchor():
    k = 12 + 1 / math.pi
    v = _validator({"geometry.elder_kads": 24, "geometry.k_gimel": k})
    v.cert_cosmo_013_wa()
    v.cert_cosmo_014_neutrino_sum()
    v.cert_cosmo_015_h0()
    for gate in ("COSMO-013", "COSMO-014", "COSMO-015"):
        assert "honesty" in v.results[gate]
    assert v.results["COSMO-014"]["status"] == "LOCKED"
    assert v.results["COSMO-013"]["honesty"]["classification"] == "PREDICTED"


def test_g81_g82_rows_keep_honesty_and_failure_text():
    v = _validator({})
    v.cert_g81_asymptotic_safety_fixed_point()
    v.cert_g82_mirror_dm_relic_abundance()
    for gate in ("G81-AS", "G82-DM"):
        assert v.results[gate]["status"] in ("LOCKED", "FAILED")
        assert "honesty" in v.results[gate]
    if v.results["G82-DM"]["status"] == "FAILED":
        assert "not integer" in v.results["G82-DM"]["metric"] or "!=" in v.results["G82-DM"]["metric"]


def test_g83_row_shares_one_honesty_block():
    v = _validator({})
    v.cert_g83_qec_golay_bridge()
    assert v.results["G83-QEC"]["honesty"]["classification"] == "DERIVED"


def test_certificate_head_order_is_stable_for_every_kind():
    head = ["proof_id", "gate_id", "gate_name", "label", "category", "phase",
            "block", "version", "wl_code", "result"]
    gate = {"id": 999, "name": "Test Gate/x", "logic": "L"}
    for cert in (gen72._pending_certificate(gate, "P", "t"),
                 gen72._static_certificate(gate, "P", "t", "C", "MATHEMATICAL", "r", "n")):
        assert list(cert)[:len(head)] == head
        assert cert["gate_id"] == 999
    assert gen72._proof_id(gate) == "G999_test_gate_x"


def test_g72_seal_fails_when_any_executed_gate_fails():
    certs = [{"gate_id": 1, "evaluation_status": "COMPUTED_FAIL"},
             {"gate_id": 2, "evaluation_status": "DECLARATIVE"},
             {"gate_id": 72}]
    evaluated, fails = gen72._apply_g72_seal(certs)
    assert fails == [1] and len(evaluated) == 1
    assert certs[2]["evaluation_status"] == "COMPUTED_FAIL"
