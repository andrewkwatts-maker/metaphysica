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
    gate_G32_wz_gut_ratio,
    gate_G40_sterile_active_mixing,
    SEMANTIC_EVALUATORS,
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
    barbelo_modulus = 163
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


# G40 baseline: exact rational 163/288 from the registry, no tolerance
def test_G40_passes_with_real_registry():
    result = gate_G40_sterile_active_mixing()
    assert result.verdict == "PASS"
    assert result.measured == 163.0 / 288.0
    assert result.numbers_invented == 0


# G40 mutation: barbelo_modulus != 163
def test_G40_mutation_barbelo_fails():
    with _patch_registry("barbelo_modulus", 162):
        result = gate_G40_sterile_active_mixing()
    assert result.verdict == "FAIL", (
        "G40 must FAIL when barbelo_modulus=162; got PASS (fake gate!)"
    )


# G40 mutation: roots_total != 288
def test_G40_mutation_roots_fails():
    with _patch_registry("roots_total", 289):
        result = gate_G40_sterile_active_mixing()
    assert result.verdict == "FAIL"


# ---------------------------------------------------------------------------
# The wiring: evaluate_gate must consult the semantic tier FIRST, and the
# map must cover exactly the 7 promoted gates -- no more, no fewer.
# ---------------------------------------------------------------------------

def test_semantic_evaluator_map_covers_exactly_the_eight():
    """The 7 Strategy-A gates plus G32 (R6 ruling: 3/8 exact at GUT)."""
    assert set(SEMANTIC_EVALUATORS) == {1, 13, 17, 22, 23, 29, 32, 40}


def test_run_all_reports_all_eight():
    assert sorted(r.gate_id for r in run_all()) == [1, 13, 17, 22, 23, 29, 32, 40]


# G32 baseline: exactly 3/8 at the GUT boundary, from the registry
def test_G32_passes_with_real_registry():
    result = gate_G32_wz_gut_ratio()
    assert result.verdict == "PASS"
    assert result.measured == 3.0 / 8.0
    assert result.numbers_invented == 0


# G32 mutation: a drifted GUT value must FAIL (no tolerance to hide in)
def test_G32_mutation_fails(tmp_path, monkeypatch):
    import json
    params = {"parameters": {"gauge.sin2_theta_W_gut": {"value": 0.3751}}}
    (tmp_path / "parameters.json").write_text(json.dumps(params))
    from metaphysica.generators import _common as gc
    monkeypatch.setattr(gc, "autogen_dir", lambda: tmp_path)
    result = gate_G32_wz_gut_ratio()
    assert result.verdict == "FAIL", (
        "G32 must FAIL when sin2_theta_W_gut=0.3751; got PASS (fake gate!)"
    )


# R6: G12 must read COMPUTED_FAIL honestly -- no invented theory buffer
def test_G12_fails_honestly_via_registry_spec():
    import json
    from pathlib import Path
    from metaphysica.generators.generate_72_certificates import evaluate_gate
    candidates = [
        Path(__file__).resolve().parents[1] / "AutoGenerated" / "parameters.json",
        Path("H:/Github/PrincipiaMetaphysica/AutoGenerated/parameters.json"),
    ]
    params = None
    for c in candidates:
        if c.is_file():
            params = json.loads(c.read_text(encoding="utf-8"))["parameters"]
            break
    if params is None:
        pytest.skip("parameters.json not available")
    e = evaluate_gate(12, {}, params)
    assert e["tier"] == "registry"
    assert e["status"] == "COMPUTED_FAIL", (
        "G12 is ~17 sigma from PDG with no cited theory uncertainty; a PASS "
        "here means someone invented a tolerance -- the R6 ruling forbids that"
    )
    assert e["checks"][0]["sigma"] > 10


# R7: G36 checks the PDG first-row measurement, two-sided, once the
# rebuild persists ckm.unitarity_row1
def test_G36_uses_pdg_first_row_when_available():
    import json
    from pathlib import Path
    from metaphysica.generators.generate_72_certificates import evaluate_gate
    candidates = [
        Path(__file__).resolve().parents[1] / "AutoGenerated" / "parameters.json",
        Path("H:/Github/PrincipiaMetaphysica/AutoGenerated/parameters.json"),
    ]
    params = None
    for c in candidates:
        if c.is_file():
            params = json.loads(c.read_text(encoding="utf-8"))["parameters"]
            break
    if params is None or "ckm.unitarity_row1" not in params:
        pytest.skip("ckm.unitarity_row1 not yet persisted; rebuild required")
    e = evaluate_gate(36, {}, params)
    assert e["tier"] == "registry"
    assert "0.9985" in e["source"] or "first-row" in e["source"]
    # The framework's near-unitary row (~0.99994) vs PDG 0.9985 +/- 0.0007
    # is ~2.1 sigma -- inside 3 sigma but live, and it can fail both ways.
    assert 1.0 < e["checks"][0]["sigma"] < 3.0


def test_evaluate_gate_uses_semantic_tier_for_promoted_gates():
    """The generator must report tier='semantic' and COMPUTED_PASS for every
    promoted gate -- if the wiring regresses, they silently fall back to the
    weaker registry/arithmetic tiers or all the way to DECLARATIVE."""
    from metaphysica.generators.generate_72_certificates import evaluate_gate
    for gid in sorted(SEMANTIC_EVALUATORS):
        e = evaluate_gate(gid, {}, {})
        assert e["tier"] == "semantic", (gid, e)
        assert e["status"] == "COMPUTED_PASS", (gid, e)
        assert e["numbers_invented"] == 0, (gid, e)


def test_evaluate_gate_semantic_tier_reports_failure_honestly():
    """Mutation at the wiring level: a broken registry value must surface as
    COMPUTED_FAIL in the certificate evaluation, not be masked by fallback
    to a lower tier."""
    from metaphysica.generators.generate_72_certificates import evaluate_gate
    with _patch_registry("roots_total", 287):
        e = evaluate_gate(1, {}, {})
    assert e["tier"] == "semantic"
    assert e["status"] == "COMPUTED_FAIL"


def test_evaluate_gate_non_semantic_gates_fall_through():
    """A gate outside the map must NOT be claimed by the semantic tier."""
    from metaphysica.generators.generate_72_certificates import evaluate_gate
    e = evaluate_gate(30, {}, {})
    assert e["tier"] != "semantic"
