"""Tests for Strategy B (Data-driven) with mutation probes.

Every gate must FAIL when the underlying registry value is deliberately broken.
"""
import json
import pytest
from unittest.mock import patch

from metaphysica.simulations.PM.validation.declarative_strategies.strategy_b_data_driven import (
    gate_G01_integer_root_parity,
    gate_G17_generation_triality,
    gate_G22_gluon_string_tension,
    gate_G23_proton_stability_floor,
    gate_G36_ckm_unitarity,
    gate_G37_cp_violation_phase,
    run_all,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _broken_params(overrides: dict) -> dict:
    """Build a minimal parameters dict with overridden values."""
    base = {
        "topology.ancestral_roots": {"value": 288},
        "fermion.n_generations": {"value": 3},
        "topology.shadow_torsion_total": {"value": 24},
        "geometry.roots_total": {"value": 288},
        "proton_decay.tau_p_years": {"value": 4.757e34},
        "bounds.tau_proton_lower": {"value": 1.67e34},
        "ckm.unitarity_test": {"value": 5.83e-5},
        "ckm.jarlskog_invariant": {"value": 2.91e-5},
        "pdg.J_ckm": {"value": 3.12e-5, "uncertainty": 1.3e-6},
    }
    for k, v in overrides.items():
        base[k] = v
    return base


def _patch_params(overrides: dict):
    params = _broken_params(overrides)
    return patch(
        "metaphysica.simulations.PM.validation.declarative_strategies"
        ".strategy_b_data_driven._params",
        return_value=params,
    )


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

def test_strategy_b_all_pass():
    results = run_all()
    failures = [(r.gate_id, r.measured, r.expected) for r in results if r.verdict != "PASS"]
    assert failures == [], f"Unexpected failures: {failures}"


# ---------------------------------------------------------------------------
# Mutation tests
# ---------------------------------------------------------------------------

def test_G01_mutation_fails():
    with _patch_params({"topology.ancestral_roots": {"value": 289}}):
        result = gate_G01_integer_root_parity()
    assert result.verdict == "FAIL", "G01 must FAIL when ancestral_roots=289"


def test_G17_mutation_fails():
    with _patch_params({"fermion.n_generations": {"value": 4}}):
        result = gate_G17_generation_triality()
    assert result.verdict == "FAIL", "G17 must FAIL when n_generations=4"


def test_G22_mutation_shadow_fails():
    with _patch_params({"topology.shadow_torsion_total": {"value": 25}}):
        result = gate_G22_gluon_string_tension()
    assert result.verdict == "FAIL", "G22 must FAIL when shadow_torsion_total=25"


def test_G22_mutation_roots_fails():
    with _patch_params({"geometry.roots_total": {"value": 290}}):
        result = gate_G22_gluon_string_tension()
    assert result.verdict == "FAIL", "G22 must FAIL when roots_total=290"


def test_G23_mutation_fails():
    with _patch_params({"proton_decay.tau_p_years": {"value": 1.0e34}}):
        result = gate_G23_proton_stability_floor()
    assert result.verdict == "FAIL", "G23 must FAIL when tau_p < bound"


def test_G36_mutation_fails():
    # G36 checks deviation < 1.0; inject deviation > 1.0
    with _patch_params({"ckm.unitarity_test": {"value": 1.5}}):
        result = gate_G36_ckm_unitarity()
    assert result.verdict == "FAIL", "G36 must FAIL when unitarity_test > 1"


def test_G37_mutation_fails():
    # Inject J_theory so far from PDG that it fails 5-sigma test
    # PDG: 3.12e-5 ± 1.3e-6 → 5-sigma window is ± 6.5e-6
    # J_theory = 1e-7 is ~240 sigma away
    with _patch_params({"ckm.jarlskog_invariant": {"value": 1e-7}}):
        result = gate_G37_cp_violation_phase()
    assert result.verdict == "FAIL", "G37 must FAIL when Jarlskog invariant is 1e-7"


# Note on G36's weak threshold:
# G36 uses deviation < 1.0 (definitional unitarity), not the physically
# relevant ~ 1e-4 threshold.  The mutation test above confirms the gate
# CAN fail, but only on a very large deviation.  The tight threshold
# (1e-4) would require a registry entry that doesn't exist — hence
# numbers_invented=1 is flagged in the production code.
def test_G36_tight_threshold_not_testable():
    """Document that G36's tight threshold cannot be reached without inventing a number."""
    with _patch_params({"ckm.unitarity_test": {"value": 1e-3}}):
        result = gate_G36_ckm_unitarity()
    # With the weak (< 1.0) threshold, 1e-3 still passes:
    assert result.verdict == "PASS", (
        "Confirmed: G36 passes on deviation=1e-3 because the tight "
        "threshold requires an invented number. Gate is WEAK."
    )
