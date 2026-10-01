"""CG.12: what selects (b_2, b_3) = (12, 43), on every switch path.

The selection composes CG.7 (the reachable family), CG.4 (pi_1 finite only at
n = 3; holonomy exactly G2 there on the compact form) and CG.8 (the bridge <->
component match only on the all-plain n = 3 classes), read through WA-1 -- all
adopted 2026-10-01 (D-015). Two switches decide what the statement may say:
`g2_form_convention` (whether step 2 speaks of holonomy) and `seed_selection`
(whether the match selects or is a finding beside the 2026-09-22 ruling). The
author asked that every switch path read correctly, so each is run here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.closed_geometry import certificate

_FORM = "METAPHYSICA_VARIANT_G2_FORM_CONVENTION"
_ROUTE = "METAPHYSICA_VARIANT_SEED_SELECTION"
_SEED = "METAPHYSICA_VARIANT_B3_SEED"


def _cg12(monkeypatch, form=None, route=None, seed="seed_43_joyce"):
    for env, value in ((_FORM, form), (_ROUTE, route), (_SEED, seed)):
        if value is None:
            monkeypatch.delenv(env, raising=False)
        else:
            monkeypatch.setenv(env, value)
    return {e["id"]: e for e in certificate()}["y7-selection"]


def test_the_selection_lands_on_the_adopted_seed(monkeypatch):
    entry = _cg12(monkeypatch)
    assert entry["label"] == "(CG.12)"
    assert entry["holds"] and entry["derived"]
    assert tuple(entry["evidence"]["selects"]) == (12, 43)
    assert "the seed in force" in entry["statement"]


def test_the_compact_path_speaks_of_holonomy(monkeypatch):
    entry = _cg12(monkeypatch, form="octonion_derived")
    assert "holonomy is exactly G2" in entry["statement"]
    assert entry["evidence"]["riemannian"] is True


def test_the_split_path_says_only_the_topological_half(monkeypatch):
    entry = _cg12(monkeypatch, form="all_plus_one")
    assert entry["holds"]
    assert "no Riemannian holonomy statement" in entry["statement"]
    assert "holonomy is exactly G2" not in entry["statement"]


def test_the_ruling_only_path_reports_a_finding(monkeypatch):
    entry = _cg12(monkeypatch, route="ruling_only")
    assert entry["holds"]
    assert entry["evidence"]["selects"] is None
    assert "2026-09-22 ruling" in entry["statement"]


def test_on_another_member_the_selection_does_not_land(monkeypatch):
    """Falsifiable: on (8, 31) the chain still selects (12, 43), so the
    theorem does not hold there and says so."""
    entry = _cg12(monkeypatch, seed="seed_31_joyce")
    assert entry["derived"]
    assert not entry["holds"]
    assert "NOT the seed in force" in entry["statement"]


def test_off_the_family_nothing_is_derived(monkeypatch):
    entry = _cg12(monkeypatch, seed="seed_24")
    assert not entry["derived"] and not entry["holds"]
    assert "not reachable by the construction" in entry["statement"]


@pytest.mark.parametrize("form", ["octonion_derived", "all_plus_one"])
@pytest.mark.parametrize("route", ["wa1_correspondence", "ruling_only"])
def test_every_switch_path_of_the_selection_reads_and_holds(monkeypatch,
                                                            form, route):
    entry = _cg12(monkeypatch, form=form, route=route)
    assert entry["holds"], (form, route, entry["statement"])
    assert entry["statement"].strip()


def test_the_selection_switch_is_declared_ruled_with_both_options():
    from metaphysica.simulations.core.variants import FORKS

    fork = FORKS["seed_selection"]
    assert fork.status == "RULED"
    assert fork.default() == "wa1_correspondence"
    assert fork.read_adopted() == fork.default()
    assert not fork.option("ruling_only").refuted
