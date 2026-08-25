"""Tests for Strategy A (Semantic) with mutation probes.

Every gate must FAIL when its underlying value is deliberately broken.
A gate that still passes after mutation is a fake gate.
"""
import pytest
from unittest.mock import patch, MagicMock
from metaphysica.simulations.PM.validation.declarative_strategies.strategy_a_semantic import (
    gate_G01_integer_root_parity,
    gate_G13_photon_zero_mass,
    gate_G17_generation_triality,
    gate_G22_gluon_string_tension,
    gate_G23_proton_stability_floor,
    gate_G29_weak_hypercharge,
    gate_G40_sterile_active_mixing,
    run_all,
)

# ---------------------------------------------------------------------------
# Baseline: all gates pass with the real registry
# ---------------------------------------------------------------------------

def test_strategy_a_all_pass():
    results = run_all()
    failures = [(r.gate_id, r.measured, r.expected) for r in results if r.verdict != "PASS"]
    assert failures == [], f"Unexpected failures: {failures}"


def test_strategy_a_no_numbers_invented():
    results = run_all()
    invented = [(r.gate_id, r.numbers_invented) for r in results if r.numbers_invented > 0]
    assert invented == [], f"Gates invented numbers: {invented}"


# ---------------------------------------------------------------------------
# Mutation tests: break the underlying value, confirm the gate FAILS.
# ---------------------------------------------------------------------------

class _FakeReg:
    """A mutable fake FormulasRegistry for injecting broken values."""
    roots_total = 288
    b3 = 24
    visible_sector = 125
    sterile_sector = 163
    n_gen = 3
    chi_eff = 72
    chi_eff_total = 144
    m_photon = None


def _patch_registry(broken_attr, broken_val):
    """Return a context manager that patches the registry with one bad value."""
    reg = _FakeReg()
    setattr(reg, broken_attr, broken_val)
    return patch(
        "metaphysica.simulations.PM.validation.declarative_strategies"
        ".strategy_a_semantic._registry",
        return_value=reg,
    )


# G01 mutation: roots_total != 288
def test_G01_mutation_fails():
    with _patch_registry("roots_total", 287):
        result = gate_G01_integer_root_parity()
    assert result.verdict == "FAIL", (
        "G01 must FAIL when roots_total=287; got PASS (fake gate!)"
    )


def test_G01_mutation_fails_extra():
    with _patch_registry("roots_total", 289):
        result = gate_G01_integer_root_parity()
    assert result.verdict == "FAIL"


# G13 mutation: m_photon != 0
def test_G13_mutation_fails():
    reg = _FakeReg()
    reg.m_photon = 1e-18  # non-zero mass injected
    with patch(
        "metaphysica.simulations.PM.validation.declarative_strategies"
        ".strategy_a_semantic._registry",
        return_value=reg,
    ):
        result = gate_G13_photon_zero_mass()
    assert result.verdict == "FAIL", (
        "G13 must FAIL when m_photon=1e-18; got PASS (fake gate!)"
    )


# G17 mutation: n_gen != 3
def test_G17_mutation_fails():
    with _patch_registry("n_gen", 4):
        result = gate_G17_generation_triality()
    assert result.verdict == "FAIL", (
        "G17 must FAIL when n_gen=4; got PASS (fake gate!)"
    )


# G22 mutation: b3 != 24
def test_G22_mutation_b3_fails():
    with _patch_registry("b3", 25):
        result = gate_G22_gluon_string_tension()
    assert result.verdict == "FAIL", (
        "G22 must FAIL when b3=25; got PASS (fake gate!)"
    )


# G22 mutation: roots_total != 288
def test_G22_mutation_roots_fails():
    with _patch_registry("roots_total", 290):
        result = gate_G22_gluon_string_tension()
    assert result.verdict == "FAIL"


# G23 mutation: proton lifetime below bound
def test_G23_mutation_fails(tmp_path, monkeypatch):
    import json
    # Write a parameters.json where tau_p < bound
    params = {
        "parameters": {
            "proton_decay.tau_p_years": {"value": 1.0e34},
            "bounds.tau_proton_lower": {"value": 1.67e34},
        }
    }
    broken = tmp_path / "parameters.json"
    broken.write_text(json.dumps(params))

    # Patch autogen_dir to return tmp_path
    from metaphysica.generators import _common as gc
    monkeypatch.setattr(gc, "autogen_dir", lambda: tmp_path)

    result = gate_G23_proton_stability_floor()
    assert result.verdict == "FAIL", (
        "G23 must FAIL when tau_p < bound; got PASS (fake gate!)"
    )


# G29 mutation: visible_sector != 125
def test_G29_mutation_visible_fails():
    with _patch_registry("visible_sector", 126):
        result = gate_G29_weak_hypercharge()
    assert result.verdict == "FAIL", (
        "G29 must FAIL when visible_sector=126; got PASS (fake gate!)"
    )


# G29 mutation: chi_eff_total != 144
def test_G29_mutation_chi_fails():
    reg = _FakeReg()
    reg.chi_eff_total = 145
    with patch(
        "metaphysica.simulations.PM.validation.declarative_strategies"
        ".strategy_a_semantic._registry",
        return_value=reg,
    ):
        result = gate_G29_weak_hypercharge()
    assert result.verdict == "FAIL"


# G40 mutation: sterile_sector != 163
def test_G40_mutation_sterile_fails():
    with _patch_registry("sterile_sector", 164):
        result = gate_G40_sterile_active_mixing()
    assert result.verdict == "FAIL", (
        "G40 must FAIL when sterile_sector=164; got PASS (fake gate!)"
    )


# G40 mutation: roots_total != 288
def test_G40_mutation_roots_fails():
    with _patch_registry("roots_total", 290):
        result = gate_G40_sterile_active_mixing()
    assert result.verdict == "FAIL"
