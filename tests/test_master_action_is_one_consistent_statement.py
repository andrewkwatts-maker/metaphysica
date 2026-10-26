"""The master action, as the engine states it, must at least be self-consistent.

Audit: PrincipiaMetaphysica/docs/plan/geometry/master_action_audit.md

These tests pin the notation and labelling fixes of that audit. They do not
rule on any number, and they do not claim the action is complete: that the
definitions still differ in field content is recorded in the audit, not here.

Conventions fixed (bulk (24,2), D = 26):
  * the measure is sqrt|G|: det G > 0 with two times, so sqrt(-G) is imaginary;
  * gravity enters as (M_*^{D-2}/2) R = R/(2 kappa^2), kappa^2 = 8 pi G_26 = M_*^{-24}
    (the exponent is D-2 = 24, not 25 and not 23; there is no G_27 in a 26D bulk);
  * M_Pl^2 for the 13D shadow on a 9D internal space is M_*^{11} Vol_9, so the
    "M_*^9 Vol(V_7)" form is the 11D one and is only an effective scale here;
  * a Yang-Mills term is -1/4 F^2 in either signature convention.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from metaphysica.config.core_formulas import CoreFormulas
from metaphysica.simulations.PM.derivations.lagrangian_master import (
    LagrangianMasterDerivation,
)
from metaphysica.simulations.PM.gauge.master_action import (
    MasterActionSimulationV22,
)

_ROOT = Path(__file__).resolve().parents[1]

_GAUGE_IDS_26D = ["pneuma-master-action-v23"]
_LAG_IDS_26D = [
    "master-action-26d-full", "einstein-hilbert-26d", "yang-mills-26d",
    "dirac-26d", "pneuma-coupling", "master-action-two-layer-or",
    "bulk-action-26d-v23",
]


@pytest.fixture(scope="module")
def gauge():
    return {f.id: f for f in MasterActionSimulationV22().get_formulas()}


@pytest.fixture(scope="module")
def lag():
    return {f.id: f for f in LagrangianMasterDerivation().get_formulas()}


def _all_26d(gauge, lag):
    out = [gauge[i] for i in _GAUGE_IDS_26D] + [lag[i] for i in _LAG_IDS_26D]
    return out + [CoreFormulas.MASTER_ACTION_26D]


def _blob(f) -> str:
    return " ".join(str(x) for x in (
        f.latex, f.plain_text, getattr(f, "html", ""), f.description,
        getattr(f, "terms", ""), getattr(f, "derivation", "")))


def test_26d_measure_is_sqrt_abs_G_not_sqrt_minus_G(gauge, lag):
    bad = [f.id for f in _all_26d(gauge, lag)
           if re.search(r"sqrt\(?\{?-\s*[gG]", f.latex + " " + f.plain_text)]
    assert not bad, f"det G > 0 for (24,2); sqrt(-G) is imaginary: {bad}"


def test_no_wrong_planck_exponent_or_G27_in_26d_formulas(gauge, lag):
    pat = re.compile(r"M_\*\^\{?-?25\}?|G_\{?27\}?")
    bad = [f.id for f in _all_26d(gauge, lag) if pat.search(_blob(f))]
    gauge_el = gauge["euler-lagrange-metric-variation"]
    if pat.search(_blob(gauge_el)):
        bad.append(gauge_el.id)
    assert not bad, f"D-2 = 24 and G_26 is the 26D constant: {bad}"
    assert "M_*^{24}" in CoreFormulas.MASTER_ACTION_26D.latex


def test_gravity_coefficient_is_the_same_everywhere(gauge, lag):
    core = CoreFormulas.MASTER_ACTION_26D
    frac = r"\frac{M_*^{24}}{2}"
    assert frac in core.latex
    assert frac in gauge["pneuma-master-action-v23"].latex
    assert "24</sup>/2" in core.html
    assert "²⁴/2" in core.plain_text
    assert "M_*^{24}}{2}" in lag["master-action-26d-full"].latex
    assert "M_*^24/2" in gauge["pneuma-master-action-v23"].plain_text


def test_yang_mills_and_dilaton_dimension_problems_are_stated(lag):
    assert "4 - D = -22" in lag["yang-mills-26d"].terms["g"]
    assert "OPEN" in lag["pneuma-coupling"].terms["phi"]


def test_bridge_metric_has_two_times(gauge):
    f = gauge["bridge-12-pair-metric-v22"]
    assert "dt_1" in f.latex and "dt_2" in f.latex
    steps = " ".join(f.derivation["steps"])
    assert "26 spatial" not in steps and "plus 1 time" not in steps


def test_master_action_dimension_count_is_24_plus_2(gauge):
    f = gauge["pneuma-master-action-v23"]
    steps = " ".join(f.derivation["steps"])
    assert "24 (bridge) + 2 (sampler) + 1 (time)" not in steps


def test_L_C_and_Weyl_mass_are_flagged_open(gauge):
    terms = gauge["pneuma-master-action-v23"].terms
    assert "OPEN" in terms["L_C"]
    assert "OPEN" in terms["m"] and "Weyl" in terms["m"]
    assert "OPEN" in terms["lambda"]


def test_4d_gauge_kinetic_term_sign(lag):
    f = lag["reduced-lagrangian-4d"]
    assert "+ \\frac{1}{4} F_{\\mu\\nu}^a" not in f.latex
    assert "- \\frac{1}{4} F_{\\mu\\nu}^a" in f.latex


def test_13d_to_4d_planck_mass_is_not_the_11d_formula(gauge, lag):
    for f in (gauge["effective-action-4d-v23"], lag["reduced-lagrangian-4d"]):
        assert "M_*^{9}" not in _blob(f), f.id
        assert "M_{11}" in _blob(f), f.id


def test_7_to_4_step_does_not_reduce_a_7d_spacetime(lag):
    f = lag["kk-ansatz-7-4"]
    assert "ds^2_6" in f.latex and "ds^2_7" not in f.latex


def test_action_definitions_are_not_labelled_derived(gauge, lag):
    postulated = [gauge["pneuma-master-action-v23"],
                  gauge["shadow-action-13d-v23"],
                  gauge["effective-action-4d-v23"]] + [
        lag[i] for i in ("master-action-26d-full", "einstein-hilbert-26d",
                         "yang-mills-26d", "dirac-26d", "pneuma-coupling")]
    bad = [f.id for f in postulated if f.category == "DERIVED"]
    assert not bad, f"an action is written down (ANSATZ), not derived: {bad}"


def test_config_class_states_the_26d_action_with_the_right_power():
    src = (_ROOT / "src/metaphysica/config/parameters/master_action.py"
           ).read_text(encoding="utf-8")
    assert "M²⁵R" not in src and "√G [" not in src
    assert "LEGACY" in src.split("BULK_PLANCK_POWER")[1].split("\n")[0]
