"""The 2026-11-01 master-action selection (docs/plan/MASTER_ACTION_SELECTION_2026-11-01.md)."""

from __future__ import annotations

import pytest

from metaphysica.simulations.core import switch_search as ss
from metaphysica.simulations.PM.gauge import master_ladder as ml


@pytest.fixture(scope="module")
def report():
    return ml.report()


def test_adopted_action_has_nine_open_terms_and_the_three_known_failures(report):
    assert report["counts"]["open_terms"] == 9
    assert sorted(report["failing_checks"]) == [
        "nonabelian_gauge_source", "owner_item_6", "zero_modes:scalar"]


def test_the_adopted_sector_choice_is_none_and_weyl_24_mostly_plus():
    from metaphysica.simulations.core.variants.catalogue.action import FORKS

    adopted = {f: [o.id for o in fk.options if o.adopted] for f, fk in FORKS.items()}
    assert adopted["action_bulk_sectors"] == ["none"]
    assert adopted["action_bulk_spinor"] == ["weyl"]
    assert adopted["action_planck_exponent"] == ["exponent_24"]
    assert adopted["action_sign_convention"] == ["mostly_plus_mtw"]


def test_the_selected_path_is_internally_consistent():
    result = ss.evaluate_combination({})
    assert result["internally_consistent"], result["problem_kinds"]
    assert result["digest"] == "4f53cda18c2baa0c"


def test_the_neutrino_sum_is_stated_once():
    from metaphysica.simulations.PM.particle.neutrino_sector import (
        SUM_CLAIM_ROW, SUM_INTERMEDIATE_ROWS, sum_claim_in_window)
    from metaphysica.simulations.core.arithma_formula import registry_value, reset_cache

    assert ss.neutrino_sum_claim_rows() == (SUM_CLAIM_ROW,)
    assert set(SUM_INTERMEDIATE_ROWS) | {SUM_CLAIM_ROW} == set(ss.NEUTRINO_MASS_SUM_ROWS)
    reset_cache()
    assert sum_claim_in_window(registry_value(SUM_CLAIM_ROW))
    assert not sum_claim_in_window(registry_value("particle.sigma_m_refined_eV"))
    assert not sum_claim_in_window(registry_value("neutrino.sum_masses"))


def test_re_t_check_fails_when_a_row_claims_it_derived(monkeypatch):
    from metaphysica.simulations.core import parameter_artifact

    live = 7.086
    rows = {"cosmology.racetrack_Re_T": {"value": live, "status": "DERIVED"}}
    monkeypatch.setattr(parameter_artifact, "load_parameters", lambda: rows)
    check = ss._re_t_check(live, lambda n: [])
    assert not check["ok"] and check["kind"] == "CONTRADICTION"
    rows["cosmology.racetrack_Re_T"]["status"] = "CALIBRATED"
    assert ss._re_t_check(live, lambda n: [])["ok"]


def test_master_action_26d_has_a_tree_and_every_reference_resolves():
    from metaphysica.config.core_formulas import CoreFormulas
    from metaphysica.simulations.PM.gauge.master_action import MasterActionSimulationV22

    core = {f.id: f for f in CoreFormulas.get_all_formulas()}
    assert "master-action-26d" in core and "master-action-27d" not in core
    sim = {f.id: f for f in MasterActionSimulationV22().get_formulas()}
    assert sim["master-action-26d"].eml_tree_str
    assert "SUPERSEDED" in sim["pneuma-master-action-v23"].description
    for f in core.values():
        for ref in f.related_formulas:
            if ref.startswith("master-action"):
                assert ref in core, "%s -> %s" % (f.id, ref)


def test_the_diagram_constant_points_at_the_selected_action():
    from pathlib import Path

    html = (Path(__file__).resolve().parents[1] / "src" / "metaphysica" / "website"
            / "Pages" / "formulas.html").read_text(encoding="utf-8")
    assert "const MASTER_ACTION_DIAGRAM_ID = 'master-action-26d';" in html
