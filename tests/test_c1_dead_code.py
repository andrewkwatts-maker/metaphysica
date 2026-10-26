"""Track C1: dead modules stay removed; the kept off-path and study modules import.

The removed modules were named nowhere in the build, tests or generators. The
kept ones are labelled off-path figures (runnable under the DISABLED b3_seed
option) or a pre-registered study.
"""
from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SIM = "src/metaphysica/simulations/"
REMOVED = [
    "src/metaphysica/generators/generate_b3_24_census.py",
    SIM + "Constants/hebrew_naming.py",
    SIM + "PM/algebra/_triple_helpers.py",
    SIM + "support/physics/shell_saturation.py",
    SIM + "validation/audit/final_gates.py",
    SIM + "validation/audit/formula_validator.py",
    SIM + "validation/audit/terminal_certificates.py",
    SIM + "validation/parameter_sensitivity_test.py",
    SIM + "validation/recursive_symmetry_gatekeeper.py",
    SIM + "validation/validate_experimental_compliance.py",
    SIM + "validation/validation_modules.py",
    SIM + "data/experimental/csv_loader.py",
    "src/metaphysica/website/output_manifest.py",
] + [SIM + "visualizations/%s.py" % n for n in (
    "algebra_diagrams", "brane_gauge_diagrams", "compactification_diagrams",
    "cosmology_diagrams", "descent_chain", "dimension_intro_diagrams",
    "entropy_basin_terminal_map", "falsifiability_dashboard",
    "gauge_theory_diagrams", "gnosis_progression", "microtubule_12pair",
    "octonionic_triality", "particle_diagrams")]
KEPT = [
    "metaphysica.simulations.PM.geometry.flux_homogeneity",
    "metaphysica.simulations.visualizations.goldilocks_plot",
    "metaphysica.simulations.visualizations.stability_heatmap",
    "metaphysica.simulations.visualizations.theory_overview_diagrams",
    "metaphysica.simulations.visualizations.ricci_flow_evolution",
]


@pytest.mark.parametrize("rel", REMOVED)
def test_removed_module_is_gone(rel):
    assert not (ROOT / rel).exists()


@pytest.mark.parametrize("dotted", KEPT)
def test_kept_module_imports(dotted):
    importlib.import_module(dotted)


def test_no_tracked_source_names_a_removed_module():
    names = [Path(r).stem for r in REMOVED]
    out = subprocess.run(["git", "grep", "-lwE", "|".join(names), "--",
                          "src", "tests", "scripts", ":!tests/test_c1_dead_code.py"],
                         cwd=ROOT, capture_output=True, text=True).stdout
    assert out.strip() == "", out
