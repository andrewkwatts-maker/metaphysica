"""The master action's open choices are catalogue forks (lane L2b)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metaphysica.simulations.core import variants
from metaphysica.simulations.PM.gauge import master_ladder as ML

FORKS = {1: "action_bulk_sectors", 2: "action_bulk_spinor",
         4: "action_planck_exponent", 5: "action_sign_convention"}
ADOPTED = {"action_bulk_sectors": "undecided", "action_bulk_spinor": "weyl",
           "action_planck_exponent": "exponent_24",
           "action_sign_convention": "mostly_plus_mtw"}


def _under(fork: str, option: str):
    with variants.forced({fork: option}):
        return ML.report()


@pytest.fixture(scope="module")
def default():
    return ML.report()


def test_adopted_option_of_each_fork_is_the_ladder_today():
    for fid, oid in ADOPTED.items():
        assert variants.FORKS[fid].default() == oid
        assert variants.FORKS[fid].read_adopted() == oid
    assert ML.resolve_options() == {k: v[2] for k, v in ML.OWNER_ITEMS.items()}


def test_every_owner_option_has_a_fork_option():
    for item, fid in FORKS.items():
        ids = variants.FORKS[fid].option_ids()
        values = ML.OWNER_ITEMS[item][1]
        assert {ML.option_id(item, v) for v in values} <= set(ids)
        for oid in ids:
            assert ML.option_id(item, ML.option_value(item, oid)) == oid


def test_override_layer_equals_fork_selection(default):
    assert ML.resolve_options({2: "dirac"})[2] == "dirac"
    with variants.forced({"action_bulk_spinor": "dirac"}):
        assert ML.resolve_options()[2] == "dirac"


def test_forks_are_read_by_report():
    variants.reset_reads()
    ML.resolve_options()
    assert all(variants.reads().get(f, 0) >= 1 for f in FORKS.values())


def test_dirac_changes_the_spinor_count(default):
    rep = _under("action_bulk_spinor", "dirac")
    assert rep["owner_items_used"]["2"] == "dirac"
    assert rep["counts"]["open_terms"] == default["counts"]["open_terms"] + 2
    assert rep["failing_checks"] == default["failing_checks"]


@pytest.mark.parametrize("exponent", ["exponent_23", "exponent_25"])
def test_wrong_planck_exponent_breaks_the_gravity_dimension(default, exponent):
    rep = _under("action_planck_exponent", exponent)
    assert {"dim:A26:R", "map:M13_11"} <= set(rep["failing_checks"])
    assert rep["established_counts"]["FAILS"] > default["established_counts"]["FAILS"]


def test_mostly_minus_flips_established_checks_to_fails(default):
    rep = _under("action_sign_convention", "mostly_minus")
    assert default["established_counts"]["FAILS"] == 0
    assert rep["established_counts"]["FAILS"] == 8
    assert rep["established_counts"]["REPRODUCED"] == 21
    assert rep["failing_checks"] == default["failing_checks"]


@pytest.mark.parametrize("sector", ["e8xe8_ym", "flux_f4", "kk_tower"])
def test_choosing_a_sector_resolves_item_1_only(default, sector):
    rep = _under("action_bulk_sectors", sector)
    assert "1" in default["owner_items_unresolved"]
    assert "1" not in rep["owner_items_unresolved"]
    assert rep["counts"] == default["counts"]
    assert rep["established_counts"] == default["established_counts"]


def test_no_sectors_removes_the_item_1_terms(default):
    rep = _under("action_bulk_sectors", "none")
    gone = {"A26:ym", "A26:kT", "A26:V", "A26:L_bridge", "A26:L_C", "A13:V_face"}
    assert gone <= set(default["open_terms"])
    assert not gone & set(rep["open_terms"])
    assert rep["counts"]["open_terms"] == default["counts"]["open_terms"] - len(gone)
