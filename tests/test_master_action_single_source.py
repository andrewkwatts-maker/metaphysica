"""One master action: every published action formula is generated from the ladder.

Brief L2c. The published latex is read from the simulations' formula definitions, not from
a build. Covers: whole-action formulas equal `action_latex` of their ladder step, term
formulas are anchored to a ladder term, retired ids are not referenced, and every row of
the L2a map is accounted for.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import replace
from pathlib import Path

import pytest

from metaphysica.actions.latex import action_latex, measure_latex
from metaphysica.actions.model import ModelError
from metaphysica.generators import formula_lint as fl
from metaphysica.simulations.PM.derivations.cosmology_sector_complete import (
    CosmologySectorCompleteDerivations,
)
from metaphysica.simulations.PM.cosmology.f_r_t_tau_gravity import FRTTauGravityV18
from metaphysica.simulations.PM.derivations.gauge_sector_complete import (
    GaugeSectorCompleteDerivations,
)
from metaphysica.simulations.PM.derivations.lagrangian_master import (
    LagrangianMasterDerivation,
)
from metaphysica.simulations.PM.field_dynamics.pneuma_mechanism import PneumaMechanismV16
from metaphysica.simulations.PM.gauge import master_ladder as ML
from metaphysica.simulations.PM.gauge import master_ladder_render as R
from metaphysica.simulations.PM.gauge.master_action import MasterActionSimulationV22
from metaphysica.simulations.PM.gauge.master_ladder_map import KINDS, MAP

_ROOT = Path(__file__).resolve().parents[1]
SURVIVOR = {"master-action-two-layer-or": "master-action-26d-full",
            "bulk-action-26d-v23": "master-action-26d-full",
            "v22-bridge-lagrangian": "bridge-lagrangian-v22",
            "su3-qcd-lagrangian-g2-v19": "su3-qcd-lagrangian-v22",
            "su2-weak-lagrangian-g2-v19": "su2-weak-lagrangian-v22"}
RETIRED = tuple(SURVIVOR)
NOT_DERIVED = ("de-frt-lagrangian-v19", "f-r-t-tau-lagrangian-v18", "pneuma-lagrangian")


@pytest.fixture(scope="module")
def formulas():
    out = {}
    for cls in (MasterActionSimulationV22, LagrangianMasterDerivation,
                GaugeSectorCompleteDerivations, CosmologySectorCompleteDerivations,
                FRTTauGravityV18, PneumaMechanismV16):
        for f in cls().get_formulas():
            out[f.id] = f
    return out


@pytest.fixture(scope="module")
def ladder():
    return ML.build_ladder(ML.resolve_options())


def _action(ladder, step_id):
    return next(s.action for s in ladder.steps if s.id == step_id)


@pytest.mark.parametrize("fid", sorted(R.WHOLE_ACTION))
def test_whole_action_latex_equals_action_latex_of_its_step(formulas, ladder, fid):
    assert formulas[fid].latex == action_latex(_action(ladder, R.WHOLE_ACTION[fid]))


@pytest.mark.parametrize("fid", sorted(R.WHOLE_ACTION))
def test_rendered_actions_pass_measure_and_planck_lint(formulas, fid):
    assert fl.check_measure(fid, formulas[fid].latex) == []
    assert fl.check_planck_exponent(fid, formulas[fid].latex) == []


@pytest.mark.parametrize("fid", sorted(R.TERM_FORMULAS))
def test_term_formula_is_anchored_to_an_existing_ladder_term(formulas, ladder, fid):
    key, text = R.TERM_FORMULAS[fid]
    aid, tid = key.split(":")
    action = next(s.action for s in ladder.steps if s.action.id == aid)
    assert any(t.id == tid for t in action.terms)
    assert formulas[fid].latex == text


@pytest.mark.parametrize("fid", sorted(R.EOM_STEPS))
def test_eom_formulas_name_the_ladder_step_they_vary(formulas, ladder, fid):
    assert formulas[fid].derivation["ladderStep"] == R.EOM_STEPS[fid]
    assert R.EOM_STEPS[fid] in [s.id for s in ladder.steps]


def test_measure_follows_the_signature(ladder):
    assert measure_latex(_action(ladder, "26D")) == r"\sqrt{|g|}"
    assert measure_latex(_action(ladder, "13D")) == r"\sqrt{-g}"


def test_a_non_open_term_without_latex_fails_early(ladder):
    a = _action(ladder, "4D")
    bad = replace(a, terms=(replace(a.terms[0], latex=None),) + a.terms[1:])
    with pytest.raises(ModelError, match="no latex"):
        action_latex(bad)


def test_open_term_without_latex_is_shown_by_symbol(ladder):
    a = _action(ladder, "4D")
    t = next(t for t in a.terms if t.open)
    shown = action_latex(replace(a, terms=(a.terms[0], replace(t, latex=None))))
    assert r"\mathrm{c\_" in shown


def test_rendered_actions_pass_the_texcheck_render_gate(formulas, tmp_path):
    node, texcheck = shutil.which("node"), _ROOT / "tools" / "texcheck"
    if node is None or not (texcheck / "node_modules" / "mathjax-full").is_dir():
        pytest.skip("texcheck not installed")
    page = tmp_path / "actions.html"
    page.write_text("\n".join("<p>$$%s$$</p>" % formulas[f].latex
                              for f in sorted(R.WHOLE_ACTION)), encoding="utf-8")
    proc = subprocess.run([node, str(texcheck / "check.js"), str(page)],
                          capture_output=True, text=True, encoding="utf-8", cwd=str(texcheck))
    report = json.loads(proc.stdout)
    assert proc.returncode == 0 and not report["errors"], report["errors"]
    assert report["checked"] >= len(R.WHOLE_ACTION)


@pytest.mark.parametrize("fid", RETIRED)
def test_retired_formulas_are_marked_and_name_the_survivor(formulas, fid):
    assert formulas[fid].description.startswith("RETIRED")
    assert SURVIVOR[fid] in formulas[fid].description
    assert SURVIVOR[fid] in formulas


@pytest.mark.parametrize("fid", NOT_DERIVED)
def test_not_derived_formulas_are_marked_not_retired(formulas, fid):
    assert formulas[fid].description.startswith("Not derived from the master action.")


def _surfaces():
    sims = (_ROOT / "src/metaphysica/simulations").rglob("*.py")
    tests = (p for p in (_ROOT / "tests").glob("*.py") if p.name != Path(__file__).name)
    return [p for p in list(sims) + list(tests) if p.name != "master_ladder_map.py"]


def test_no_retired_id_is_referenced_from_a_published_surface():
    """Only a retired formula's own definition and its sim's provided-ids list name it."""
    bad = []
    for path in _surfaces():
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for rid in RETIRED:
                if '"%s"' % rid not in line:
                    continue
                is_def = re.search(r'(?<![\w])id="%s"' % re.escape(rid), line)
                provided = re.fullmatch(r'\s*"%s",\s*(#.*)?' % re.escape(rid), line)
                if not (is_def or provided):
                    bad.append("%s:%d %s" % (path.name, n, rid))
    assert not bad, bad


def test_map_rows_are_all_accounted_for():
    counts = Counter(v[0] for v in MAP.values())
    assert set(counts) <= set(KINDS)
    assert (counts["step"], counts["reduction"], counts["retire"], counts["out"]) == (17, 4, 6, 4)
    assert len(MAP) == 31


def test_every_step_row_has_a_rendering_decision():
    rendered = set(R.WHOLE_ACTION) | set(R.TERM_FORMULAS) | set(R.EOM_STEPS)
    steps = {k for k, v in MAP.items() if v[0] == "step"}
    # e8x8-visible-action is not an action formula; the engine cannot render it (reported)
    left = steps - rendered - set(RETIRED) - {"e8x8-visible-action"}
    assert not left, "step rows with no rendering decision: %s" % sorted(left)


def test_retire_rows_are_retired_or_marked_for_the_owner():
    for k, v in MAP.items():
        if v[0] == "retire" and k != "sp2r-gauge-fixed-action":  # retired 2026-08-31
            assert k in RETIRED or k in NOT_DERIVED, k
