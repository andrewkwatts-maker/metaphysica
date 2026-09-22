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


def _seed_b3() -> int:
    """b_3 of the live seed. Tests that hardcoded 24 were pinning the
    off-path branch by accident once the adoption landed."""
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    return seed_values(resolve_path())[0]


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

    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    seed_b3 = seed_values(resolve_path())[0]
    assert seed_b3 == 43, "the adopted b3_seed branch moved; re-measure"

    selector = DynamicalVacuumSelector()
    result = selector.select_vacuum()

    tree = selector.eml_tree
    # Tree must carry a b3_leaf handle from the build path.
    assert "b3_leaf" in tree, "EML tree missing b3 leaf reference"
    # The tree's b3 leaf reports the LIVE seed via tension(). Measured
    # 2026-09-22, b3_seed adoption: 43.0, where it read 24.0 before the
    # ruling.
    b3_tension = float(tree["b3_leaf"].tension())
    assert math.isclose(b3_tension, float(seed_b3), rel_tol=1e-9), (
        f"b3 leaf tension {b3_tension} != {seed_b3} (G2 third Betti number "
        f"of the adopted seed)"
    )

    # HEALED 2026-09-23. The two sides used to sit on different b_3 values:
    # the tree followed the seed through b3_leaf() while the float pipeline
    # took its b_3 from the class's own seed-blind ``DEFAULT_B3 = 24``, the
    # fifth seed-blind writer (it published cosmology.b3 = 24 beside
    # particle.b3 = 43, which the ambiguous-alias guard caught). The frozen
    # default is gone -- resolution happens at call time from the live seed
    # -- so both sides now sit on the SAME b_3 and this is an agreement
    # check rather than a recorded divergence.
    assert result["eml_value"] is not None, "EML value not computed"
    assert result["b3"] == _seed_b3(), (
        "select_vacuum no longer follows the live seed; a frozen default "
        "has come back"
    )
    # RETIRED 2026-09-23, exactly as the old assertion instructed: "the
    # seed-blind default has healed; re-measure this pin and retire the
    # divergence rather than leaving a check that cannot fire." It healed,
    # so the divergence pin is gone and AGREEMENT is required instead.
    # Measured on the adopted seed: both sides 1.6753435421813e+37. The old
    # float side, 2.0470466728037693e+24, was the b_3 = 24 value the frozen
    # DEFAULT_B3 produced; it survives on the off-path branch below.
    assert math.isclose(
        result["eml_value"], result["dynamically_selected"], rel_tol=1e-6
    ), (
        "the EML tree and the float pipeline disagree again (%r vs %r) -- "
        "a seed-blind default has come back somewhere in this module"
        % (result["eml_value"], result["dynamically_selected"])
    )

    seeded = DynamicalVacuumSelector().select_vacuum(b3=seed_b3)
    assert math.isclose(
        seeded["eml_value"],
        seeded["dynamically_selected"],
        rel_tol=1e-6,
    ), (
        f"EML tree ({seeded['eml_value']:.6e}) disagrees with float "
        f"pipeline ({seeded['dynamically_selected']:.6e}) at b_3 = "
        f"{seed_b3}, so the tree is not the pipeline's expression"
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

def test_the_class_carries_no_frozen_b3():
    """The seed-blind DEFAULT_B3 is gone and must not return.

    It was a default ARGUMENT, which is exactly where a frozen value hides:
    callers that pass nothing get the literal, and the row it publishes
    (cosmology.b3) disagrees with every other b_3 in the artifact.
    """
    assert not hasattr(DynamicalVacuumSelector, "DEFAULT_B3"), (
        "DEFAULT_B3 is back on the class; resolution belongs at call time"
    )
    assert DynamicalVacuumSelector.DEFAULT_FLUX_MODES == 12
    assert DynamicalVacuumSelector().select_vacuum()["b3"] == _seed_b3()


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
    """log_vacua_raw = b3 * ln(flux_modes) + 8 * ln(10), on the LIVE seed."""
    result = prune_landscape()
    expected = _seed_b3() * math.log(12) + 8 * math.log(10)
    assert math.isclose(
        result["log_vacua_raw"], expected, rel_tol=1e-12
    ), f"log_vacua_raw {result['log_vacua_raw']} != formula {expected}"


def test_pruning_factor_matches_formula():
    """pruning_factor = exp(-0.92 * b3), on the LIVE seed."""
    result = prune_landscape()
    expected = math.exp(-0.92 * _seed_b3())
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
