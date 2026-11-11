"""Validation-data close-out XV-09: C002 and C003 take their expected values from the path helpers."""

import inspect

import pytest

from metaphysica.simulations.PM.geometry import b3_path
from metaphysica.simulations.PM.geometry.chi_eff_branches import N_GEN_DIVISOR
from metaphysica.simulations.PM.validation.CERTIFICATES import PrincipiaValidator
from metaphysica.simulations.PM.validation.certificate_gates import core
from metaphysica.simulations.core.variants.selection import forced


def _run(gate, key, chi):
    v = PrincipiaValidator.__new__(PrincipiaValidator)
    v.reg, v.results = {"topology.mephorash_chi": {"value": chi}}, {}
    getattr(v, gate)()
    return v.results[key]


def _path_chi():
    return N_GEN_DIVISOR * b3_path.n_gen_report()["n_gen"]


@pytest.mark.parametrize("gate,key", [("cert_c002_three_generations", "C002-GEN"),
                                      ("cert_c003_chi_effective", "C003-CHI")])
def test_gates_lock_on_the_active_path(gate, key):
    assert _run(gate, key, _path_chi())["status"] == "LOCKED"


def test_c002_expected_is_the_path_n_gen(monkeypatch):
    real = b3_path.n_gen_report()
    monkeypatch.setattr(b3_path, "n_gen_report", lambda path=None: {**real, "n_gen": 4})
    row = _run("cert_c002_three_generations", "C002-GEN", N_GEN_DIVISOR * 4)
    assert row["expected"] == 4 and row["status"] == "LOCKED"


def test_c003_expected_is_the_path_n_gen(monkeypatch):
    real = b3_path.n_gen_report()
    monkeypatch.setattr(b3_path, "n_gen_report", lambda path=None: {**real, "n_gen": 4})
    row = _run("cert_c003_chi_effective", "C003-CHI", N_GEN_DIVISOR * 4)
    assert row["expected"] == N_GEN_DIVISOR * 4 and row["status"] == "LOCKED"


def test_forced_n_gen_source_moves_both_gates():
    chi = _path_chi()
    with forced({"n_gen_source": "b3_over_dim_O"}):
        n_gen = b3_path.n_gen_report()["n_gen"]
        c002 = _run("cert_c002_three_generations", "C002-GEN", chi)
        c003 = _run("cert_c003_chi_effective", "C003-CHI", chi)
    assert c002["expected"] == n_gen and c003["expected"] == N_GEN_DIVISOR * n_gen
    if n_gen != int(n_gen):
        assert c002["status"] == "FAILED" and c003["status"] == "FAILED"


def test_missing_registry_value_fails():
    for gate, key in (("cert_c002_three_generations", "C002-GEN"),
                      ("cert_c003_chi_effective", "C003-CHI")):
        assert _run(gate, key, None)["status"] == "FAILED"


def test_gate_bodies_type_no_generation_count():
    for fn in (core.CoreGates.cert_c002_three_generations, core.CoreGates.cert_c003_chi_effective):
        body = inspect.getsource(fn).split('"""')[2]
        for literal in ("== 3", "// 48", "/ 48", "48 *", "144", "expected\": 3"):
            assert literal not in body
