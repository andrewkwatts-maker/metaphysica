"""Regression tests for ``simulations.PM.cosmology.vacuum_selection``.

Validates the v25.0 dynamical vacuum selection module:
  1. dynamically_selected < raw_vacua (the suppression actually ran)
  2. b3 appears as a leaf in the EML operator tree (b3-traceability)
  3. raw_vacua > 10^30 (the landscape is genuinely huge pre-selection)

The third test also indirectly validates the
log_vacua_raw = b3*ln(flux_modes) + 8*ln(10) formula: with b3=24
and flux_modes=12, log_vacua_raw ~ 78 (natural log) ~ 33.8 (base 10),
so raw_vacua ~ 10^33.8 > 10^30.
"""
from __future__ import annotations

import math

import pytest

from metaphysica.simulations.PM.cosmology.vacuum_selection import (
    ANTHROPIC_REJECTED_STR,
    ATTRACTOR_DECAY_RATE,
    DynamicalVacuumSelector,
    LANDSCAPE_LOG_SCALE,
    prune_landscape,
)


# ── Test 1: suppression worked ──────────────────────────────────────────────

def test_dynamically_selected_less_than_raw():
    """The pruning factor must strictly reduce the vacuum count."""
    result = prune_landscape()
    assert result["dynamically_selected"] < result["raw_vacua"], (
        f"Dynamic selection failed: selected={result['dynamically_selected']:.3e} "
        f">= raw={result['raw_vacua']:.3e}"
    )
    # Check the ratio matches the pruning factor.
    ratio = result["dynamically_selected"] / result["raw_vacua"]
    assert math.isclose(ratio, result["pruning_factor"], rel_tol=1e-9), (
        f"Suppression ratio {ratio:.6e} != pruning_factor "
        f"{result['pruning_factor']:.6e}"
    )


# ── Test 2: b3 leaf in EML tree ─────────────────────────────────────────────

def test_b3_leaf_in_eml_tree():
    """The EML operator tree must contain a b3 leaf rooted at FormulasRegistry."""
    try:
        from metaphysica.simulations.core.eml_integration import EML_AVAILABLE
    except ImportError:  # pragma: no cover
        EML_AVAILABLE = False

    if not EML_AVAILABLE:
        pytest.skip("eml-math + eml-spectral not installed in this env")

    selector = DynamicalVacuumSelector()
    result = selector.select_vacuum()

    tree = selector.eml_tree
    # Tree must carry a b3_leaf handle from the build path.
    assert "b3_leaf" in tree, "EML tree missing b3 leaf reference"
    # Tree's b3 leaf must report value 24 via tension().
    b3_tension = float(tree["b3_leaf"].tension())
    assert math.isclose(b3_tension, 24.0, rel_tol=1e-9), (
        f"b3 leaf tension {b3_tension} != 24 (G2 third Betti number)"
    )
    # Tree root EML evaluation must agree with the float pipeline.
    assert result["eml_value"] is not None, "EML value not computed"
    assert math.isclose(
        result["eml_value"],
        result["dynamically_selected"],
        rel_tol=1e-6,
    ), (
        f"EML tree ({result['eml_value']:.6e}) disagrees with float "
        f"pipeline ({result['dynamically_selected']:.6e})"
    )


# ── Test 3: huge landscape ──────────────────────────────────────────────────

def test_raw_vacua_exceeds_ten_to_the_thirty():
    """Pre-selection landscape must be cosmologically huge (>10^30)."""
    result = prune_landscape()
    assert result["raw_vacua"] > 1e30, (
        f"Raw landscape too small: {result['raw_vacua']:.3e} <= 10^30. "
        "Either b3 or flux_modes inputs were corrupted."
    )


# ── Bonus sanity checks ─────────────────────────────────────────────────────

def test_default_inputs_match_topology():
    """Default b3=24 and flux_modes=12 (= b3/2 paired bridges)."""
    assert DynamicalVacuumSelector.DEFAULT_B3 == 24
    assert DynamicalVacuumSelector.DEFAULT_FLUX_MODES == 12


def test_attractor_constants_match_spec():
    """ATTRACTOR_DECAY_RATE = 0.92, LANDSCAPE_LOG_SCALE = 8 per
    PossibleImprovements.txt section 3."""
    assert ATTRACTOR_DECAY_RATE == 0.92
    assert LANDSCAPE_LOG_SCALE == 8


def test_anthropic_rejected_string_present():
    """The output dict must report the human-readable rejection fraction."""
    result = prune_landscape()
    assert result["anthropic_rejected"] == ANTHROPIC_REJECTED_STR
    assert "%" in result["anthropic_rejected"]


def test_log_vacua_raw_matches_formula():
    """log_vacua_raw = b3 * ln(flux_modes) + 8 * ln(10)."""
    result = prune_landscape()
    expected = 24 * math.log(12) + 8 * math.log(10)
    assert math.isclose(
        result["log_vacua_raw"], expected, rel_tol=1e-12
    ), f"log_vacua_raw {result['log_vacua_raw']} != formula {expected}"


def test_pruning_factor_matches_formula():
    """pruning_factor = exp(-0.92 * b3) with b3=24."""
    result = prune_landscape()
    expected = math.exp(-0.92 * 24)
    assert math.isclose(
        result["pruning_factor"], expected, rel_tol=1e-12
    )


def test_classification_string():
    """Output must declare DYNAMICALLY_SELECTED classification."""
    result = prune_landscape()
    assert result["classification"] == "DYNAMICALLY_SELECTED"


def test_overriding_b3_and_flux():
    """select_vacuum honors explicit b3 and flux_modes overrides."""
    selector = DynamicalVacuumSelector()
    result = selector.select_vacuum(b3=24, flux_modes=24)
    # With flux_modes=24, log_vacua_raw = 24*ln(24) + 8*ln(10)
    expected_log = 24 * math.log(24) + 8 * math.log(10)
    assert math.isclose(result["log_vacua_raw"], expected_log, rel_tol=1e-12)
    assert result["flux_modes"] == 24
