"""Smoke test: every PM module that uses the published `eml-math` /
`eml-spectral` packages must import cleanly.

These imports broke once already when eml-math v1.2.0 split the algebra
layer (Clifford / octonion / E7 / E8 / Freudenthal / metric tensors)
out into the sister `eml-spectral` package. This test catches the same
class of break next time either dep ships a major version.

Run with:
    pytest tests/test_eml_imports.py -v
"""
from __future__ import annotations

import importlib

import pytest


# ── eml-math: stays in the slim core (v1.2.0+) ───────────────────────────────

EML_MATH_MODULES = [
    "eml_math",
    "eml_math.point",
    "eml_math.operators",
    "eml_math.tree",
    "eml_math.evaluator",
    "eml_math.flow",
    "eml_math.flow_layout",
    "eml_math.famous",
    "eml_math.symbols",
    "eml_math.discover",
    "eml_math.web",
    "eml_math.constants",
]

EML_MATH_NAMES = [
    ("eml_math", "EMLPoint"),
    ("eml_math.constants", "PLANCK_D"),
    ("eml_math.constants", "OVERFLOW_THRESHOLD"),
]


# ── eml-spectral: algebras, lattices, spacetime ──────────────────────────────

EML_SPECTRAL_MODULES = [
    "eml_spectral",
    "eml_spectral.pair",
    "eml_spectral.state",
    "eml_spectral.geometric_algebra",
    "eml_spectral.octonion",
    "eml_spectral.metric",
    "eml_spectral.fourvector",
    "eml_spectral.momentum",
    "eml_spectral.ndim",
    "eml_spectral.discrete",
    "eml_spectral.spacetime",
    "eml_spectral.exceptional",
    "eml_spectral.exceptional.freudenthal",
    "eml_spectral.exceptional.e7_56",
    "eml_spectral.exceptional.e8_248",
]

EML_SPECTRAL_NAMES = [
    ("eml_spectral", "EMLPair"),
    ("eml_spectral", "EMLState"),
    ("eml_spectral", "EMLNDVector"),
    ("eml_spectral", "MetricTensor"),
    ("eml_spectral", "Octonion"),
    ("eml_spectral", "EMLMultivector"),
    ("eml_spectral", "FourMomentum"),
    ("eml_spectral", "MinkowskiFourVector"),
    ("eml_spectral", "e8_lattice_points"),
    ("eml_spectral", "leech_lattice_points"),
    ("eml_spectral.exceptional.freudenthal", "FreudenthalTripleSystem"),
    ("eml_spectral.exceptional.e7_56", "E7_56"),
    ("eml_spectral.exceptional.e8_248", "E8_248"),
    ("eml_spectral.exceptional.e8_248", "E8xE8"),
    ("eml_spectral.geometric_algebra", "EMLMultivector"),
    # v1.0.0 additions: spectral flow, G2 seeds, helper batch ops
    ("eml_spectral", "spectral_flow"),
    ("eml_spectral", "racetrack_fixed_point"),
    ("eml_spectral", "topology_invariant"),
    ("eml_spectral", "G2_SEEDS"),
    ("eml_spectral", "_HAS_RUST"),
    ("eml_spectral", "iterate"),
    ("eml_spectral", "find_resonance_bands"),
    ("eml_spectral", "frame_shift_count"),
    ("eml_spectral", "lattice_distance"),
    ("eml_spectral", "is_lattice_neighbor"),
    ("eml_spectral", "basis_octonion"),
]


# ── eml-spectral v1.0.0 Rust accelerator (optional, gated on _HAS_RUST) ──────

EML_SPECTRAL_RUST_FNS = [
    "octonion_mul", "octonion_mul_n", "octonion_norm_n",
    "spectral_flow_step", "spectral_flow_n", "spectral_flow_batch",
    "geometric_product_n",
    "e8_norms_squared_n", "e8_min_norm_squared",
    "leech_min_norm_squared",
    "add_n",
]


# ── PM modules that import from EML — they must all load without error ──────

PM_MODULES_USING_EML = [
    "metaphysica.simulations.core.eml_integration",
    "metaphysica.simulations.core.eml_cross_check",
    "metaphysica.simulations.PM.algebra.freudenthal_triple",
    "metaphysica.simulations.PM.algebra.e7_representation",
    "metaphysica.simulations.PM.algebra.e8x8_splitting",
    "metaphysica.simulations.PM.algebra.clifford_unification",
    "metaphysica.simulations.PM.algebra.gaugino_condensation",
    "metaphysica.simulations.base.simulation_base",
]


# ── Tests ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("module", EML_MATH_MODULES)
def test_eml_math_module_imports(module: str) -> None:
    """Every documented eml-math sub-module must import."""
    importlib.import_module(module)


@pytest.mark.parametrize("module,name", EML_MATH_NAMES)
def test_eml_math_name_resolves(module: str, name: str) -> None:
    """Every name PM relies on from eml-math must exist."""
    mod = importlib.import_module(module)
    assert hasattr(mod, name), f"{module}.{name} missing — eml-math API drifted"


@pytest.mark.parametrize("module", EML_SPECTRAL_MODULES)
def test_eml_spectral_module_imports(module: str) -> None:
    """Every eml-spectral sub-module PM uses must import."""
    importlib.import_module(module)


@pytest.mark.parametrize("module,name", EML_SPECTRAL_NAMES)
def test_eml_spectral_name_resolves(module: str, name: str) -> None:
    """Every name PM imports from eml-spectral must exist."""
    mod = importlib.import_module(module)
    assert hasattr(mod, name), f"{module}.{name} missing — eml-spectral API drifted"


@pytest.mark.parametrize("module", PM_MODULES_USING_EML)
def test_pm_module_loads(module: str) -> None:
    """Every PM module that touches eml-math / eml-spectral must import
    without error against the currently-installed package versions."""
    importlib.import_module(module)


@pytest.mark.parametrize("fn_name", EML_SPECTRAL_RUST_FNS)
def test_eml_spectral_rust_accelerator(fn_name: str) -> None:
    """When _HAS_RUST is True the eml_spectral_core extension must
    expose every named Rust batch op. Skipped on builds without Rust."""
    import eml_spectral
    if not getattr(eml_spectral, "_HAS_RUST", False):
        pytest.skip("Rust accelerator not built for this install")
    core = importlib.import_module("eml_spectral.eml_spectral_core")
    assert hasattr(core, fn_name), (
        f"eml_spectral.eml_spectral_core.{fn_name} missing — rust API drifted"
    )
