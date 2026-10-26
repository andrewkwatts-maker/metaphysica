"""D-027 ruling 3: dimensionful rows with no honest scale input do not score.

UNIT_CHECK (c, exact in SI) and CIRCULAR (scale input is the measured
quantity) rows keep their values but leave the PASS/FAIL tally and chi^2.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from metaphysica.generators import generate_validation_certificates as gvc
from metaphysica.simulations.PM.validation.statistical_rigor_validator import (
    NON_SCORING_VERDICTS, SCORING_VERDICTS)

SRC = Path(gvc.__file__).resolve().parents[1] / "simulations" / "PM"


def _rec(value, exp, unc, sigma, status="", meta=None):
    return {"value": value, "experimental_value": exp,
            "experimental_uncertainty": unc, "sigma_deviation": sigma,
            "validation_status": status, "bound_type": "central_value",
            "status": "PREDICTED", "metadata": meta or {}}


@pytest.fixture
def report(tmp_path, monkeypatch):
    params = {
        "t.c": _rec(299792423.0, 299792458.0, 1.0, 35.0, "FAIL",
                    {"scoring_exclusion": "UNIT_CHECK",
                     "scoring_exclusion_reason": "c exact in SI"}),
        "t.circ": _rec(70.0, 73.0, 1.0, 3.0, "TENSION",
                       {"scoring_exclusion": "CIRCULAR",
                        "scoring_exclusion_reason": "scale is measured H0"}),
        "t.ratio": _rec(0.31, 0.30, 0.01, 1.0, "PASS"),
        "t.bad": _rec(1.0, 2.0, 0.1, 10.0, "FAIL"),
    }
    (tmp_path / "parameters.json").write_text(
        json.dumps({"parameters": params}), encoding="utf-8")
    monkeypatch.setattr(gvc, "autogen_dir", lambda: tmp_path)
    monkeypatch.setattr(gvc, "_resolve_theory_policy", lambda: "always")
    rows = gvc.build_report()
    return rows, {v["path"]: v for v in rows["validations"]}


def test_c_is_unit_check_and_excluded(report):
    _, by = report
    assert by["t.c"]["verdict"] == "UNIT_CHECK"
    assert by["t.c"]["value"] == 299792423.0
    assert "UNIT_CHECK" in NON_SCORING_VERDICTS


def test_circular_row_excluded_with_reason(report):
    _, by = report
    assert by["t.circ"]["verdict"] == "CIRCULAR"
    assert by["t.circ"]["scoring_exclusion_reason"] == "scale is measured H0"
    assert "CIRCULAR" in NON_SCORING_VERDICTS


def test_dimensionless_row_still_scored(report):
    _, by = report
    assert by["t.ratio"]["verdict"] == "PASS"
    assert by["t.bad"]["verdict"] == "FAIL"
    assert {"PASS", "FAIL"} <= SCORING_VERDICTS


def test_totals_equal_sum_over_scored_rows(report):
    rep, by = report
    s = rep["summary"]
    scored = [v for v in by.values() if v["verdict"] in SCORING_VERDICTS]
    assert sum(s.get(k, 0) for k in ("pass", "marginal", "tension", "fail")) \
        == len(scored) == 2
    assert s["unit_check"] == 1 and s["circular"] == 1
    assert s["total"] == 4


def test_exclusion_without_reason_fails_early():
    with pytest.raises(ValueError):
        gvc._declared_exclusion({"scoring_exclusion": "CIRCULAR"})
    with pytest.raises(ValueError):
        gvc._declared_exclusion({"scoring_exclusion": "BOGUS",
                                 "scoring_exclusion_reason": "x"})


@pytest.mark.parametrize("rel,path,kind", [
    ("cosmology/speed_of_light.py", "cosmology.speed_of_light_derived", "UNIT_CHECK"),
    ("paper/appendices/appendix_z_terminal_ledger.py", "cosmology.H0_physical", "CIRCULAR"),
    ("cosmology/cosmological_constant.py", "cosmology.Lambda_derived", "CIRCULAR"),
    ("cosmology/cosmological_constant.py", "cosmology.rho_vacuum", "CIRCULAR"),
    ("particle/higgs_brane_partition.py", "higgs.m_higgs_local", "CIRCULAR"),
    ("particle/higgs_mass.py", "higgs.m_higgs_pred", "CIRCULAR"),
    # 2026-10-26: the Planck-scale rows are the CODATA M_Pl itself, so they
    # had scored PASS against their own input.
    ("cosmology/cosmology_intro.py", "cosmology.M_Pl_4D", "CIRCULAR"),
    ("geometry/geometric_anchors.py", "geometry.m_planck_4d", "CIRCULAR"),
    ("derivations/gr_spacetime.py", "gravity.newton_constant_theory", "CIRCULAR"),
])
def test_declared_rows_carry_the_marking(rel, path, kind):
    text = (SRC / rel).read_text(encoding="utf-8")
    block = text.split(f'path="{path}"', 1)[1].split("Parameter(", 1)[0]
    assert re.search(rf'scoring_exclusion="{kind}"', block)


def test_patch_scoring_exclusion_on_registered_param():
    from metaphysica.simulations.base.registry import PMRegistry
    reg = PMRegistry()
    reg.set_param("t.h0", 40.0, "test", status="DERIVED")
    reg.patch_scoring_exclusion("t.h0", "CIRCULAR", "scale is measured H0")
    meta = reg._parameters["t.h0"].metadata
    assert meta["scoring_exclusion"] == "CIRCULAR"
    with pytest.raises(ValueError):
        reg.patch_scoring_exclusion("t.h0", "CIRCULAR", "")


def test_geometric_anchors_applies_its_declared_exclusions():
    """It registers through set_param, not inject_outputs, so the marking on
    geometry.m_planck_4d never reached the registry and it still scored PASS."""
    from metaphysica.simulations.base.registry import PMRegistry
    from metaphysica.simulations.PM.geometry.geometric_anchors import (
        GeometricAnchorsSimulation)
    reg = PMRegistry()
    GeometricAnchorsSimulation().execute(reg, verbose=False)
    meta = reg._parameters["geometry.m_planck_4d"].metadata
    assert meta["scoring_exclusion"] == "CIRCULAR"
    assert "sqrt(8 pi)" in meta["scoring_exclusion_reason"]


def test_anchor_rows_do_not_claim_a_topological_derivation():
    """Anchors are computed at ANCHOR_FIT = 24, not derived from the live b3."""
    from metaphysica.simulations.base.registry import PMRegistry
    from metaphysica.simulations.PM.geometry.geometric_anchors import (
        GeometricAnchorsSimulation)
    reg = PMRegistry()
    GeometricAnchorsSimulation().execute(reg, verbose=False)
    derivation = reg._parameters["geometry.w_zero"].metadata["derivation"]
    assert "ANCHOR_FIT = 24" in derivation and "provenance OPEN" in derivation
